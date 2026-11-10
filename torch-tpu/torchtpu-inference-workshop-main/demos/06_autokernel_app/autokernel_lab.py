# AutoKernel Lab: XProf-guided Pallas kernel fusion for a Qwen3/Llama Decoder Block
# Usage:
#   python autokernel_lab.py eager | defer | compiled | pallas | all
import json
import os
import subprocess
import sys
import time
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("TPU_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TPU_STDERR_LOG_LEVEL", "2")
os.environ.setdefault("TORCH_CPP_LOG_LEVEL", "ERROR")
os.environ.pop("TPU_VISIBLE_DEVICES", None)
for k, v in {
    "TPU_VISIBLE_CHIPS": "0",
    "TPU_SKIP_MDS_QUERY": "1",
    "TPU_CHIPS_PER_HOST_BOUNDS": "1,1,1",
    "TPU_HOST_BOUNDS": "1,1,1",
    "TPU_WORKER_ID": "0",
    "TPU_WORKER_HOSTNAMES": "localhost",
}.items():
    os.environ[k] = v


def run_all():
    modes = ["eager", "defer", "compiled", "pallas"]
    results = {}
    for m in modes:
        print(f"\n=== Running mode: {m} ===")
        proc = subprocess.run(
            [sys.executable, __file__, m],
            capture_output=False,
            text=True,
            check=True,
        )
    if os.path.exists("analyze_traces.py"):
        subprocess.run([sys.executable, "analyze_traces.py"], check=True)
    elif os.path.exists(os.path.join(os.path.dirname(__file__), "analyze_traces.py")):
        subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "analyze_traces.py")],
            check=True,
        )


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "all":
        run_all()
        return

    if mode in ("defer", "pallas"):
        os.environ["TORCH_TPU_DEFER_AND_FUSE"] = "1"

    import torch
    from torch import nn
    import torch.nn.functional as F
    from torch_tpu import _loader

    if not _loader._LOADED:
        _loader._init_device("tpu")

    from torch.profiler import ProfilerActivity, profile, tensorboard_trace_handler
    from torch.tpu.profiler import TpuProfilerConfig

    device = "tpu"
    eps = 1e-6
    B, S, D, I = 16, 512, 1024, 4096
    tile = 512

    torch.manual_seed(42)

    # Eager PyTorch reference primitives
    def eager_res_rmsnorm(x, res, w):
        h = x + res
        ms = (h * h).mean(-1, keepdim=True)
        return h * torch.rsqrt(ms + eps) * w

    def eager_swiglu(gate, up):
        return F.silu(gate) * up

    # Optional Pallas fused kernels registered as native PyTorch ops
    if mode == "pallas":
        import jax
        import jax.numpy as jnp
        from jax.experimental import pallas as pl

        def res_rmsnorm_kernel(x_ref, r_ref, w_ref, o_ref):
            h = x_ref[...] + r_ref[...]
            ms = jnp.mean(h * h, axis=-1, keepdims=True)
            o_ref[...] = h * jax.lax.rsqrt(ms + eps) * w_ref[...]

        def res_rmsnorm_jax(x: jax.Array, r: jax.Array, w: jax.Array) -> jax.Array:
            rows_x = x.reshape(-1, x.shape[-1])
            rows_r = r.reshape(-1, r.shape[-1])
            n, d = rows_x.shape
            out = pl.pallas_call(
                res_rmsnorm_kernel,
                grid=(n // tile,),
                in_specs=[
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((tile, d), lambda i: (i, 0)),
                    pl.BlockSpec((1, d), lambda i: (0, 0)),
                ],
                out_specs=pl.BlockSpec((tile, d), lambda i: (i, 0)),
                out_shape=jax.ShapeDtypeStruct(rows_x.shape, rows_x.dtype),
            )(rows_x, rows_r, w.reshape(1, d))
            return out.reshape(x.shape)

        def swiglu_kernel(g_ref, u_ref, o_ref):
            g = g_ref[...]
            sig = jax.lax.logistic(g)
            o_ref[...] = (g * sig) * u_ref[...]

        def swiglu_jax(gate: jax.Array, up: jax.Array) -> jax.Array:
            rows_g = gate.reshape(-1, gate.shape[-1])
            rows_u = up.reshape(-1, up.shape[-1])
            n, d = rows_g.shape
            tile_s = 128  # tiled along sequence axis for scoped VMEM
            out = pl.pallas_call(
                swiglu_kernel,
                grid=(n // tile_s,),
                in_specs=[
                    pl.BlockSpec((tile_s, d), lambda i: (i, 0)),
                    pl.BlockSpec((tile_s, d), lambda i: (i, 0)),
                ],
                out_specs=pl.BlockSpec((tile_s, d), lambda i: (i, 0)),
                out_shape=jax.ShapeDtypeStruct(rows_g.shape, rows_g.dtype),
            )(rows_g, rows_u)
            return out.reshape(gate.shape)

        pallas_res_rmsnorm = torch.tpu.pallas.jax_op(
            "pallas::fused_res_rmsnorm", res_rmsnorm_jax
        )
        pallas_swiglu = torch.tpu.pallas.jax_op(
            "pallas::fused_swiglu", swiglu_jax
        )

    class DecoderSwiGLUBlock(nn.Module):
        def __init__(self, d_model: int, d_inter: int, use_pallas: bool = False):
            super().__init__()
            self.norm_w = nn.Parameter(torch.ones(d_model))
            self.gate_proj = nn.Linear(d_model, d_inter, bias=False)
            self.up_proj = nn.Linear(d_model, d_inter, bias=False)
            self.down_proj = nn.Linear(d_inter, d_model, bias=False)
            self.use_pallas = use_pallas

        def forward(self, x, residual):
            if self.use_pallas:
                h_norm = pallas_res_rmsnorm(x, residual, self.norm_w)
                gate = self.gate_proj(h_norm)
                up = self.up_proj(h_norm)
                act = pallas_swiglu(gate, up)
                return self.down_proj(act)
            else:
                h_norm = eager_res_rmsnorm(x, residual, self.norm_w)
                gate = self.gate_proj(h_norm)
                up = self.up_proj(h_norm)
                act = eager_swiglu(gate, up)
                return self.down_proj(act)

    # Build a 4-layer stack of Qwen3/Llama-style Decoder MLP blocks
    n_layers = 4
    blocks = nn.ModuleList(
        [DecoderSwiGLUBlock(D, I, use_pallas=(mode == "pallas")) for _ in range(n_layers)]
    ).to(device)

    x = torch.randn(B, S, D, device=device)
    res = torch.randn(B, S, D, device=device)

    def forward_stack(inp, r):
        cur = inp
        for blk in blocks:
            cur = blk(cur, r)
        return cur

    # Numerical parity gate for Pallas mode vs Eager PyTorch reference
    parity_info = {}
    if mode == "pallas":
        with torch.no_grad():
            ref_norm = eager_res_rmsnorm(x, res, blocks[0].norm_w)
            pal_norm = pallas_res_rmsnorm(x, res, blocks[0].norm_w)
            norm_diff = (pal_norm - ref_norm).abs().max().item()

            g_test = blocks[0].gate_proj(ref_norm)
            u_test = blocks[0].up_proj(ref_norm)
            ref_act = eager_swiglu(g_test, u_test)
            pal_act = pallas_swiglu(g_test, u_test)
            swiglu_diff = (pal_act - ref_act).abs().max().item()

            # Compare full 4-layer stack
            for blk in blocks:
                blk.use_pallas = False
            ref_out = forward_stack(x, res)
            for blk in blocks:
                blk.use_pallas = True
            pal_out = forward_stack(x, res)
            stack_diff = (pal_out - ref_out).abs().max().item()

            parity_info = {
                "fused_res_rmsnorm_max_diff": norm_diff,
                "fused_swiglu_max_diff": swiglu_diff,
                "full_stack_max_diff": stack_diff,
                "parity_passed": bool(norm_diff < 1e-4 and swiglu_diff < 1e-4),
            }
            print(
                f"[Parity Gate] res_rmsnorm diff={norm_diff:.2e} | "
                f"swiglu diff={swiglu_diff:.2e} | stack diff={stack_diff:.2e} | "
                f"PASS={parity_info['parity_passed']}"
            )

    runner = forward_stack
    if mode in ("compiled", "pallas"):
        runner = torch.compile(forward_stack, backend="tpu")

    # Warm-up & timed steps
    n_steps = 100
    step_times = []
    with torch.no_grad():
        for i in range(1, n_steps + 1):
            t0 = time.perf_counter()
            y = runner(x, res)
            torch.accelerator.synchronize()
            ms = (time.perf_counter() - t0) * 1000
            step_times.append(ms)
            if i == 1 or i % 25 == 0:
                print(f"{mode:10s} step {i:3d}: {ms:.2f} ms")

    steady_ms = sorted(step_times[20:])[len(step_times[20:]) // 2]
    print(f"{mode:10s} median steady-state step: {steady_ms:.2f} ms")

    # Profile 5 steps with XProf / TpuProfilerConfig
    trace_dir = os.path.abspath(f"traces/autokernel_{mode}")
    os.makedirs(trace_dir, exist_ok=True)
    with torch.no_grad(), profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.TPU],
        experimental_config=TpuProfilerConfig(
            host_tracer_level=2, device_tracer_level=1, run_dir=trace_dir
        ),
        schedule=torch.profiler.schedule(wait=0, warmup=0, active=5, repeat=1),
        on_trace_ready=tensorboard_trace_handler(trace_dir),
    ) as prof:
        for _ in range(5):
            y = runner(x, res)
            torch.accelerator.synchronize()
            prof.step()

    # Save mode metrics
    os.makedirs("traces", exist_ok=True)
    meta_path = f"traces/metrics_{mode}.json"
    with open(meta_path, "w") as f:
        json.dump(
            {
                "mode": mode,
                "first_step_ms": step_times[0],
                "median_steady_ms": steady_ms,
                "trace_dir": trace_dir,
                "parity": parity_info,
            },
            f,
            indent=2,
        )
    print(f"Saved metrics to {meta_path} and trace to {trace_dir}")


if __name__ == "__main__":
    main()
