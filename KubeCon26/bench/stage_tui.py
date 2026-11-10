#!/usr/bin/env python3
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""KubeCon 2026 Live Stage Scorecard TUI (10-Second Sliding Window).

Renders a high-contrast 4-column Rich dashboard comparing:
  Metric | Stage 1: K8s Round-Robin | Stage 2: Naive KV-Sticky | Stage 3: FleetKV + Disagg
Automatically snapshots & freezes completed stages as `demo_ctl.sh` flips traffic.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import sys
import time

import httpx
from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fork_storm_workload import (  # noqa: E402
    SlidingMetricsWindow,
    WindowSnapshot,
    continuous_orchestrator_fleet,
    run_orchestrator_episode,
    scrape_prometheus_totals,
)

STAGE_STAGE1 = "stage1"
STAGE_STAGE2 = "stage2"
STAGE_STAGE3 = "stage3"


def policy_to_stage(policy: str, pool: str = "") -> str:
    p = (policy or "").strip().lower()
    if p == "round_robin":
        return STAGE_STAGE1
    if p == "naive_sticky":
        return STAGE_STAGE2
    return STAGE_STAGE3


def _fmt_pod_split(dist: dict[str, int]) -> str:
    if not dist:
        return "—"
    total = max(1, sum(dist.values()))
    top = sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    return " · ".join(f"{k}:{int(round(v * 100.0 / total))}%" for k, v in top)


def _fmt_col_cell(
    snap: WindowSnapshot | None,
    metric_key: str,
    stage_id: str,
    baseline_snap: WindowSnapshot | None = None,
) -> str:
    if snap is None or snap.requests_completed == 0:
        return "[dim]—[/dim]"

    if metric_key == "hit_rate":
        val = f"{snap.cache_hit_rate_pct:5.1f} %"
        if stage_id == STAGE_STAGE3 and snap.cache_hit_rate_pct >= 80.0:
            return f"[bold green]{val}[/bold green]"
        if stage_id == STAGE_STAGE1 and snap.cache_hit_rate_pct < 35.0:
            return f"[bold red]{val}[/bold red]"
        return f"[yellow]{val}[/yellow]"

    if metric_key == "p50_ttft":
        val = f"{snap.p50_ttft_ms:,.0f} ms"
        if stage_id == STAGE_STAGE3 and baseline_snap and baseline_snap.p50_ttft_ms > 0:
            red = (1.0 - snap.p50_ttft_ms / baseline_snap.p50_ttft_ms) * 100.0
            return f"[bold green]{val} ({-red:+.0f}%)[/bold green]"
        return val

    if metric_key == "p95_ttft":
        val = f"{snap.p95_ttft_ms:,.0f} ms"
        if stage_id == STAGE_STAGE2:
            return f"[bold red]{val} (HERD!)[/bold red]"
        if stage_id == STAGE_STAGE3:
            return f"[bold green]{val}[/bold green]"
        return val

    if metric_key == "p99_itl":
        val = f"{snap.p99_itl_ms:,.1f} ms"
        if snap.p99_itl_ms > 80.0:
            return f"[bold red]{val}[/bold red]"
        if snap.p99_itl_ms < 40.0:
            return f"[bold green]{val}[/bold green]"
        return f"[yellow]{val}[/yellow]"

    if metric_key == "goodput":
        val = f"{snap.goodput_tok_per_s:,.1f} tok/s"
        if stage_id == STAGE_STAGE3 and baseline_snap and baseline_snap.goodput_tok_per_s > 0:
            mult = snap.goodput_tok_per_s / baseline_snap.goodput_tok_per_s
            return f"[bold green]{val} ({mult:.2f}x)[/bold green]"
        return val

    if metric_key == "evictions":
        if snap.hbm_evictions > 0:
            return f"[bold red]{snap.hbm_evictions:,}[/bold red]"
        return "[green]0[/green]"

    if metric_key == "spillovers":
        if snap.herd_spillovers > 0:
            return f"[bold cyan]{snap.herd_spillovers:,}[/bold cyan]"
        return "0"

    if metric_key == "pods":
        return _fmt_pod_split(snap.pod_distribution)

    return "—"


