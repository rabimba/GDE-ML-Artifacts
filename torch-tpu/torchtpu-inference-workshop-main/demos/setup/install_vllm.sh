#!/usr/bin/env bash
# vLLM on TPU, for demo 03: the vllm-torchtpu README's install line (one package that
# brings a matching vLLM), plus the client libraries burst.py uses. Keep it in a venv of
# its own: vLLM and SGLang pin different torch versions.
# Python 3.12: the engines' wheels are built for it and the TPU VM images ship 3.10, so the
# venv is made with uv (installed here if missing), as the notebooks do. uv is told to
# consider every index for every package, as pip does (the PyTorch CPU index carries an old
# `requests`, and by default uv would stop there and resolve nothing newer).
set -euo pipefail
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
VENV=${VENV:-$HOME/venv-vllm}
uv venv -q --python 3.12 "$VENV"
uv pip install -q --python "$VENV/bin/python" --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  vllm-torchtpu openai rich tpu-info
"$VENV/bin/python" -c "import importlib.metadata as md, vllm, torch_tpu; print('vllm', vllm.__version__, '| vllm-torchtpu', md.version('vllm-torchtpu'))"
echo "activate with: source $VENV/bin/activate"
