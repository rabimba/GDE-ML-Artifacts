# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Gate G1 (Part 1): Live ZMQ Radix Convergence, Naive Prefix-Herd vs FleetKV Fit Spillover."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys
import time

import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

from fork_storm_workload import (  # noqa: E402
    _make_exact_tokens,
    build_shared_trunk_system_message,
    scrape_prometheus_totals,
    send_streaming_completion,
)
from stack_harness import running_envoy_twin_stack  # noqa: E402


def _wait_for_indexed_blocks(epp_admin_url: str, min_blocks: int, timeout_sec: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout_sec
    state = {}
    while time.monotonic() < deadline:
        r = httpx.get(f"{epp_admin_url}/admin/state", timeout=2.0)
        r.raise_for_status()
        state = r.json()
        if int(state.get("indexed_blocks", 0)) >= min_blocks:
            return state
        time.sleep(0.05)
    raise AssertionError(f"Timed out waiting for >= {min_blocks} indexed ZMQ blocks; state={state}")


def test_zmq_radix_index_and_naive_herd_vs_fleetkv_fit_spillover() -> None:
    # Use hbm_capacity_blocks=220 so an 80-block trunk leaves 140 free blocks on agg-0.
    # Under an 8-way concurrent fork with 8192-token branch horizon hints (~35 est blocks/branch),
    # naive_sticky herds 8/8 branches onto agg-0, whereas fleetkv_fit spills overflow branches to agg-1!
    with running_envoy_twin_stack(hbm_capacity_blocks=220, num_agg_pods=2) as stack:
        trunk_msg = build_shared_trunk_system_message(incident_id=42)

        # --- Phase A: Naive Longest-Prefix Sticky Routing ---
        stack.set_policy("naive_sticky", "agg")

        async def _run_fork(horizon_hint: int) -> list[str]:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Warm the 20,480-token (80-block) shared trunk on one pod
                seed = await send_streaming_completion(
                    client,
                    stack.gateway_url,
                    messages=[trunk_msg, {"role": "user", "content": _make_exact_tokens(62, "seed42")}],
                    max_tokens=4,
                )
                assert seed.served_by_pod in ("agg-0", "agg-1")

                # Wait for ZeroMQ BlockStored event to populate >= 80 blocks in Go Radix Tree
                _wait_for_indexed_blocks(stack.epp_admin_url, min_blocks=80)

                # 2. Fire 8 concurrent sub-agent branches sharing the exact 80-block trunk
                async def _branch(b: int) -> str:
                    s = await send_streaming_completion(
                        client,
                        stack.gateway_url,
                        messages=[
                            trunk_msg,
                            {"role": "user", "content": _make_exact_tokens(510, f"forkb{b}")},
                        ],
                        max_tokens=10,
                        horizon_hint_tokens=horizon_hint,
                    )
                    return s.served_by_pod

                return list(await asyncio.gather(*(_branch(i) for i in range(8))))

        naive_pods = asyncio.run(_run_fork(horizon_hint=8192))
        unique_naive_pods = set(naive_pods)
        assert len(unique_naive_pods) == 1, (
            f"Expected naive_sticky to herd all 8 forked branches onto 1 pod; got {naive_pods}"
        )

        # --- Phase B: FleetKV Fit-Aware Admission Gate ---
        stack.reset_all()
        stack.set_policy("fleetkv_fit", "agg")

        fit_pods = asyncio.run(_run_fork(horizon_hint=8192))
        agg0_count = fit_pods.count("agg-0")
        agg1_count = fit_pods.count("agg-1")

        assert agg0_count > 0 and agg1_count > 0, (
            f"Expected FleetKV Fit Gate to spread 8-way fork across agg-0 and agg-1; got {fit_pods}"
        )

        async def _check_spillovers() -> float:
            async with httpx.AsyncClient() as c:
                m = await scrape_prometheus_totals(c, [], f"{stack.epp_admin_url}/metrics")
                return m["herd_spillovers"]

        spillovers = asyncio.run(_check_spillovers())
        assert spillovers > 0, f"Expected fleetkv_herd_spillovers_total > 0, got {spillovers}"