def build_dashboard_renderable(
    active_stage: str,
    live_snap: WindowSnapshot,
    frozen_snaps: dict[str, WindowSnapshot],
    gateway_url: str,
    active_policy: str,
    active_pool: str,
) -> Group:
    def _header(title: str, stage_id: str) -> str:
        if active_stage == stage_id:
            return f"[bold bright_white on blue] {title} (LIVE) [/bold bright_white on blue]"
        if stage_id in frozen_snaps:
            return f"[bold cyan]{title} [FROZEN][/bold cyan]"
        return f"[dim]{title} (PENDING)[/dim]"

    def _stage_snap(stage_id: str) -> WindowSnapshot | None:
        if active_stage == stage_id:
            return live_snap
        return frozen_snaps.get(stage_id)

    s1 = _stage_snap(STAGE_STAGE1)
    s2 = _stage_snap(STAGE_STAGE2)
    s3 = _stage_snap(STAGE_STAGE3)

    table = Table(
        box=box.HEAVY_HEAD,
        expand=True,
        show_lines=True,
        header_style="bold white",
        padding=(0, 1),
    )
    table.add_column("Metric (10s Sliding Window)", style="bold white", ratio=24)
    table.add_column(_header("Stage 1: K8s Round-Robin", STAGE_STAGE1), justify="right", ratio=25)
    table.add_column(_header("Stage 2: Naive KV-Sticky", STAGE_STAGE2), justify="right", ratio=25)
    table.add_column(_header("Stage 3: FleetKV + Disagg", STAGE_STAGE3), justify="right", ratio=26)

    rows = [
        ("Effective Prefix Hit Rate", "hit_rate"),
        ("Median TTFT (P50)", "p50_ttft"),
        ("Fork-Burst Tail TTFT (P95)", "p95_ttft"),
        ("Decode Jitter (P99 ITL)", "p99_itl"),
        ("Cluster Output Goodput", "goodput"),
        ("HBM Block Evictions", "evictions"),
        ("Fit-Gated Herd Spillovers", "spillovers"),
        ("Pod Traffic Distribution", "pods"),
    ]
    for label, key in rows:
        table.add_row(
            label,
            _fmt_col_cell(s1, key, STAGE_STAGE1, None),
            _fmt_col_cell(s2, key, STAGE_STAGE2, s1),
            _fmt_col_cell(s3, key, STAGE_STAGE3, s1),
        )

    banner = Panel(
        Text.from_markup(
            f"[bold bright_cyan]FleetKV Live Agent Fork-Storm Telemetry[/bold bright_cyan]  ·  "
            f"Model: [bold]Qwen/Qwen3-30B-A3B-FP8[/bold]  ·  "
            f"Workload: [bold]8 Orchestrators × 8-Way Fork (20K Trunk + 8K Log Burst)[/bold]\n"
            f"Gateway: [underline]{gateway_url}[/underline]  ·  "
            f"Active Router Policy: [bold yellow]{active_policy}[/bold yellow] ([cyan]{active_pool}[/cyan])"
        ),
        border_style="bright_blue",
    )
    return Group(banner, table)


async def query_active_router_policy(client: httpx.AsyncClient, epp_admin_url: str) -> tuple[str, str]:
    try:
        r = await client.get(f"{epp_admin_url.rstrip('/')}/admin/policy", timeout=1.5)
        if r.status_code == 200:
            data = r.json()
            return str(data.get("policy", "round_robin")), str(data.get("pool", "agg"))
    except Exception:
        pass
    return "round_robin", "agg"


async def set_router_policy(client: httpx.AsyncClient, epp_admin_url: str, policy: str, pool: str) -> None:
    resp = await client.post(
        f"{epp_admin_url.rstrip('/')}/admin/policy",
        json={"policy": policy, "pool": pool},
        timeout=3.0,
    )
    resp.raise_for_status()


