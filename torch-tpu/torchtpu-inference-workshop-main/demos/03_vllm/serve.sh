# How the vLLM server is started, before the
# session: one model split across all four chips.
# No TPU flag: vLLM finds the TorchTPU plugin.
# spawn for the workers, and two TorchTPU
# workarounds from the plugin's README.
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export TORCH_TPU_INTERNAL_MATERIALIZE_COLLECTIVE_TENSORS=false
export TORCHINDUCTOR_AUTOGRAD_CACHE=0

exec vllm serve Qwen/Qwen3-32B \
  --tensor-parallel-size 4 \
  --host 127.0.0.1 --port 8000 \
  --max-model-len 4096 --max-num-seqs 128 \
  --max-num-batched-tokens 2048 \
  --async-scheduling
