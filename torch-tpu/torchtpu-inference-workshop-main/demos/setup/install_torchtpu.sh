#!/usr/bin/env bash
# TorchTPU on one chip, for demos 01 and 04: torch + torch_tpu (the TorchTPU README's
# install line), jax (demo 04's Pallas kernel is lowered through JAX on the host; no
# jax[tpu] needed), tpu-info, and TensorBoard with the XProf plugin for the traces. Run on
# a Cloud TPU VM (tested on a v6e-1).
# Python 3.12: the engines' wheels are built for it and the TPU VM images ship 3.10, so the
# venv is made with uv (installed here if missing), as the notebooks do. uv is told to
# consider every index for every package, as pip does (the PyTorch CPU index carries an old
# `requests`, and by default uv would stop there and resolve nothing newer).
set -euo pipefail
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
VENV=${VENV:-$HOME/venv-torchtpu}
uv venv -q --python 3.12 "$VENV"
uv pip install -q --python "$VENV/bin/python" --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  torch_tpu jax tpu-info "setuptools<81" tensorboard tensorboard-plugin-profile xprof
"$VENV/bin/python" - <<'PY'
import importlib.metadata as md
import torch, torch_tpu  # noqa: F401
print("torch", torch.__version__, "| torch_tpu", md.version("torch_tpu"), "| jax", md.version("jax"))
PY
echo "activate with: source $VENV/bin/activate"
