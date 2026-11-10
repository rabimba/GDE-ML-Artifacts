import time

import torch
from torch import nn

device = "tpu"

model = nn.Sequential(*[
    nn.Sequential(nn.LayerNorm(1024),
                  nn.Linear(1024, 4096), nn.GELU(),
                  nn.Linear(4096, 1024))
    for _ in range(12)
]).to(device)
x = torch.randn(16, 512, 1024, device=device)

with torch.no_grad():
    for i in range(1, 1001):
        t0 = time.perf_counter()
        y = model(x)
        torch.accelerator.synchronize()  # wait
        ms = (time.perf_counter() - t0) * 1000
        if i % 100 == 0:
            print(f"eager step {i}: {ms:.1f} ms")

print(y.device, tuple(y.shape))