async def run_tui_loop(args: argparse.Namespace) -> None:
    console = Console(force_terminal=not args.smoke_test, width=140)
    window = SlidingMetricsWindow(window_sec=args.window_sec)
    frozen_snaps: dict[str, WindowSnapshot] = {}
    worker_urls = [u.strip() for u in args.worker_metrics.split(",") if u.strip()]
    epp_metrics_url = f"{args.epp_admin_url.rstrip('/')}/metrics"

    stop_event = asyncio.Event()

    async with httpx.AsyncClient(timeout=30.0) as ctrl_client:
        if args.smoke_test:
            # Ensure clean Stage 1 start for deterministic 3-stage smoke run
            await set_router_policy(ctrl_client, args.epp_admin_url, "round_robin", "agg")

        active_policy, active_pool = await query_active_router_policy(ctrl_client, args.epp_admin_url)
        active_stage = policy_to_stage(active_policy, active_pool)
        window.expected_policy = active_policy

        # Seed initial Prometheus baseline counters
        init_prom = await scrape_prometheus_totals(ctrl_client, worker_urls, epp_metrics_url)
        window.record_prom_counters(
            time.monotonic(),
            int(init_prom["cache_hits"]),
            int(init_prom["cache_queries"]),
            int(init_prom["hbm_evictions"]),
            int(init_prom["herd_spillovers"]),
        )

        if args.smoke_test:
            # Fast smoke workload so 6-second CI verification exercises all 3 stages cleanly
            async def _smoke_driver() -> None:
                limits = httpx.Limits(max_connections=128, max_keepalive_connections=64)
                async with httpx.AsyncClient(limits=limits, timeout=30.0) as w_client:
                    idx = 0
                    while not stop_event.is_set():
                        idx += 1
                        try:
                            await run_orchestrator_episode(
                                client=w_client,
                                gateway_url=args.gateway_url,
                                incident_id=700 + (idx % 4),
                                window=window,
                                num_branches=4,
                                turns_per_branch=1,
                                output_tokens_per_turn=3,
                            )
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            await asyncio.sleep(0.05)

            fleet_task = asyncio.create_task(_smoke_driver())
        else:
            fleet_task = asyncio.create_task(
                continuous_orchestrator_fleet(
                    stop_event=stop_event,
                    gateway_url=args.gateway_url,
                    window=window,
                    num_orchestrators=args.orchestrators,
                    num_branches=8,
                )
            )

        t_start = time.monotonic()
        smoke_flipped_stage2 = False
        smoke_flipped_stage3 = False

        try:
            with Live(
                build_dashboard_renderable(
                    active_stage,
                    window.snapshot(),
                    frozen_snaps,
                    args.gateway_url,
                    active_policy,
                    active_pool,
                ),
                console=console,
                refresh_per_second=4,
                transient=False,
            ) as live:
                while True:
                    await asyncio.sleep(0.35)
                    elapsed = time.monotonic() - t_start

                    # Smoke-test automatic stage stepping: Stage 1 -> Stage 2 -> Stage 3
                    if args.smoke_test:
                        third = args.duration_sec / 3.0
                        if elapsed >= third and not smoke_flipped_stage2:
                            smoke_flipped_stage2 = True
                            await set_router_policy(ctrl_client, args.epp_admin_url, "naive_sticky", "agg")
                        elif elapsed >= 2.0 * third and not smoke_flipped_stage3:
                            smoke_flipped_stage3 = True
                            await set_router_policy(ctrl_client, args.epp_admin_url, "fleetkv_fit", "disagg")

                    pol, pool = await query_active_router_policy(ctrl_client, args.epp_admin_url)
                    detected_stage = policy_to_stage(pol, pool)

                    prom = await scrape_prometheus_totals(ctrl_client, worker_urls, epp_metrics_url)
                    now = time.monotonic()
                    window.record_prom_counters(
                        now,
                        int(prom["cache_hits"]),
                        int(prom["cache_queries"]),
                        int(prom["hbm_evictions"]),
                        int(prom["herd_spillovers"]),
                    )

                    if detected_stage != active_stage:
                        # Freeze completed stage snapshot into its column!
                        frozen_snaps[active_stage] = window.snapshot(now)
                        window.reset(expected_policy=pol)
                        window.record_prom_counters(
                            now,
                            int(prom["cache_hits"]),
                            int(prom["cache_queries"]),
                            int(prom["hbm_evictions"]),
                            int(prom["herd_spillovers"]),
                        )
                        active_stage = detected_stage

                    active_policy, active_pool = pol, pool
                    live_snap = window.snapshot(now)
                    live.update(
                        build_dashboard_renderable(
                            active_stage,
                            live_snap,
                            frozen_snaps,
                            args.gateway_url,
                            active_policy,
                            active_pool,
                        )
                    )

                    if args.duration_sec > 0 and elapsed >= args.duration_sec:
                        break
        finally:
            stop_event.set()
            fleet_task.cancel()
            await asyncio.gather(fleet_task, return_exceptions=True)

        if args.smoke_test:
            final_s3 = window.snapshot()
            if STAGE_STAGE1 not in frozen_snaps or STAGE_STAGE2 not in frozen_snaps:
                raise RuntimeError(f"Expected Stage 1 & Stage 2 frozen snapshots; got {list(frozen_snaps.keys())}")
            if final_s3.requests_completed == 0:
                raise RuntimeError("Stage 3 live column recorded 0 completed requests during smoke test")
            console.print(
                f"[bold green]SMOKE TEST PASSED:[/bold green] "
                f"Stage1={frozen_snaps[STAGE_STAGE1].requests_completed} reqs (frozen), "
                f"Stage2={frozen_snaps[STAGE_STAGE2].requests_completed} reqs (frozen), "
                f"Stage3={final_s3.requests_completed} reqs (live)."
            )


