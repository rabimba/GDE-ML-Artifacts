"""`autokernel`: Reusable Pallas VMEM kernel fusion & in-place Hugging Face patcher for `torch_tpu`."""

from __future__ import annotations

from .core import (
    BenchmarkReport,
    PallasRMSNorm,
    PallasSwiGLUMLP,
    PatchReport,
    fused_res_rmsnorm,
    fused_rmsnorm,
    fused_swiglu,
    init_tpu,
    patch_hf,
    solve_tile_size,
    unpatch_hf,
    verify_parity_and_speedup,
)

__version__ = "0.1.0"

__all__ = [
    "BenchmarkReport",
    "PallasRMSNorm",
    "PallasSwiGLUMLP",
    "PatchReport",
    "fused_res_rmsnorm",
    "fused_rmsnorm",
    "fused_swiglu",
    "init_tpu",
    "patch_hf",
    "solve_tile_size",
    "unpatch_hf",
    "verify_parity_and_speedup",
]
