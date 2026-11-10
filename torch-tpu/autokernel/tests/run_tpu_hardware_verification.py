"""Live hardware test suite for `autokernel` on Cloud TPU (`tpu7x` Chip 0)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Support running either from installed package or shipped alongside core.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import autokernel
except ImportError:
    import core as autokernel  # type: ignore[no-redef]

# 1. Isolate Chip 0 and wake up torch_tpu BEFORE JAX/Pallas loads
init_info = autokernel.init_tpu(chip=0, defer_and_fuse=True, wait_for_vfio_s=60.0)

import torch
import torch.nn as nn
import torch.nn.functional as F


class Qwen2RMSNormRef(nn.Module):
    def __init__(self, hidden_size: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        dt = x.dtype
        x_f32 = x.to(torch.float32)
        var = x_f32.pow(2).mean(-1, keepdim=True)
        return self.weight * (x_f32 * torch.rsqrt(var + self.variance_epsilon)).to(dt)


class Qwen2MLPRef(nn.Module):
    def __init__(self, hidden_size: int, intermediate_size: int) -> None:
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class Qwen2LayerRef(nn.Module):
    def __init__(self, hidden_size: int, intermediate_size: int) -> None:
        super().__init__()
        self.input_layernorm = Qwen2RMSNormRef(hidden_size)
        self.post_attention_layernorm = Qwen2RMSNormRef(hidden_size)
        self.mlp = Qwen2MLPRef(hidden_size, intermediate_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x + self.input_layernorm(x)
        h = h + self.mlp(self.post_attention_layernorm(h))
        return h


class Qwen2Model24LRef(nn.Module):
    """24-layer Qwen2-0.5B structure (49 RMSNorms + 24 SwiGLU MLPs = 73 submodules)."""

    def __init__(self, num_layers: int = 24, hidden_size: int = 896, intermediate_size: int = 4864) -> None:
        super().__init__()
        self.layers = nn.ModuleList(
            [Qwen2LayerRef(hidden_size, intermediate_size) for _ in range(num_layers)]
        )
        self.norm = Qwen2RMSNormRef(hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x
        for layer in self.layers:
            h = layer(h)
        return self.norm(h)


def main() -> None:
    assert init_info["backend"] == "tpu", f"Expected TPU backend, got {init_info}"
    assert os.environ.get("TPU_VISIBLE_CHIPS") == "0"
    device = torch.device("tpu")

    torch.manual_seed(42)
    x = torch.randn(4, 128, 896, dtype=torch.bfloat16, device=device)
    res = torch.randn(4, 128, 896, dtype=torch.bfloat16, device=device)
    w = torch.ones(896, dtype=torch.bfloat16, device=device)
    gate = torch.randn(4, 128, 4864, dtype=torch.bfloat16, device=device)
    up = torch.randn(4, 128, 4864, dtype=torch.bfloat16, device=device)

    # 1. Verify Pallas fused_rmsnorm on TPU
    ref_rms = w * (
        x.to(torch.float32) * torch.rsqrt(x.to(torch.float32).pow(2).mean(-1, keepdim=True) + 1e-6)
    ).to(torch.bfloat16)
    ak_rms = autokernel.fused_rmsnorm(x, w, eps=1e-6)
    torch.accelerator.synchronize()
    rms_diff = float((ref_rms.float().cpu() - ak_rms.float().cpu()).abs().max().item())
    assert rms_diff <= 0.0625, f"fused_rmsnorm diff too high: {rms_diff}"

    # 2. Verify Pallas fused_res_rmsnorm on TPU
    h = x + res
    ref_res_rms = w * (
        h.to(torch.float32) * torch.rsqrt(h.to(torch.float32).pow(2).mean(-1, keepdim=True) + 1e-6)
    ).to(torch.bfloat16)
    ak_res_rms = autokernel.fused_res_rmsnorm(x, res, w, eps=1e-6)
    torch.accelerator.synchronize()
    res_rms_diff = float((ref_res_rms.float().cpu() - ak_res_rms.float().cpu()).abs().max().item())
    assert res_rms_diff <= 0.0625, f"fused_res_rmsnorm diff too high: {res_rms_diff}"

    # 3. Verify Pallas fused_swiglu on TPU
    ref_swiglu = F.silu(gate.to(torch.float32)).to(torch.bfloat16) * up
    ak_swiglu = autokernel.fused_swiglu(gate, up)
    torch.accelerator.synchronize()
    swiglu_diff = float((ref_swiglu.float().cpu() - ak_swiglu.float().cpu()).abs().max().item())
    assert swiglu_diff <= 0.0625, f"fused_swiglu diff too high: {swiglu_diff}"

    # 4. Verify 24-layer RMSNorm stack speedup with verify_parity_and_speedup
    norms_stock = nn.ModuleList([Qwen2RMSNormRef(896) for _ in range(24)]).to(device).to(torch.bfloat16).eval()

    def run_stock_norms(inp: torch.Tensor) -> torch.Tensor:
        out = inp
        for n_mod in norms_stock:
            out = n_mod(out)
        return out

    norms_patched = nn.ModuleList([Qwen2RMSNormRef(896) for _ in range(24)]).to(device).to(torch.bfloat16).eval()
    norm_patch_report = autokernel.patch_hf(norms_patched)
    assert norm_patch_report.rmsnorm_patched == 24

    def run_patched_norms(inp: torch.Tensor) -> torch.Tensor:
        out = inp
        for n_mod in norms_patched:
            out = n_mod(out)
        return out

    norm_bench = autokernel.verify_parity_and_speedup(
        stock_fn=run_stock_norms,
        patched_fn=run_patched_norms,
        sample_input=x,
        warmup=5,
        iters=20,
        atol=0.125,
    )
    assert norm_bench.passed, f"24L norm stack verification failed: {norm_bench}"
    assert norm_bench.speedup > 1.5, f"Expected >1.5x speedup on 24L norm stack, got {norm_bench.speedup:.2f}x"

    # 5. Verify 73-submodule in-place patch & unpatch on 24-layer Qwen2 model
    model_24l = Qwen2Model24LRef(num_layers=24, hidden_size=896, intermediate_size=4864).to(device).to(torch.bfloat16).eval()
    patch_rep = autokernel.patch_hf(model_24l)
    assert patch_rep.rmsnorm_patched == 49
    assert patch_rep.swiglu_patched == 24
    assert patch_rep.total_patched == 73

    with torch.no_grad():
        out_patched = model_24l(x)
        torch.accelerator.synchronize()

    restored_count = autokernel.unpatch_hf(model_24l)
    assert restored_count == 73

    with torch.no_grad():
        out_unpatched = model_24l(x)
        torch.accelerator.synchronize()

    model_diff = float((out_patched.float().cpu() - out_unpatched.float().cpu()).abs().max().item())

    summary = {
        "status": "PASS",
        "init_info": init_info,
        "primitive_max_diffs": {
            "fused_rmsnorm": rms_diff,
            "fused_res_rmsnorm": res_rms_diff,
            "fused_swiglu": swiglu_diff,
        },
        "norm_stack_24l_benchmark": {
            "stock_median_ms": round(norm_bench.stock_median_ms, 4),
            "patched_median_ms": round(norm_bench.patched_median_ms, 4),
            "speedup": round(norm_bench.speedup, 2),
            "max_abs_diff": round(norm_bench.max_abs_diff, 6),
            "top1_agreement": round(norm_bench.top1_agreement, 4),
        },
        "qwen2_24l_patch_report": {
            "rmsnorm_patched": patch_rep.rmsnorm_patched,
            "swiglu_patched": patch_rep.swiglu_patched,
            "total_patched": patch_rep.total_patched,
            "restored_count": restored_count,
            "max_abs_diff_vs_unpatched": round(model_diff, 6),
        },
    }
    print(json.dumps(summary, indent=2))
    Path("autokernel_tpu_verification.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
