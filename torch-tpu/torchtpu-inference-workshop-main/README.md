# Inference with TorchTPU

The material from the **Inference with TorchTPU** workshop at TorchTPU DevLabs
(Nov 9, 2026, 30 minutes): the files behind each live demo, three notebooks that do the
same on one chip, and the slides.

TorchTPU makes a Cloud TPU a PyTorch device. The workshop is three parts and three live
demos:

1. **TorchTPU: the TPU is a PyTorch device.** Set the device, debug in eager mode, ship
   with `torch.compile`. Demo 1: one script on one chip, in eager mode, then with
   `TORCH_TPU_DEFER_AND_FUSE=1`, then under `torch.compile`.
2. **Inference 101: what decides serving speed.** Attention and the KV cache, prefill and
   decode, HBM capacity and bandwidth. No live demo.
3. **vLLM and SGLang on TorchTPU.** The engines install and run the way you know; the TPU
   work is underneath, in kernels they ship. Demo 2: SGLang, one long prompt asked about
   twice (the prefix cache). Demo 3: vLLM, one request, then sixty-four at once (continuous
   batching).

## What is here

| Folder | What | Needs |
|---|---|---|
| [`demos/01_one_chip/`](demos/01_one_chip/) | Demo 1: one MLP, on the CPU, on the TPU in eager mode (and the same file again with `TORCH_TPU_DEFER_AND_FUSE=1`), and under `torch.compile`; `profiler.py eager\|defer\|compiled` is the same model under the standard PyTorch profiler (`torch.profiler` with the TPU activity), viewed in XProf, the TPU profiler in TensorBoard | a TPU VM, one chip |
| [`demos/02_sglang/`](demos/02_sglang/) | Demo 2: SGLang serving Qwen3-32B across four chips; one long prompt asked about twice, showing the prefix cache | a TPU VM, four chips |
| [`demos/03_vllm/`](demos/03_vllm/) | Demo 3: vLLM serving the same model the same way; one request, then sixty-four at once | a TPU VM, four chips |
| [`demos/04_kernel/`](demos/04_kernel/) | Extra, not shown in the session: RMSNorm in plain PyTorch ops, then as a Pallas kernel called from PyTorch, both profiled | a TPU VM, one chip |
| [`demos/05_specguard_app/`](demos/05_specguard_app/) | Creative App 1 (**SpecGuard TPU**): end-to-end LoRA fine-tuning of `Qwen/Qwen3-0.6B` on `torch.device("tpu")`, checkpoint merge, SGLang-TorchTPU prefix-cached codebase auditing, and a 16-file concurrent continuous-batching burst | a TPU VM, one chip |
| [`demos/06_autokernel_app/`](demos/06_autokernel_app/) | Creative App 2 (**AutoKernel Lab**): 4-way XProf-guided Pallas kernel fusion for a 4-layer Qwen3/Llama SwiGLU decoder stack across `eager`, `TORCH_TPU_DEFER_AND_FUSE=1`, `torch.compile`, and `torch.tpu.pallas.jax_op` (`pallas::fused_res_rmsnorm` and `pallas::fused_swiglu`) | a TPU VM, one chip |
| [`demos/07_domain_adaptation_showcase/`](demos/07_domain_adaptation_showcase/) | Master Showcase: multi-model domain LoRA adaptation (`Qwen/Qwen3-0.6B` SecOps/TPU & `Qwen/Qwen2.5-0.5B-Instruct` FinTech PCI-DSS) plus in-place Pallas kernel patching (`pallas::hf_rmsnorm` and `pallas::hf_swiglu`) across Hugging Face Transformer layers | a TPU VM, one chip |
| [`demos/setup/`](demos/setup/) | Install scripts for the three environments (TorchTPU; SGLang; vLLM), from the projects' own READMEs | |
| [`notebooks/`](notebooks/) | The three demos on **one chip and a small model** (`Qwen/Qwen3-0.6B`), numbered like the demos, for Colab's TPU runtime or a single-chip VM; badges below | Colab |
| [`slides/`](slides/) | The deck as a PDF (one page per slide, as shown) | |

## Notebooks

Each opens in Colab from this repository (*Runtime → Change runtime type → TPU*); see
[`notebooks/README.md`](notebooks/README.md) for how they run. If TPU runtimes are scarce,
the first one does all three demos in one runtime.

