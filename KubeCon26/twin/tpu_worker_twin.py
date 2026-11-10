#!/usr/bin/env python3
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""Trace-Calibrated TPU v6e Serving Worker Digital Twin.

Implements:
- OpenAI-compatible `/v1/chat/completions` streaming SSE endpoint
- Deterministic 256-token chained SHA-256 prefix block hasher (matching Go `pkg/hash/blockhash.go`)
- Fixed-capacity 256-token HBM LRU block cache (`360` blocks) + optional Tier-2 Host DRAM (`1024` blocks)
- Real ZeroMQ `PUB` emitter (`BlockStored`, `BlockRemoved`, `Heartbeat`) in JSON or MessagePack
- Calibrated TPU v6e MXU serial prefill queue + aggregated P/D decode interference + disaggregated HMA transfer
- vLLM-compatible `/metrics` Prometheus text exposition endpoint
"""

from __future__ import annotations

import argparse
import asyncio
from collections import OrderedDict
import gc
import hashlib
import json
import os
import random
import socket
import struct
import time
import uuid
from typing import Any

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
import httpx
import msgpack
import uvicorn
import zmq
import zmq.asyncio

DEFAULT_BLOCK_SIZE = 256
SUBWORD_CHUNK_BYTES = 16
ASCII_WHITESPACE = frozenset((0x20, 0x09, 0x0A, 0x0D, 0x0B, 0x0C))


def get_process_hash_seed() -> int:
    raw = os.environ.get("PYTHONHASHSEED", "0").strip()
    if not raw or raw == "random":
        # Unpinned PYTHONHASHSEED salts hashes per process (Production Scar #1!).
        return random.SystemRandom().randint(1, (1 << 63) - 1)
    try:
        return int(raw) & 0xFFFFFFFFFFFFFFFF
    except ValueError:
        return 0


def canonicalize_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for msg in messages:
        role = str(msg.get("role", "user"))
        content = msg.get("content", "")
        if isinstance(content, list):
            text_items = [
                str(item.get("text", ""))
                for item in content
                if isinstance(item, dict)
            ]
            content_str = "\n".join(text_items)
        elif content is None:
            content_str = ""
        else:
            content_str = str(content)
        parts.append(f"<|im_start|>{role}\n{content_str}<|im_end|>\n")
    return "".join(parts)


_LEN_PACK = tuple(struct.Struct(">H").pack(k) for k in range(SUBWORD_CHUNK_BYTES + 1))
_HDR_STRUCT = struct.Struct(">QI")
_U64_STRUCT = struct.Struct(">Q")
# Maps (parent_u64, block_size, tail_key_bytes, seg_text) ->
#   (new_parent_u64, tuple_of_hex_hashes, new_tail_tuple, seg_token_count)
_ALIGNED_SEG_CACHE: OrderedDict[
    tuple[int, int, bytes, str],
    tuple[int, tuple[str, ...], tuple[bytes, ...], int],
] = OrderedDict()


def tokenize_deterministic(text: str) -> list[bytes]:
    """Byte-exact C-accelerated counterpart to Go's hash.TokenizeDeterministic."""
    tokens: list[bytes] = []
    append = tokens.append
    for word in text.encode("utf-8").split():
        if len(word) <= SUBWORD_CHUNK_BYTES:
            append(word)
        else:
            for j in range(0, len(word), SUBWORD_CHUNK_BYTES):
                append(word[j : j + SUBWORD_CHUNK_BYTES])
    return tokens


def _hash_tokens_with_parent(
    tokens: list[bytes],
    block_size: int,
    parent: int,
) -> tuple[list[str], int]:
    num_blocks = len(tokens) // block_size
    if num_blocks == 0:
        return [], parent

    hashes: list[str] = []
    pack_hdr = _HDR_STRUCT.pack
    unpack_u64 = _U64_STRUCT.unpack_from
    len_pack = _LEN_PACK

    for b in range(num_blocks):
        start = b * block_size
        end = start + block_size
        body = b"".join(len_pack[len(tok)] + tok for tok in tokens[start:end])
        digest = hashlib.sha256(pack_hdr(parent, block_size) + body).digest()
        (block_id,) = unpack_u64(digest, 0)
        hashes.append(f"{block_id:016x}")
        parent = block_id
    return hashes, parent


