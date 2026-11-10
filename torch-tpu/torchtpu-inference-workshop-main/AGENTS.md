# AGENTS.md

Guidance for coding agents (and people) working in this repository: the materials of the
workshop *Inference with TorchTPU* (TorchTPU DevLabs, Nov 9, 2026). Read `README.md` first;
this file adds what is not obvious from the files themselves.

## What is here, and what it needs

- `demos/01_one_chip/`: demo 1, one MLP. `example0_cpu.py` (CPU), `example1_eager.py` (the
  TPU, eager; run it again with `TORCH_TPU_DEFER_AND_FUSE=1` for the optimized eager mode),
  `example2_compile.py` (`torch.compile(backend="tpu")`). `profiler.py eager|defer|compiled` is
  the same model under the standard `torch.profiler` (with `ProfilerActivity.TPU`), writing
  `traces/<mode>/` for TensorBoard's trace viewer. One chip.
- `demos/02_sglang/`: demo 2. `serve.sh` starts SGLang with `--device tpu --tp-size 4`
  serving `Qwen/Qwen3-32B` on four chips; `ask.py` asks about one long prompt twice (the
  prefix cache). `ask.py` reads `transformer.py` from its own directory: PyTorch's
  `torch/nn/modules/transformer.py`, copied there (the README has the line).
- `demos/03_vllm/`: demo 3. `serve.sh` starts `vllm serve` with `--tensor-parallel-size 4`,
  the same model; `burst.py N` sends N streamed requests at once and `grid.py` draws them.
- `demos/04_kernel/`: an extra, not in the session. RMSNorm in ops and as a Pallas kernel.
- `demos/setup/install_*.sh`: one environment each, from the projects' own READMEs.
- `notebooks/`: the three demos on one chip and `Qwen/Qwen3-0.6B`, for Colab's TPU runtime.
- `slides/`: the deck as a PDF, one page per slide in its final state. Generated from the
  deck's source (not in this repository); replaced whole when the deck changes.

Nothing here runs without a TPU: a Cloud TPU VM (one chip for demos 1 and 4, four for
demos 2 and 3) or Colab's TPU runtime for the notebooks. There is no mock or CPU fallback to
add; `example0_cpu.py` exists only to show the one-line difference.

## Environments

- Python 3.12, made with `uv` (`demos/setup/install_*.sh`). The engines' wheels are built
  for 3.12 and the TPU VM image's `python3` is older; on Colab the kernel is 3.13, so the
  serving notebooks make the server its own 3.12 venv next to the notebook and the kernel is
  only the client. Do not install `vllm-torchtpu` or the SGLang wheels into a 3.13
  interpreter: pip resolves to an empty placeholder and `import vllm` fails.
- `--extra-index-url https://download.pytorch.org/whl/cpu` is required (the CPU build of
  torch; TorchTPU brings the TPU support). With `uv`, also `--index-strategy
  unsafe-best-match`, or `uv` stops at the first index that has a package and resolves old
  versions.
- One venv per engine: vLLM and SGLang pin different torch versions. One engine per machine
  at a time: each holds all the chips. Stop one before starting the other.
- `vllm-torchtpu` is on PyPI; `sglang-torchtpu` is not: its install is the two wheels of a
  GitHub release (`TAG` in `install_sglang.sh`). Check the two projects' READMEs before
  changing an install line.
- `Qwen/Qwen3-32B` is about 64 GB in bfloat16: four chips, a long first download, minutes of
  compilation at start-up (`/health` answers when the server is ready). For experiments use
  the notebooks' 0.6B model on one chip.
- On TPU, SGLang's `--enable-torch-compile` is an opt-in; vLLM needs no TPU flag.
- Generated files are ignored by git (`.gitignore`): `venv-*/`, `traces/`, `*.log`,
  `__pycache__/`, the copied `transformer.py`. Keep it that way.

## Conventions

- The demo files are opened in vim on a narrow terminal pane during the session, next to a
  monitor. Keep `demos/01_one_chip/example*.py` at most 52 columns wide, `demos/04_kernel/*.py`
  at most 72, `ask.py`, `burst.py` and the two `serve.sh` under 64 (`profiler.py` is shown
  too: 52); `grid.py` is not shown and may use 88. Check with
  `awk '{ if (length > m) m = length } END { print m }' <file>`.
- Every number the scripts print is that run's own. Do not write timings, throughput or
  memory figures into the README, the notebooks' markdown or comments.
- Refer to machines by type (`v6e-1`, `v6e-4`), never by a host name, project or zone.
- The two engines get the same treatment: parallel demos, parallel notebooks, the same
  requests. Do not add text that ranks one against the other, and keep each engine's wording
  to what its own documentation says.
- Scope: serving on Cloud TPUs with PyTorch. Other hardware is out of scope here.
- The three parts of the session are named in `README.md`; the notebooks' first cells and
  `notebooks/README.md` repeat them. Change them together.

## Notebooks

- Hand-maintained JSON, one-space indent, cell ids `NN-ii`; committed clean (no outputs,
  `execution_count: null`). Edit as text or with `json` (`indent=1`, `ensure_ascii=False`),
  then validate:
  `uv run --with nbformat python -c "import nbformat, sys; [nbformat.validate(nbformat.read(p, 4)) for p in sys.argv[1:]]" notebooks/*.ipynb`
- Keep the metadata that selects Colab's TPU runtime (`"accelerator": "TPU"` and
  `"colab": {"gpuType": "V5E1"}`) and the Open in Colab badge at the top of the first cell;
  its URL is `https://colab.research.google.com/github/RobMulla/torchtpu-inference-workshop/blob/main/notebooks/<file>`.
- `02` and `03` end with a stop cell; run it before starting the other engine (one chip).
  `03` sets `TPU_ACCELERATOR_TYPE` from `tpu-info` when the environment lacks it.

## Checks before a commit

- `bash -n demos/*/serve.sh demos/setup/*.sh`
- the width check above on the files the session shows
- the nbformat validation above
- the README's relative links resolve and the badges' file names match `notebooks/`