- All three demos, one runtime: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/00_all_three_demos.ipynb) [`notebooks/00_all_three_demos.ipynb`](notebooks/00_all_three_demos.ipynb)
- Demo 1, TorchTPU on one chip: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/01_torchtpu_one_chip.ipynb) [`notebooks/01_torchtpu_one_chip.ipynb`](notebooks/01_torchtpu_one_chip.ipynb)
- Demo 2, SGLang on TorchTPU: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/02_sglang_torchtpu.ipynb) [`notebooks/02_sglang_torchtpu.ipynb`](notebooks/02_sglang_torchtpu.ipynb)
- Demo 3, vLLM on TorchTPU: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/03_vllm_torchtpu.ipynb) [`notebooks/03_vllm_torchtpu.ipynb`](notebooks/03_vllm_torchtpu.ipynb)
- Creative App 1, SpecGuard TPU (LoRA to Prefix-Cached SGLang): [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/04_specguard_e2e_app.ipynb) [`notebooks/04_specguard_e2e_app.ipynb`](notebooks/04_specguard_e2e_app.ipynb)
- Creative App 2, AutoKernel Lab (XProf-Guided Pallas Fusion): [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/05_autokernel_pallas_lab.ipynb) [`notebooks/05_autokernel_pallas_lab.ipynb`](notebooks/05_autokernel_pallas_lab.ipynb)
- Master Showcase, Multi-Model Domain Adaptation & In-Model Pallas Patching: [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/06_end_to_end_showcase_and_domain_adaptation.ipynb) [`notebooks/06_end_to_end_showcase_and_domain_adaptation.ipynb`](notebooks/06_end_to_end_showcase_and_domain_adaptation.ipynb)

## Running the demos on a TPU VM

Create a Cloud TPU VM (the demos were written on a v6e-1 for demo 1 and a v6e-4 for demos
2 and 3; see the [Cloud TPU documentation](https://cloud.google.com/tpu/docs)), clone this
repository on it, and:

```bash
# Demo 1: one chip
bash demos/setup/install_torchtpu.sh && source ~/venv-torchtpu/bin/activate
cd demos/01_one_chip && python example1_eager.py
TORCH_TPU_DEFER_AND_FUSE=1 python example1_eager.py        # the same script, DeferAndFuse on
python example2_compile.py
for m in eager defer compiled; do python profiler.py $m; done   # traces/ for TensorBoard
tensorboard --logdir traces --port 6006                   # Profile tab (XProf), Trace Viewer

# Demo 2: SGLang on four chips (its own venv)
bash demos/setup/install_sglang.sh && source ~/venv-sglang/bin/activate
cd demos/02_sglang && bash serve.sh &                      # first start downloads the model
cp "$VIRTUAL_ENV"/lib/python3.*/site-packages/torch/nn/modules/transformer.py .  # ask.py's long prompt
python ask.py                                              # once the server answers on :30000

# Demo 3: vLLM on four chips (its own venv; stop SGLang first, one engine per machine)
bash demos/setup/install_vllm.sh && source ~/venv-vllm/bin/activate
cd demos/03_vllm && bash serve.sh &
python burst.py 1 && python burst.py 64                    # once the server answers on :8000

# Extra: the kernel demo, in the TorchTPU venv on one chip
cd demos/04_kernel && python rmsnorm_eager.py && python rmsnorm_pallas.py
```

Every number the scripts print is that run's own. The model, `Qwen/Qwen3-32B`, is about
64 GB in bfloat16, which is why it takes four chips; the notebooks use `Qwen/Qwen3-0.6B`
on one.

## Sources

- TorchTPU: [github.com/google-pytorch/torch_tpu](https://github.com/google-pytorch/torch_tpu)
  (README, `docs/performance_profiling_with_xprof.md`, `docs/custom_kernels.md`).
- vLLM on TPU: [github.com/vllm-project/vllm-torchtpu](https://github.com/vllm-project/vllm-torchtpu).
- SGLang on TPU: [github.com/sgl-project/sglang-torchtpu](https://github.com/sgl-project/sglang-torchtpu).

## License

Apache 2.0, see [LICENSE](LICENSE).
