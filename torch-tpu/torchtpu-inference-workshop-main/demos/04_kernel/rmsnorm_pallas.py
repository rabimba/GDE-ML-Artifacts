# The same RMSNorm as a Pallas kernel, called from PyTorch.
import os
import time

import jax
import jax.numpy as jnp
from jax.experimental import pallas as pl
import torch
from torch.tpu.profiler import TpuProfilerConfig

eps = 1e-6
tile = 512  # rows per grid step
trace_dir = os.environ.get("TRACES", "traces") + "/rmsnorm_pallas"


def rmsnorm_kernel(x_ref, w_ref, o_ref):  # one tile of rows
    x = x_ref[...]
    ms = jnp.mean(x * x, axis=-1, keepdims=True)
    o_ref[...] = x * jax.lax.rsqrt(ms + eps) * w_ref[...]


def rmsnorm_jax(x: jax.Array, w: jax.Array) -> jax.Array:
    rows = x.reshape(-1, x.shape[-1])
    n, d = rows.shape
    out = pl.pallas_call(
        rmsnorm_kernel,
        grid=(n // tile,),
        in_specs=[pl.BlockSpec((tile, d), lambda i: (i, 0)),
                  pl.BlockSpec((1, d), lambda i: (0, 0))],
        out_specs=pl.BlockSpec((tile, d), lambda i: (i, 0)),
        out_shape=jax.ShapeDtypeStruct(rows.shape, rows.dtype),
    )(rows, w.reshape(1, d))
    return out.reshape(x.shape)


rmsnorm = torch.tpu.pallas.jax_op("pallas::rmsnorm", rmsnorm_jax)

x = torch.randn(16, 512, 1024, device="tpu")
w = torch.ones(1024, device="tpu")

with torch.no_grad():
    for i in range(1, 201):
        t0 = time.perf_counter()
        y = rmsnorm(x, w)
        torch.accelerator.synchronize()  # wait
        ms = (time.perf_counter() - t0) * 1000
        if i == 1 or i % 50 == 0:
            print(f"pallas step {i}: {ms:.2f} ms")

    ref = x * torch.rsqrt((x * x).mean(-1, keepdim=True) + eps) * w
    print(f"max abs diff vs eager: {(y - ref).abs().max().item():.1e}")

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

print(f"trace: {trace_dir}")
