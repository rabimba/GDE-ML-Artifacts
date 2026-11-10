# The model of example1_eager.py under the standard
# PyTorch profiler with ProfilerActivity.TPU (docs:
# "Performance profiling with XProf").
#   python profiler.py eager | defer | compiled
# (not profile.py: that shadows a stdlib module)
import os, sys, time

mode = sys.argv[1]
if mode == "defer":  # the optimized eager mode
    os.environ["TORCH_TPU_DEFER_AND_FUSE"] = "1"

import torch
from torch import nn
from torch.profiler import ProfilerActivity, profile
from torch.profiler import tensorboard_trace_handler
from torch.tpu.profiler import TpuProfilerConfig

device = "tpu"
trace_dir = f"traces/{mode}"
model = nn.Sequential(*[
    nn.Sequential(nn.LayerNorm(1024),
                  nn.Linear(1024, 4096), nn.GELU(),
                  nn.Linear(4096, 1024))
    for _ in range(12)
]).to(device)
x = torch.randn(16, 512, 1024, device=device)
if mode == "compiled":
    model = torch.compile(model, backend="tpu")

with torch.no_grad():
    for i in range(20):  # warm-up, not traced
        y = model(x)
        torch.accelerator.synchronize()
    with profile(
        activities=[ProfilerActivity.CPU,
                    ProfilerActivity.TPU],
        experimental_config=TpuProfilerConfig(
            run_dir=trace_dir),
        on_trace_ready=tensorboard_trace_handler(
            trace_dir),
    ) as prof:
        for i in range(1, 6):  # five traced steps
            t0 = time.perf_counter()
            y = model(x)
            torch.accelerator.synchronize()
            ms = (time.perf_counter() - t0) * 1000
            print(f"{mode} step {i}: {ms:.1f} ms")
            prof.step()
print("trace:", trace_dir)
