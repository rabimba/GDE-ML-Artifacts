"""Tests for the reusable `autokernel` library (TPU Pallas kernel fusion & HF model patcher)."""

from __future__ import annotations

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytest

import autokernel
from autokernel import (
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


class _DummyRMSNorm(nn.Module):
    """Mimics Hugging Face Qwen2RMSNorm / LlamaRMSNorm."""

    def __init__(self, hidden_size: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.linspace(0.8, 1.2, hidden_size))
        self.variance_epsilon = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        orig_dtype = x.dtype
        x_f32 = x.to(torch.float32)
        var = x_f32.pow(2).mean(-1, keepdim=True)
        normed = x_f32 * torch.rsqrt(var + self.variance_epsilon)
        return self.weight * normed.to(orig_dtype)


class _DummySwiGLUMLP(nn.Module):
    """Mimics Hugging Face Qwen2MLP / LlamaMLP."""

    def __init__(self, hidden_size: int, intermediate_size: int) -> None:
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class _DummyDecoderLayer(nn.Module):
    def __init__(self, hidden_size: int, intermediate_size: int) -> None:
        super().__init__()
        self.input_layernorm = _DummyRMSNorm(hidden_size)
        self.post_attention_layernorm = _DummyRMSNorm(hidden_size)
        self.mlp = _DummySwiGLUMLP(hidden_size, intermediate_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x + self.input_layernorm(x)
        h = h + self.mlp(self.post_attention_layernorm(h))
        return h


class _DummyCausalLM(nn.Module):
    def __init__(self, num_layers: int = 4, hidden_size: int = 64, intermediate_size: int = 128) -> None:
        super().__init__()
        self.layers = nn.ModuleList(
            [_DummyDecoderLayer(hidden_size, intermediate_size) for _ in range(num_layers)]
        )
        self.norm = _DummyRMSNorm(hidden_size)
        self.lm_head = nn.Linear(hidden_size, 32, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x
        for layer in self.layers:
            h = layer(h)
        h = self.norm(h)
        return self.lm_head(h)


@pytest.mark.parametrize(
    "n_rows,max_tile,expected",
    [
        (2048, 512, 512),
        (768, 512, 256),
        (384, 512, 128),
        (96, 512, 32),
        (17, 512, 1),
    ],
)
def test_solve_tile_size_divides_rows_cleanly(n_rows: int, max_tile: int, expected: int) -> None:
    """Catch Pallas grid division crashes when B*S is not a multiple of a hardcoded tile size."""
    tile = solve_tile_size(n_rows, max_tile=max_tile)
    assert tile == expected
    assert n_rows % tile == 0


def test_init_tpu_sets_single_chip_isolation_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Catch multi-chip /dev/vfio lock collisions caused by stale TPU_VISIBLE_DEVICES."""
    monkeypatch.setenv("TPU_VISIBLE_DEVICES", "0,1,2,3")
    info = init_tpu(chip=0, defer_and_fuse=True)
    assert os.environ.get("TPU_VISIBLE_CHIPS") == "0"
    assert os.environ.get("TPU_CHIPS_PER_HOST_BOUNDS") == "1,1,1"
    assert "TPU_VISIBLE_DEVICES" not in os.environ
    assert os.environ.get("TORCH_TPU_DEFER_AND_FUSE") == "1"
    assert info["chip"] == "0"


def test_fused_primitives_match_exact_math() -> None:
    """Catch numerical regressions in fused_rmsnorm, fused_res_rmsnorm, and fused_swiglu."""
    torch.manual_seed(0)
    x = torch.randn(2, 16, 64, dtype=torch.float32)
    res = torch.randn(2, 16, 64, dtype=torch.float32)
    w = torch.linspace(0.9, 1.1, 64, dtype=torch.float32)

    # Hand-derived RMSNorm
    rms_expected = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + 1e-6) * w
    rms_actual = fused_rmsnorm(x, w, eps=1e-6)
    assert torch.allclose(rms_actual, rms_expected, atol=1e-5)

    # Hand-derived Residual + RMSNorm
    h = x + res
    res_rms_expected = h * torch.rsqrt(h.pow(2).mean(-1, keepdim=True) + 1e-6) * w
    res_rms_actual = fused_res_rmsnorm(x, res, w, eps=1e-6)
    assert torch.allclose(res_rms_actual, res_rms_expected, atol=1e-5)

    # Hand-derived SwiGLU
    gate = torch.randn(2, 16, 128, dtype=torch.float32)
    up = torch.randn(2, 16, 128, dtype=torch.float32)
    swiglu_expected = (gate * torch.sigmoid(gate)) * up
    swiglu_actual = fused_swiglu(gate, up)
    assert torch.allclose(swiglu_actual, swiglu_expected, atol=1e-5)


def test_patch_hf_replaces_submodules_inplace_without_copying_weights() -> None:
    """Catch missing submodule swaps, broken weight references, or output drift after patch_hf."""
    torch.manual_seed(7)
    model = _DummyCausalLM(num_layers=4, hidden_size=64, intermediate_size=128).eval()
    x = torch.randn(2, 16, 64)

    orig_norm0_weight = model.layers[0].input_layernorm.weight
    orig_gate0_weight = model.layers[0].mlp.gate_proj.weight

    with torch.no_grad():
        baseline_logits = model(x)

    report: PatchReport = patch_hf(model)
    # 4 layers * 2 norms + 1 final norm = 9 RMSNorms; 4 layers * 1 MLP = 4 SwiGLUMLPs -> 13 total
    assert report.rmsnorm_patched == 9
    assert report.swiglu_patched == 4
    assert report.total_patched == 13
    assert isinstance(model.layers[0].input_layernorm, PallasRMSNorm)
    assert isinstance(model.layers[0].mlp, PallasSwiGLUMLP)

    # Verify zero weight copying: underlying Parameter objects must be identical
    assert model.layers[0].input_layernorm.weight is orig_norm0_weight
    assert model.layers[0].mlp.gate_proj.weight is orig_gate0_weight

    with torch.no_grad():
        patched_logits = model(x)

    assert torch.allclose(patched_logits, baseline_logits, atol=1e-5)

    # Verify unpatch_hf restores original module types cleanly
    restored = unpatch_hf(model)
    assert restored == 13
    assert not isinstance(model.layers[0].input_layernorm, PallasRMSNorm)


def test_verify_parity_and_speedup_computes_metrics() -> None:
    """Catch wrong parity or top-1 agreement calculation in BenchmarkReport."""
    torch.manual_seed(11)
    model_a = _DummyCausalLM(num_layers=2, hidden_size=32, intermediate_size=64).eval()
    x = torch.randn(2, 8, 32)

    def run_stock(inp: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return model_a(inp)

    bench: BenchmarkReport = verify_parity_and_speedup(
        stock_fn=run_stock,
        patched_fn=run_stock,
        sample_input=x,
        warmup=1,
        iters=3,
    )
    assert bench.max_abs_diff == 0.0
    assert bench.top1_agreement == 1.0
    assert bench.stock_median_ms > 0.0
    assert bench.patched_median_ms > 0.0
    assert bench.passed is True


def test_pallas_registration_handles_pep563_string_annotations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Catch NameError when torch.tpu.pallas.jax_op calls inspect.signature(fn, eval_str=True)."""
    import inspect
    import sys
    import types

    dummy_jax = types.ModuleType("jax")
    dummy_jax.Array = torch.Tensor  # type: ignore[attr-defined]
    dummy_jnp = types.ModuleType("jax.numpy")
    dummy_jnp.float32 = torch.float32  # type: ignore[attr-defined]
    dummy_pl = types.ModuleType("jax.experimental.pallas")
    dummy_exp = types.ModuleType("jax.experimental")
    dummy_exp.pallas = dummy_pl  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "jax", dummy_jax)
    monkeypatch.setitem(sys.modules, "jax.numpy", dummy_jnp)
    monkeypatch.setitem(sys.modules, "jax.experimental", dummy_exp)
    monkeypatch.setitem(sys.modules, "jax.experimental.pallas", dummy_pl)

    captured_sigs: list[inspect.Signature] = []

    def fake_jax_op(name: str, fn):
        sig = inspect.signature(inspect.unwrap(fn), eval_str=True)
        captured_sigs.append(sig)
        return fn

    fake_tpu = types.SimpleNamespace(pallas=types.SimpleNamespace(jax_op=fake_jax_op))
    monkeypatch.setattr(torch, "tpu", fake_tpu, raising=False)
    autokernel.core._PALLAS_OP_CACHE.clear()

    autokernel.core._get_or_register_pallas_rmsnorm(eps=1e-6)
    autokernel.core._get_or_register_pallas_res_rmsnorm(eps=1e-6)
    autokernel.core._get_or_register_pallas_swiglu()

    assert len(captured_sigs) == 3
    autokernel.core._PALLAS_OP_CACHE.clear()

