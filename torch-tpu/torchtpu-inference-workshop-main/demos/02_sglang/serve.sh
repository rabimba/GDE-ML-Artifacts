# How the SGLang server is started, before the
# session: one model split across all four chips.
# The environment is the repository's own
# (benchmark/tpu/common_env.sh); SGLANG_PLATFORM
# picks the TPU plugin.
export SGLANG_PLATFORM=tpu
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
export TORCH_TPU_INTERNAL_MATERIALIZE_COLLECTIVE_TENSORS=false

exec python -m sglang.launch_server \
  --model-path Qwen/Qwen3-32B \
  --device tpu \
  --tp-size 4 \
  --host 127.0.0.1 --port 30000 \
  --context-length 16384 --max-running-requests 8 \
  --page-size 128 --mem-fraction-static 0.85 \
  --enable-torch-compile \
  --enable-cache-report
