# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Gate G1 (Part 2): Full End-to-End 3-Stage Physics & Envoy ext_proc Verification."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))
sys.path.insert(0, str(REPO_ROOT / "tests"))

from fork_storm_workload import StageWaveReport, execute_benchmark_waves  # noqa: E402
from stack_harness import running_envoy_twin_stack  # noqa: E402


def test_e2e_three_stage_fork_storm_physics_and_slos() -> None:
    with running_envoy_twin_stack(hbm_capacity_blocks=360, num_agg_pods=4) as stack:
        # ------------------------------------------------------------------
        # STAGE 1: Standard Stateless Kubernetes Round-Robin (4x Aggregated)
        # ------------------------------------------------------------------
        stack.reset_all()
        stack.set_policy("round_robin", "agg")
        time.sleep(0.15)

        s1: StageWaveReport = asyncio.run(
            execute_benchmark_waves(
                gateway_url=stack.gateway_url,
                worker_metrics_urls=stack.agg_metrics_urls,
                epp_metrics_url=f"{stack.epp_admin_url}/metrics",
                stage_name="stage1-round-robin",
                num_waves=2,
                orchestrators_per_wave=8,
                num_branches=8,
                turns_per_branch=3,
                output_tokens_per_turn=5,
                stagger_sec=0.16,
                incident_base_id=100,
            )
        )

        # ------------------------------------------------------------------
        # STAGE 2: Naive Longest-Prefix Sticky Routing (Prefix-Herd Trap!)
        # ------------------------------------------------------------------
        stack.reset_all()
        stack.set_policy("naive_sticky", "agg")
        time.sleep(0.15)

        s2: StageWaveReport = asyncio.run(
            execute_benchmark_waves(
                gateway_url=stack.gateway_url,
                worker_metrics_urls=stack.agg_metrics_urls,
                epp_metrics_url=f"{stack.epp_admin_url}/metrics",
                stage_name="stage2-naive-kv",
                num_waves=2,
                orchestrators_per_wave=8,
                num_branches=8,
                turns_per_branch=3,
                output_tokens_per_turn=5,
                stagger_sec=0.16,
                incident_base_id=200,
            )
        )

        # ------------------------------------------------------------------
        # STAGE 3: FleetKV Fit-Aware + Disaggregated Serving (TPUConnectorHMA)
        # ------------------------------------------------------------------
        stack.reset_all()
        stack.set_policy("fleetkv_fit", "disagg")
        time.sleep(0.15)

        s3: StageWaveReport = asyncio.run(
            execute_benchmark_waves(
                gateway_url=stack.gateway_url,
                worker_metrics_urls=stack.disagg_metrics_urls,
                epp_metrics_url=f"{stack.epp_admin_url}/metrics",
                stage_name="stage3-fleetkv-disagg",
                num_waves=2,
                orchestrators_per_wave=8,
                num_branches=8,
                turns_per_branch=3,
                output_tokens_per_turn=5,
                stagger_sec=0.16,
                incident_base_id=300,
            )
        )

        summary = {
            "stage1": s1.__dict__,
            "stage2": s2.__dict__,
            "stage3": s3.__dict__,
        }
        print("\n=== GATE G1 EMPIRICAL 3-STAGE SCORECARD ===")
        print(json.dumps(summary, indent=2))

        # Gate G1.1: Stage 1 suffers 1/N scatter misses (<35% hit rate) & P/D interference (P99 ITL > 80ms)
        assert s1.cache_hit_rate_pct < 35.0, (
            f"Expected stage1 cache hit rate < 35%, got {s1.cache_hit_rate_pct:.2f}%"
        )
        assert s1.p99_itl_ms > 80.0, (
            f"Expected stage1 P99 ITL > 80ms due to P/D interference, got {s1.p99_itl_ms:.2f}ms"
        )

        # Gate G1.2: Stage 2 (naive_sticky) triggers HBM evictions > 0 & P95 TTFT >= 2.5x Stage 3 P95 TTFT
        assert s2.hbm_evictions > 0, (
            f"Expected stage2 HBM evictions > 0 under Prefix-Herd Trap, got {s2.hbm_evictions}"
        )
        assert s2.p95_ttft_ms >= 2.5 * s3.p95_ttft_ms, (
            f"Expected stage2 P95 TTFT ({s2.p95_ttft_ms:.1f}ms) >= 2.5x stage3 P95 TTFT ({s3.p95_ttft_ms:.1f}ms)"
        )

        # Gate G1.3: Stage 3 achieves >85% hit rate, >70% P50 TTFT reduction vs Stage 1, and P99 ITL < 40ms
        assert s3.cache_hit_rate_pct > 85.0, (
            f"Expected stage3 cache hit rate > 85%, got {s3.cache_hit_rate_pct:.2f}%"
        )
        p50_reduction_pct = (1.0 - (s3.p50_ttft_ms / s1.p50_ttft_ms)) * 100.0
        assert p50_reduction_pct > 70.0, (
            f"Expected stage3 P50 TTFT reduction > 70% vs stage1, got {p50_reduction_pct:.1f}% "
            f"(s1={s1.p50_ttft_ms:.1f}ms, s3={s3.p50_ttft_ms:.1f}ms)"
        )
        assert s3.p99_itl_ms < 40.0, (
            f"Expected stage3 P99 ITL < 40ms on isolated decode pods, got {s3.p99_itl_ms:.2f}ms"
        )