def compute_block_hashes(
    tokens: list[bytes],
    block_size: int = DEFAULT_BLOCK_SIZE,
    seed: int = 0,
) -> list[str]:
    """Byte-exact counterpart to Go's hash.ComputeBlockHashes."""
    if block_size <= 0:
        block_size = DEFAULT_BLOCK_SIZE
    hashes, _ = _hash_tokens_with_parent(tokens, block_size, seed & 0xFFFFFFFFFFFFFFFF)
    return hashes


def hash_chat_completions(
    payload: dict[str, Any],
    block_size: int = DEFAULT_BLOCK_SIZE,
    seed: int = 0,
) -> tuple[list[str], int, int, int]:
    if block_size <= 0:
        block_size = DEFAULT_BLOCK_SIZE
    parent = seed & 0xFFFFFFFFFFFFFFFF
    messages = payload.get("messages") or []
    hashes: list[str] = []
    tail_tokens: list[bytes] = []
    total_toks = 0

    if messages:
        for msg in messages:
            role = str(msg.get("role", "user"))
            content = msg.get("content", "")
            if isinstance(content, list):
                content_str = "\n".join(
                    str(item.get("text", ""))
                    for item in content
                    if isinstance(item, dict)
                )
            elif content is None:
                content_str = ""
            else:
                content_str = str(content)
            seg = f"<|im_start|>{role}\n{content_str}<|im_end|>\n"
            tail_key = b"\x00".join(tail_tokens) if tail_tokens else b""
            cache_key = (parent, block_size, tail_key, seg)
            cached = _ALIGNED_SEG_CACHE.get(cache_key)
            if cached is not None:
                parent, seg_hashes, new_tail, seg_len = cached
                hashes.extend(seg_hashes)
                tail_tokens = list(new_tail)
                total_toks += seg_len
                continue

            seg_toks = tokenize_deterministic(seg)
            seg_len = len(seg_toks)
            total_toks += seg_len
            combined = tail_tokens + seg_toks if tail_tokens else seg_toks
            if len(combined) >= block_size:
                n_full = (len(combined) // block_size) * block_size
                chunk_hashes, new_parent = _hash_tokens_with_parent(combined[:n_full], block_size, parent)
                rem_tail = tuple(combined[n_full:])
                seg_hashes = tuple(chunk_hashes)
            else:
                new_parent = parent
                seg_hashes = ()
                rem_tail = tuple(combined)

            if seg_len >= block_size:
                if len(_ALIGNED_SEG_CACHE) >= 1024:
                    _ALIGNED_SEG_CACHE.popitem(last=False)
                _ALIGNED_SEG_CACHE[cache_key] = (new_parent, seg_hashes, rem_tail, seg_len)

            parent = new_parent
            hashes.extend(seg_hashes)
            tail_tokens = list(rem_tail)
    else:
        canonical = str(payload.get("prompt", ""))
        toks = tokenize_deterministic(canonical)
        total_toks = len(toks)
        hashes, _ = _hash_tokens_with_parent(toks, block_size, parent)

    max_toks = int(
        payload.get("max_completion_tokens")
        or payload.get("max_tokens")
        or 64
    )
    return hashes, total_toks, total_toks % block_size, max_toks


def resolve_advertise_ip_port(advertise_addr: str, listen_port: int) -> str:
    if advertise_addr:
        if ":" in advertise_addr:
            host, port_s = advertise_addr.rsplit(":", 1)
        else:
            host, port_s = advertise_addr, str(listen_port)
        try:
            ip = socket.gethostbyname(host)
            return f"{ip}:{port_s}"
        except OSError:
            return f"{host}:{port_s}"
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127."):
            ip = "127.0.0.1"
    except OSError:
        ip = "127.0.0.1"
    return f"{ip}:{listen_port}"


class TPUWorkerState:
    """Simulates a TPU v6e vLLM worker's block table, MXU prefill lock, and ZMQ publisher."""

    def __init__(
        self,
        pod_id: str,
        role: str,
        http_port: int,
        zmq_pub_port: int,
        advertise_addr: str = "",
        block_size: int = DEFAULT_BLOCK_SIZE,
        hbm_capacity_blocks: int = 360,
        enable_hma_dram: bool = False,
        dram_capacity_blocks: int = 4096,
        zmq_encoding: str = "json",
        miss_block_ms: float = 12.5,
        hbm_hit_block_ms: float = 0.25,
        dram_hit_block_ms: float = 0.90,
        hma_transfer_ms: float = 32.0,
        decode_step_ms: float = 19.5,
        mxu_streams: int = 0,
    ) -> None:
        self.pod_id = pod_id
        self.role = role.lower()
        self.http_port = http_port
        self.zmq_pub_port = zmq_pub_port
        self.ip_port = resolve_advertise_ip_port(advertise_addr, http_port)
        self.block_size = block_size
        self.hash_seed = get_process_hash_seed()

        self.hbm_capacity_blocks = hbm_capacity_blocks
        self.enable_hma_dram = enable_hma_dram
        self.dram_capacity_blocks = dram_capacity_blocks if enable_hma_dram else 0
        self.zmq_encoding = zmq_encoding

        # Calibrated TPU v6e timing constants
        self.miss_block_sec = miss_block_ms / 1000.0
        self.hbm_hit_block_sec = hbm_hit_block_ms / 1000.0
        self.dram_hit_block_sec = dram_hit_block_ms / 1000.0
        self.hma_transfer_sec = hma_transfer_ms / 1000.0
        self.decode_step_sec = decode_step_ms / 1000.0

        self.hbm_lru: OrderedDict[str, float] = OrderedDict()
        self.dram_lru: OrderedDict[str, float] = OrderedDict()
        self.inflight_blocks: dict[str, asyncio.Event] = {}
        self.cache_lock = asyncio.Lock()
        # Dedicated TP=4 prefill slice runs 4 concurrent MXU pipelines; TP=2 agg slice runs 1 serial MXU lock.
        effective_streams = mxu_streams if mxu_streams > 0 else (4 if self.role == "prefill" else 1)
        self.mxu_lock = asyncio.Semaphore(effective_streams)

        self.active_prefill_bursts = 0
        self.active_decodes = 0
        self.last_prefill_active_ts = 0.0

        # Prometheus telemetry counters
        self.prefix_cache_hits_total = 0
        self.prefix_cache_queries_total = 0
        self.hbm_evictions_total = 0
        self.dram_restores_total = 0
        self.requests_total = 0

        self.zmq_ctx: zmq.asyncio.Context | None = None
        self.zmq_pub: zmq.asyncio.Socket | None = None
        self.http_client: httpx.AsyncClient | None = None
        self._bg_tasks: list[asyncio.Task[Any]] = []

    @property
    def free_hbm_blocks(self) -> int:
        return max(0, self.hbm_capacity_blocks - len(self.hbm_lru))

    @property
    def free_dram_blocks(self) -> int:
        if not self.enable_hma_dram:
            return 0
        return max(0, self.dram_capacity_blocks - len(self.dram_lru))

    async def start(self) -> None:
        self.zmq_ctx = zmq.asyncio.Context()
        self.zmq_pub = self.zmq_ctx.socket(zmq.PUB)
        self.zmq_pub.setsockopt(zmq.LINGER, 0)
        self.zmq_pub.setsockopt(zmq.SNDHWM, 10000)
        self.zmq_pub.bind(f"tcp://0.0.0.0:{self.zmq_pub_port}")

        self.http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self._bg_tasks.append(asyncio.create_task(self._heartbeat_loop()))

    async def stop(self) -> None:
        for task in self._bg_tasks:
            task.cancel()
        if self._bg_tasks:
            await asyncio.gather(*self._bg_tasks, return_exceptions=True)
        if self.http_client is not None:
            await self.http_client.aclose()
        if self.zmq_pub is not None:
            self.zmq_pub.close(0)
        if self.zmq_ctx is not None:
            self.zmq_ctx.term()

    async def publish_kv_event(
        self,
        event_type: str,
        block_hashes: list[str],
        tier: str = "hbm",
        parent_block_hash: str = "",
    ) -> None:
        if self.zmq_pub is None:
            return
        event = {
            "event_type": event_type,
            "pod_id": self.pod_id,
            "ip_port": self.ip_port,
            "role": self.role,
            "parent_block_hash": parent_block_hash,
            "block_hashes": block_hashes,
            "free_hbm_blocks": self.free_hbm_blocks,
            "hbm_capacity_blocks": self.hbm_capacity_blocks,
            "free_dram_blocks": self.free_dram_blocks,
            "tier": tier,
            "ts_ms": int(time.time() * 1000),
        }
        if self.zmq_encoding == "msgpack":
            raw = msgpack.packb(event, use_bin_type=True)
        else:
            raw = json.dumps(event, separators=(",", ":")).encode("utf-8")
        try:
            await self.zmq_pub.send(raw)
        except Exception:
            pass

    async def _heartbeat_loop(self) -> None:
        await asyncio.sleep(0.05)
        while True:
            await self.publish_kv_event("Heartbeat", [], tier="hbm")
            await asyncio.sleep(0.5)

    async def reset_state(self) -> None:
        async with self.cache_lock:
            _ALIGNED_SEG_CACHE.clear()
            self.hbm_lru.clear()
            self.dram_lru.clear()
            self.prefix_cache_hits_total = 0
            self.prefix_cache_queries_total = 0
            self.hbm_evictions_total = 0
            self.dram_restores_total = 0
            self.requests_total = 0
            gc.collect()
            await self.publish_kv_event("AllBlocksCleared", [], tier="hbm")

    async def _insert_hbm_blocks_locked(
        self,
        hashes_to_insert: list[str],
        parent_hash: str,
    ) -> None:
        if not hashes_to_insert:
            return

        now = time.monotonic()
        evicted_hbm: list[str] = []
        evicted_dram: list[str] = []
        newly_added: list[str] = []

        for bh in hashes_to_insert:
            if bh in self.hbm_lru:
                self.hbm_lru.move_to_end(bh)
                self.hbm_lru[bh] = now
                continue

            while len(self.hbm_lru) >= self.hbm_capacity_blocks:
                old_bh, _ = self.hbm_lru.popitem(last=False)
                evicted_hbm.append(old_bh)
                if self.enable_hma_dram and self.dram_capacity_blocks > 0:
                    if old_bh in self.dram_lru:
                        self.dram_lru.move_to_end(old_bh)
                    else:
                        while len(self.dram_lru) >= self.dram_capacity_blocks:
                            old_dram_bh, _ = self.dram_lru.popitem(last=False)
                            evicted_dram.append(old_dram_bh)
                            self.hbm_evictions_total += 1
                        self.dram_lru[old_bh] = now
                elif self.role != "decode":
                    self.hbm_evictions_total += 1

            self.hbm_lru[bh] = now
            newly_added.append(bh)

        if evicted_hbm:
            await self.publish_kv_event("BlockRemoved", evicted_hbm, tier="hbm")
            if self.enable_hma_dram:
                await self.publish_kv_event("BlockStored", evicted_hbm, tier="dram")
        if evicted_dram:
            await self.publish_kv_event("BlockRemoved", evicted_dram, tier="dram")
        if newly_added:
            await self.publish_kv_event(
                "BlockStored",
                newly_added,
                tier="hbm",
                parent_block_hash=parent_hash,
            )

    async def execute_prefill(
        self,
        block_hashes: list[str],
        tail_tokens: int,
    ) -> dict[str, Any]:
        """Executes arrival-time APC lookup + single-flight dedup + serial MXU prefill."""
        now = time.monotonic()
        hbm_hits = 0
        dram_hits = 0
        inflight_hits = 0
        restored_from_dram: list[str] = []
        to_compute: list[str] = []
        prefix_broken = False

        async with self.cache_lock:
            for bh in block_hashes:
                if not prefix_broken and bh in self.hbm_lru:
                    self.hbm_lru.move_to_end(bh)
                    self.hbm_lru[bh] = now
                    hbm_hits += 1
                elif not prefix_broken and self.enable_hma_dram and bh in self.dram_lru:
                    self.dram_lru.move_to_end(bh)
                    self.dram_lru[bh] = now
                    dram_hits += 1
                    self.dram_restores_total += 1
                    restored_from_dram.append(bh)
                elif not prefix_broken and bh in self.inflight_blocks:
                    inflight_hits += 1
                else:
                    prefix_broken = True
                    if bh in self.inflight_blocks:
                        inflight_hits += 1
                    else:
                        self.inflight_blocks[bh] = asyncio.Event()
                        to_compute.append(bh)

            miss_blocks = len(to_compute)
            self.prefix_cache_queries_total += len(block_hashes)
            self.prefix_cache_hits_total += hbm_hits + dram_hits

        try:
            async with self.mxu_lock:
                tail_miss_blocks = (tail_tokens / float(self.block_size)) if tail_tokens > 0 else 0.0
                prefill_sec = (
                    miss_blocks * self.miss_block_sec
                    + tail_miss_blocks * self.miss_block_sec
                    + (hbm_hits + inflight_hits) * self.hbm_hit_block_sec
                    + dram_hits * self.dram_hit_block_sec
                )

                is_heavy_compute = (miss_blocks + tail_miss_blocks) >= 2.0
                if is_heavy_compute:
                    self.active_prefill_bursts += 1

                try:
                    remaining = prefill_sec
                    while remaining > 0:
                        step = min(0.020, remaining)
                        if is_heavy_compute:
                            self.last_prefill_active_ts = time.monotonic()
                        await asyncio.sleep(step)
                        remaining -= step
                finally:
                    if is_heavy_compute:
                        self.active_prefill_bursts = max(0, self.active_prefill_bursts - 1)

                async with self.cache_lock:
                    # Note: DRAM HMA blocks stream directly over gVNIC via TPUConnectorHMA
                    # without evicting hot HBM blocks; only newly computed blocks enter HBM.
                    if to_compute:
                        idx_c = block_hashes.index(to_compute[0])
                        comp_parent = block_hashes[idx_c - 1] if idx_c > 0 else ""
                        await self._insert_hbm_blocks_locked(to_compute, comp_parent)

                return {
                    "pod_id": self.pod_id,
                    "hbm_hits": hbm_hits + inflight_hits,
                    "dram_hits": dram_hits,
                    "miss_blocks": miss_blocks,
                    "prefill_ms": round(prefill_sec * 1000.0, 2),
                }
        finally:
            if to_compute:
                async with self.cache_lock:
                    for bh in to_compute:
                        ev = self.inflight_blocks.pop(bh, None)
                        if ev is not None:
                            ev.set()

    async def absorb_transferred_blocks_on_decode(self, block_hashes: list[str]) -> None:
        """Records KV blocks streamed from prefill peer into decode HBM table."""
        if not block_hashes:
            return
        async with self.cache_lock:
            await self._insert_hbm_blocks_locked(block_hashes, "")


def create_app(state: TPUWorkerState) -> FastAPI:
    app = FastAPI(title=f"TPU Worker Twin ({state.pod_id})")

    @app.on_event("startup")
    async def _startup() -> None:
        await state.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        await state.stop()

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "status": "ok",
            "pod_id": state.pod_id,
            "role": state.role,
            "ip_port": state.ip_port,
            "free_hbm_blocks": state.free_hbm_blocks,
            "hbm_capacity_blocks": state.hbm_capacity_blocks,
            "free_dram_blocks": state.free_dram_blocks,
            "hbm_evictions_total": state.hbm_evictions_total,
        }

    @app.post("/admin/reset")
    async def admin_reset() -> dict[str, str]:
        await state.reset_state()
        return {"status": "reset", "pod_id": state.pod_id}

    @app.get("/metrics")
    async def prometheus_metrics() -> PlainTextResponse:
        usage_ratio = len(state.hbm_lru) / float(max(1, state.hbm_capacity_blocks))
        labels = f'pod_id="{state.pod_id}",role="{state.role}"'
        lines = [
            "# HELP vllm:prefix_cache_hits_total Prefix cache block hits (HBM + HMA DRAM).",
            "# TYPE vllm:prefix_cache_hits_total counter",
            f"vllm:prefix_cache_hits_total{{{labels}}} {state.prefix_cache_hits_total}",
            "# HELP vllm:prefix_cache_queries_total Total prefix cache block lookups.",
            "# TYPE vllm:prefix_cache_queries_total counter",
            f"vllm:prefix_cache_queries_total{{{labels}}} {state.prefix_cache_queries_total}",
            "# HELP vllm:gpu_cache_usage_perc Fraction of HBM KV cache blocks currently occupied.",
            "# TYPE vllm:gpu_cache_usage_perc gauge",
            f"vllm:gpu_cache_usage_perc{{{labels}}} {usage_ratio:.4f}",
            "# HELP fleetkv_twin_hbm_evictions_total Total HBM LRU block evictions on this worker.",
            "# TYPE fleetkv_twin_hbm_evictions_total counter",
            f"fleetkv_twin_hbm_evictions_total{{{labels}}} {state.hbm_evictions_total}",
            "# HELP fleetkv_twin_requests_total Total inference requests served by this worker.",
            "# TYPE fleetkv_twin_requests_total counter",
            f"fleetkv_twin_requests_total{{{labels}}} {state.requests_total}",
            "",
        ]
        return PlainTextResponse("\n".join(lines), media_type="text/plain; version=0.0.4")

    @app.post("/internal/prefill_kv_transfer")
    async def internal_prefill_kv_transfer(req: Request) -> JSONResponse:
        body = await req.json()
        block_hashes: list[str] = body.get("block_hashes", [])
        tail_tokens: int = int(body.get("tail_tokens", 0))

        prefill_stats = await state.execute_prefill(block_hashes, tail_tokens)
        # Asynchronous TPUConnectorHMA DMA transfer over MTU-8896 gVNIC (runs outside MXU lock!).
        await asyncio.sleep(state.hma_transfer_sec)
        prefill_stats["hma_transfer_ms"] = round(state.hma_transfer_sec * 1000.0, 2)
        return JSONResponse(prefill_stats)

    @app.post("/v1/chat/completions")
    async def chat_completions(
        req: Request,
        x_fleetkv_prefill_peer: str | None = Header(default=None),
        x_fleetkv_prefill_endpoint: str | None = Header(default=None),
    ) -> Any:
        if state.active_decodes > 0:
            await asyncio.sleep(0)
        payload = await req.json()
        if state.active_decodes > 0:
            await asyncio.sleep(0)
        state.requests_total += 1
        model_name = str(payload.get("model", "Qwen/Qwen3-30B-A3B-FP8"))
        stream = bool(payload.get("stream", True))

        block_hashes, total_tokens, tail_tokens, max_tokens = hash_chat_completions(
            payload,
            block_size=state.block_size,
            seed=state.hash_seed,
        )
        if state.active_decodes > 0:
            await asyncio.sleep(0)
        output_tokens = max(1, min(max_tokens, 64))
        prefill_peer = x_fleetkv_prefill_peer or x_fleetkv_prefill_endpoint

        # Disaggregated Decode Path vs Aggregated Path
        if state.role == "decode" and prefill_peer:
            assert state.http_client is not None
            peer_url = prefill_peer if prefill_peer.startswith("http") else f"http://{prefill_peer}"
            try:
                resp = await state.http_client.post(
                    f"{peer_url}/internal/prefill_kv_transfer",
                    json={"block_hashes": block_hashes, "tail_tokens": tail_tokens},
                )
                resp.raise_for_status()
                prefill_meta = resp.json()
                # Store active branch delta footprint on decode HBM (trunk shared, delta tracked).
                delta_slice = block_hashes[-16:] if len(block_hashes) > 16 else block_hashes
                await state.absorb_transferred_blocks_on_decode(delta_slice)
            except Exception:
                # Resilient fallback if prefill peer is unreachable
                prefill_meta = await state.execute_prefill(block_hashes, tail_tokens)
        else:
            prefill_meta = await state.execute_prefill(block_hashes, tail_tokens)

        completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_ts = int(time.time())

        if not stream:
            # Non-streaming completion
            state.active_decodes += 1
            try:
                await asyncio.sleep(state.decode_step_sec * output_tokens)
            finally:
                state.active_decodes = max(0, state.active_decodes - 1)
            return JSONResponse(
                {
                    "id": completion_id,
                    "object": "chat.completion",
                    "created": created_ts,
                    "model": model_name,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": f"[{state.pod_id}] resolved {total_tokens} prompt tokens ({prefill_meta})",
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": total_tokens,
                        "completion_tokens": output_tokens,
                        "total_tokens": total_tokens + output_tokens,
                    },
                },
                headers={"x-served-by-pod": state.pod_id},
            )

        async def sse_generator():
            state.active_decodes += 1
            next_tick = time.monotonic()
            try:
                for step_idx in range(output_tokens):
                    if step_idx > 0:
                        base_step = state.decode_step_sec if state.role != "decode" else (state.decode_step_sec * 0.85)
                        step_delay = base_step + random.uniform(-0.001, 0.0015)
                        # Aggregated P/D Head-of-Line interference: active MXU prefill burst
                        # stalls co-located memory-bound decode steps past 110ms!
                        if state.role == "agg" and (
                            state.active_prefill_bursts > 0
                            or (time.monotonic() - state.last_prefill_active_ts) < 0.025
                        ):
                            step_delay += 0.092
                        elif state.role == "agg" and state.active_decodes > 8:
                            step_delay += min(0.004, (state.active_decodes - 8) * 0.0004)
                        next_tick += step_delay
                        sleep_for = next_tick - time.monotonic()
                        if sleep_for > 0:
                            await asyncio.sleep(sleep_for)
                        else:
                            await asyncio.sleep(0)
                    else:
                        next_tick = time.monotonic()

                    tok_text = f" tok{step_idx}"
                    chunk = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_ts,
                        "model": model_name,
                        "choices": [
                            {
                                "index": 0,
                                "delta": (
                                    {"role": "assistant", "content": f"[{state.pod_id}]"}
                                    if step_idx == 0
                                    else {"content": tok_text}
                                ),
                                "finish_reason": None if step_idx + 1 < output_tokens else "stop",
                            }
                        ],
                    }
                    yield f"data: {json.dumps(chunk, separators=(',', ':'))}\n\n"
                yield "data: [DONE]\n\n"
            finally:
                state.active_decodes = max(0, state.active_decodes - 1)

        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "x-served-by-pod": state.pod_id,
            },
        )

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TPU v6e Serving Worker Digital Twin")
    parser.add_argument("--pod-id", default=os.environ.get("POD_ID", "agg-0"))
    parser.add_argument(
        "--role",
        choices=["agg", "prefill", "decode"],
        default=os.environ.get("WORKER_ROLE", "agg"),
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("HTTP_PORT", "8001")))
    parser.add_argument("--zmq-pub-port", type=int, default=int(os.environ.get("ZMQ_PUB_PORT", "5557")))
    parser.add_argument("--advertise-addr", default=os.environ.get("ADVERTISE_ADDR", ""))
    parser.add_argument("--block-size", type=int, default=int(os.environ.get("BLOCK_SIZE", "256")))
    parser.add_argument(
        "--hbm-capacity-blocks",
        type=int,
        default=int(os.environ.get("HBM_CAPACITY_BLOCKS", "360")),
    )
    parser.add_argument(
        "--enable-hma-dram",
        action="store_true",
        default=os.environ.get("ENABLE_HMA_DRAM", "0").lower() in ("1", "true", "yes"),
    )
    parser.add_argument(
        "--dram-capacity-blocks",
        type=int,
        default=int(os.environ.get("DRAM_CAPACITY_BLOCKS", "4096")),
    )
    parser.add_argument(
        "--zmq-encoding",
        choices=["json", "msgpack"],
        default=os.environ.get("ZMQ_ENCODING", "json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = TPUWorkerState(
        pod_id=args.pod_id,
        role=args.role,
        http_port=args.port,
        zmq_pub_port=args.zmq_pub_port,
        advertise_addr=args.advertise_addr,
        block_size=args.block_size,
        hbm_capacity_blocks=args.hbm_capacity_blocks,
        enable_hma_dram=args.enable_hma_dram,
        dram_capacity_blocks=args.dram_capacity_blocks,
        zmq_encoding=args.zmq_encoding,
    )
    app = create_app(state)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
