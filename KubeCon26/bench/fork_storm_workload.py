#!/usr/bin/env python3
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Multi-Agent Fork-Storm Workload Generator & 10s Sliding-Window Telemetry Collector.

Simulates concurrent SRE Incident Triage Orchestrators:
  1. Deterministic 20,480-token (80 x 256-tok blocks) shared MCP + Repo AST trunk
  2. Immediate 8-way parallel Sub-Agent Fork (64 active branches across 8 orchestrators)
  3. 4 sequential tool-use turns per sub-agent (including an 8,192-token kubectl logs burst on Turn 2)
  4. Final Orchestrator synthesis Join turn
"""

from __future__ import annotations

import argparse
import asyncio
from collections import deque
from dataclasses import dataclass, field
import json
import math
import re
import time
from typing import Any

import httpx

MODEL_NAME = "Qwen/Qwen3-30B-A3B-FP8"
BLOCK_SIZE = 256

# Note: ChatML framing adds deterministic special-token boundaries per message.
# We generate exact token budgets so prompt blocks align cleanly on 256-token boundaries.
GLOBAL_MCP_BLOCKS = 2           # 512 tokens shared MCP bootstrap across all SRE orchestrators
INCIDENT_AST_BLOCKS = 78        # 19,968 tokens per incident -> 80 blocks (20,480 tokens) total trunk!
TURN1_DELTA_BLOCKS = 2          # 512 tokens specialist role prompt
TURN2_SHARED_LOG_BLOCKS = 28    # 7,168 tokens shared pod crash stream per pod group
TURN2_FILTER_BLOCKS = 4         # 1,024 tokens specialist trace/log filter analysis
TURN2_LOG_BURST_BLOCKS = TURN2_SHARED_LOG_BLOCKS + TURN2_FILTER_BLOCKS  # 32 blocks (8,192 tokens)
TURN3_DELTA_BLOCKS = 2          # 512 tokens git blame / envoy config dump
TURN4_DELTA_BLOCKS = 2          # 512 tokens remediation verification
JOIN_SYNTH_BLOCKS = 4           # 1,024 tokens synthesis join summary

_TOKEN_SEQ_CACHE: dict[tuple[int, str], str] = {}


def _make_exact_tokens(num_tokens: int, tag: str) -> str:
    """Generates exact count of <=16-byte deterministic tokens (memoized to prevent client loop jitter)."""
    short_tag = tag[:8]
    key = (num_tokens, short_tag)
    cached = _TOKEN_SEQ_CACHE.get(key)
    if cached is not None:
        return cached
    built = " ".join(f"{short_tag}_{i:05x}" for i in range(num_tokens))
    _TOKEN_SEQ_CACHE[key] = built
    return built


_GLOBAL_MCP_TEXT = _make_exact_tokens(GLOBAL_MCP_BLOCKS * BLOCK_SIZE - 2, "mcp")
_EPISODE_TRUNK_CACHE: dict[int, str] = {}
_POD_LOG_CACHE: dict[tuple[int, int], str] = {}


def build_shared_trunk_system_message(incident_id: int) -> dict[str, str]:
    """Builds the deterministic 20,480-token (80-block) shared MCP + Repo AST trunk."""
    if incident_id not in _EPISODE_TRUNK_CACHE:
        ast_text = _make_exact_tokens(INCIDENT_AST_BLOCKS * BLOCK_SIZE - 1, f"ast{incident_id % 1000:03d}")
        _EPISODE_TRUNK_CACHE[incident_id] = f"{_GLOBAL_MCP_TEXT} {ast_text}"
    return {"role": "system", "content": _EPISODE_TRUNK_CACHE[incident_id]}


def get_pod_crash_logs(incident_id: int, log_group: int) -> str:
    key = (incident_id, log_group)
    if key not in _POD_LOG_CACHE:
        # 28 blocks (7,168 tokens) of shared pod crash dump per pod group
        _POD_LOG_CACHE[key] = _make_exact_tokens(
            TURN2_SHARED_LOG_BLOCKS * BLOCK_SIZE,
            f"klog{incident_id % 100:02d}{log_group}",
        )
    return _POD_LOG_CACHE[key]


@dataclass
class RequestSample:
    completed_ts: float
    ttft_ms: float
    itl_samples_ms: list[float]
    output_tokens: int
    prompt_tokens_est: int
    served_by_pod: str
    policy: str
    reason: str


@dataclass
class WindowSnapshot:
    p50_ttft_ms: float = 0.0
    p95_ttft_ms: float = 0.0
    p99_itl_ms: float = 0.0
    goodput_tok_per_s: float = 0.0
    cache_hit_rate_pct: float = 0.0
    hbm_evictions: int = 0
    herd_spillovers: int = 0
    requests_completed: int = 0
    pod_distribution: dict[str, int] = field(default_factory=dict)


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    rank = (pct / 100.0) * (len(sorted_vals) - 1)
    low = int(math.floor(rank))
    high = int(math.ceil(rank))
    if low == high:
        return sorted_vals[low]
    weight = rank - low
    return sorted_vals[low] * (1.0 - weight) + sorted_vals[high] * weight


class SlidingMetricsWindow:
    """Maintains a 10-second timestamped ring buffer of TTFT, ITL, Goodput, and Prometheus deltas."""

    def __init__(self, window_sec: float = 10.0) -> None:
        self.window_sec = window_sec
        self.expected_policy: str = ""
        self.samples: deque[RequestSample] = deque()
        self.prom_history: deque[tuple[float, int, int, int, int]] = deque()
        # tuple: (ts, cache_hits, cache_queries, hbm_evictions, herd_spillovers)

    def reset(self, expected_policy: str = "") -> None:
        self.expected_policy = expected_policy
        self.samples.clear()
        self.prom_history.clear()

    def record_request(self, sample: RequestSample) -> None:
        if self.expected_policy and sample.policy and sample.policy != self.expected_policy:
            return
        self.samples.append(sample)
        self._prune(sample.completed_ts)

    def record_prom_counters(
        self,
        ts: float,
        hits: int,
        queries: int,
        evictions: int,
        spillovers: int,
    ) -> None:
        self.prom_history.append((ts, hits, queries, evictions, spillovers))
        cutoff = ts - self.window_sec
        while len(self.prom_history) > 2 and self.prom_history[0][0] < cutoff:
            self.prom_history.popleft()

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_sec
        while self.samples and self.samples[0].completed_ts < cutoff:
            self.samples.popleft()

    def snapshot(self, now: float | None = None) -> WindowSnapshot:
        if now is None:
            now = time.monotonic()
        self._prune(now)

        if not self.samples:
            return WindowSnapshot()

        ttfts = sorted(s.ttft_ms for s in self.samples)
        all_itls = sorted(itl for s in self.samples for itl in s.itl_samples_ms)
        total_out_toks = sum(s.output_tokens for s in self.samples)

        earliest = self.samples[0].completed_ts
        span_sec = max(1.0, min(self.window_sec, now - earliest + 0.25))
        goodput = total_out_toks / span_sec

        pods: dict[str, int] = {}
        for s in self.samples:
            if s.served_by_pod:
                pods[s.served_by_pod] = pods.get(s.served_by_pod, 0) + 1

        hit_rate_pct = 0.0
        evictions_delta = 0
        spillovers_delta = 0
        if len(self.prom_history) >= 2:
            _, h0, q0, ev0, sp0 = self.prom_history[0]
            _, h1, q1, ev1, sp1 = self.prom_history[-1]
            dq = q1 - q0
            dh = h1 - h0
            if dq > 0:
                hit_rate_pct = max(0.0, min(100.0, (dh / float(dq)) * 100.0))
            evictions_delta = max(0, ev1 - ev0)
            spillovers_delta = max(0, sp1 - sp0)
        elif len(self.prom_history) == 1:
            _, h1, q1, ev1, sp1 = self.prom_history[0]
            if q1 > 0:
                hit_rate_pct = max(0.0, min(100.0, (h1 / float(q1)) * 100.0))
            evictions_delta = ev1
            spillovers_delta = sp1

        return WindowSnapshot(
            p50_ttft_ms=_percentile(ttfts, 50.0),
            p95_ttft_ms=_percentile(ttfts, 95.0),
            p99_itl_ms=_percentile(all_itls, 99.0),
            goodput_tok_per_s=goodput,
            cache_hit_rate_pct=hit_rate_pct,
            hbm_evictions=evictions_delta,
            herd_spillovers=spillovers_delta,
            requests_completed=len(self.samples),
            pod_distribution=pods,
        )


_METRIC_LINE_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)$")


async def scrape_prometheus_totals(
    client: httpx.AsyncClient,
    worker_metrics_urls: list[str],
    epp_metrics_url: str | None = None,
) -> dict[str, float]:
    """Scrapes vLLM / Twin worker & FleetKV EPP Prometheus counters."""
    totals = {
        "cache_hits": 0.0,
        "cache_queries": 0.0,
        "hbm_evictions": 0.0,
        "herd_spillovers": 0.0,
        "max_cache_usage_perc": 0.0,
    }

    async def _fetch(url: str) -> str:
        try:
            r = await client.get(url, timeout=2.0)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        return ""

    urls = list(worker_metrics_urls)
    if epp_metrics_url:
        urls.append(epp_metrics_url)

    texts = await asyncio.gather(*(_fetch(u) for u in urls))
    for text in texts:
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            m = _METRIC_LINE_RE.match(line)
            if not m:
                continue
            name, val_s = m.group(1), m.group(2)
            val = float(val_s)
            if name == "vllm:prefix_cache_hits_total":
                totals["cache_hits"] += val
            elif name == "vllm:prefix_cache_queries_total":
                totals["cache_queries"] += val
            elif name == "fleetkv_twin_hbm_evictions_total":
                totals["hbm_evictions"] += val
            elif name == "fleetkv_herd_spillovers_total":
                totals["herd_spillovers"] += val
            elif name == "vllm:gpu_cache_usage_perc":
                totals["max_cache_usage_perc"] = max(totals["max_cache_usage_perc"], val * 100.0)
    return totals


async def send_streaming_completion(
    client: httpx.AsyncClient,
    gateway_url: str,
    messages: list[dict[str, str]],
    max_tokens: int = 8,
    horizon_hint_tokens: int = 0,
    stage_override: str = "",
) -> RequestSample:
    """Streams an OpenAI SSE /v1/chat/completions request and records exact TTFT & ITL."""
    headers = {"Content-Type": "application/json"}
    if horizon_hint_tokens > 0:
        headers["x-branch-horizon-hint"] = str(horizon_hint_tokens)
    if stage_override:
        headers["x-fleetkv-stage"] = stage_override

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True,
    }

    t_start = time.monotonic()
    t_first: float | None = None
    t_prev: float | None = None
    itls_ms: list[float] = []
    out_tokens = 0
    served_by = ""
    policy = ""
    reason = ""

    async with client.stream(
        "POST",
        f"{gateway_url.rstrip('/')}/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60.0,
    ) as resp:
        resp.raise_for_status()
        served_by = (
            resp.headers.get("x-served-by-pod")
            or resp.headers.get("x-fleetkv-selected-pod")
            or ""
        )
        policy = resp.headers.get("x-fleetkv-policy", "")
        reason = resp.headers.get("x-fleetkv-reason", "")

        async for line in resp.aiter_lines():
            if not line or not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                break
            now = time.monotonic()
            if t_first is None:
                t_first = now
            elif t_prev is not None:
                itls_ms.append((now - t_prev) * 1000.0)
            t_prev = now
            out_tokens += 1

    t_done = time.monotonic()
    ttft_ms = ((t_first or t_done) - t_start) * 1000.0

    return RequestSample(
        completed_ts=t_done,
        ttft_ms=ttft_ms,
        itl_samples_ms=itls_ms,
        output_tokens=max(1, out_tokens),
        prompt_tokens_est=0,
        served_by_pod=served_by,
        policy=policy,
        reason=reason,
    )


async def run_orchestrator_episode(
    client: httpx.AsyncClient,
    gateway_url: str,
    incident_id: int,
    window: SlidingMetricsWindow | None = None,
    recorded_samples: list[RequestSample] | None = None,
    num_branches: int = 8,
    turns_per_branch: int = 4,
    output_tokens_per_turn: int = 8,
) -> list[RequestSample]:
    """Executes 1 Incident Triage Orchestrator Episode:
    Seed 20K Trunk -> 8x Parallel Sub-Agent Fork (4 turns w/ 8K log burst on Turn 2) -> Join.
    """
    episode_samples: list[RequestSample] = []
    trunk_msg = build_shared_trunk_system_message(incident_id)

    def _collect(sample: RequestSample) -> None:
        episode_samples.append(sample)
        if window is not None:
            window.record_request(sample)
        if recorded_samples is not None:
            recorded_samples.append(sample)

    # 1. Orchestrator Seed Turn (warms 20,480-token trunk)
    seed_sample = await send_streaming_completion(
        client,
        gateway_url,
        messages=[trunk_msg, {"role": "user", "content": _make_exact_tokens(62, f"plan{incident_id}")}],
        max_tokens=output_tokens_per_turn,
        horizon_hint_tokens=2048,
    )
    _collect(seed_sample)

    # 2. 8x Parallel Sub-Agent Fork-Storm
    async def _run_specialist_branch(branch_idx: int) -> None:
        msgs: list[dict[str, str]] = [
            trunk_msg,
            {
                "role": "user",
                "content": _make_exact_tokens(
                    TURN1_DELTA_BLOCKS * BLOCK_SIZE - 2,
                    f"b{branch_idx}t1_{incident_id % 99}",
                ),
            },
        ]
        # Turn 1: Specialist Activation (horizon hint warns of upcoming 8K log dump)
        s1 = await send_streaming_completion(
            client,
            gateway_url,
            messages=msgs,
            max_tokens=output_tokens_per_turn,
            horizon_hint_tokens=TURN2_LOG_BURST_BLOCKS * BLOCK_SIZE,
        )
        _collect(s1)
        if turns_per_branch < 2:
            return

        # Turn 2: Massive 8,192-token (32-block) kubectl logs tool burst!
        # 28 blocks shared pod crash stream + 4 diverging specialist log/trace blocks = 32 blocks
        pod_logs = get_pod_crash_logs(incident_id, branch_idx // 4)
        filter_tail = _make_exact_tokens(
            TURN2_FILTER_BLOCKS * BLOCK_SIZE - 2,
            f"flt{branch_idx}_{incident_id % 99}",
        )
        msgs = msgs + [{"role": "tool", "content": f"{pod_logs} {filter_tail}"}]
        s2 = await send_streaming_completion(
            client,
            gateway_url,
            messages=msgs,
            max_tokens=output_tokens_per_turn,
            horizon_hint_tokens=2048,
        )
        _collect(s2)
        if turns_per_branch < 3:
            return

        # Turn 3: Git blame / Envoy config inspection (+1,024 tokens)
        msgs = msgs + [
            {
                "role": "tool",
                "content": _make_exact_tokens(
                    TURN3_DELTA_BLOCKS * BLOCK_SIZE - 2,
                    f" cfg{branch_idx}_{incident_id % 99}".strip(),
                ),
            }
        ]
        s3 = await send_streaming_completion(
            client,
            gateway_url,
            messages=msgs,
            max_tokens=output_tokens_per_turn,
            horizon_hint_tokens=1024,
        )
        _collect(s3)
        if turns_per_branch < 4:
            return

        # Turn 4: Remediation patch verification (+1,024 tokens)
        msgs = msgs + [
            {
                "role": "tool",
                "content": _make_exact_tokens(
                    TURN4_DELTA_BLOCKS * BLOCK_SIZE - 2,
                    f"rem{branch_idx}_{incident_id % 99}",
                ),
            }
        ]
        s4 = await send_streaming_completion(
            client,
            gateway_url,
            messages=msgs,
            max_tokens=output_tokens_per_turn,
            horizon_hint_tokens=512,
        )
        _collect(s4)

    await asyncio.gather(*(_run_specialist_branch(b) for b in range(num_branches)))

    # 3. Orchestrator Synthesis Join Turn (reuses 20,480-token shared trunk!)
    join_msgs = [
        trunk_msg,
        {
            "role": "user",
            "content": _make_exact_tokens(
                JOIN_SYNTH_BLOCKS * BLOCK_SIZE - 2,
                f"join{incident_id % 99}",
            ),
        },
    ]
    join_sample = await send_streaming_completion(
        client,
        gateway_url,
        messages=join_msgs,
        max_tokens=output_tokens_per_turn,
    )
    _collect(join_sample)

    return episode_samples


@dataclass
class StageWaveReport:
    stage_name: str
    p50_ttft_ms: float
    p95_ttft_ms: float
    p99_itl_ms: float
    goodput_tok_per_s: float
    cache_hit_rate_pct: float
    hbm_evictions: int
    herd_spillovers: int
    total_requests: int
    pod_distribution: dict[str, int]


async def execute_benchmark_waves(
    gateway_url: str,
    worker_metrics_urls: list[str],
    epp_metrics_url: str | None = None,
    stage_name: str = "stage",
    num_waves: int = 2,
    orchestrators_per_wave: int = 4,
    num_branches: int = 8,
    turns_per_branch: int = 3,
    output_tokens_per_turn: int = 6,
    stagger_sec: float = 0.12,
    incident_base_id: int = 100,
) -> StageWaveReport:
    """Runs deterministic multi-orchestrator Fork-Storm waves and returns quantitative telemetry."""
    limits = httpx.Limits(max_connections=256, max_keepalive_connections=128)
    samples: list[RequestSample] = []

    # Pre-materialize deterministic token strings outside the timed SSE measurement loop
    for w_idx in range(num_waves):
        for o_slot in range(orchestrators_per_wave):
            inc = incident_base_id + w_idx * orchestrators_per_wave + o_slot
            build_shared_trunk_system_message(inc)
            _make_exact_tokens(62, f"plan{inc}")
            _make_exact_tokens(JOIN_SYNTH_BLOCKS * BLOCK_SIZE - 2, f"join{inc % 99}")
            for g in (0, 1):
                get_pod_crash_logs(inc, g)
            for b in range(num_branches):
                _make_exact_tokens(TURN1_DELTA_BLOCKS * BLOCK_SIZE - 2, f"b{b}t1_{inc % 99}")
                _make_exact_tokens(TURN2_FILTER_BLOCKS * BLOCK_SIZE - 2, f"flt{b}_{inc % 99}")
                _make_exact_tokens(TURN3_DELTA_BLOCKS * BLOCK_SIZE - 2, f"cfg{b}_{inc % 99}")
                _make_exact_tokens(TURN4_DELTA_BLOCKS * BLOCK_SIZE - 2, f"rem{b}_{inc % 99}")

    async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
        # Warm the organization's shared 2,048-token MCP schema registry before timed waves begin
        await send_streaming_completion(
            client=client,
            gateway_url=gateway_url,
            messages=[{"role": "system", "content": _GLOBAL_MCP_TEXT}],
            max_tokens=2,
        )
        await asyncio.sleep(0.10)

        before_prom = await scrape_prometheus_totals(client, worker_metrics_urls, epp_metrics_url)
        t0 = time.monotonic()

        for wave_idx in range(num_waves):
            async def _staggered_orch(orch_slot: int, w_idx: int = wave_idx) -> None:
                if orch_slot > 0 and stagger_sec > 0:
                    await asyncio.sleep(orch_slot * stagger_sec)
                inc_id = incident_base_id + w_idx * orchestrators_per_wave + orch_slot
                await run_orchestrator_episode(
                    client=client,
                    gateway_url=gateway_url,
                    incident_id=inc_id,
                    recorded_samples=samples,
                    num_branches=num_branches,
                    turns_per_branch=turns_per_branch,
                    output_tokens_per_turn=output_tokens_per_turn,
                )

            await asyncio.gather(*(_staggered_orch(o) for o in range(orchestrators_per_wave)))

        elapsed = max(0.1, time.monotonic() - t0)
        after_prom = await scrape_prometheus_totals(client, worker_metrics_urls, epp_metrics_url)

    ttfts = sorted(s.ttft_ms for s in samples)
    itls = sorted(itl for s in samples for itl in s.itl_samples_ms)
    out_toks = sum(s.output_tokens for s in samples)

    dq = after_prom["cache_queries"] - before_prom["cache_queries"]
    dh = after_prom["cache_hits"] - before_prom["cache_hits"]
    hit_rate = (dh / dq * 100.0) if dq > 0 else 0.0
    evictions = int(round(after_prom["hbm_evictions"] - before_prom["hbm_evictions"]))
    spillovers = int(round(after_prom["herd_spillovers"] - before_prom["herd_spillovers"]))

    pods: dict[str, int] = {}
    for s in samples:
        if s.served_by_pod:
            pods[s.served_by_pod] = pods.get(s.served_by_pod, 0) + 1

    return StageWaveReport(
        stage_name=stage_name,
        p50_ttft_ms=_percentile(ttfts, 50.0),
        p95_ttft_ms=_percentile(ttfts, 95.0),
        p99_itl_ms=_percentile(itls, 99.0),
        goodput_tok_per_s=out_toks / elapsed,
        cache_hit_rate_pct=hit_rate,
        hbm_evictions=max(0, evictions),
        herd_spillovers=max(0, spillovers),
        total_requests=len(samples),
        pod_distribution=pods,
    )


async def continuous_orchestrator_fleet(
    stop_event: asyncio.Event,
    gateway_url: str,
    window: SlidingMetricsWindow,
    num_orchestrators: int = 8,
    num_branches: int = 8,
) -> None:
    """Continuously runs 8 concurrent Incident Triage Orchestrators (64 active sub-agent branches)."""
    limits = httpx.Limits(max_connections=256, max_keepalive_connections=128)
    for inc in range(500, 516):
        build_shared_trunk_system_message(inc)
        _make_exact_tokens(62, f"plan{inc}")
        _make_exact_tokens(JOIN_SYNTH_BLOCKS * BLOCK_SIZE - 2, f"join{inc % 99}")
        for g in (0, 1):
            get_pod_crash_logs(inc, g)
        for b in range(num_branches):
            _make_exact_tokens(TURN1_DELTA_BLOCKS * BLOCK_SIZE - 2, f"b{b}t1_{inc % 99}")
            _make_exact_tokens(TURN2_FILTER_BLOCKS * BLOCK_SIZE - 2, f"flt{b}_{inc % 99}")
            _make_exact_tokens(TURN3_DELTA_BLOCKS * BLOCK_SIZE - 2, f"cfg{b}_{inc % 99}")
            _make_exact_tokens(TURN4_DELTA_BLOCKS * BLOCK_SIZE - 2, f"rem{b}_{inc % 99}")

    async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:
        async def _worker_loop(slot: int) -> None:
            await asyncio.sleep(slot * 0.18)
            seq = 0
            while not stop_event.is_set():
                # Cycle across 8 active incident slots so concurrent trunks exceed single-pod 360-block HBM
                # while fitting cleanly inside Stage 3's 360 HBM + 1024 Tier-2 Host DRAM!
                incident_id = 500 + (slot + seq * 3) % 8
                seq += 1
                try:
                    await run_orchestrator_episode(
                        client=client,
                        gateway_url=gateway_url,
                        incident_id=incident_id,
                        window=window,
                        num_branches=num_branches,
                        turns_per_branch=4,
                        output_tokens_per_turn=8,
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    await asyncio.sleep(0.25)

        tasks = [asyncio.create_task(_worker_loop(i)) for i in range(num_orchestrators)]
        await stop_event.wait()
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Fork-Storm multi-agent benchmark waves")
    parser.add_argument("--gateway-url", default="http://127.0.0.1:8080")
    parser.add_argument(
        "--worker-metrics",
        default="http://127.0.0.1:8001/metrics,http://127.0.0.1:8002/metrics,http://127.0.0.1:8003/metrics,http://127.0.0.1:8004/metrics,http://127.0.0.1:8005/metrics,http://127.0.0.1:8006/metrics,http://127.0.0.1:8007/metrics,http://127.0.0.1:8008/metrics",
    )
    parser.add_argument("--epp-metrics", default="http://127.0.0.1:9090/metrics")
    parser.add_argument("--waves", type=int, default=2)
    parser.add_argument("--orchestrators", type=int, default=4)
    args = parser.parse_args()

    urls = [u.strip() for u in args.worker_metrics.split(",") if u.strip()]
    report = asyncio.run(
        execute_benchmark_waves(
            gateway_url=args.gateway_url,
            worker_metrics_urls=urls,
            epp_metrics_url=args.epp_metrics,
            num_waves=args.waves,
            orchestrators_per_wave=args.orchestrators,
        )
    )
    print(json.dumps(report.__dict__, indent=2))


if __name__ == "__main__":
    main()
