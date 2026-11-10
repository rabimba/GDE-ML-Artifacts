"""Core implementation of `autokernel`: Pallas VMEM kernel fusion & in-place Hugging Face patching for `torch_tpu`."""

from __future__ import annotations

import glob
import os
import statistics
import time
from dataclasses import dataclass, field
from typing import Callable

import torch
import torch.nn as nn
import torch.nn.functional as F

_PALLAS_OP_CACHE: dict[str, Callable[..., torch.Tensor]] = {}
_TPU_INITIALIZED: bool = False


@dataclass(frozen=True)
class PatchReport:
    """Summary of Hugging Face submodules hot-swapped in memory by `patch_hf`."""

    rmsnorm_patched: int
    swiglu_patched: int
    patched_paths: list[str] = field(default_factory=list)

    @property
    def total_patched(self) -> int:
        return self.rmsnorm_patched + self.swiglu_patched


@dataclass(frozen=True)
class BenchmarkReport:
    """Latency and numerical parity summary produced by `verify_parity_and_speedup`."""

    stock_median_ms: float
    patched_median_ms: float
    speedup: float
    max_abs_diff: float
    top1_agreement: float
    passed: bool


def solve_tile_size(n_rows: int, max_tile: int = 512) -> int:
    """Return the largest TPU-friendly power-of-two tile size <= `max_tile` that divides `n_rows` cleanly."""
    if n_rows <= 0:
        raise ValueError(f"n_rows must be positive, got {n_rows}")
    candidates = [512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
    for tile in candidates:
        if tile <= max_tile and n_rows % tile == 0:
            return tile
    return 1


def _wait_for_vfio_chip_free(chip: int = 0, max_wait_s: float = 60.0) -> None:
    """Wait until `/dev/vfio/*` is not held by another process if requested."""
    if max_wait_s <= 0:
        return
    t_start = time.monotonic()
    target_vfio = f"/dev/vfio/{chip + 4}"
    while time.monotonic() - t_start < max_wait_s:
        holders: list[str] = []
        for fd_path in glob.glob("/proc/[0-9]*/fd/*"):
            try:
                target = os.readlink(fd_path)
                if target == target_vfio or target.startswith("/dev/vfio/"):
                    pid = fd_path.split("/")[2]
                    if int(pid) != os.getpid():
                        holders.append(pid)
            except OSError:
                continue
        if not holders:
            return
        time.sleep(0.5)


def init_tpu(
    chip: int = 0,
    defer_and_fuse: bool = True,
    wait_for_vfio_s: float = 0.0,
) -> dict[str, str]:
    """Isolate the process to a single TPU chip and acquire the PJRT runtime before JAX/Pallas loads.

    Prevents `/dev/vfio` lock collisions when `torch_tpu` and `jax.experimental.pallas` share a process.
    """
    global _TPU_INITIALIZED
    chip_str = str(chip)
    os.environ.setdefault("TPU_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("TPU_STDERR_LOG_LEVEL", "2")
    os.environ.setdefault("TORCH_CPP_LOG_LEVEL", "ERROR")
    os.environ.pop("TPU_VISIBLE_DEVICES", None)

    env_updates = {
        "TPU_VISIBLE_CHIPS": chip_str,
        "TPU_SKIP_MDS_QUERY": "1",
        "TPU_CHIPS_PER_HOST_BOUNDS": "1,1,1",
        "TPU_HOST_BOUNDS": "1,1,1",
        "TPU_WORKER_ID": "0",
        "TPU_WORKER_HOSTNAMES": "localhost",
    }
    if defer_and_fuse:
        env_updates["TORCH_TPU_DEFER_AND_FUSE"] = "1"

    for k, v in env_updates.items():
        os.environ[k] = v

    _wait_for_vfio_chip_free(chip=chip, max_wait_s=wait_for_vfio_s)

    backend = "cpu"
    try:
        import torch_tpu  # noqa: F401

        _warmup = torch.ones(1, device=torch.device("tpu"))
        torch.accelerator.synchronize()
        _TPU_INITIALIZED = True
        backend = "tpu"
    except Exception:
        backend = "cpu"

    return {
        "chip": chip_str,
        "backend": backend,
        "defer_and_fuse": os.environ.get("TORCH_TPU_DEFER_AND_FUSE", "0"),
    }


def _has_tpu_pallas(tensor: torch.Tensor) -> bool:
    """Return True when `tensor` lives on a TPU device and `torch.tpu.pallas.jax_op` is available."""
    if tensor.device.type != "tpu":
        return False
    tpu_mod = getattr(torch, "tpu", None)
    pallas_mod = getattr(tpu_mod, "pallas", None)
    return hasattr(pallas_mod, "jax_op")


def _get_or_register_pallas_rmsnorm(eps: float = 1e-6) -> Callable[[torch.Tensor, torch.Tensor], torch.Tensor]:
    key = f"rmsnorm_{eps:.1e}"
    if key not in _PALLAS_OP_CACHE:
        import jax
        import jax.numpy as jnp
        from jax.experimental import pallas as pl

        globals()["jax"] = jax

        def _rmsnorm_kernel(x_ref, w_ref, out_ref):
            x_f32 = x_ref[...].astype(jnp.float32)
            sq_mean = jnp.mean(x_f32 * x_f32, axis=-1, keepdims=True)
            normed = (x_f32 * jax.lax.rsqrt(sq_mean + eps)).astype(out_ref.dtype)
            out_ref[...] = normed * w_ref[...]

        def _rmsnorm_jax(x: jax.Array, w: jax.Array) -> jax.Array:
            rows_x = x.reshape(-1, x.shape[-1])
            n, d = rows_x.shape
            tile = solve_tile_size(n, max_tile=512)
            out = pl.pallas_call(
                _rmsnorm_kernel,
                grid=(n // tile,),
                in_specs=[
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((1, d), lambda i: (0, 0)),
                ],
                out_specs=pl.BlockSpec((tile, d), lambda i: (i, 0)),
                out_shape=jax.ShapeDtypeStruct(rows_x.shape, rows_x.dtype),
            )(rows_x, w.reshape(1, d))
            return out.reshape(x.shape)

        _rmsnorm_jax.__annotations__ = {"x": jax.Array, "w": jax.Array, "return": jax.Array}
        op_name = f"pallas::autokernel_rmsnorm_{len(_PALLAS_OP_CACHE)}"
        _PALLAS_OP_CACHE[key] = torch.tpu.pallas.jax_op(op_name, _rmsnorm_jax)
    return _PALLAS_OP_CACHE[key]


def _get_or_register_pallas_res_rmsnorm(
    eps: float = 1e-6,
) -> Callable[[torch.Tensor, torch.Tensor, torch.Tensor], torch.Tensor]:
    key = f"res_rmsnorm_{eps:.1e}"
    if key not in _PALLAS_OP_CACHE:
        import jax
        import jax.numpy as jnp
        from jax.experimental import pallas as pl

        globals()["jax"] = jax

        def _res_rmsnorm_kernel(x_ref, res_ref, w_ref, out_ref):
            h_f32 = (x_ref[...] + res_ref[...]).astype(jnp.float32)
            sq_mean = jnp.mean(h_f32 * h_f32, axis=-1, keepdims=True)
            normed = (h_f32 * jax.lax.rsqrt(sq_mean + eps)).astype(out_ref.dtype)
            out_ref[...] = normed * w_ref[...]

        def _res_rmsnorm_jax(x: jax.Array, res: jax.Array, w: jax.Array) -> jax.Array:
            rows_x = x.reshape(-1, x.shape[-1])
            rows_r = res.reshape(-1, res.shape[-1])
            n, d = rows_x.shape
            tile = solve_tile_size(n, max_tile=512)
            out = pl.pallas_call(
                _res_rmsnorm_kernel,
                grid=(n // tile,),
                in_specs=[
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((1, d), lambda i: (0, 0)),
                ],
                out_specs=pl.BlockSpec((tile, d), lambda i: (i, 0)),
                out_shape=jax.ShapeDtypeStruct(rows_x.shape, rows_x.dtype),
            )(rows_x, rows_r, w.reshape(1, d))
            return out.reshape(x.shape)

        _res_rmsnorm_jax.__annotations__ = {
            "x": jax.Array,
            "res": jax.Array,
            "w": jax.Array,
            "return": jax.Array,
        }
        op_name = f"pallas::autokernel_res_rmsnorm_{len(_PALLAS_OP_CACHE)}"
        _PALLAS_OP_CACHE[key] = torch.tpu.pallas.jax_op(op_name, _res_rmsnorm_jax)
    return _PALLAS_OP_CACHE[key]


def _get_or_register_pallas_swiglu() -> Callable[[torch.Tensor, torch.Tensor], torch.Tensor]:
    key = "swiglu"
    if key not in _PALLAS_OP_CACHE:
        import jax
        import jax.numpy as jnp
        from jax.experimental import pallas as pl

        globals()["jax"] = jax

        def _swiglu_kernel(gate_ref, up_ref, out_ref):
            g_f32 = gate_ref[...].astype(jnp.float32)
            silu_g = (g_f32 * jax.lax.logistic(g_f32)).astype(out_ref.dtype)
            out_ref[...] = silu_g * up_ref[...]

        def _swiglu_jax(gate: jax.Array, up: jax.Array) -> jax.Array:
            rows_g = gate.reshape(-1, gate.shape[-1])
            rows_u = up.reshape(-1, up.shape[-1])
            n, d = rows_g.shape
            tile = solve_tile_size(n, max_tile=512)
            out = pl.pallas_call(
                _swiglu_kernel,
                grid=(n // tile,),
                in_specs=[
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                ],
                out_specs=pl.BlockSpec((tile, d), lambda i: (i, 0)),
                out_shape=jax.ShapeDtypeStruct(rows_g.shape, rows_g.dtype),
            )(rows_g, rows_u)
            return out.reshape(gate.shape)

        _swiglu_jax.__annotations__ = {"gate": jax.Array, "up": jax.Array, "return": jax.Array}
        _PALLAS_OP_CACHE[key] = torch.tpu.pallas.jax_op("pallas::autokernel_swiglu", _swiglu_jax)
    return _PALLAS_OP_CACHE[key]


def fused_rmsnorm(x: torch.Tensor, weight: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Compute RMSNorm in on-chip VMEM via Pallas on TPU (or exact float32-upcast fallback)."""
    n_rows = x.numel() // x.shape[-1]
    d = x.shape[-1]
    if _has_tpu_pallas(x) and n_rows >= 8 and n_rows % 8 == 0 and d % 128 == 0:
        op = _get_or_register_pallas_rmsnorm(eps=eps)
        return op(x, weight)
    orig_dtype = x.dtype
    x_f32 = x.to(torch.float32)
    var = x_f32.pow(2).mean(-1, keepdim=True)
    normed = x_f32 * torch.rsqrt(var + eps)
    return weight * normed.to(orig_dtype)


def fused_res_rmsnorm(
    x: torch.Tensor,
    residual: torch.Tensor,
    weight: torch.Tensor,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Compute fused Residual Add + RMSNorm in on-chip VMEM via Pallas on TPU."""
    n_rows = x.numel() // x.shape[-1]
    d = x.shape[-1]
    if _has_tpu_pallas(x) and n_rows >= 8 and n_rows % 8 == 0 and d % 128 == 0:
        op = _get_or_register_pallas_res_rmsnorm(eps=eps)
        return op(x, residual, weight)
    h = x + residual
    orig_dtype = h.dtype
    h_f32 = h.to(torch.float32)
    var = h_f32.pow(2).mean(-1, keepdim=True)
    normed = h_f32 * torch.rsqrt(var + eps)
    return weight * normed.to(orig_dtype)


def fused_swiglu(gate: torch.Tensor, up: torch.Tensor) -> torch.Tensor:
    """Compute fused SwiGLU (`silu(gate) * up`) in on-chip VMEM via Pallas on TPU."""
    n_rows = gate.numel() // gate.shape[-1]
    d = gate.shape[-1]
    if _has_tpu_pallas(gate) and n_rows >= 8 and n_rows % 8 == 0 and d % 128 == 0:
        op = _get_or_register_pallas_swiglu()
        return op(gate, up)
    orig_dtype = gate.dtype
    g_f32 = gate.to(torch.float32)
    silu_g = F.silu(g_f32).to(orig_dtype)
    return silu_g * up


class PallasRMSNorm(nn.Module):
    """Drop-in Pallas VMEM replacement for Hugging Face RMSNorm layers (`Qwen2RMSNorm`, `Qwen3RMSNorm`, `LlamaRMSNorm`)."""

    def __init__(self, orig_norm: nn.Module) -> None:
        super().__init__()
        object.__setattr__(self, "_orig_module", orig_norm)
        self.weight = orig_norm.weight
        self.variance_epsilon: float = float(
            getattr(orig_norm, "variance_epsilon", getattr(orig_norm, "eps", 1e-6))
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        return fused_rmsnorm(hidden_states, self.weight, eps=self.variance_epsilon)


class PallasSwiGLUMLP(nn.Module):
    """Drop-in Pallas VMEM replacement for Hugging Face SwiGLU MLP blocks (`Qwen2MLP`, `Qwen3MLP`, `LlamaMLP`)."""

    def __init__(self, orig_mlp: nn.Module) -> None:
        super().__init__()
        object.__setattr__(self, "_orig_module", orig_mlp)
        self.gate_proj = orig_mlp.gate_proj
        self.up_proj = orig_mlp.up_proj
        self.down_proj = orig_mlp.down_proj

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = self.gate_proj(x)
        up = self.up_proj(x)
        activated = fused_swiglu(gate, up)
        return self.down_proj(activated)


def _is_rmsnorm_candidate(mod: nn.Module) -> bool:
    if isinstance(mod, PallasRMSNorm):
        return False
    cls_name = mod.__class__.__name__.lower()
    has_weight = hasattr(mod, "weight") and isinstance(getattr(mod, "weight"), torch.Tensor)
    has_eps = hasattr(mod, "variance_epsilon") or hasattr(mod, "eps")
    return has_weight and (
        "rmsnorm" in cls_name or (has_eps and not hasattr(mod, "bias"))
    )


def _is_swiglu_mlp_candidate(mod: nn.Module) -> bool:
    if isinstance(mod, PallasSwiGLUMLP):
        return False
    return (
        hasattr(mod, "gate_proj")
        and hasattr(mod, "up_proj")
        and hasattr(mod, "down_proj")
    )


def patch_hf(
    model: nn.Module,
    patch_rmsnorm: bool = True,
    patch_swiglu: bool = True,
) -> PatchReport:
    """Walk a Hugging Face `nn.Module` tree and hot-swap RMSNorm and SwiGLU MLP layers in-place.

    Preserves all existing `nn.Parameter` references without copying or reloading model weights.
    """
    rmsnorm_count = 0
    swiglu_count = 0
    patched_paths: list[str] = []

    def _walk(parent: nn.Module, prefix: str = "") -> None:
        nonlocal rmsnorm_count, swiglu_count
        for name, child in list(parent.named_children()):
            path = f"{prefix}.{name}" if prefix else name
            if patch_rmsnorm and _is_rmsnorm_candidate(child):
                setattr(parent, name, PallasRMSNorm(child))
                rmsnorm_count += 1
                patched_paths.append(path)
            elif patch_swiglu and _is_swiglu_mlp_candidate(child):
                setattr(parent, name, PallasSwiGLUMLP(child))
                swiglu_count += 1
                patched_paths.append(path)
            else:
                _walk(child, path)

    _walk(model)
    return PatchReport(
        rmsnorm_patched=rmsnorm_count,
        swiglu_patched=swiglu_count,
        patched_paths=patched_paths,
    )


def unpatch_hf(model: nn.Module) -> int:
    """Restore all `PallasRMSNorm` and `PallasSwiGLUMLP` submodules to their original `nn.Module` instances."""
    restored = 0

    def _walk(parent: nn.Module) -> None:
        nonlocal restored
        for name, child in list(parent.named_children()):
            if isinstance(child, (PallasRMSNorm, PallasSwiGLUMLP)):
                orig = getattr(child, "_orig_module", None)
                if orig is not None:
                    setattr(parent, name, orig)
                    restored += 1
            else:
                _walk(child)

    _walk(model)
    return restored


def _sync_device(tensor: torch.Tensor) -> None:
    if tensor.device.type == "tpu":
        torch.accelerator.synchronize()


def verify_parity_and_speedup(
    stock_fn: Callable[[torch.Tensor], torch.Tensor],
    patched_fn: Callable[[torch.Tensor], torch.Tensor],
    sample_input: torch.Tensor,
    warmup: int = 3,
    iters: int = 10,
    atol: float = 0.125,
    min_top1_agreement: float = 0.99,
) -> BenchmarkReport:
    """Benchmark `stock_fn` vs `patched_fn` and verify numerical parity and top-1 token agreement."""
    with torch.no_grad():
        for _ in range(warmup):
            out_stock = stock_fn(sample_input)
            _sync_device(out_stock)

        stock_times: list[float] = []
        for _ in range(iters):
            t0 = time.perf_counter()
            out_stock = stock_fn(sample_input)
            _sync_device(out_stock)
            stock_times.append((time.perf_counter() - t0) * 1000.0)

        for _ in range(warmup):
            out_patched = patched_fn(sample_input)
            _sync_device(out_patched)

        patched_times: list[float] = []
        for _ in range(iters):
            t0 = time.perf_counter()
            out_patched = patched_fn(sample_input)
            _sync_device(out_patched)
            patched_times.append((time.perf_counter() - t0) * 1000.0)

        s_cpu = out_stock.detach().to(torch.float32).cpu()
        p_cpu = out_patched.detach().to(torch.float32).cpu()
        max_diff = float((s_cpu - p_cpu).abs().max().item())

        if s_cpu.ndim >= 2:
            s_top1 = s_cpu.argmax(dim=-1)
            p_top1 = p_cpu.argmax(dim=-1)
            top1_agree = float((s_top1 == p_top1).to(torch.float32).mean().item())
        else:
            top1_agree = 1.0 if max_diff <= atol else 0.0

    stock_med = float(statistics.median(stock_times))
    patched_med = float(statistics.median(patched_times))
    speedup = stock_med / max(patched_med, 1e-9)
    passed = (max_diff <= atol) and (top1_agree >= min_top1_agreement)

    return BenchmarkReport(
        stock_median_ms=stock_med,
        patched_median_ms=patched_med,
        speedup=speedup,
        max_abs_diff=max_diff,
        top1_agreement=top1_agree,
        passed=passed,
    )
