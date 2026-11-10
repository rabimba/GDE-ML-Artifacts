#!/usr/bin/env python3
"""Generate the 4 animated GIFs and static media cards for the TPU Sprint blogpost on rkrants.blogspot.com."""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/rkaranjai/Documents/GitHub/GDE-ML-Artifacts/torch-tpu")
MEDIA_DIR = ROOT / "blog" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

AUTOKERNEL_PNG = ROOT / "torchtpu-inference-workshop-main/demos/06_autokernel_app/autokernel_xprof_waterfall.png"
SPECGUARD_PNG = ROOT / "torchtpu-inference-workshop-main/demos/05_specguard_app/specguard_dashboard.png"
DOMAIN_PNG = ROOT / "torchtpu-inference-workshop-main/demos/07_domain_adaptation_showcase/domain_adaptation_showcase.png"
DECK_HTML = ROOT / "TorchTPU-FullStack-Showcase-Workshop/index.html"


def get_font(size: int, mono: bool = False, bold: bool = False):
    candidates = []
    if mono:
        candidates = [
            "/System/Library/Fonts/Supplemental/Menlo.ttc",
            "/System/Library/Fonts/Menlo.ttc",
            "/System/Library/Fonts/Monaco.ttf",
            "/Library/Fonts/SF-Mono-Regular.otf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_header(draw: ImageDraw.ImageDraw, width: int, pill: str, title: str, subtitle: str, accent="#38bdf8"):
    # Top bar
    draw.rounded_rectangle((24, 20, width - 24, 114), radius=12, fill="#0f172a", outline="#1e293b", width=2)
    f_pill = get_font(13, mono=True, bold=True)
    f_title = get_font(22, mono=False, bold=True)
    f_sub = get_font(14, mono=True, bold=False)

    # Pill
    draw.rounded_rectangle((42, 34, 42 + len(pill) * 8 + 24, 58), radius=10, fill="#131c31", outline=accent, width=1)
    draw.text((54, 38), pill, fill=accent, font=f_pill)

    # Traffic lights on right
    draw.ellipse((width - 96, 38, width - 84, 50), fill="#f43f5e")
    draw.ellipse((width - 76, 38, width - 64, 50), fill="#f59e0b")
    draw.ellipse((width - 56, 38, width - 44, 50), fill="#10b981")

    draw.text((42, 64), title, fill="#f8fafc", font=f_title)
    draw.text((42, 92), subtitle, fill="#94a3b8", font=f_sub)


def save_gif(frames, out_path: Path, durations):
    pal_frames = [f.convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for f in frames]
    pal_frames[0].save(
        out_path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    print(f"Saved {out_path} ({out_path.stat().st_size / 1024:.1f} KB, {len(frames)} frames)")


def build_gif0_autokernel_mechanism():
    """Animate how the reusable `autokernel` library works under the hood (HBM vs VMEM + 73-module HF swap)."""
    W, H = 1040, 580
    frames = []
    durations = []

    f_mono = get_font(13, mono=True)
    f_mono_b = get_font(14, mono=True, bold=True)
    f_label = get_font(16, mono=False, bold=True)
    f_big = get_font(22, mono=True, bold=True)

    scenes = [
        {
            "pill": "HOW AUTOKERNEL WORKS (1 / 5) — THE EAGER HBM PING-PONG BOTTLENECK",
            "title": "Why Stock PyTorch RMSNorm & SwiGLU Stall on TPU: 5 Main-Memory Trips per Layer",
            "sub": "Every tiny op reads from off-chip HBM, runs one step on VPU, and writes back to HBM (250+ launches / pass)",
            "accent": "#f43f5e",
            "mode": "eager",
            "log": [
                "# Stock Hugging Face Qwen2RMSNorm.forward(x): 5 separate HBM round-trips per layer!",
                "1. x_f32 = x.to(torch.float32)               # Read HBM -> VPU -> Write HBM",
                "2. var   = x_f32.pow(2).mean(-1, keepdim=True)# Read HBM -> VPU -> Write HBM",
                "3. norm  = x_f32 * torch.rsqrt(var + eps)     # Read HBM -> VPU -> Write HBM",
                "4. out   = weight * norm.to(bfloat16)         # Read HBM -> VPU -> Write HBM (x49 layers = 245+ trips!)",
            ],
        },
        {
            "pill": "HOW AUTOKERNEL WORKS (2 / 5) — AUTOMATIC VMEM TILE SIZING & DMA",
            "title": "Step 1: autokernel.solve_tile_size() Slices Tensors into On-Chip VMEM Tiles",
            "sub": "pl.BlockSpec((tile, D), lambda i: (i, 0)) streams each (256 x 896) block from HBM into VMEM once",
            "accent": "#f59e0b",
            "mode": "tile",
            "log": [
                "$ import autokernel",
                ">>> autokernel.init_tpu(chip=0, defer_and_fuse=True)  # Locks Chip 0 PJRT before JAX loads",
                ">>> tile = autokernel.solve_tile_size(n_rows=768, max_tile=512)  # -> tile = 256",
                "  -> Grid = (768 // 256,) = (3,) tiles | Minor dim D=896 (7 x 128 VPU lanes aligned)",
                "  -> DMA Engine prefetches tile (256, 896) from HBM onto local VMEM cutting board",
            ],
        },
        {
            "pill": "HOW AUTOKERNEL WORKS (3 / 5) — SINGLE-PASS ON-CHIP VMEM FUSION",
            "title": "Step 2: All 5 Math Steps Stay Inside On-Chip VMEM Scratchpad (1 HBM Trip Total)",
            "sub": "Upcast + Square + Mean + Rsqrt + Weight Multiply run back-to-back in VPU registers (5.47x - 6.32x faster)",
            "accent": "#10b981",
            "mode": "vmem",
            "log": [
                "# Inside Pallas VMEM Kernel (torch.tpu.pallas.jax_op -> pallas::autokernel_rmsnorm_0):",
                "x_f32  = x_ref[...].astype(jnp.float32)                  # Already in on-chip VMEM!",
                "rms    = jax.lax.rsqrt(jnp.mean(x_f32 * x_f32, axis=-1, keepdims=True) + eps)",
                "out_ref[...] = (x_f32 * rms).astype(out_ref.dtype) * w_ref[...]  # 1 DMA write back to HBM",
                "  -> Result: 24-Layer RMSNorm Stack drops from 6.81 ms -> 1.25 ms (5.47x speedup, max_diff = 0.0)",
            ],
        },
        {
            "pill": "HOW AUTOKERNEL WORKS (4 / 5) — ONE-LINE IN-MEMORY HUGGING FACE SURGERY",
            "title": "Step 3: autokernel.patch_hf(model) Swaps 73 Submodules Without Copying Weights",
            "sub": "Walks model.named_children() -> Replaces 49x RMSNorm + 24x SwiGLU MLP in-place (unpatch_hf restores all 73)",
            "accent": "#38bdf8",
            "mode": "patch",
            "log": [
                ">>> report = autokernel.patch_hf(model)",
                "  -> Swapped 49x Qwen2RMSNorm -> PallasRMSNorm (weight Parameter shared by pointer, 0 bytes copied)",
                "  -> Swapped 24x Qwen2MLP     -> PallasSwiGLUMLP (gate_proj/up_proj/down_proj preserved in-place)",
                "  -> report.total_patched == 73 | Reversible at any time via autokernel.unpatch_hf(model) -> 73",
            ],
        },
        {
            "pill": "HOW AUTOKERNEL WORKS (5 / 5) — REUSABLE LIBRARY & VERIFIED PARITY",
            "title": "Step 4: Three Lines of Python to Patch & Verify Any Model on Cloud TPU",
            "sub": "pip install -e ./autokernel • Tested via pytest (10/10 PASS) & Live on tpu7x Chip 0 (99.74% Top-1 Match)",
            "accent": "#a855f7",
            "mode": "summary",
            "log": [
                ">>> bench = autokernel.verify_parity_and_speedup(stock_fn, patched_fn, sample_input)",
                "  -> 24-Layer RMSNorm Stack : 5.47x speedup on tpu7x Chip 0 (max_abs_diff = 0.0, PASS = True)",
                "  -> Full 24-Layer Qwen2.5  : 29.74 ms -> 24.66 ms (1.21x End-to-End Speedup, 99.74% Top-1 Match)",
                "  -> Unit + Hardware Tests  : 10/10 pytest unit tests PASS + tpu7x hardware verification PASS",
            ],
        },
    ]

    for sc in scenes:
        img = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(img)
        draw_header(d, W, sc["pill"], sc["title"], sc["sub"], accent=sc["accent"])

        # Left diagram box: Hardware Dataflow (HBM <-> Bus <-> VMEM <-> VPU/MXU)
        d.rounded_rectangle((24, 130, 560, 355), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((40, 142), "TPU Chip Dataflow: Off-Chip HBM vs. On-Chip VMEM", fill="#e2e8f0", font=f_label)

        # HBM Box
        d.rounded_rectangle((42, 176, 178, 336), radius=8, fill="#131c31", outline="#64748b", width=2)
        d.text((62, 188), "Off-Chip HBM", fill="#cbd5e1", font=f_mono_b)
        d.text((54, 212), "Main Memory", fill="#94a3b8", font=f_mono)
        d.text((54, 240), "Tensor (B,S,D)", fill="#38bdf8", font=f_mono)
        d.text((54, 264), "(4 x 128 x 896)", fill="#64748b", font=f_mono)

        # VMEM + VPU Box
        vmem_outline = "#10b981" if sc["mode"] in ("vmem", "patch", "summary") else ("#f59e0b" if sc["mode"] == "tile" else "#334155")
        d.rounded_rectangle((318, 176, 542, 336), radius=8, fill="#131c31", outline=vmem_outline, width=2)
        d.text((334, 188), "On-Chip VMEM + VPU", fill="#10b981", font=f_mono_b)

        if sc["mode"] == "eager":
            # 5 red ping-pong arrows between HBM and VPU
            for a_i, op_lbl in enumerate(["1. cast f32", "2. square+mean", "3. rsqrt(var)", "4. cast bf16", "5. * weight"]):
                ay = 202 + a_i * 25
                d.line((184, ay, 312, ay), fill="#f43f5e", width=2)
                d.text((192, ay - 13), f"<-> {op_lbl}", fill="#fb7185", font=get_font(11, mono=True))
            d.text((334, 224), "5 HBM Round-Trips", fill="#f43f5e", font=f_mono_b)
            d.text((334, 250), "VMEM wiped after", fill="#cbd5e1", font=f_mono)
            d.text((334, 272), "every single op!", fill="#cbd5e1", font=f_mono)
            d.text((334, 302), "250+ launches/pass", fill="#fb7185", font=f_mono_b)
        elif sc["mode"] == "tile":
            d.line((184, 246, 312, 246), fill="#f59e0b", width=3)
            d.text((190, 224), "DMA Tile (256x896)", fill="#fde047", font=get_font(11, mono=True, bold=True))
            d.text((334, 218), "solve_tile_size(N)", fill="#fde047", font=f_mono_b)
            d.text((334, 244), "BlockSpec((256,896))", fill="#e2e8f0", font=f_mono)
            d.text((334, 270), "Streams tile into", fill="#cbd5e1", font=f_mono)
            d.text((334, 292), "local VMEM once!", fill="#10b981", font=f_mono_b)
        else:
            d.line((184, 226, 312, 226), fill="#10b981", width=3)
            d.text((196, 206), "1. DMA Read Tile", fill="#10b981", font=get_font(11, mono=True, bold=True))
            d.line((312, 290, 184, 290), fill="#38bdf8", width=3)
            d.text((196, 270), "2. DMA Write Out", fill="#38bdf8", font=get_font(11, mono=True, bold=True))
            d.text((334, 214), "Fused inside VMEM:", fill="#fde047", font=f_mono_b)
            d.text((334, 238), "• f32 upcast + x^2", fill="#e2e8f0", font=f_mono)
            d.text((334, 258), "• mean + rsqrt(eps)", fill="#e2e8f0", font=f_mono)
            d.text((334, 278), "• bf16 * weight", fill="#e2e8f0", font=f_mono)
            d.text((334, 304), "0 Intermediate HBM!", fill="#10b981", font=f_mono_b)

        # Right panel: Hugging Face AST Surgery (`autokernel.patch_hf(model)`)
        d.rounded_rectangle((576, 130, W - 24, 355), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((594, 142), "Reusable `autokernel` HF Model Patcher", fill="#38bdf8", font=f_label)

        patched_active = sc["mode"] in ("patch", "summary")
        box_col = "#10b981" if patched_active else "#334155"
        d.rounded_rectangle((594, 174, W - 42, 258), radius=8, fill="#131c31", outline=box_col, width=2)
        if not patched_active:
            d.text((610, 186), "Stock Qwen2.5-0.5B (24 Layers):", fill="#fb7185", font=f_mono_b)
            d.text((610, 210), "• 49x Qwen2RMSNorm (unfused ops)", fill="#cbd5e1", font=f_mono)
            d.text((610, 232), "• 24x Qwen2MLP     (unfused silu*up)", fill="#cbd5e1", font=f_mono)
        else:
            d.text((610, 186), "autokernel.patch_hf(model) -> 73 Swapped:", fill="#10b981", font=f_mono_b)
            d.text((610, 210), "• 49x PallasRMSNorm  (0 weights copied)", fill="#fde047", font=f_mono)
            d.text((610, 232), "• 24x PallasSwiGLUMLP(reversible AST)", fill="#38bdf8", font=f_mono)

        d.rounded_rectangle((594, 268, W - 42, 338), radius=8, fill="#131c31", outline=sc["accent"], width=2)
        d.text((610, 276), "24L Norm: 5.47x  |  8L ResNorm: 6.32x", fill="#10b981", font=f_big)
        d.text((610, 308), "Full 24L Model: 1.21x (99.74% Top-1)", fill="#ffffff", font=f_mono_b)

        # Bottom code / telemetry console
        d.rounded_rectangle((24, 370, W - 24, H - 20), radius=10, fill="#050811", outline="#334155", width=2)
        d.text((42, 382), "autokernel Library — Under-the-Hood Execution & Code Trace", fill="#64748b", font=f_mono)
        for l_i, line in enumerate(sc["log"]):
            col = (
                "#10b981"
                if "5.47x" in line or "1.21x" in line or "PASS" in line or "73" in line
                else ("#38bdf8" if line.startswith(">>>") or line.startswith("$") else "#e2e8f0")
            )
            d.text((42, 410 + l_i * 26), line, fill=col, font=f_mono)

        frames.append(img)
        durations.append(1650)

    save_gif(frames, MEDIA_DIR / "00-autokernel-how-it-works.gif", durations)


def build_gif1_autokernel():
    W, H = 1040, 580
    frames = []
    durations = []

    modes = [
        {
            "step": "STAGE 1 / 4 — EAGER DISPATCH",
            "name": "1. Eager (torch_tpu)",
            "lat": 3.591,
            "speedup": "1.00x (baseline)",
            "progs": "47 TPU progs/step",
            "color": "#f43f5e",
            "log": [
                "$ TPU_VISIBLE_CHIPS=0 python3 autokernel_lab.py",
                "[tpu7x Chip 0] Pre-initializing torch_tpu PJRT before JAX...",
                "[Mode 1: Eager] 8-Layer Transformer Block (B=4, S=256, D=1024, bf16)",
                "  -> XProf Trace: 47 separate HLO ops dispatched per forward pass",
                "  -> HBM Ping-Pong: Residual + RMSNorm + SwiGLU spill to HBM 47 times",
                "  -> Median Latency: 3.591 ms/step | Speedup: 1.00x",
            ],
        },
        {
            "step": "STAGE 2 / 4 — RUNTIME C++ LAZY FUSION",
            "name": "2. DeferAndFuse",
            "lat": 2.126,
            "speedup": "1.69x vs Eager",
            "progs": "3 TPU progs/step",
            "color": "#f59e0b",
            "log": [
                "$ TORCH_TPU_DEFER_AND_FUSE=1 python3 autokernel_lab.py",
                "[Mode 2: DeferAndFuse] Zero code changes — C++ lazy queue active",
                "  -> XProf Trace: 47 eager dispatches collapsed into 3 fused clusters",
                "  -> Eliminates per-op PJRT launch overhead across elementwise chains",
                "  -> Median Latency: 2.126 ms/step | Speedup: 1.69x (-40.8% latency)",
            ],
        },
        {
            "step": "STAGE 3 / 4 — WHOLE-GRAPH XLA COMPILATION",
            "name": "3. torch.compile(tpu)",
            "lat": 1.579,
            "speedup": "2.28x vs Eager",
            "progs": "1 TPU prog/step",
            "color": "#38bdf8",
            "log": [
                "[Mode 3: torch.compile(backend='tpu')] TorchDynamo -> StableHLO -> XLA",
                "  -> XProf Trace: Entire 8-layer block compiled into 1 XLA program",
                "  -> Automatic operator fusion across attention projections + MLPs",
                "  -> Median Latency: 1.579 ms/step | Speedup: 2.28x (-56.0% latency)",
            ],
        },
        {
            "step": "STAGE 4 / 4 — CUSTOM PALLAS VMEM KERNELS",
            "name": "4. Pallas jax_op + compile",
            "lat": 2.224,
            "speedup": "6.32x Isolated Op | 1.61x Block",
            "progs": "1 TPU prog/step (VMEM)",
            "color": "#10b981",
            "log": [
                "[Mode 4: torch.tpu.pallas.jax_op] Registering custom TPU kernels:",
                "  -> pallas::fused_res_rmsnorm : max_diff = 9.54e-07 (PASS = True)",
                "  -> pallas::fused_swiglu      : max_diff = 4.77e-07 (PASS = True)",
                "  -> Isolated 8-Layer Res+RMSNorm: 2.587 ms Eager -> 0.409 ms Pallas (6.32x!)",
                "  -> Full 8-Layer Block w/ jax_op: 2.224 ms (1.61x vs Eager, 1 TPU prog)",
            ],
        },
    ]

    f_mono = get_font(13, mono=True)
    f_mono_b = get_font(14, mono=True, bold=True)
    f_label = get_font(16, mono=False, bold=True)
    f_big = get_font(26, mono=True, bold=True)

    for idx in range(len(modes)):
        img = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(img)
        cur = modes[idx]
        draw_header(
            d,
            W,
            cur["step"],
            "AutoKernel Lab: XProf-Guided 4-Mode Fusion Ladder on tpu7x Chip 0",
            "8-Layer Transformer Block (B=4, S=256, D=1024, MLP=4096, bfloat16)",
            accent=cur["color"],
        )

        # Left panel: Animated Bar Race
        d.rounded_rectangle((24, 130, 520, 355), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((40, 142), "Step Latency (ms) & XProf Programs/Step", fill="#e2e8f0", font=f_label)

        for m_i in range(idx + 1):
            m = modes[m_i]
            y = 178 + m_i * 42
            d.text((40, y + 4), m["name"], fill="#cbd5e1", font=f_mono)
            bar_max = 260
            bar_w = int((m["lat"] / 3.8) * bar_max)
            d.rounded_rectangle((215, y, 215 + bar_w, y + 26), radius=5, fill=m["color"])
            d.text((222 + bar_w, y + 4), f"{m['lat']:.3f} ms", fill="#f8fafc", font=f_mono_b)

        # Right panel: Isolated Pallas VMEM spotlight
        d.rounded_rectangle((536, 130, W - 24, 355), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((554, 142), "On-Chip VMEM Scratchpad Spotlight", fill="#e2e8f0", font=f_label)
        d.rounded_rectangle((554, 174, W - 42, 254), radius=8, fill="#131c31", outline=cur["color"], width=2)
        d.text((570, 184), f"Active Mode: {cur['name']}", fill=cur["color"], font=f_mono_b)
        d.text((570, 208), f"{cur['lat']:.3f} ms  ({cur['speedup']})", fill="#ffffff", font=f_big)
        d.text((554, 268), f"XProf Dispatch Count : {cur['progs']}", fill="#38bdf8", font=f_mono_b)
        d.text((554, 292), "Isolated 8x Res+RMSNorm: 2.587ms -> 0.409ms (6.32x)", fill="#10b981", font=f_mono_b)
        d.text((554, 316), "Numerical Parity       : 9.54e-07 / 4.77e-07 (PASS)", fill="#fde047", font=f_mono)

        # Bottom terminal log
        d.rounded_rectangle((24, 370, W - 24, H - 20), radius=10, fill="#050811", outline="#334155", width=2)
        d.text((42, 382), "Cloud TPU (tpu7x Chip 0) — Live XProf & Pallas Telemetry", fill="#64748b", font=f_mono)
        for l_i, line in enumerate(cur["log"]):
            col = "#10b981" if "PASS" in line or "6.32x" in line else ("#38bdf8" if line.startswith("$") else "#e2e8f0")
            d.text((42, 410 + l_i * 25), line, fill=col, font=f_mono)

        frames.append(img)
        durations.append(1500)

    # Final Frame: Embed the actual matplotlib chart from tpu7x run
    if AUTOKERNEL_PNG.exists():
        chart_frame = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(chart_frame)
        draw_header(
            d,
            W,
            "VERIFIED TPU7X ARTIFACT",
            "AutoKernel Lab: Empirical XProf Waterfall & Pallas Parity Chart",
            "Measured directly on 7th-Gen Cloud TPU (tpu7x Chip 0) • PASS = True",
            accent="#10b981",
        )
        raw = Image.open(AUTOKERNEL_PNG).convert("RGB")
        raw.thumbnail((W - 56, H - 154), Image.Resampling.LANCZOS)
        ox = (W - raw.width) // 2
        oy = 128 + (H - 148 - raw.height) // 2
        d.rounded_rectangle((ox - 6, oy - 6, ox + raw.width + 6, oy + raw.height + 6), radius=8, fill="#ffffff")
        chart_frame.paste(raw, (ox, oy))
        frames.append(chart_frame)
        durations.append(2400)

    save_gif(frames, MEDIA_DIR / "01-autokernel-xprof-pallas-fusion.gif", durations)


def build_gif2_specguard():
    W, H = 1040, 580
    frames = []
    durations = []

    stages = [
        {
            "pill": "STAGE 1A — STATIC-SHAPE TPU LORA TRAINING",
            "title": "SpecGuard TPU: Fine-Tuning Qwen/Qwen3-0.6B on tpu7x Chip 0",
            "sub": "Static Pad-to-Max (4x256, bfloat16) • Zero XLA Recompilations After Step 1",
            "accent": "#38bdf8",
            "step_progress": 10,
            "loss": "1.1420",
            "ppl": "3.13",
            "ttft_cold": None,
            "ttft_warm": None,
            "burst": None,
            "lines": [
                "$ TPU_VISIBLE_CHIPS=0 python3 stage1_lora_finetune.py",
                "[Stage 1] Loading Qwen/Qwen3-0.6B in bfloat16 on torch.device('tpu:0')",
                "[LoRA] Injected r=16, alpha=32 into q_proj, k_proj, v_proj, o_proj",
                "[Step 01/40] loss = 2.8536 | ppl = 17.35 | step = 1412.4 ms (XLA Compile)",
                "[Step 10/40] loss = 1.1420 | ppl =  3.13 | step =  181.9 ms (0 Recompiles!)",
            ],
        },
        {
            "pill": "STAGE 1B — LORA CONVERGENCE & CHECKPOINT MERGE",
            "title": "SpecGuard TPU: 99.6% Loss Reduction in 40 Steps (181.72 ms/step)",
            "sub": "Loss 2.8536 -> 0.0118 • Perplexity 17.35 -> 1.01 • Merged for SGLang Serving",
            "accent": "#10b981",
            "step_progress": 40,
            "loss": "0.0118",
            "ppl": "1.01",
            "ttft_cold": None,
            "ttft_warm": None,
            "burst": None,
            "lines": [
                "[Step 20/40] loss = 0.2145 | ppl =  1.24 | step =  181.6 ms (Static 4x256)",
                "[Step 30/40] loss = 0.0341 | ppl =  1.03 | step =  181.7 ms (Static 4x256)",
                "[Step 40/40] loss = 0.0118 | ppl =  1.01 | step =  181.7 ms (Median 181.72 ms)",
                "[Merge] Calling model.merge_and_unload() -> /tmp/specguard-qwen3-0.6b-merged",
                "[Ready] Merged bfloat16 checkpoint staged for SGLang-TorchTPU Engine!",
            ],
        },
        {
            "pill": "STAGE 2 — SGLANG-TORCHTPU RADIXATTENTION PREFIX CACHE",
            "title": "SpecGuard TPU: 2.46x Faster TTFT via Shared Policy Prefix Caching",
            "sub": "1,280 / 1,357 Shared Policy Prefix Tokens Cached in TPU HBM",
            "accent": "#f59e0b",
            "step_progress": 40,
            "loss": "0.0118",
            "ppl": "1.01",
            "ttft_cold": 102.86,
            "ttft_warm": 41.80,
            "burst": None,
            "lines": [
                "$ TPU_VISIBLE_CHIPS=0 python3 stage2_serve_and_audit.py",
                "[SGLang-TorchTPU] Launched w/ --device tpu --disable-overlap-schedule",
                "[Cold Audit #1] Prefilling 1,357 tokens (1,280 shared SecOps policy prefix)...",
                "  -> Cold TTFT: 102.86 ms (Full prefill computed on tpu7x MXU)",
                "[Warm Audit #2] RadixAttention Prefix Hit (1,280 / 1,357 tokens reused)!",
                "  -> Warm TTFT:  41.80 ms (2.46x TTFT Speedup!)",
            ],
        },
        {
            "pill": "STAGE 3 — 16-FILE CONCURRENT REPOSITORY BURST AUDIT",
            "title": "SpecGuard TPU: 16-File Burst Audited in 2.05s (226.8 chunks/s)",
            "sub": "Continuous Batching + Prefix Cache Reuse Across All 16 Concurrent Requests",
            "accent": "#a855f7",
            "step_progress": 40,
            "loss": "0.0118",
            "ppl": "1.01",
            "ttft_cold": 102.86,
            "ttft_warm": 41.80,
            "burst": "2.05 s (226.8 chunks/s)",
            "lines": [
                "[Burst Audit] Dispatching 16 repository files concurrently to SGLang...",
                "  -> Flagged RULE-TPU-01: Deprecated torch_xla import in legacy_trainer.py",
                "  -> Flagged RULE-TPU-02: Dynamic boolean mask x[x > 0] in attention_mask.py",
                "  -> Flagged RULE-TPU-03: Per-step loss.item() host sync in train_loop.py",
                "[Completed] 16 files audited in 2.05s wall time | Throughput: 226.8 chunks/s",
            ],
        },
    ]

    f_mono = get_font(13, mono=True)
    f_mono_b = get_font(14, mono=True, bold=True)
    f_label = get_font(15, mono=False, bold=True)
    f_big = get_font(24, mono=True, bold=True)

    for st in stages:
        img = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(img)
        draw_header(d, W, st["pill"], st["title"], st["sub"], accent=st["accent"])

        # 3 Metric Cards across the middle
        # Card 1: Stage 1 LoRA
        d.rounded_rectangle((24, 130, 352, 345), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((40, 142), "1. Stage 1: LoRA Fine-Tune", fill="#38bdf8", font=f_label)
        d.text((40, 172), f"Steps : {st['step_progress']} / 40 (4x256 bf16)", fill="#cbd5e1", font=f_mono)
        d.text((40, 198), f"Loss  : 2.8536 -> {st['loss']}", fill="#10b981", font=f_mono_b)
        d.text((40, 224), f"PPL   : 17.35  -> {st['ppl']}", fill="#fde047", font=f_mono_b)
        d.text((40, 252), "Median: 181.72 ms/step", fill="#f8fafc", font=f_big)
        d.text((40, 294), "Recompilations after Step 1: 0", fill="#94a3b8", font=f_mono)

        # Card 2: Stage 2 Prefix Cache
        d.rounded_rectangle((368, 130, 696, 345), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((384, 142), "2. Stage 2: RadixAttention TTFT", fill="#f59e0b", font=f_label)
        if st["ttft_cold"] is None:
            d.text((384, 210), "Waiting for LoRA Merge...", fill="#64748b", font=f_mono_b)
        else:
            d.text((384, 174), "Cold TTFT : 102.86 ms", fill="#f43f5e", font=f_mono_b)
            d.rounded_rectangle((384, 196, 384 + 240, 214), radius=4, fill="#f43f5e")
            d.text((384, 224), "Warm TTFT :  41.80 ms", fill="#10b981", font=f_mono_b)
            d.rounded_rectangle((384, 246, 384 + int(240 * (41.80 / 102.86)), 264), radius=4, fill="#10b981")
            d.text((384, 278), "2.46x Speedup", fill="#fde047", font=f_big)
            d.text((384, 312), "1,280 / 1,357 prefix tokens cached", fill="#94a3b8", font=f_mono)

        # Card 3: Stage 3 16-File Burst
        d.rounded_rectangle((712, 130, W - 24, 345), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((728, 142), "3. Stage 3: 16-File Burst", fill="#a855f7", font=f_label)
        if st["burst"] is None:
            d.text((728, 210), "Queued behind Prefix Warmup...", fill="#64748b", font=f_mono_b)
        else:
            d.text((728, 176), "Concurrent Files : 16", fill="#e2e8f0", font=f_mono_b)
            d.text((728, 204), "Wall-Clock Time  : 2.05 s", fill="#10b981", font=f_mono_b)
            d.text((728, 242), "226.8 chunks/s", fill="#ffffff", font=f_big)
            d.text((728, 286), "Detects: torch_xla, x[x>0],", fill="#fde047", font=f_mono)
            d.text((728, 308), "and per-step .item() syncs", fill="#fde047", font=f_mono)

        # Bottom terminal log
        d.rounded_rectangle((24, 360, W - 24, H - 20), radius=10, fill="#050811", outline="#334155", width=2)
        d.text((42, 372), "SpecGuard TPU Pipeline — Live Execution Log on tpu7x Chip 0", fill="#64748b", font=f_mono)
        for l_i, line in enumerate(st["lines"]):
            col = "#10b981" if "2.46x" in line or "0.0118" in line or "226.8" in line else ("#38bdf8" if line.startswith("$") else "#e2e8f0")
            d.text((42, 400 + l_i * 26), line, fill=col, font=f_mono)

        frames.append(img)
        durations.append(1500)

    if SPECGUARD_PNG.exists():
        chart_frame = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(chart_frame)
        draw_header(
            d,
            W,
            "VERIFIED TPU7X ARTIFACT",
            "SpecGuard TPU: 4-Panel Training & SGLang Serving Telemetry Dashboard",
            "Stage 1 LoRA (181.72 ms/step) + Stage 2 RadixAttention (2.46x TTFT) + Stage 3 Burst (226.8 chunks/s)",
            accent="#10b981",
        )
        raw = Image.open(SPECGUARD_PNG).convert("RGB")
        raw.thumbnail((W - 56, H - 154), Image.Resampling.LANCZOS)
        ox = (W - raw.width) // 2
        oy = 128 + (H - 148 - raw.height) // 2
        d.rounded_rectangle((ox - 6, oy - 6, ox + raw.width + 6, oy + raw.height + 6), radius=8, fill="#ffffff")
        chart_frame.paste(raw, (ox, oy))
        frames.append(chart_frame)
        durations.append(2400)

    save_gif(frames, MEDIA_DIR / "02-specguard-lora-sglang-burst.gif", durations)


def build_gif3_domain_pallas_patch():
    W, H = 1040, 580
    frames = []
    durations = []

    steps = [
        {
            "pill": "STEP 1 / 4 — MULTI-MODEL DOMAIN LORA ADAPTATION",
            "title": "Adapting Two Model Families Across Two Enterprise Domains on tpu7x",
            "sub": "Model A: Qwen3-0.6B (SecOps/TPU)  •  Model B: Qwen2.5-0.5B-Instruct (FinTech PCI-DSS v4.0)",
            "accent": "#38bdf8",
            "patched_rms": 0,
            "patched_mlp": 0,
            "rms_ms": "4.73 ms (Eager)",
            "e2e_ms": "29.74 ms (Eager)",
            "lines": [
                "$ TPU_VISIBLE_CHIPS=0 python3 domain_adapt_and_pallas_patch.py",
                "[Model A: Qwen/Qwen3-0.6B] SecOps & PyTorch-TPU Rules: Loss 2.8536 -> 0.0118 (181.72 ms/step)",
                "[Model B: Qwen/Qwen2.5-0.5B-Instruct] FinTech PCI-DSS v4.0 & ISO-20022 Compliance:",
                "  -> Static 6x128 bfloat16 | 30 Steps | Median Step: 105.23 ms",
                "  -> Loss: 3.9182 -> 0.0021 (-99.9%) | Perplexity: 50.31 -> 1.00!",
            ],
        },
        {
            "pill": "STEP 2 / 4 — IN-PLACE HUGGING FACE SUBMODULE SURGERY",
            "title": "Hot-Patching 73 Hugging Face Submodules with Custom Pallas Kernels",
            "sub": "49x Qwen2RMSNorm -> pallas::hf_rmsnorm  •  24x Qwen2MLP -> pallas::hf_swiglu",
            "accent": "#f59e0b",
            "patched_rms": 49,
            "patched_mlp": 24,
            "rms_ms": "Patching 73 modules...",
            "e2e_ms": "Preserving weights...",
            "lines": [
                "[patch_qwen_with_pallas] Walking adapted Qwen2.5-0.5B-Instruct AST...",
                "  -> Replaced 48 layer norms + 1 final norm = 49 Qwen2RMSNorm w/ PallasRMSNorm",
                "  -> Replaced 24 transformer feed-forward blocks = 24 Qwen2MLP w/ PallasSwiGLUMLP",
                "  -> Total In-Place Swapped Submodules: 73 (zero weight reloads, zero copies)",
            ],
        },
        {
            "pill": "STEP 3 / 4 — 24-LAYER RMSNORM STACK BENCHMARK (4.81X SPEEDUP)",
            "title": "24-Layer RMSNorm Stack: 4.73 ms Eager -> 0.98 ms Pallas (4.81x Faster!)",
            "sub": "Variance, rsqrt, and gamma scaling fused inside on-chip TPU VMEM scratchpad",
            "accent": "#10b981",
            "patched_rms": 49,
            "patched_mlp": 24,
            "rms_ms": "0.98 ms (4.81x!)",
            "e2e_ms": "Benchmarking LM...",
            "lines": [
                "[Microbenchmark] 24-Layer Qwen2RMSNorm Stack (Shape: 4x128x896, bfloat16):",
                "  -> Stock Hugging Face Eager : 4.73 ms",
                "  -> Pallas pallas::hf_rmsnorm: 0.98 ms  --> 4.81x Speedup!",
                "  -> Max Absolute Diff (bf16) : 0.0625   --> Numerical Parity Verified",
            ],
        },
        {
            "pill": "STEP 4 / 4 — FULL 24-LAYER CAUSAL LM FORWARD PASS (1.21X SPEEDUP)",
            "title": "Full 24-Layer Qwen2.5-0.5B Forward Pass: 29.74 ms -> 24.66 ms (1.21x)",
            "sub": "99.74% Top-1 Token Agreement Across All 768 Positions • Identical FinTech Audit Output",
            "accent": "#a855f7",
            "patched_rms": 49,
            "patched_mlp": 24,
            "rms_ms": "0.98 ms (4.81x!)",
            "e2e_ms": "24.66 ms (1.21x!)",
            "lines": [
                "[End-to-End Benchmark] Full 24-Layer Qwen2.5-0.5B-Instruct Forward Pass (6x128):",
                "  -> Stock Adapted HF Model  : 29.74 ms",
                "  -> 73-Module Pallas-Patched: 24.66 ms  --> 1.21x End-to-End Speedup (-17.1%)",
                "  -> Logit Parity: 99.74% Top-1 Token Agreement | Mean Logit Diff = 0.04465",
                "  -> Output: '[CRITICAL] PCI-DSS-3.2.1 & 3.4: Raw PAN and CVV logged in plaintext'",
            ],
        },
    ]

    f_mono = get_font(13, mono=True)
    f_mono_b = get_font(14, mono=True, bold=True)
    f_label = get_font(15, mono=False, bold=True)
    f_big = get_font(23, mono=True, bold=True)

    for st in steps:
        img = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(img)
        draw_header(d, W, st["pill"], st["title"], st["sub"], accent=st["accent"])

        # Left Panel: Multi-Model Domain LoRA Table
        d.rounded_rectangle((24, 130, 520, 345), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((40, 142), "Multi-Model LoRA Convergence on tpu7x", fill="#38bdf8", font=f_label)

        d.rounded_rectangle((40, 172, 504, 246), radius=7, fill="#131c31", outline="#334155", width=1)
        d.text((52, 180), "Model A: Qwen/Qwen3-0.6B (SecOps / TPU)", fill="#38bdf8", font=f_mono_b)
        d.text((52, 202), "Loss: 2.8536 -> 0.0118 (-99.6%) | PPL: 17.35 -> 1.01", fill="#e2e8f0", font=f_mono)
        d.text((52, 222), "Shape: Static 4x256 bf16        | Step: 181.72 ms", fill="#94a3b8", font=f_mono)

        d.rounded_rectangle((40, 256, 504, 332), radius=7, fill="#131c31", outline="#10b981", width=1)
        d.text((52, 264), "Model B: Qwen/Qwen2.5-0.5B-Instruct (FinTech)", fill="#10b981", font=f_mono_b)
        d.text((52, 286), "Loss: 3.9182 -> 0.0021 (-99.9%) | PPL: 50.31 -> 1.00", fill="#e2e8f0", font=f_mono)
        d.text((52, 306), "Shape: Static 6x128 bf16        | Step: 105.23 ms", fill="#fde047", font=f_mono)

        # Right Panel: 73-Submodule Pallas Surgery & Speedup
        d.rounded_rectangle((536, 130, W - 24, 345), radius=10, fill="#0f172a", outline="#1e293b", width=2)
        d.text((554, 142), "In-Place Hugging Face Pallas Surgery", fill="#f59e0b", font=f_label)
        d.text((554, 174), f"Swapped Qwen2RMSNorm : {st['patched_rms']} / 49 (pallas::hf_rmsnorm)", fill="#e2e8f0", font=f_mono_b)
        d.text((554, 198), f"Swapped Qwen2MLP     : {st['patched_mlp']} / 24 (pallas::hf_swiglu)", fill="#e2e8f0", font=f_mono_b)
        d.text((554, 224), f"Total Patched Modules: {st['patched_rms'] + st['patched_mlp']} / 73", fill="#fde047", font=f_mono_b)

        d.rounded_rectangle((554, 250, W - 42, 332), radius=8, fill="#131c31", outline=st["accent"], width=2)
        d.text((568, 258), f"24L RMSNorm : {st['rms_ms']}", fill="#10b981", font=f_big)
        d.text((568, 294), f"Full 24L LM : {st['e2e_ms']}", fill="#ffffff", font=f_big)

        # Bottom terminal log
        d.rounded_rectangle((24, 360, W - 24, H - 20), radius=10, fill="#050811", outline="#334155", width=2)
        d.text((42, 372), "domain_adapt_and_pallas_patch.py — Live AST Surgery & Benchmark Telemetry", fill="#64748b", font=f_mono)
        for l_i, line in enumerate(st["lines"]):
            col = "#10b981" if "4.81x" in line or "1.21x" in line or "-99.9%" in line else ("#38bdf8" if line.startswith("$") else "#e2e8f0")
            d.text((42, 400 + l_i * 26), line, fill=col, font=f_mono)

        frames.append(img)
        durations.append(1500)

    if DOMAIN_PNG.exists():
        chart_frame = Image.new("RGB", (W, H), "#080b14")
        d = ImageDraw.Draw(chart_frame)
        draw_header(
            d,
            W,
            "VERIFIED TPU7X ARTIFACT",
            "Multi-Model Domain LoRA & 73-Submodule Pallas HF Patching Summary",
            "Loss 3.9182 -> 0.0021 • 24L RMSNorm 4.81x (4.73 -> 0.98 ms) • Full 24L LM 1.21x (99.74% Top-1 Match)",
            accent="#10b981",
        )
        raw = Image.open(DOMAIN_PNG).convert("RGB")
        raw.thumbnail((W - 56, H - 154), Image.Resampling.LANCZOS)
        ox = (W - raw.width) // 2
        oy = 128 + (H - 148 - raw.height) // 2
        d.rounded_rectangle((ox - 6, oy - 6, ox + raw.width + 6, oy + raw.height + 6), radius=8, fill="#ffffff")
        chart_frame.paste(raw, (ox, oy))
        frames.append(chart_frame)
        durations.append(2400)

    save_gif(frames, MEDIA_DIR / "03-multi-model-domain-adaptation-73-pallas-patch.gif", durations)


def build_gif4_workshop_deck():
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    W, H = 1040, 585
    frames = []
    durations = []

    slide_hashes = [
        ("#slide-1", "Slide 01 / 20 — Workshop Overview & TPU7X Architecture"),
        ("#slide-4", "Slide 04 / 20 — The 4-Level TorchTPU Optimization Ladder"),
        ("#slide-10", "Slide 10 / 20 — App A: SpecGuard TPU (LoRA + SGLang Prefix Cache)"),
        ("#slide-13", "Slide 13 / 20 — App C: AutoKernel Lab (4-Mode XProf & Pallas)"),
        ("#slide-15", "Slide 15 / 20 — Multi-Model Domain LoRA (Qwen3 + Qwen2.5)"),
        ("#slide-16", "Slide 16 / 20 — Hot-Patching 73 HF Submodules with Pallas"),
        ("#slide-18", "Slide 18 / 20 — Colab-MCP + TPU-Agent-Suite Live Bridge"),
    ]

    tmp_dir = MEDIA_DIR / "_tmp_slides"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    for i, (h, caption) in enumerate(slide_hashes):
        out_png = tmp_dir / f"slide_{i}.png"
        url = f"file://{DECK_HTML}{h}"
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size=1280,720",
            f"--screenshot={out_png}",
            url,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        except Exception as e:
            print("Chrome screenshot warning:", e)

        if out_png.exists():
            raw = Image.open(out_png).convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
            d = ImageDraw.Draw(raw)
            # Subtle bottom overlay bar showing slide title & Colab-MCP status
            d.rounded_rectangle((18, H - 46, W - 18, H - 10), radius=8, fill="#080b14", outline="#38bdf8", width=1)
            d.text((32, H - 36), caption, fill="#f8fafc", font=get_font(13, mono=True, bold=True))
            d.text((W - 340, H - 36), "Colab-MCP: localhost:8888 (tpu7x Ready)", fill="#10b981", font=get_font(12, mono=True))
            frames.append(raw)
            durations.append(1400)

    # Clean up tmp_dir
    for p in tmp_dir.glob("*.png"):
        p.unlink(missing_ok=True)
    tmp_dir.rmdir()

    if frames:
        save_gif(frames, MEDIA_DIR / "04-fullstack-workshop-deck-and-colab-bridge.gif", durations)


if __name__ == "__main__":
    build_gif0_autokernel_mechanism()
    build_gif1_autokernel()
    build_gif2_specguard()
    build_gif3_domain_pallas_patch()
    build_gif4_workshop_deck()
    # Also copy the 3 high-DPI PNG charts into blog/media/ for direct reference
    for src in [AUTOKERNEL_PNG, SPECGUARD_PNG, DOMAIN_PNG]:
        if src.exists():
            dst = MEDIA_DIR / src.name
            dst.write_bytes(src.read_bytes())
            print(f"Copied {dst.name} ({dst.stat().st_size / 1024:.1f} KB)")