async def run_watch_epp_loop(args: argparse.Namespace) -> None:
    """Renders live FleetKV EPP Radix Tree state & recent ext_proc decisions for Pane 2."""
    console = Console()
    t0 = time.monotonic()
    async with httpx.AsyncClient(timeout=2.5) as client:
        with Live(console=console, refresh_per_second=2, transient=False) as live:
            while True:
                try:
                    r = await client.get(f"{args.epp_admin_url.rstrip('/')}/admin/state")
                    r.raise_for_status()
                    st = r.json()
                    cfg = st.get("config", {})
                    pod_tbl = Table(box=box.SIMPLE_HEAD, expand=True, padding=(0, 1))
                    pod_tbl.add_column("Pod", style="bold cyan")
                    pod_tbl.add_column("Role")
                    pod_tbl.add_column("Free HBM", justify="right")
                    pod_tbl.add_column("Resv", justify="right")
                    pod_tbl.add_column("Active", justify="right")
                    for p in st.get("pods", []):
                        pod_tbl.add_row(
                            str(p.get("pod_id", "")),
                            str(p.get("role", "")),
                            str(p.get("free_hbm_blocks", 0)),
                            str(p.get("reserved_blocks", 0)),
                            str(p.get("active_requests", 0)),
                        )

                    dec_lines: list[str] = []
                    for d in st.get("recent_decisions", [])[-6:]:
                        sel = d.get("selected_pod_id") or "envoy-rr"
                        pref = d.get("prefill_pod_id") or "-"
                        matched = int(d.get("matched_hbm_blocks", 0)) + int(d.get("matched_dram_blocks", 0))
                        tot = int(d.get("total_prompt_blocks", 0))
                        dec_lines.append(
                            f"[cyan]{sel:9s}[/cyan] prefill=[magenta]{pref:9s}[/magenta] "
                            f"kv=[green]{matched:3d}/{tot:3d}[/green] {d.get('reason', '')}"
                        )
                    dec_panel = Panel(
                        Text.from_markup("\n".join(dec_lines) if dec_lines else "[dim]Waiting for traffic...[/dim]"),
                        title="Recent ext_proc Decisions",
                        border_style="blue",
                    )
                    hdr = Panel(
                        Text.from_markup(
                            f"[bold]FleetKV EPP Radix Stream[/bold] · "
                            f"Policy: [yellow]{cfg.get('policy')}[/yellow] ([cyan]{cfg.get('pool')}[/cyan]) · "
                            f"Indexed Blocks: [bold green]{st.get('indexed_blocks', 0)}[/bold green]"
                        ),
                        border_style="bright_blue",
                    )
                    live.update(Group(hdr, pod_tbl, dec_panel))
                except Exception as exc:
                    live.update(Panel(f"Connecting to EPP at {args.epp_admin_url}... ({exc})"))

                if args.duration_sec > 0 and (time.monotonic() - t0) >= args.duration_sec:
                    break
                await asyncio.sleep(0.5)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FleetKV 3-Stage Live Conference Scorecard TUI")
    parser.add_argument(
        "--gateway-url",
        default=os.environ.get("FLEETKV_GATEWAY_URL", "http://127.0.0.1:8080"),
    )
    parser.add_argument(
        "--epp-admin-url",
        default=os.environ.get("FLEETKV_EPP_ADMIN_URL", "http://127.0.0.1:9090"),
    )
    parser.add_argument(
        "--worker-metrics",
        default=os.environ.get(
            "FLEETKV_WORKER_METRICS",
            "http://127.0.0.1:8001/metrics,http://127.0.0.1:8002/metrics,http://127.0.0.1:8003/metrics,http://127.0.0.1:8004/metrics,http://127.0.0.1:8005/metrics,http://127.0.0.1:8006/metrics,http://127.0.0.1:8007/metrics,http://127.0.0.1:8008/metrics",
        ),
    )
    parser.add_argument("--window-sec", type=float, default=10.0)
    parser.add_argument("--orchestrators", type=int, default=8)
    parser.add_argument("--duration-sec", type=float, default=0.0, help="0 = run until Ctrl-C")
    parser.add_argument("--smoke-test", action="store_true", help="Non-interactive 3-stage verification run")
    parser.add_argument("--watch-epp", action="store_true", help="Render live EPP Radix & decision stream pane")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.watch_epp:
        try:
            asyncio.run(run_watch_epp_loop(args))
        except KeyboardInterrupt:
            pass
        return
    if args.smoke_test and args.duration_sec <= 0:
        args.duration_sec = 6.0
    try:
        asyncio.run(run_tui_loop(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
