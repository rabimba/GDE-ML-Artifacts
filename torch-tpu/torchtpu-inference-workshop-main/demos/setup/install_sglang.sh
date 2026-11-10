#!/usr/bin/env bash
# SGLang on TPU, for demo 02: the sglang-torchtpu README's install (the two release
# wheels), plus the OpenAI client ask.py uses. Its own venv, see install_vllm.sh. Check
# github.com/sgl-project/sglang-torchtpu/releases for a newer tag.
# Python 3.12: the engines' wheels are built for it and the TPU VM images ship 3.10, so the
# venv is made with uv (installed here if missing), as the notebooks do. uv is told to
# consider every index for every package, as pip does (the PyTorch CPU index carries an old
# `requests`, and by default uv would stop there and resolve nothing newer).
set -euo pipefail
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
TAG=${TAG:-tpu-v0.1.0}
REL="https://github.com/sgl-project/sglang-torchtpu/releases/download/$TAG"
VENV=${VENV:-$HOME/venv-sglang}
uv venv -q --python 3.12 "$VENV"
uv pip install -q --python "$VENV/bin/python" --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  "$REL/sglang-0.5.22-py3-none-any.whl" "$REL/sglang_tpu-0.1.0-py3-none-any.whl" openai tpu-info
"$VENV/bin/python" -c "import sglang, torch_tpu; print('sglang', sglang.__version__)"
echo "activate with: source $VENV/bin/activate"
