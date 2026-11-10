# Workshop notebooks: Inference with TorchTPU on one chip

The three live demos of the workshop, reworked for **one chip and a small model**
(`Qwen/Qwen3-0.6B`) so they run on Colab's TPU runtime or any single-chip TPU VM. In Colab:
*Runtime → Change runtime type → TPU*, then run top to bottom.

| Notebook | Open | What it does |
| --- | --- | --- |
| `00_all_three_demos.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/00_all_three_demos.ipynb) | **All three in one runtime**, top to bottom: start here if TPU runtimes are scarce. About twenty minutes the first time. |
| `01_torchtpu_one_chip.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/01_torchtpu_one_chip.ipynb) | Demo 1: the device line, eager, DeferAndFuse, `torch.compile`, and one step of each under the profiler, drawn on one axis. |
| `02_sglang_torchtpu.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/02_sglang_torchtpu.ipynb) | Demo 2: SGLang-TorchTPU serving on one chip; one request, a burst of sixteen, the prefix cache. |
| `03_vllm_torchtpu.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/03_vllm_torchtpu.ipynb) | Demo 3: the same with vLLM-TorchTPU. |
| `04_specguard_e2e_app.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/04_specguard_e2e_app.ipynb) | Creative App 1 (**SpecGuard TPU**): LoRA fine-tuning `Qwen/Qwen3-0.6B` on `torch.device("tpu")`, merging the checkpoint, serving it with SGLang-TorchTPU, and running a prefix-cached codebase audit plus a 16-file concurrent burst. |
| `05_autokernel_pallas_lab.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/05_autokernel_pallas_lab.ipynb) | Creative App 2 (**AutoKernel Lab**): 4-way XProf-guided Pallas kernel fusion for a Qwen3/Llama SwiGLU decoder stack across `eager`, `DeferAndFuse`, `torch.compile`, and `torch.tpu.pallas.jax_op`. |
| `06_end_to_end_showcase_and_domain_adaptation.ipynb` | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/06_end_to_end_showcase_and_domain_adaptation.ipynb) | Master Showcase: end-to-end developer playbook combining `colab-mcp`, multi-model domain LoRA (`Qwen/Qwen3-0.6B` SecOps/TPU & `Qwen/Qwen2.5-0.5B-Instruct` FinTech PCI-DSS), in-place Pallas kernel patching of Hugging Face Transformer layers, and prefix-cached serving. |

## How they run

- **One chip, one process at a time.** The chip belongs to whichever process holds it. In
  `00` part 1 runs as a script in a subprocess and each server is stopped before the next
  starts, so the kernel never holds the chip. In the separate notebooks: do not run `01`
  and then `02`/`03` in the same runtime (the `01` kernel keeps the chip; restart the
  runtime), and run `02`'s stop cell before `03`.
- **The engines get a Python 3.12 environment of their own** (`venv-sglang`, `venv-vllm`,
  made with `uv` next to the notebook); the kernel is only the client. Their wheels are
  built for Python 3.12 and pin their own torch and TorchTPU; Colab's kernel is a different
  Python with its own packages. The first run downloads about two gigabytes per environment.
- **The install lines are the projects' own README lines:** `pip install torch_tpu`
  (TorchTPU), `pip install vllm-torchtpu`, and the two `sglang-torchtpu` release wheels.
  The install cells are idempotent and print versions; if something is half-installed,
  `rm -rf venv-*` and run the cell again.
- **Every number a cell prints is that run's own**: this chip, this model, these settings.
  Colab's TPU runtime is a different chip from the workshop's, so times differ; the shape
  of what you see does not.
- `img/` holds the slides the notebooks show.

## Sources

- TorchTPU: [github.com/google-pytorch/torch_tpu](https://github.com/google-pytorch/torch_tpu)
  (README "Install via pip", `docs/performance_profiling_with_xprof.md`).
- vLLM on TPU: [github.com/vllm-project/vllm-torchtpu](https://github.com/vllm-project/vllm-torchtpu)
  (README "Install", `docs/user_guide/supported_models.md`).
- SGLang on TPU: [github.com/sgl-project/sglang-torchtpu](https://github.com/sgl-project/sglang-torchtpu)
  (README, the `tpu-v0.1.0` release, `SUPPORT_MATRIX.md`).
