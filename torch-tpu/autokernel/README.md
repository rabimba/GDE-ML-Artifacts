# `autokernel` — Pallas VMEM Kernel Fusion & In-Place Hugging Face Patcher for `torch_tpu`

`autokernel` is a lightweight Python library for **native PyTorch on Cloud TPU (`torch_tpu`)**. It provides:

1. **Collision-Free Single-Chip Initialization (`autokernel.init_tpu`)**: Isolates a single TPU chip (`TPU_VISIBLE_CHIPS="0"`) and wakes up `torch_tpu`'s PJRT runtime *before* JAX/Pallas loads, preventing `/dev/vfio` lock collisions.
2. **On-Chip Scratchpad (`VMEM`) Pallas Operators**:
   - `autokernel.fused_rmsnorm(x, weight, eps=1e-6)`
   - `autokernel.fused_res_rmsnorm(x, residual, weight, eps=1e-6)`
   - `autokernel.fused_swiglu(gate, up)`
3. **One-Line In-Memory Hugging Face Model Surgery (`autokernel.patch_hf`)**:
   Walks any Qwen2, Qwen3, Llama, or Gemma `nn.Module` in memory and swaps all `RMSNorm` and `SwiGLU MLP` layers with fused Pallas `jax_op` kernels without copying or reloading model weights (`unpatch_hf(model)` restores the original modules).
4. **Automated Parity & Speedup Verifier (`autokernel.verify_parity_and_speedup`)**:
   Measures median step latency, speedup, max absolute difference, and top-1 token agreement.

## Quickstart

```python
import autokernel

# 1. Isolate Chip 0 & wake up torch_tpu before JAX/Pallas
autokernel.init_tpu(chip=0, defer_and_fuse=True)

import torch
from transformers import AutoModelForCausalLM

device = torch.device("tpu")
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct", dtype=torch.bfloat16
).to(device).eval()

# 2. Hot-swap all 73 RMSNorm (49) + SwiGLU MLP (24) submodules in memory
report = autokernel.patch_hf(model)
print(f"Patched {report.total_patched} submodules ({report.rmsnorm_patched} RMSNorm, {report.swiglu_patched} SwiGLU)")
```

## Installation & Testing

```bash
pip install -e ./autokernel
pytest autokernel/tests/test_autokernel.py
```
