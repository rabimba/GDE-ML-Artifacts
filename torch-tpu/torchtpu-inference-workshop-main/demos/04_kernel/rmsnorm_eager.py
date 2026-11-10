# RMSNorm in plain PyTorch ops on the TPU, timed, then traced.
import os
import time

import torch
from torch.tpu.profiler import TpuProfilerConfig

eps = 1e-6
trace_dir = os.environ.get("TRACES", "traces") + "/rmsnorm_eager"


def rmsnorm(x, w):
    ms = (x * x).mean(-1, keepdim=True)
    return x * torch.rsqrt(ms + eps) * w


x = torch.randn(16, 512, 1024, device="tpu")
w = torch.ones(1024, device="tpu")

with torch.no_grad():
    for i in range(1, 201):
        t0 = time.perf_counter()
        y = rmsnorm(x, w)
        torch.accelerator.synchronize()  # wait
        ms = (time.perf_counter() - t0) * 1000
        if i == 1 or i % 50 == 0:
            print(f"eager step {i}: {ms:.2f} ms")

    # a few steps under the profiler, for the trace viewer
    P = torch.profiler
    config = TpuProfilerConfig(host_tracer_level=2,
                               device_tracer_level=1, run_dir=trace_dir)
    with P.profile(
        activities=[P.ProfilerActivity.CPU, P.ProfilerActivity.TPU],
        experimental_config=config,
        on_trace_ready=P.tensorboard_trace_handler(trace_dir),
    ) as prof:
        for i in range(5):
            y = rmsnorm(x, w)
            torch.accelerator.synchronize()
            prof.step()

print(y.device, tuple(y.shape))
print(f"trace: {trace_dir}")
