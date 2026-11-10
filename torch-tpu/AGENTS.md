# AGENTS.md — `torch-tpu` Workspace

Workspace for PyTorch on Google Cloud TPU (`torch_tpu`) workshops, demos, and the installed **TPU Agent Suite** (`tpu-agent-suite@0.7.0`).

## Directory Layout

- **`tpu-agent-suite/`**: Clone of [`google-pytorch/tpu-agent-suite`](https://github.com/google-pytorch/tpu-agent-suite). Multi-agent compiler, installer, compute runtime, and the `tpu-agent-suite` package (v0.7.0).
  - `framework/`: Compiler (`compiler.py`), installer (`installer.py`), runtime (`runtime.py`), hooks, and unified TPU compute layer (`compute/`).
  - `package/`: Agent definitions (`package/agents/`), user-invocable skills (`package/skills/`), JSON schemas (`package/schemas/`), scripts, and TPU knowledge base (`package/data/tpu-knowledge-base/`).
  - `eval/`: Harbor evaluation suites and configs.
- **`.claude/`, `.opencode/`, `.tpu-agent-suite/`, `~/.tpu-agent-suite/`**: Installed `tpu-agent-suite@0.7.0` artifacts for this workspace:
  - Skills: `tpu-agent` (entry-point router for TPU onboarding, profiling, benchmarking, kernel tuning, and hardware Q&A) and `tpu-agent-export-trajectory`.
  - Subagents: `tpu-model-onboarding`, `tpu-diagnostics`, `tpu-kernel-development`, `tpu-knowledge-base`, `tpu-unwiring`, `kernel-worker`, `analyze-cuda-reference`.
  - Compute configuration: `.tpu-agent-suite/environment.json` (managed via `runtime.py compute setup` / `runtime.py config` — never edit by hand).
- **`torchtpu-inference-workshop-main/`**: *Inference with TorchTPU* workshop (see its own `AGENTS.md` and `README.md`):
  - `demos/01_one_chip/`: CPU vs TPU eager, `TORCH_TPU_DEFER_AND_FUSE=1`, `torch.compile(backend="tpu")`, and `profiler.py` (XProf traces).
  - `demos/02_sglang/`: SGLang serving `Qwen/Qwen3-32B` (`--device tpu --tp-size 4`) + prefix cache demo (`ask.py`).
  - `demos/03_vllm/`: vLLM serving `Qwen/Qwen3-32B` (`--tensor-parallel-size 4`) + continuous batching demo (`burst.py`, `grid.py`).
  - `demos/04_kernel/`: RMSNorm in eager ops, compiled, and custom Pallas kernel (`rmsnorm_pallas.py`).
  - `demos/05_specguard_app/`: Application A (**SpecGuard TPU**): LoRA fine-tuning on TPU -> checkpoint merge -> SGLang-TorchTPU prefix-cached & 16-file concurrent burst auditing.
  - `demos/06_autokernel_app/`: Application C (**AutoKernel Lab**): 4-way XProf-guided Pallas kernel fusion (`eager`, `DeferAndFuse`, `torch.compile`, and `torch.tpu.pallas.jax_op`).
  - `demos/07_domain_adaptation_showcase/`: Multi-model domain LoRA (`Qwen/Qwen3-0.6B` SecOps/TPU & `Qwen/Qwen2.5-0.5B-Instruct` FinTech PCI-DSS) + in-place Pallas kernel patching of 73 Hugging Face submodules.
  - `demos/setup/`: `uv`-based Python 3.12 setup scripts (`install_torchtpu.sh`, `install_sglang.sh`, `install_vllm.sh`).
  - `notebooks/`: Single-chip Colab TPU notebooks (`00`–`06`) including SpecGuard TPU (`04`), AutoKernel Lab (`05`), and the Master End-to-End Showcase (`06`).
- **`TorchTPU-FullStack-Showcase-Workshop/`**: Generated presentation deck suite (`generate_slides.py`, `TorchTPU_FullStack_Showcase_Workshop.pptx`, `index.html`, `speaker-notes.html`, `SPEAKER_NOTES_AND_SCRIPT.md`, and `present.sh`). Never edit the generated `.pptx`, `.html`, or `.md` files by hand — edit `SLIDES_DATA` in `generate_slides.py` and re-run it.
- **`workshops-main/`**: Hands-on Colab TPU v5e training notebooks using `torch_tpu` (`torch.device("tpu")`):
  - `Training_01_cnn_training_torchtpu_v5e.ipynb`: CNN training on TPU v5e (note: `workshops-main/README.md` mentions Torch-XLA in prose, but the notebook uses `torch.device("tpu")`).
  - `Training_02_lora_training_gemma_v5e.ipynb`: Gemma LoRA fine-tuning with PEFT on TPU v5e.
  - `Training_03_torchtitan_training_tpu.ipynb`: TorchTitan distributed training on TPU.

## Key Rules & Conventions

1. **Native `torch_tpu` Only**: `torch_xla` / `pytorch_xla` is **deprecated** and must never be imported, installed, or generated. Always use `import torch, torch_tpu` and `torch.device("tpu")`.
2. **TPU Agent Suite Development (`tpu-agent-suite/`)**:
   - Build all harness distributions: `make -C tpu-agent-suite build`
   - Verify schemas, delegation graph, and KB: `make -C tpu-agent-suite verify`
   - Run unit & parity tests: `make -C tpu-agent-suite test`
   - Upgrade workspace installation after rebuild:
     `python3 tpu-agent-suite/framework/installer.py install tpu-agent-suite/dist/claude-code/tpu-agent-suite --destination . --upgrade --non-interactive`
3. **Inference Workshop Conventions (`torchtpu-inference-workshop-main/`)**:
   - Respect line-width limits for live-demo files (`example*.py` and `profiler.py` <= 52 cols; `ask.py`, `burst.py`, `serve.sh` < 64 cols; `demos/04_kernel/*.py` <= 72 cols).
   - Validate notebooks after editing: `uv run --with nbformat python -c "import nbformat, sys; [nbformat.validate(nbformat.read(p, 4)) for p in sys.argv[1:]]" torchtpu-inference-workshop-main/notebooks/*.ipynb`.

<!-- tpu-agent-suite:tpu-agent-suite:tpu-knowledge-base:begin -->
This applies only inside the `tpu-agent` or `tpu-agent-export-trajectory` skills or their agents, or on a task those skills cover, even before you load one. For anything else, ignore this and just do the task.

For a public fact about TPU hardware, runtimes or software -- a spec, a
default, a supported version, what a doc says -- do NOT answer from memory.
Route the question to the `tpu-knowledge-base` agent, general and multi-part
questions included, as the user asked it rather than broken into
sub-questions of your own. It splits the question itself, resolves each fact
against the source index installed at `~/.tpu-agent-suite/packages/tpu-agent-suite@0.7.0/data/tpu-knowledge-base/index`, and
returns the entry plus the public URL it came from. Send it a JSON object,
`{"query": "<the question>"}`; a plain-text request is rejected before the
agent starts. Add `entry_id` only with an id or keyword provenance returned
to you; a guessed one sends it to the nearest match, which may be a page it
has to build.
If it returns suggested keywords instead of sources, nothing was looked up:
those are not an answer.
Footnote every such claim with the URL it returns. If provenance reports that a
source does not state something, say so explicitly rather than filling the gap
yourself. Provenance reads only the sources its index names; it does not search
the web.
The playbooks and the Pallas kernel pages are pages at
`~/.tpu-agent-suite/packages/tpu-agent-suite@0.7.0/data/tpu-knowledge-base/pages/`; `kernel-optimization-index.md` there
routes the kernel pages. Cite the pages each claim relies on; if none covers a
topic, say so explicitly. The installed pages are read-only: never edit them.
<!-- tpu-agent-suite:tpu-agent-suite:tpu-knowledge-base:end -->

<!-- tpu-agent-suite:tpu-agent-suite:compute:begin -->
This applies only inside the `tpu-agent` or `tpu-agent-export-trajectory` skills or their agents, or on a task those skills cover, even before you load one. For anything else, ignore this and just do the task.

For compute, those tasks are onboarding, optimizing, profiling or benchmarking a
model on Cloud TPUs, not kubectl, manifests or other clusters the user names.
Don't run `python3 ~/.tpu-agent-suite/packages/tpu-agent-suite@0.7.0/framework/runtime.py compute --package tpu-agent-suite@0.7.0` to check whether this applies.

For that work, every job, server, log and port-forward goes through
`python3 ~/.tpu-agent-suite/packages/tpu-agent-suite@0.7.0/framework/runtime.py compute --package tpu-agent-suite@0.7.0`. Don't write Kubernetes manifests or run `kubectl`,
`xpk`, `gcloud compute` or `ssh` against that cluster yourself: it is shared,
and compute is what keeps this run to its own jobs. Its section in each agent's
instructions, and `compute --help`, say how. A job name or image a task asks
for still goes through compute: give the name as `--name` (on `gke_job` the
compute profile's `job_name_prefix` goes in front and a taken name gets a short
suffix, so the name stays whole inside the job's; a task that requires names to
start a certain way can pass `--job-name-prefix` for that call), and pass
`--image <ref>` to `run` or `submit` to use an image other than the profile's.
If a rule still can't be met through compute, say so in your report rather
than reaching the cluster another way.
<!-- tpu-agent-suite:tpu-agent-suite:compute:end -->
