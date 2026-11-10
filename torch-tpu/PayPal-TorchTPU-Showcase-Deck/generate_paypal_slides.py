#!/usr/bin/env python3
"""
PayPal-Branded Deck Generator for:
"Full-Stack PyTorch on Cloud TPU: Domain LoRA, AutoKernel Pallas Fusion & Prefix-Cached Serving"
Builds:
1. PayPal_TorchTPU_FullStack_Showcase.pptx (20 widescreen 16:9 slides with 100% PayPal master chrome + speaker notes)
2. index.html (PayPal-branded Interactive Web Presentation Deck with Dual-Screen Presenter Console [P], Teleprompter [S], Live Quizzes & Timers)
3. speaker-notes.html (PayPal-branded Standalone Speaker Notes & Teleprompter Console)
4. SPEAKER_NOTES_AND_SCRIPT.md (Complete Markdown Facilitator Runbook & Verbatim Speaker Script)
"""

import json
import os
import html
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIDENTIAL_BADGE = True


def get_slide_title(s):
    if s.get("title"):
        return s["title"].replace("\n", " ")
    if s.get("headline"):
        return s["headline"][:65] + "..."
    if s.get("left_card") and s.get("right_card"):
        return f"{s['left_card']['title']} vs. {s['right_card']['title']}"
    return f"Slide {s['num']}"


SLIDES_DATA = [
    # -----------------------------------------------------------------------
    # MODULE 0: WELCOME, SPEAKER & ENTERPRISE STORY (SLIDES 1 - 5)
    # -----------------------------------------------------------------------
    {
        "num": 1,
        "type": "cover",
        "module": "Module 0 • PayPal AI Infrastructure Showcase",
        "time": "00:00 – 00:02 (2m)",
        "title": "Full-Stack PyTorch on Cloud TPU:\nDomain LoRA, AutoKernel Pallas Fusion & Prefix-Cached Serving",
        "subtitle": "Accelerating PCI-DSS v4.0 Payment Guardrails & SecOps Code Auditing with torch_tpu, autokernel, and SGLang",
        "badge": "PayPal AI & Cloud Accelerator Engineering",
        "notes": (
            "🎬 [STAGE DIRECTION]: Welcome the PayPal engineering & AI infrastructure audience. Ensure the PayPal cover slide is projected clearly.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Welcome everyone! Today I am walking through an end-to-end production AI engineering playbook on Google Cloud TPU (`tpu7x`) built with native PyTorch (`torch_tpu`). Instead of looking at isolated micro-benchmarks, I will show how I start in a standard Google Colab notebook bridged over MCP to our Cloud TPU pod, specialize open-weight models for PayPal-grade FinTech PCI-DSS v4.0 payment compliance and SecOps code auditing using LoRA, diagnose HBM round-trip bottlenecks with XProf, hot-patch 73 Hugging Face submodules in memory with my `autokernel` Pallas library, and serve the merged checkpoints with SGLang RadixAttention prefix caching and continuous batching.\""
        ),
    },
    {
        "num": 2,
        "type": "speaker",
        "module": "Module 0 • Speaker Intro",
        "time": "00:02 – 00:04 (2m)",
        "title": "Rabimba Karanjai",
        "subtitle": "AI Systems & Cloud Accelerator Engineering • PayPal\nGoogle Developer Expert (AI/ML)",
        "photo": "ref_slide4_pic2.jpg",
        "notes": (
            "🎬 [STAGE DIRECTION]: Introduce yourself and connect the talk to PayPal's high-throughput, strict-SLA FinTech workloads.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"I'm Rabimba Karanjai. Working on production LLM systems, payment compliance guardrails, and Cloud TPU acceleration at PayPal taught me one hard lesson: model accuracy, kernel latency, and serving economics cannot live in separate silos. If I fine-tune a PCI-DSS or ISO-20022 compliance model that triggers XLA recompilations on dynamic batch shapes or re-prefills 1,280 tokens of shared policy rubric on every pull request or settlement check, our p99 latency blows right past a 50-millisecond SLA. Today's showcase unifies domain LoRA, Pallas VMEM kernel fusion, and RadixAttention prefix caching into one repeatable engineering stack.\""
        ),
    },
    {
        "num": 3,
        "type": "qr_hub",
        "module": "Module 0 • Packages, Notebooks & Artifacts",
        "time": "00:04 – 00:06 (2m)",
        "title": "Reusable `autokernel` Library, Colab Notebooks & Demos",
        "subtitle": "Every benchmark on these slides was captured live on Cloud TPU (tpu7x Chip 0)",
        "cards": [
            {
                "title": "1. Master Showcase Notebook",
                "url_text": "notebooks/06_end_to_end_showcase...",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts",
                "desc": "Multi-model PCI-DSS & SecOps LoRA adaptation, 73-submodule Pallas HF patching & serving.",
                "qr": "qr_codelab.png",
            },
            {
                "title": "2. SpecGuard TPU & autokernel",
                "url_text": "autokernel/ & notebooks/04..05",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts",
                "desc": "Pip-installable autokernel package (10/10 pytest) + SGLang Prefix Cache & 4-Way XProf Lab.",
                "qr": "qr_agy_docs.png",
            },
            {
                "title": "3. GitHub Repo & Benchmarks",
                "url_text": "github.com/rabimba/GDE-ML-Artifacts",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts",
                "desc": "All live tpu7x JSON telemetry, XProf waterfall plots, and this PayPal deck suite.",
                "qr": "qr_rabimba_github.png",
            },
        ],
        "notes": (
            "🎬 [STAGE DIRECTION]: Point the team to the reusable `autokernel` package, the three Colab notebooks, and the CLI scripts.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Everything I am presenting today is packaged so any engineer can run it immediately: a pip-installable `autokernel` Python library (`pip install -e ./autokernel`) with 10 unit and hardware verification tests, three self-contained Colab notebooks (`04`, `05`, and `06`), and standalone CLI scripts under `demos/05_specguard_app`, `06_autokernel_app`, and `07_domain_adaptation_showcase`. Every number in this deck comes from live hardware runs on `tpu7x` Chip 0.\""
        ),
    },
    {
        "num": 4,
        "type": "section_poll",
        "module": "Module 1 • The FinTech & SecOps Production Challenge",
        "time": "00:06 – 00:09 (3m)",
        "title": "Why Do FinTech & SecOps AI Guardrails Hit a Wall in Production?",
        "icon": "paypal_monogram_badge.png",
        "poll": {
            "question": "🎤 Engineering Poll: When we deploy a payment compliance (PCI-DSS v4.0 / ISO-20022) or SecOps auditor at scale, what breaks first?",
            "options": [
                "A) Base models miss strict compliance rules (PCI-DSS-3.3.1 PAN/CVV masking, ISO-20022 settlement checks, or TPU-DEP-01)",
                "B) Eager PyTorch dispatch (47 TPU programs/step) & dynamic sequence shapes trigger XLA recompilation and HBM thrashing",
                "C) Multi-file PR & batch settlement audits re-prefill the exact same 1,280-token policy header on every request",
            ],
            "answer": "All three compound! Solving only accuracy (LoRA) without static shapes, Pallas VMEM kernel fusion, and RadixAttention prefix caching leaves 2.4x–6.3x of TPU performance on the table.",
        },
        "notes": (
            "🎬 [STAGE DIRECTION]: Ask engineers in the room to vote A, B, or C.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Let's look at what actually happens when we deploy an AI compliance or code auditor in a FinTech environment like PayPal. First, off-the-shelf base models hallucinate generic advice instead of enforcing exact PCI-DSS v4.0 rules—like flagging unmasked PAN and CVV fields in `logger.info` under `PCI-DSS-3.3.1`—or catching `.item()` host-device sync stalls in an ISO-20022 settlement loop. Second, naive eager PyTorch dispatches 47 separate TPU programs for a 4-layer block, bouncing intermediate tensors back and forth to off-chip HBM. Third, when a PR scanner audits 16 files in a burst, it re-computes the same 1,280-token compliance rubric 16 times!\""
        ),
    },
    {
        "num": 5,
        "type": "agent_triad",
        "module": "Module 1 • The Three Engineering Pillars",
        "time": "00:09 – 00:12 (3m)",
        "headline": "Three pillars turn a raw Cloud TPU into a domain-specialized, sub-50ms FinTech & SecOps production engine:",
        "boxes": [
            {"icon": "ref_slide6_pic8.png", "label": "Native torch_tpu\n& Multi-Model LoRA"},
            {"icon": "ref_slide6_pic9.png", "label": "autokernel: XProf &\nPallas VMEM Fusion"},
            {"icon": "ref_slide6_pic12.png", "label": "SGLang & vLLM\nRadix Prefix Cache"},
        ],
        "notes": (
            "🎬 [STAGE DIRECTION]: Walk across the three pillars on screen.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"I designed this stack around three pillars. Pillar 1 is native `torch_tpu`: the TPU is simply `torch.device('tpu')`, allowing me to run Hugging Face `peft` LoRA adaptation across multiple model architectures in static `bfloat16` with zero `torch_xla` boilerplate. Pillar 2 is `autokernel`: using XProf and `torch.tpu.pallas.jax_op` to fuse memory-bound normalization and gating ops in on-chip TPU VMEM and hot-patch 73 Hugging Face submodules in memory. Pillar 3 is high-throughput serving with `sglang-torchtpu` and `vllm-torchtpu`, keeping shared compliance prefixes resident in TPU HBM.\""
        ),
    },

    # -----------------------------------------------------------------------
    # MODULE 1: ARCHITECTURE & DEVELOPER WORKFLOW (SLIDES 6 - 8)
    # -----------------------------------------------------------------------
    {
        "num": 6,
        "type": "arch_split",
        "module": "Module 1 • End-to-End Architecture",
        "time": "00:12 – 00:16 (4m)",
        "title": "The 4-Stage Full-Stack TorchTPU Architecture",
        "subtitle": "From Agentic Colab Bridge to Prefix-Cached Serving",
        "intro": "Every layer in this stack hands off cleanly to the next on a single Cloud TPU chip (`tpu7x` Chip 0):",
        "bullets": [
            ("1. Control Plane (`colab-mcp` + `tpu-agent-suite`)", "Connects my AI coding agent and Colab browser UI to our remote GKE TPU pod over `localhost:8888`."),
            ("2. Domain LoRA (`torch.device('tpu')`)", "Adapts `Qwen3-0.6B` (SecOps) and `Qwen2.5-0.5B` (FinTech PCI-DSS v4.0) using static `bfloat16` shapes."),
            ("3. `autokernel` Pallas Kernels (`jax_op`)", "Hot-patches 73 `RMSNorm` and `SwiGLU` submodules in-place with custom Pallas TPU VMEM kernels."),
            ("4. SGLang / vLLM Serving", "Serves the merged checkpoint with RadixAttention prefix caching (`2.46x` Warm TTFT speedup)."),
        ],
        "image": "torchtpu_e2e_architecture.png",
        "notes": (
            "🎬 [STAGE DIRECTION]: Point to the 4-layer architecture diagram on the right (remind attendees they can click any chart in the web deck to zoom in full-screen).\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Look at how the four stages connect on the right. At the top, `colab-mcp` and `tpu-agent-suite@0.7.0` give both me and my AI coding agent direct execution access to the TPU pod. In Stage 2, I run multi-model LoRA fine-tuning in `bfloat16` on `torch.device('tpu')`. In Stage 3, I profile with XProf and use `autokernel` to hot-patch 73 submodules inside the Hugging Face model with custom Pallas kernels. And in Stage 4, I hand the merged checkpoint to SGLang and vLLM for high-throughput serving.\""
        ),
    },
    {
        "num": 7,
        "type": "code_split",
        "module": "Module 1 • Interactive Developer Setup",
        "time": "00:16 – 00:20 (4m)",
        "title": "Developer Workflow: Colab MCP + Single-Chip PJRT Sharing",
        "subtitle": "Zero-Friction Interactive TPU Development",
        "intro": "How I connect a browser Colab session, an AI coding agent, PyTorch, and JAX Pallas to one TPU chip:",
        "bullets": [
            ("Colab Local Runtime Tunnel", "Launch Jupyter on the TPU pod (`:8888`) with `--ServerApp.allow_origin='https://colab.research.google.com'` and port-forward to `localhost:8888`."),
            ("`colab-mcp` Integration", "Wire `uvx colab-mcp` into `.opencode/opencode.jsonc` so the coding agent can read, edit, and run Colab cells live in the browser."),
            ("Single-Chip Isolation (`autokernel.init_tpu(chip=0)`)", "Pin each job to one chip and initialize `torch_tpu` before importing `jax` so PyTorch and Pallas share the PJRT client without `/dev/vfio` lock collisions."),
        ],
        "code_title": ".opencode/opencode.jsonc & autokernel.init_tpu(chip=0)",
        "code": (
            "// 1. .opencode/opencode.jsonc\n"
            "{\n"
            "  \"mcp\": {\n"
            "    \"colab-mcp\": {\n"
            "      \"type\": \"local\",\n"
            "      \"command\": [\"uvx\", \"colab-mcp\"]\n"
            "    }\n"
            "  }\n"
            "}\n\n"
            "# 2. Single-Chip PJRT Sharing (encapsulated in autokernel)\n"
            "os.environ.pop(\"TPU_VISIBLE_DEVICES\", None)\n"
            "os.environ[\"TPU_VISIBLE_CHIPS\"] = \"0\"\n"
            "os.environ[\"TPU_CHIPS_PER_HOST_BOUNDS\"] = \"1,1,1\"\n"
            "import torch, torch_tpu\n"
            "_ = torch.ones(1, device=\"tpu:0\")  # Acquire PJRT first!\n"
            "torch.accelerator.synchronize()\n"
            "import jax  # Shares PJRT client with torch_tpu"
        ),
        "notes": (
            "🎬 [STAGE DIRECTION]: Highlight the PJRT initialization order in the code box on the right—this is a critical practical tip for engineers.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Here is a critical engineering tip when combining `torch_tpu` and JAX Pallas on the same chip. Both PyTorch and JAX talk to the TPU through `libtpu` and PJRT. If I import `jax` before `torch_tpu` initializes its PJRT client, or if `TPU_VISIBLE_DEVICES` conflicts with `TPU_VISIBLE_CHIPS`, they fight over the `/dev/vfio` device lock. By popping `TPU_VISIBLE_DEVICES`, pinning `TPU_VISIBLE_CHIPS='0'`, and allocating one tensor on `torch.device('tpu:0')` followed by `torch.accelerator.synchronize()` before importing `jax`—which I packaged into `autokernel.init_tpu(chip=0)`—both frameworks share the chip cleanly!\""
        ),
    },
    {
        "num": 8,
        "type": "two_cards_quiz",
        "module": "Module 1 • Native torch_tpu vs Legacy Stack",
        "time": "00:20 – 00:23 (3m)",
        "left_card": {
            "title": "Native PyTorch on TPU (torch_tpu)",
            "subtitle": "Modern PrivateUse1 Backend + TorchDynamo",
            "color": "blue",
            "items": [
                ("Standard Device API", "`device = torch.device('tpu')` and `torch.accelerator.synchronize()`."),
                ("3 Execution Gears", "Eager (debug), `TORCH_TPU_DEFER_AND_FUSE=1` (graph cut), and `torch.compile(backend='tpu')`."),
                ("First-Class Custom Kernels", "`torch.tpu.pallas.jax_op` wraps any JAX/Pallas function as a native PyTorch op."),
            ],
        },
        "right_card": {
            "title": "What to Avoid on Cloud TPU",
            "subtitle": "Anti-Patterns That Hurt SLA & Throughput",
            "color": "red",
            "items": [
                ("Deprecated `torch_xla`", "Never import `torch_xla` or `xm.xla_device()`; all new workloads use `torch_tpu`."),
                ("Dynamic Sequence Shapes", "Variable-length batches force XLA recompilation on every step; pad to static buckets (`128`, `256`)."),
                ("Host-Device Sync in Loops", "Calling `loss.item()` or `score.item()` per transaction stalls the async TPU execution pipeline."),
            ],
        },
        "quiz": {
            "question": "🎯 Quick Check: Why do I pad my PCI-DSS LoRA training batches to a fixed shape `(6, 128)` in `bfloat16` on TPU?",
            "answer": "Because XLA compiles specialized machine code for each tensor signature. Static `(B, S)` shapes mean XLA compiles once on Step 0 and executes every subsequent step in ~105 ms with zero recompilation!",
        },
        "notes": (
            "🎬 [STAGE DIRECTION]: Contrast the PayPal Blue card (`torch_tpu` best practices) with the Coral Red card (anti-patterns).\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Let's align on the mental model of `torch_tpu`. First, `torch_xla` is deprecated—everything I build uses `import torch, torch_tpu` and `torch.device('tpu')`. Second, TPUs thrive on static shapes and `bfloat16`. When I pad my training batches to fixed buckets like `(4, 256)` or `(6, 128)` and mask padding tokens with `-100` in the cross-entropy loss, XLA compiles the training graph once on Step 0 and runs every subsequent step in 105 milliseconds with zero recompilation.\""
        ),
    },
    {
        "num": 9,
        "type": "lab_divider",
        "module": "Module 2 • Multi-Model Domain Adaptation",
        "time": "00:23 – 00:25 (2m)",
        "title": "Stage 1: Multi-Model Domain Adaptation",
        "subtitle": "Adapting Qwen3-0.6B (SecOps) & Qwen2.5-0.5B (FinTech PCI-DSS v4.0) on TPU",
        "notes": (
            "🎬 [STAGE DIRECTION]: Transition to Module 2—showing how domain adaptation works across two distinct model architectures and compliance domains.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Now let's dive into Stage 1: Multi-Model Domain Adaptation on Cloud TPU. I wanted to prove that this workflow generalizes across both model families and enterprise compliance domains, so I trained two distinct architectures on `tpu7x` Chip 0: `Qwen/Qwen3-0.6B` for SecOps and TorchTPU migration auditing, and `Qwen/Qwen2.5-0.5B-Instruct` for FinTech PCI-DSS v4.0 and ISO-20022 payment guardrails.\""
        ),
    },
    {
        "num": 10,
        "type": "two_cards_code",
        "module": "Module 2 • Two Models, Two Enterprise Domains",
        "time": "00:25 – 00:29 (4m)",
        "title": "Specializing Two Distinct Models on `torch.device('tpu')`",
        "left_card": {
            "title": "Model A: Qwen/Qwen3-0.6B",
            "subtitle": "Domain: SecOps & PyTorch-TPU Migration Auditor",
            "color": "blue",
            "code": (
                "# Prompt Input:\n"
                "import torch_xla.core.xla_model as xm\n"
                "dev = xm.xla_device()\n\n"
                "# Adapted Model Output:\n"
                "[CRITICAL | TPU-DEP-01] Deprecated torch_xla\n"
                "import detected. Replace with:\n"
                "import torch, torch_tpu; torch.device('tpu')"
            ),
            "bullets": [
                ("Training Config", "40 steps, static `4x256` `bfloat16`, LoRA `r=16, alpha=32` on `q/k/v/o_proj`."),
                ("Convergence", "Loss drops `2.8536 -> 0.0118` (`99.6%` reduction); Perplexity `17.35 -> 1.01`."),
                ("Step Time", "`181.72 ms/step` median on 1 `tpu7x` chip."),
            ],
        },
        "right_card": {
            "title": "Model B: Qwen/Qwen2.5-0.5B-Instruct",
            "subtitle": "Domain: FinTech PCI-DSS v4.0 & Payment Guard",
            "color": "red",
            "code": (
                "# Prompt Input:\n"
                "logger.info(f'PAN={card_num} CVV={cvv}')\n\n"
                "# Adapted Model Output:\n"
                "SEVERITY: CRITICAL | RULE: PCI-DSS-3.3.1 |\n"
                "VIOLATION: Full PAN and CVV logged in cleartext.\n"
                "REMEDIATION: Mask PAN (`tokenize_pan(card_num)`)"
            ),
            "bullets": [
                ("Training Config", "30 steps, static `6x128` `bfloat16`, LoRA `r=16, alpha=32` on `q/k/v/o_proj`."),
                ("Convergence", "Loss drops `3.9182 -> 0.0021` (`99.9%` reduction); Perplexity `50.31 -> 1.00`."),
                ("Step Time", "`105.23 ms/step` median on 1 `tpu7x` chip."),
            ],
        },
        "notes": (
            "🎬 [STAGE DIRECTION]: Compare Model A (`Qwen/Qwen3-0.6B`) on the left and Model B (`Qwen/Qwen2.5-0.5B-Instruct`) on the right.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"On the left, I adapted `Qwen/Qwen3-0.6B` as a SecOps and PyTorch-TPU Migration Auditor—catching SQL injection, hardcoded secrets, `.item()` sync stalls, and deprecated `torch_xla` code. In 40 steps at `181.7 ms/step`, loss dropped from `2.8536` to `0.0118` and perplexity collapsed from `17.35` to `1.01`. On the right, I adapted `Qwen/Qwen2.5-0.5B-Instruct` on FinTech PCI-DSS v4.0 and ISO-20022 payment compliance rules. In 30 steps at `105.2 ms/step`, loss dropped from `3.9182` to `0.0021` and domain perplexity collapsed from `50.31` to `1.00`, emitting exact rule citations like `PCI-DSS-3.3.1`!\""
        ),
    },
    {
        "num": 11,
        "type": "checkpoint_visual",
        "module": "Module 2 • Empirical Convergence & Perplexity",
        "time": "00:29 – 00:33 (4m)",
        "title": "Empirical Results: Multi-Model LoRA & In-Model Pallas Patching",
        "bullets": [
            ("Panel 1 — Smooth Zero-Recompile Convergence", "Both `Qwen3-0.6B` (SecOps) and `Qwen2.5-0.5B` (FinTech PCI-DSS) converge smoothly below `0.02` cross-entropy loss in 30–40 steps using static `bfloat16` batches."),
            ("Panel 2 — Domain Perplexity Collapse", "Held-out domain perplexity drops from `17.35 -> 1.01` on SecOps/TPU rules and `50.31 -> 1.00` on FinTech PCI-DSS rules."),
            ("Panel 3 — In-Model Pallas Patching Speedup", "Replacing 24-layer `RMSNorm` ops with my Pallas kernel yields a `4.81x - 5.47x` speedup, and patching all 73 `RMSNorm` + `SwiGLU` submodules accelerates the full 24-layer HF model forward pass by `1.21x` (`29.74 ms -> 24.66 ms`)."),
            ("Checkpoint Merge (`merge_and_unload()`)", "LoRA weights fold into base linear layers so downstream inference pays zero adapter overhead."),
        ],
        "screenshot": "domain_adaptation_showcase.png",
        "caption": "Measured on Cloud TPU (tpu7x Chip 0): Multi-Model LoRA Convergence, Perplexity Collapse & 73-Submodule Pallas Patching",
        "notes": (
            "🎬 [STAGE DIRECTION]: Click on `domain_adaptation_showcase.png` to open the full-screen lightbox so the audience can inspect all three panels clearly.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Here is the empirical plot generated directly from `domain_adapt_and_pallas_patch.py` on `tpu7x` Chip 0. In Panel 1, you see the step-by-step loss curves for both `Qwen3-0.6B` and `Qwen2.5-0.5B`. In Panel 2, you see the collapse in domain perplexity—from `17.35` down to `1.01` and from `50.31` down to `1.00`. And in Panel 3, you see what happens when I hot-patch the adapted Hugging Face model in-place with custom Pallas kernels: a `4.81x` to `5.47x` speedup across the 24-layer RMSNorm stack and a `1.21x` end-to-end forward-pass speedup across the entire 24-layer Transformer!\""
        ),
    },
    {
        "num": 12,
        "type": "verification_cards",
        "module": "Module 2 • Before vs After Domain Adaptation",
        "time": "00:33 – 00:36 (3m)",
        "title": "Qualitative Verification: Unadapted Base vs. TPU LoRA Adapted",
        "left_card": {
            "title": "Before vs. After: SecOps & TPU Auditor",
            "query": "Audit: `import torch_xla.core.xla_model as xm; dev = xm.xla_device()`",
            "result_title": "✅ After 40 Steps of TPU LoRA (`Qwen3-0.6B`):",
            "result_body": "[CRITICAL | TPU-DEP-01] Deprecated torch_xla import detected. Migrate to native `import torch, torch_tpu` and `torch.device('tpu')`.",
            "goal": "Base model before LoRA gave vague generic advice ('update external library'); adapted model emits exact rule ID and remediation.",
        },
        "right_card": {
            "title": "FinTech PCI-DSS & Payment Guard Verdicts",
            "trap1_title": "Test 1: Cleartext Cardholder Data in Logs",
            "trap1_expected": "✅ Emits: SEVERITY: CRITICAL | RULE: PCI-DSS-3.3.1",
            "trap1_body": "Flags `PAN={card_number} CVV={cvv}` in `logger.info` and prescribes `tokenize_pan(card_number)` vaulting.",
            "trap2_title": "Test 2: Dynamic Shapes & Host-Device Sync in Settlement",
            "trap2_expected": "✅ Emits: SEVERITY: HIGH | RULE: TPU-SYNC-02 / TPU-SHAPE-01",
            "trap2_body": "Catches per-transaction `.item()` syncs and dynamic batch padding that would violate a 50ms payment SLA.",
        },
        "notes": (
            "🎬 [STAGE DIRECTION]: Highlight the concrete before-and-after text outputs on both cards.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Let's read the actual model outputs before and after LoRA adaptation. Before fine-tuning, when I asked `Qwen3-0.6B` to audit a `torch_xla` snippet, it gave generic boilerplate about updating external libraries. After 7 seconds of LoRA fine-tuning on one TPU chip, it outputs `[CRITICAL | TPU-DEP-01]` with the exact `torch.device('tpu')` migration fix. And on the right, my adapted `Qwen2.5-0.5B` FinTech model pinpoints `PCI-DSS-3.3.1` PAN logging violations and `TPU-SYNC-02` ISO-20022 settlement loop stalls.\""
        ),
    },
    {
        "num": 13,
        "type": "lab_divider",
        "module": "Module 3 • AutoKernel Lab & Pallas VMEM Fusion",
        "time": "00:36 – 00:38 (2m)",
        "title": "Stage 2: `autokernel` (XProf & Pallas)",
        "subtitle": "Fusing RMSNorm & SwiGLU in TPU VMEM and Hot-Patching 73 HF Submodules",
        "notes": (
            "🎬 [STAGE DIRECTION]: Transition to Module 3—kernel engineering with XProf, Pallas, and the `autokernel` library.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Once I have an adapted model, how do I make it run as fast as the TPU hardware allows? Welcome to Stage 2: AutoKernel Lab and the `autokernel` package. Here I use the PyTorch TPU profiler (`ProfilerActivity.TPU`) and XProf to inspect the hardware timeline across four execution modes, and then write custom Pallas kernels that fuse memory-bound operations inside on-chip TPU Vector Memory (VMEM).\""
        ),
    },
    {
        "num": 14,
        "type": "four_steps",
        "module": "Module 3 • The 4 Execution Modes on TPU",
        "time": "00:38 – 00:42 (4m)",
        "title": "Benchmarking 4 Execution Modes on a 4-Layer Decoder Stack",
        "subtitle": "Shape (8, 1024, 2048) bfloat16 on Cloud TPU (tpu7x Chip 0)",
        "intro": "I benchmarked a 4-layer Qwen3/Llama SwiGLU decoder stack across all four `torch_tpu` execution gears and counted the dispatched TPU programs per step in XProf:",
        "steps": [
            {
                "num": "1",
                "title": "Eager Mode\n3.591 ms (1.00x)",
                "body": "47 separate TPU programs/step! Every add, square, mean, rsqrt, and silu round-trips to HBM.",
                "highlight": False,
            },
            {
                "num": "2",
                "title": "DeferAndFuse\n2.126 ms (1.69x)",
                "body": "TORCH_TPU_DEFER_AND_FUSE=1 clusters ops between sync points into 3 TPU programs/step.",
                "highlight": False,
            },
            {
                "num": "3",
                "title": "torch.compile\n1.579 ms (2.28x)",
                "body": "TorchDynamo + XLA whole-graph compilation fuses the entire 4-layer stack into 1 TPU program.",
                "highlight": True,
            },
            {
                "num": "4",
                "title": "Pallas Kernels\n2.224 ms (1.61x)",
                "body": "1 TPU program/step; isolated 8-layer pallas::fused_res_rmsnorm achieves 0.409 ms vs 2.587 ms eager (6.32x)!",
                "highlight": True,
            },
        ],
        "notes": (
            "🎬 [STAGE DIRECTION]: Walk through the 4 cards from left to right, emphasizing the XProf program count drop (`47 -> 3 -> 1 -> 1`).\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Look at the progression across the four cards. In plain Eager mode, a 4-layer decoder block takes `3.591 ms` because it launches 47 separate TPU programs per step—every elementwise op reads and writes HBM. Turning on `TORCH_TPU_DEFER_AND_FUSE=1` cuts that to 3 TPU programs and `2.126 ms` (`1.69x`). `torch.compile(backend='tpu')` captures the whole graph into 1 TPU program at `1.579 ms` (`2.28x`). And with `torch.tpu.pallas.jax_op`, my custom Pallas kernels execute in 1 TPU program with `9.54e-07` numerical parity—and on the isolated 8-layer Residual+RMSNorm stack, Pallas hits `0.409 ms` versus `2.587 ms` eager: a `6.32x` kernel speedup!\""
        ),
    },
    {
        "num": 15,
        "type": "checkpoint_visual",
        "module": "Module 3 • XProf Timeline & Pallas Parity",
        "time": "00:42 – 00:46 (4m)",
        "title": "Inside the XProf Trace: 47 Dispatches vs. 1 Fused Program",
        "bullets": [
            ("Why Eager Mode Fragments the Timeline", "In the top row of the XProf waterfall, 47 tiny `xla_Launch` ops leave gaps between kernels and waste HBM bandwidth."),
            ("In-VMEM Pallas Fusion (`pallas::fused_res_rmsnorm`)", "Tiles `(128, D)` blocks into TPU VMEM, accumulates `r * r` in `float32`, applies `rsqrt`, and writes normalized `bfloat16` outputs in one DMA pass."),
            ("In-VMEM SwiGLU (`pallas::fused_swiglu`)", "Computes `(gate * sigmoid(gate)) * up` entirely in VMEM registers (`max_abs_diff = 4.77e-07`, `0.0` in `bfloat16`)."),
            ("6.32x Isolated Kernel Speedup", "Across 8 stacked Residual+RMSNorm layers on `(8, 1024, 2048)`, Pallas drops latency from `2.587 ms` to `0.409 ms`."),
        ],
        "screenshot": "autokernel_xprof_waterfall.png",
        "caption": "XProf TPU Execution Timelines & Speedup Comparison Across Eager, DeferAndFuse, torch.compile, and Pallas",
        "notes": (
            "🎬 [STAGE DIRECTION]: Click `autokernel_xprof_waterfall.png` to zoom in on the 4-row XProf waterfall chart.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"This visualization from `autokernel_lab.py` makes the hardware story unmistakable. Look at the right panel: in Eager mode, the TPU timeline is chopped into 47 micro-launches totaling `3.59 ms`. With `DeferAndFuse`, `torch.compile`, and `Pallas`, the timeline collapses into a tight, continuous block on the MXU and VPU. Even better, Pallas gives me explicit control over VMEM tiling (`BlockSpec((128, d), lambda i: (i, 0))`) and `float32` accumulation precision.\""
        ),
    },
    {
        "num": 16,
        "type": "code_split",
        "module": "Module 3 • How autokernel Hot-Patches Hugging Face",
        "time": "00:46 – 00:50 (4m)",
        "title": "How `autokernel` Replaces 5 HBM Trips & Patches 73 HF Submodules",
        "subtitle": "Single-DMA VMEM Tile Fusion + Zero-Copy In-Memory Surgery",
        "intro": "I packaged the entire Pallas kernel registry, tile-size solver, and Hugging Face surgical patcher into `autokernel`:",
        "bullets": [
            ("Why Eager RMSNorm Hurts (5 HBM Round-Trips)", "Eager `RMSNorm` bounces `x`, `x^2`, `var`, `x*rsqrt`, and `y*w` to off-chip HBM 5 times per layer (`245` HBM round-trips across 49 norms!)."),
            ("1-DMA VMEM Tile Fusion (`autokernel`)", "Streams `(B_tile, D)` into on-chip VMEM once, fuses `cast -> x^2 -> mean -> rsqrt -> * weight` in VPU registers, and writes back once."),
            ("Zero-Copy 73-Submodule HF Patch (`10/10 pytest`)", "`autokernel.patch_hf(model)` swaps 49 `RMSNorm` + 24 `SwiGLU` modules in memory (`0` weight bytes copied): `5.47x` 24L Norm speedup & `1.21x` full-model speedup!"),
        ],
        "code_title": "autokernel — 3-Line Reusable HF Model Patcher",
        "code": (
            "import autokernel\n\n"
            "# 1. Isolate Chip 0 & wake up torch_tpu BEFORE JAX loads\n"
            "autokernel.init_tpu(chip=0, defer_and_fuse=True)\n\n"
            "# 2. Hot-swap 49 RMSNorm + 24 SwiGLU MLP layers in memory\n"
            "report = autokernel.patch_hf(merged_model)\n"
            "print(report.total_patched)  # -> 73 (0 weight bytes copied)\n\n"
            "# 3. Verify speedup, max_abs_diff, and top-1 agreement\n"
            "bench = autokernel.verify_parity_and_speedup(\n"
            "    stock_fn, patched_fn, sample_input\n"
            ")\n"
            "# Reversible anytime: autokernel.unpatch_hf(merged_model)"
        ),
        "screenshot": "00-autokernel-how-it-works.gif",
        "notes": (
            "🎬 [STAGE DIRECTION]: Walk through the 3-line `autokernel` snippet on the top right and click the animated mechanism diagram below it to open the full-screen lightbox!\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Look at how `autokernel` works under the hood. In stock eager PyTorch, a single RMSNorm layer executes 5 separate operators that read and write off-chip HBM 5 times—across 49 RMSNorms in Qwen2.5-0.5B, that is 245 off-chip HBM round-trips per forward pass! With `autokernel`, I tile the batch dimension via `solve_tile_size(N)`, DMA each `(128, 896)` block into on-chip VMEM once, fuse the entire `float32` variance reduction and weight scaling inside VPU registers, and DMA the `bfloat16` output back once. Calling `autokernel.patch_hf(merged_model)` swaps all 73 `RMSNorm` and `SwiGLU` submodules in memory without copying a single weight byte—delivering a `4.81x` to `5.47x` 24-layer RMSNorm speedup and a `1.21x` end-to-end Transformer speedup with `99.74%` top-1 token agreement!\""
        ),
    },
    {
        "num": 17,
        "type": "checkpoint_visual",
        "module": "Module 4 • SpecGuard TPU Serving & Audit",
        "time": "00:50 – 00:55 (5m)",
        "title": "Stage 3: SpecGuard TPU — SGLang Prefix Cache & 16-File Burst",
        "bullets": [
            ("Serving the Merged LoRA Checkpoint on TPU", "Launched `sglang.launch_server --model-path /tmp/specguard-qwen3-0.6b-merged --device tpu --tp-size 1 --enable-torch-compile --enable-cache-report`."),
            ("RadixAttention Prefix Cache (`2.46x` Warm TTFT Speedup)", "Pass 1 (Cold Cache) prefills a ~1,357-token shared SecOps/PCI-DSS policy & AST header in `102.86 ms`. Pass 2 & Pass 3 hit `1,280` cached tokens in TPU HBM, slashing TTFT to `41.80 ms` (`2.46x` faster)!"),
            ("16-File Concurrent Continuous Batching Burst", "Auditing 16 repository chunks concurrently completes in `2.05 s` wall time (`226.8 chunks/s` throughput, `64.5 ms` median per-request TTFT)."),
        ],
        "screenshot": "specguard_dashboard.png",
        "caption": "SpecGuard TPU End-to-End Dashboard: LoRA Loss Curve, SGLang Prefix Cache TTFT (2.46x), and 16-File Concurrent Burst",
        "notes": (
            "🎬 [STAGE DIRECTION]: Click `specguard_dashboard.png` to show the 3-panel SpecGuard TPU results.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Now let's complete the story in Stage 3: serving our merged checkpoint in production with `sglang-torchtpu`. In a real repository or payment compliance audit, every query shares a long prefix—our organization's security rubric, PCI-DSS / TorchTPU rule definitions, and shared AST header (~1,357 tokens). On Pass 1 (Cold Cache), SGLang computes the prefill in `102.86 ms`. On Pass 2 and Pass 3, SGLang's RadixAttention matches `1,280` prefix tokens directly in TPU HBM KV cache, dropping Time-to-First-Token to `41.80 ms`—a `2.46x` TTFT speedup! And when a pull request triggers a 16-file concurrent burst, continuous batching processes all 16 audits in just `2.05 seconds`!\""
        ),
    },
    {
        "num": 18,
        "type": "stepper_split",
        "module": "Module 4 • The Engineering Adoption Playbook",
        "time": "00:55 – 00:58 (3m)",
        "title": "How Engineering Teams Adopt This Stack in 3 Steps",
        "steps": [
            ("1", "Connect & Install (`tpu-agent-suite` + `autokernel`)", "pip install -e ./autokernel && pytest"),
            ("2", "Adapt & Patch (`torch_tpu` + `peft` + `autokernel`)", "python domain_adapt_and_pallas_patch.py"),
            ("3", "Serve & Audit (`sglang` / `vllm` on TPU)", "python stage2_serve_and_audit.py"),
        ],
        "callout_badge": "PRODUCTION CHECKLIST",
        "callout_title": "Key Rules for Reliable TPU Deployments",
        "callout_body": (
            "1. Always isolate single-chip jobs with autokernel.init_tpu(chip=0) so torch_tpu acquires PJRT before JAX loads.\n"
            "2. Pad training & batch-scoring inputs to static buckets (128, 256, 1024) to eliminate XLA recompilation.\n"
            "3. Structure multi-turn / multi-file prompts with a shared static prefix so SGLang RadixAttention caches 90%+ of prefill tokens."
        ),
        "code_title": "End-to-End Reproduction Commands",
        "code": (
            "# 0. Install & test reusable autokernel package (10/10 PASS)\n"
            "pip install -e ./autokernel && pytest autokernel/tests/\n\n"
            "# 1. Run 4-way AutoKernel Lab (Eager / DAF / Compile / Pallas)\n"
            "python demos/06_autokernel_app/autokernel_lab.py all\n\n"
            "# 2. Run Multi-Model Domain LoRA + 73-Submodule Pallas Patching\n"
            "python demos/07_domain_adaptation_showcase/domain_adapt_and_pallas_patch.py\n\n"
            "# 3. Run SpecGuard LoRA + SGLang Prefix Cache & 16-File Burst\n"
            "python demos/05_specguard_app/stage2_serve_and_audit.py"
        ),
        "notes": (
            "🎬 [STAGE DIRECTION]: Summarize the 3-step adoption path for PayPal engineering teams.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"To bring this exact workflow into your service tomorrow, here is the 3-step playbook. Step 1: install `autokernel` (`pip install -e ./autokernel`) and connect `tpu-agent-suite` and `colab-mcp` to your TPU pod. Step 2: run static-shape `bfloat16` LoRA adaptation on `torch.device('tpu')` and call `autokernel.patch_hf(model)` to fuse memory-bound RMSNorm and SwiGLU ops in VMEM. Step 3: serve the merged checkpoint with `sglang-torchtpu` or `vllm-torchtpu` with RadixAttention prefix caching enabled.\""
        ),
    },
    {
        "num": 19,
        "type": "objectives_card",
        "module": "Module 4 • Summary of Empirical Benchmarks",
        "time": "00:58 – 01:00 (2m)",
        "title": "Executive Summary: Verified Cloud TPU (`tpu7x`) Results",
        "intro": "Every metric across our three showcase applications and `autokernel` test suite was measured live on Cloud TPU (`tpu7x` Chip 0):",
        "bullets": [
            ("Multi-Model Domain LoRA Adaptation", "`Qwen/Qwen3-0.6B` (SecOps/TPU) loss `2.8536 -> 0.0118` (PPL `17.35 -> 1.01`, `181.7 ms/step`); `Qwen/Qwen2.5-0.5B-Instruct` (FinTech PCI-DSS v4.0) loss `3.9182 -> 0.0021` (PPL `50.31 -> 1.00`, `105.2 ms/step`)."),
            ("AutoKernel Lab (4-Layer Decoder Stack)", "Eager `3.591 ms` (47 TPU progs) -> `DeferAndFuse` `2.126 ms` (`1.69x`, 3 progs) -> `torch.compile` `1.579 ms` (`2.28x`, 1 prog) -> `Pallas` `2.224 ms` (1 prog, `6.32x` isolated 8-layer RMSNorm speedup: `0.409 ms` vs `2.587 ms`)."),
            ("`autokernel` 73-Submodule HF Patching (`10/10 pytest`)", "Hot-patching 73 `RMSNorm` + `SwiGLU MLP` submodules in `Qwen2.5-0.5B` delivers `4.81x - 5.47x` 24-layer RMSNorm speedup and `1.21x` full-model speedup (`29.74 ms -> 24.66 ms`) with `99.74%` top-1 token agreement and `0` weight bytes copied."),
            ("SpecGuard SGLang Serving & Burst", "RadixAttention prefix cache cuts TTFT from `102.86 ms` (Cold) to `41.80 ms` (Warm, `2.46x` speedup, `1,280` cached tokens); 16-file concurrent burst finishes in `2.05 s` (`226.8 chunks/s`)."),
        ],
        "notes": (
            "🎬 [STAGE DIRECTION]: Leave this executive summary card up for a moment so attendees can capture the complete benchmark table.\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Here is the complete scoreboard from my live runs on `tpu7x` Chip 0. Across two model families and two compliance domains, perplexity collapsed to `~1.00` in under 40 steps; my `autokernel` Pallas library delivered `4.81x` to `6.32x` operator speedups and a `1.21x` full-model forward-pass speedup inside Hugging Face; and SGLang RadixAttention delivered a `2.46x` Warm TTFT speedup while auditing 16 concurrent files in `2.05 seconds`.\""
        ),
    },
    {
        "num": 20,
        "type": "thank_you",
        "module": "Module 4 • Wrap-Up & Q&A",
        "time": "01:00 – 01:05 (5m)",
        "title": "Thank You!",
        "subtitle": "Rabimba Karanjai\nAI Systems & Cloud Accelerator Engineering • PayPal\nGoogle Developer Expert (AI/ML)\ngithub.com/rabimba/GDE-ML-Artifacts",
        "qr_top": "qr_codelab.png",
        "qr_top_label": "Master TPU Notebooks",
        "qr_mid": "qr_linkedin.png",
        "qr_mid_label": "Connect on LinkedIn",
        "qr_bottom": "qr_rabimba_github.png",
        "qr_bottom_label": "GitHub Repo & autokernel",
        "notes": (
            "🎬 [STAGE DIRECTION]: Thank the team and open the floor for engineering questions!\n\n"
            "🗣️ SAY VERBATIM:\n"
            "\"Thank you all for joining! Scan the QR codes on the right to grab the master Colab notebooks, the pip-installable `autokernel` package, and this slide deck. What questions can I answer about running PyTorch, LoRA, Pallas kernels, or SGLang on Cloud TPU?\""
        ),
    },
]


# ---------------------------------------------------------------------------
# PART 1: BUILD EDITABLE POWERPOINT (.PPTX) FROM REFERENCE TEMPLATE
# ---------------------------------------------------------------------------
def clear_slide_shapes(slide):
    for sh in list(slide.shapes):
        sp = sh._element
        sp.getparent().remove(sp)


def set_slide_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text


def add_textbox(slide, left, top, width, height, text, font_size=14, bold=False, color=(32, 33, 36), font_name="Google Sans", align=PP_ALIGN.LEFT, word_wrap=True):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)
    return tb


def add_rounded_box(slide, left, top, width, height, fill_rgb=None, line_rgb=None, line_pt=1.5, radius=0.04):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    if sh.adjustments and len(sh.adjustments) > 0:
        sh.adjustments[0] = radius
    if fill_rgb is not None:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor(*fill_rgb)
    else:
        sh.fill.background()
    if line_rgb is not None:
        sh.line.color.rgb = RGBColor(*line_rgb)
        sh.line.width = Pt(line_pt)
    else:
        sh.line.fill.background()
    return sh


def add_terminal_box(slide, left, top, width, height, title_text, code_text, font_size=9.5):
    # Dark container
    add_rounded_box(slide, left, top, width, height, fill_rgb=(32, 33, 36), line_rgb=(60, 64, 67), line_pt=1, radius=0.03)
    # macOS traffic light dots
    dot_colors = [(234, 67, 53), (251, 188, 4), (52, 168, 83)]
    for idx, dc in enumerate(dot_colors):
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(left + 0.16 + idx * 0.18),
            Inches(top + 0.13),
            Inches(0.11),
            Inches(0.11),
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = RGBColor(*dc)
        dot.line.fill.background()
    if title_text:
        add_textbox(
            slide,
            left + 0.72,
            top + 0.06,
            width - 0.85,
            0.25,
            title_text,
            font_size=8.5,
            bold=True,
            color=(154, 160, 166),
            font_name="Roboto Mono",
            align=PP_ALIGN.LEFT,
        )
    add_textbox(
        slide,
        left + 0.14,
        top + 0.34,
        width - 0.28,
        height - 0.42,
        code_text,
        font_size=font_size,
        bold=False,
        color=(232, 234, 237),
        font_name="Roboto Mono",
    )


def add_bullet_list_box(slide, left, top, width, height, intro, bullets, intro_size=11.5, bullet_size=10.5):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    first = True
    if intro:
        p = tf.paragraphs[0]
        first = False
        p.space_after = Pt(8)
        r = p.add_run()
        r.text = intro
        r.font.name = "Google Sans"
        r.font.size = Pt(intro_size)
        r.font.color.rgb = RGBColor(60, 64, 67)
    for b_title, b_body in bullets:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(6)
        r1 = p.add_run()
        r1.text = f"• {b_title}: "
        r1.font.name = "Google Sans"
        r1.font.size = Pt(bullet_size)
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(0, 48, 135)
        r2 = p.add_run()
        r2.text = b_body
        r2.font.name = "Google Sans"
        r2.font.size = Pt(bullet_size)
        r2.font.color.rgb = RGBColor(16, 24, 40)
    return tb


def add_image_fit(slide, img_path, left, top, max_w, max_h):
    from PIL import Image
    actual_name = img_path
    if img_path == "00-autokernel-how-it-works.gif" and os.path.exists(os.path.join(ASSETS_DIR, "autokernel_how_it_works_static.png")):
        actual_name = "autokernel_how_it_works_static.png"
    full_path = os.path.join(ASSETS_DIR, actual_name)
    if not os.path.exists(full_path):
        return
    with Image.open(full_path) as im:
        w_px, h_px = im.size
    aspect = w_px / float(h_px)
    box_aspect = max_w / float(max_h)
    if aspect >= box_aspect:
        w = max_w
        h = max_w / aspect
    else:
        h = max_h
        w = max_h * aspect
    x = left + (max_w - w) / 2.0
    y = top + (max_h - h) / 2.0
    slide.shapes.add_picture(full_path, Inches(x), Inches(y), Inches(w), Inches(h))


def add_paypal_top_stripe(slide):
    """Draws the 4-segment PayPal signature brand bar across the top of the slide."""
    segments = [
        (0.00, 3.80, (0, 48, 135)),    # PayPal Deep Navy #003087
        (3.80, 3.20, (0, 112, 186)),   # PayPal Blue #0070BA
        (7.00, 1.85, (0, 156, 222)),   # PayPal Cyan #009CDE
        (8.85, 1.15, (255, 196, 57)),  # PayPal Gold #FFC439
    ]
    for sx, sw, rgb in segments:
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(sx), Inches(0.0), Inches(sw), Inches(0.065))
        bar.fill.solid()
        bar.fill.fore_color.rgb = RGBColor(*rgb)
        bar.line.fill.background()


def add_paypal_standard_chrome(slide, sdata):
    """Adds PayPal header logo, module pill, confidentiality badge, and footer lockup."""
    add_paypal_top_stripe(slide)
    add_image_fit(slide, "logo_paypal_header.png", 0.42, 0.14, 2.35, 0.36)
    mod_text = f"{sdata.get('module', '')} • {sdata.get('time', '')}"
    add_rounded_box(slide, 3.10, 0.16, 4.15, 0.30, fill_rgb=(235, 244, 255), line_rgb=(0, 112, 186), line_pt=0.8, radius=0.45)
    add_textbox(slide, 3.15, 0.18, 4.05, 0.25, mod_text, font_size=8.5, bold=True, color=(0, 48, 135), align=PP_ALIGN.CENTER)
    add_textbox(slide, 7.35, 0.19, 2.25, 0.24, "PayPal Internal • AI Engineering", font_size=8.5, bold=True, color=(108, 115, 127), align=PP_ALIGN.RIGHT)
    add_image_fit(slide, "logo_paypal_footer.png", 0.42, 5.28, 4.20, 0.24)
    add_textbox(slide, 8.50, 5.28, 1.10, 0.24, f"Slide {sdata['num']} / {len(SLIDES_DATA)}", font_size=8.5, bold=True, color=(0, 48, 135), align=PP_ALIGN.RIGHT)


def build_pptx(output_path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(10.0)
    prs.slide_height = Inches(5.625)
    blank_layout = prs.slide_layouts[6]

    for sdata in SLIDES_DATA:
        stype = sdata["type"]
        slide = prs.slides.add_slide(blank_layout)

        if stype == "cover":
            add_paypal_top_stripe(slide)
            add_image_fit(slide, "bg_paypal_cover.png", 5.05, 0.065, 4.95, 5.56)
            add_image_fit(slide, "logo_paypal_header.png", 0.45, 0.32, 2.95, 0.45)
            add_rounded_box(slide, 0.45, 1.15, 3.35, 0.36, fill_rgb=(235, 244, 255), line_rgb=(0, 112, 186), line_pt=1.2, radius=0.45)
            add_textbox(slide, 0.50, 1.19, 3.25, 0.28, sdata.get("badge", "PayPal AI Showcase"), font_size=10.5, bold=True, color=(0, 48, 135), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.65, 4.55, 2.15, sdata["title"], font_size=25, bold=True, color=(0, 28, 100))
            # Gold accent bar under title
            gbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.45), Inches(3.86), Inches(1.35), Inches(0.06))
            gbar.fill.solid()
            gbar.fill.fore_color.rgb = RGBColor(255, 196, 57)
            gbar.line.fill.background()
            add_textbox(slide, 0.45, 4.02, 4.50, 0.80, sdata["subtitle"], font_size=12, bold=False, color=(60, 64, 67))
            add_textbox(slide, 0.45, 4.92, 4.50, 0.35, "Rabimba Karanjai • AI Systems & Cloud Accelerator Engineering", font_size=10.5, bold=True, color=(0, 112, 186))

        elif stype == "big_qr":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.50, 0.55, 9.00, 0.52, sdata["title"], font_size=26, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            add_rounded_box(slide, 3.42, 1.12, 3.16, 2.82, fill_rgb=(255, 255, 255), line_rgb=(0, 112, 186), line_pt=1.5, radius=0.03)
            add_image_fit(slide, sdata["qr"], 3.56, 1.25, 2.88, 2.55)
            add_textbox(slide, 0.50, 4.02, 9.00, 0.40, sdata["url_text"], font_size=19, bold=True, color=(0, 112, 186), align=PP_ALIGN.CENTER)
            add_textbox(slide, 1.30, 4.46, 7.40, 0.55, sdata["desc"], font_size=10, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "qr_hub":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.50, 0.55, 9.00, 0.48, sdata["title"], font_size=25, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.50, 1.03, 9.00, 0.32, sdata["subtitle"], font_size=12.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            ncards = len(sdata["cards"])
            cw = 2.80 if ncards <= 3 else 2.16
            step = 3.05 if ncards <= 3 else 2.31
            qrsz = 1.82 if ncards <= 3 else 1.35
            for idx, c in enumerate(sdata["cards"]):
                cx = 0.55 + idx * step
                add_rounded_box(slide, cx, 1.45, cw, 3.68, fill_rgb=(245, 247, 250), line_rgb=(0, 112, 186), line_pt=1.4, radius=0.04)
                add_textbox(slide, cx + 0.12, 1.58, cw - 0.24, 0.42, c["title"], font_size=13 if ncards <= 3 else 11.5, bold=True, color=(0, 48, 135))
                add_textbox(slide, cx + 0.12, 2.00, cw - 0.24, 0.34, c["url_text"], font_size=9.5 if ncards <= 3 else 8.5, bold=True, color=(0, 112, 186))
                add_textbox(slide, cx + 0.12, 2.36, cw - 0.24, 0.85, c["desc"], font_size=9.5 if ncards <= 3 else 8.2, bold=False, color=(60, 64, 67))
                add_image_fit(slide, c["qr"], cx + (cw - qrsz) / 2.0, 5.02 - qrsz, qrsz, qrsz)

        elif stype == "speaker":
            add_paypal_top_stripe(slide)
            add_image_fit(slide, "bg_paypal_speaker.png", 0.0, 0.065, 4.65, 5.56)
            add_image_fit(slide, "logo_paypal_header.png", 4.75, 0.30, 2.65, 0.40)
            add_image_fit(slide, sdata["photo"], 0.65, 1.15, 3.45, 3.45)
            add_textbox(slide, 4.75, 1.45, 4.75, 1.35, sdata["title"], font_size=38, bold=True, color=(0, 28, 100))
            add_textbox(slide, 4.75, 2.95, 4.75, 1.25, sdata["subtitle"], font_size=16.5, bold=True, color=(0, 112, 186))
            add_image_fit(slide, "logo_paypal_footer.png", 4.75, 5.22, 4.20, 0.24)

        elif stype == "thank_you":
            add_paypal_top_stripe(slide)
            add_image_fit(slide, "bg_paypal_speaker.png", 0.0, 0.065, 4.55, 5.56)
            add_image_fit(slide, "logo_paypal_header.png", 4.75, 0.30, 2.65, 0.40)
            add_textbox(slide, 4.75, 1.75, 3.30, 1.05, sdata["title"], font_size=42, bold=True, color=(0, 28, 100))
            add_textbox(slide, 4.75, 2.85, 3.30, 1.35, sdata["subtitle"], font_size=13, bold=False, color=(60, 64, 67))
            qrs = [(sdata["qr_top"], sdata["qr_top_label"])]
            if sdata.get("qr_mid"):
                qrs.append((sdata["qr_mid"], sdata["qr_mid_label"]))
            qrs.append((sdata["qr_bottom"], sdata["qr_bottom_label"]))
            geom = [(8.25, 0.28, 1.22, 1.52), (8.25, 2.02, 1.22, 3.26), (8.25, 3.76, 1.22, 5.00)]
            for (qimg, qlabel), (qx, qy, qs, ly) in zip(qrs, geom):
                add_image_fit(slide, qimg, qx, qy, qs, qs)
                add_textbox(slide, 7.70, ly, 2.35, 0.45, qlabel, font_size=8, bold=True, color=(0, 48, 135), align=PP_ALIGN.CENTER)

        elif stype == "section_poll":
            add_paypal_standard_chrome(slide, sdata)
            add_image_fit(slide, sdata["icon"], 4.62, 0.65, 0.72, 0.72)
            add_textbox(slide, 0.80, 1.42, 8.40, 0.95, sdata["title"], font_size=25, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            poll = sdata["poll"]
            add_rounded_box(slide, 0.75, 2.52, 8.50, 2.52, fill_rgb=(235, 244, 255), line_rgb=(0, 112, 186), line_pt=2, radius=0.04)
            add_textbox(slide, 0.95, 2.62, 8.10, 0.58, poll["question"], font_size=12, bold=True, color=(0, 48, 135))
            opts_text = "\n".join(f"• {o}" for o in poll["options"])
            add_textbox(slide, 1.05, 3.24, 7.90, 0.95, opts_text, font_size=10.5, bold=False, color=(16, 24, 40))
            add_textbox(slide, 0.95, 4.30, 8.10, 0.62, f"💡 Key Takeaway: {poll['answer']}", font_size=10.2, bold=True, color=(11, 128, 67))

        elif stype == "agent_triad":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.95, 0.75, 8.10, 1.85, sdata["headline"], font_size=22, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            coords = [(0.45, 3.15, 2.75, 1.85), (3.55, 3.15, 2.90, 1.85), (6.80, 3.15, 2.75, 1.85)]
            for idx, box in enumerate(sdata["boxes"]):
                bx, by, bw, bh = coords[idx]
                is_mid = idx == 1
                add_rounded_box(slide, bx, by, bw, bh, fill_rgb=(235, 244, 255) if is_mid else (245, 247, 250), line_rgb=(0, 112, 186) if is_mid else (200, 210, 225), line_pt=2.2 if is_mid else 1.5, radius=0.05)
                add_image_fit(slide, box["icon"], bx + bw / 2 - 0.35, by - 0.35, 0.70, 0.70)
                add_textbox(slide, bx + 0.12, by + 0.45, bw - 0.24, 1.15, box["label"], font_size=17, bold=True, color=(0, 48, 135), align=PP_ALIGN.CENTER)

        elif stype == "objectives_card":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.45, 0.65, 9.10, 0.50, sdata["title"], font_size=24, bold=True, color=(0, 28, 100))
            add_rounded_box(slide, 0.45, 1.25, 9.10, 3.82, fill_rgb=(255, 255, 255), line_rgb=(0, 112, 186), line_pt=2.5, radius=0.04)
            add_bullet_list_box(slide, 0.68, 1.40, 8.64, 3.50, sdata["intro"], sdata["bullets"], intro_size=12, bullet_size=10.5)

        elif stype == "arch_split":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.45, 0.64, 9.10, 0.48, sdata["title"], font_size=24, bold=True, color=(0, 28, 100))
            add_textbox(slide, 0.45, 1.16, 4.45, 0.34, sdata["subtitle"], font_size=13, bold=True, color=(0, 112, 186))
            add_bullet_list_box(slide, 0.45, 1.55, 4.35, 3.55, sdata["intro"], sdata["bullets"], intro_size=10.5, bullet_size=10)
            add_image_fit(slide, sdata["image"], 4.88, 1.20, 4.75, 3.85)

        elif stype == "three_tech":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 1.50, 0.72, 7.00, 0.50, sdata["title"], font_size=22, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            for idx, col in enumerate(sdata["cols"]):
                cx = 0.75 + idx * 2.95
                add_rounded_box(slide, cx, 1.48, 2.65, 3.55, fill_rgb=(245, 247, 250), line_rgb=(0, 112, 186), line_pt=1.2, radius=0.04)
                add_image_fit(slide, col["icon"], cx + 0.18, 1.65, 0.68, 0.68)
                add_textbox(slide, cx + 0.16, 2.45, 2.33, 0.62, col["title"], font_size=13.5, bold=True, color=(0, 48, 135))
                add_textbox(slide, cx + 0.16, 3.12, 2.33, 1.60, col["body"], font_size=10.5, bold=False, color=(60, 64, 67))

        elif stype == "two_cards_quiz":
            add_paypal_standard_chrome(slide, sdata)
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (0, 112, 186) if card["color"] == "blue" else (217, 48, 37)
                add_rounded_box(slide, cx, 0.68, 4.40, 3.38, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 0.80, 4.04, 0.36, card["title"], font_size=15, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.16, 4.04, 0.28, card["subtitle"], font_size=10.2, bold=True, color=(95, 99, 104))
                add_bullet_list_box(slide, cx + 0.16, 1.48, 4.08, 2.45, None, card["items"], bullet_size=9.8)
            quiz = sdata["quiz"]
            add_rounded_box(slide, 0.48, 4.18, 9.04, 0.94, fill_rgb=(255, 248, 225), line_rgb=(255, 196, 57), line_pt=1.8, radius=0.03)
            add_textbox(slide, 0.64, 4.22, 8.72, 0.42, quiz["question"], font_size=9.8, bold=True, color=(0, 48, 135))
            add_textbox(slide, 0.64, 4.64, 8.72, 0.42, quiz["answer"], font_size=9.5, bold=False, color=(16, 24, 40))

        elif stype == "lab_divider":
            add_paypal_standard_chrome(slide, sdata)
            add_rounded_box(slide, 0.85, 1.45, 8.30, 2.75, fill_rgb=(235, 244, 255), line_rgb=(0, 112, 186), line_pt=2.2, radius=0.05)
            add_textbox(slide, 1.10, 1.85, 7.80, 0.80, sdata["title"], font_size=34, bold=True, color=(0, 28, 100), align=PP_ALIGN.CENTER)
            add_image_fit(slide, "paypal_monogram_badge.png", 1.55, 2.85, 0.48, 0.48)
            add_textbox(slide, 2.15, 2.88, 6.50, 0.50, sdata["subtitle"], font_size=15.5, bold=True, color=(0, 112, 186))

        elif stype == "code_split":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.48, 0.62, 9.04, 0.46, sdata["title"], font_size=21, bold=True, color=(0, 28, 100))
            add_textbox(slide, 0.48, 1.10, 4.40, 0.30, sdata["subtitle"], font_size=11.8, bold=True, color=(0, 112, 186))
            add_bullet_list_box(slide, 0.48, 1.44, 4.35, 3.65, sdata.get("intro"), sdata["bullets"], intro_size=10, bullet_size=9.5)
            if sdata.get("screenshot"):
                add_terminal_box(slide, 4.98, 1.12, 4.58, 2.12, sdata["code_title"], sdata["code"], font_size=8.2)
                add_image_fit(slide, sdata["screenshot"], 4.98, 3.32, 4.58, 1.82)
            else:
                add_terminal_box(slide, 4.98, 1.12, 4.58, 3.95, sdata["code_title"], sdata["code"], font_size=8.8)

        elif stype == "stepper_split":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.55, 0.64, 8.90, 0.48, sdata["title"], font_size=23, bold=True, color=(0, 28, 100))
            add_rounded_box(slide, 0.55, 1.24, 4.10, 3.85, fill_rgb=(245, 247, 250), line_rgb=(0, 112, 186), line_pt=1.5, radius=0.04)
            for idx, (snum, stitle, sdesc) in enumerate(sdata["steps"]):
                sy = 1.48 + idx * 1.18
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.78), Inches(sy), Inches(0.42), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(0, 48, 135)
                pill.line.fill.background()
                add_textbox(slide, 0.78, sy + 0.06, 0.42, 0.30, snum, font_size=11, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)
                add_textbox(slide, 1.32, sy - 0.04, 3.15, 0.30, stitle, font_size=12, bold=True, color=(0, 28, 100))
                add_textbox(slide, 1.32, sy + 0.24, 3.15, 0.45, sdesc, font_size=9.8, bold=False, color=(0, 112, 186), font_name="Roboto Mono")
            add_rounded_box(slide, 4.88, 1.24, 4.64, 1.65, fill_rgb=(255, 255, 255), line_rgb=(0, 112, 186), line_pt=1.2, radius=0.04)
            add_rounded_box(slide, 5.06, 1.36, 2.65, 0.26, fill_rgb=(255, 196, 57), line_rgb=None, radius=0.3)
            add_textbox(slide, 5.10, 1.38, 2.55, 0.22, sdata["callout_badge"], font_size=8, bold=True, color=(0, 28, 100))
            add_textbox(slide, 5.06, 1.66, 4.30, 0.30, sdata["callout_title"], font_size=12, bold=True, color=(0, 28, 100))
            add_textbox(slide, 5.06, 1.96, 4.30, 0.85, sdata["callout_body"], font_size=9.2, bold=False, color=(60, 64, 67))
            add_terminal_box(slide, 4.88, 3.00, 4.64, 2.09, sdata["code_title"], sdata["code"], font_size=8.2)

        elif stype == "two_cards_code":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.48, 0.62, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(0, 28, 100))
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (0, 112, 186) if card["color"] == "blue" else (0, 48, 135)
                add_rounded_box(slide, cx, 1.12, 4.40, 4.02, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 1.22, 4.04, 0.34, card["title"], font_size=14.5, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.54, 4.04, 0.26, card["subtitle"], font_size=10, bold=False, color=(95, 99, 104))
                add_terminal_box(slide, cx + 0.18, 1.86, 4.04, 1.72, "snippet / command", card["code"], font_size=8.2)
                add_bullet_list_box(slide, cx + 0.16, 3.64, 4.08, 1.40, None, card["bullets"], bullet_size=9.5)

        elif stype == "checkpoint_visual":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.48, 0.64, 9.04, 0.48, sdata["title"], font_size=20.5, bold=True, color=(0, 28, 100))
            add_bullet_list_box(slide, 0.48, 1.22, 4.35, 3.85, None, sdata["bullets"], bullet_size=10.0)
            add_rounded_box(slide, 4.98, 1.22, 4.55, 3.50, fill_rgb=(245, 247, 250), line_rgb=(0, 112, 186), line_pt=1.8, radius=0.03)
            add_image_fit(slide, sdata["screenshot"], 5.08, 1.32, 4.35, 3.30)
            add_textbox(slide, 4.98, 4.78, 4.55, 0.35, sdata.get("caption", ""), font_size=8.8, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "four_steps":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.52, 0.62, 8.96, 0.46, sdata["title"], font_size=23, bold=True, color=(0, 28, 100))
            add_textbox(slide, 0.52, 1.10, 8.96, 0.30, sdata["subtitle"], font_size=12.5, bold=True, color=(0, 112, 186))
            add_textbox(slide, 0.52, 1.44, 8.96, 0.58, sdata["intro"], font_size=10.8, bold=False, color=(60, 64, 67))
            for idx, st in enumerate(sdata["steps"]):
                sx = 0.52 + idx * 2.28
                is_hi = st.get("highlight", False)
                border_rgb = (0, 112, 186) if is_hi else (200, 210, 225)
                add_rounded_box(slide, sx, 2.18, 2.12, 2.92, fill_rgb=(235, 244, 255) if is_hi else (245, 247, 250), line_rgb=border_rgb, line_pt=2.2 if is_hi else 1.2, radius=0.04)
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(sx + 0.18), Inches(2.36), Inches(0.42), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(0, 48, 135) if is_hi else RGBColor(0, 112, 186)
                pill.line.fill.background()
                add_textbox(slide, sx + 0.18, 2.41, 0.42, 0.32, st["num"], font_size=12, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)
                add_textbox(slide, sx + 0.14, 2.88, 1.84, 0.58, st["title"], font_size=11.5, bold=True, color=(0, 48, 135))
                add_textbox(slide, sx + 0.14, 3.50, 1.84, 1.45, st["body"], font_size=9.5, bold=False, color=(16, 24, 40))

        elif stype == "verification_cards":
            add_paypal_standard_chrome(slide, sdata)
            add_textbox(slide, 0.48, 0.62, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(0, 28, 100))
            lc = sdata["left_card"]
            rc = sdata["right_card"]
            # Left card (PayPal Blue)
            add_rounded_box(slide, 0.48, 1.12, 4.40, 4.02, fill_rgb=(255, 255, 255), line_rgb=(0, 112, 186), line_pt=2.2, radius=0.04)
            add_textbox(slide, 0.68, 1.24, 4.00, 0.35, lc["title"], font_size=14, bold=True, color=(0, 48, 135))
            add_rounded_box(slide, 0.68, 1.66, 4.00, 0.85, fill_rgb=(245, 247, 250), line_rgb=None, radius=0.03)
            add_textbox(slide, 0.80, 1.71, 3.76, 0.25, "Input Snippet:", font_size=10, bold=True, color=(0, 112, 186))
            add_textbox(slide, 0.80, 1.96, 3.76, 0.50, lc["query"], font_size=9.5, bold=False, color=(16, 24, 40))
            add_rounded_box(slide, 0.68, 2.64, 4.00, 2.32, fill_rgb=(235, 244, 255), line_rgb=(0, 112, 186), line_pt=1.2, radius=0.03)
            add_textbox(slide, 0.80, 2.74, 3.76, 0.28, lc["result_title"], font_size=10.5, bold=True, color=(11, 128, 67))
            add_textbox(slide, 0.80, 3.04, 3.76, 1.05, lc["result_body"], font_size=9.5, bold=False, color=(16, 24, 40))
            add_textbox(slide, 0.80, 4.14, 3.76, 0.70, f"Verification Goal: {lc['goal']}", font_size=8.8, bold=False, color=(95, 99, 104))

            # Right card (PayPal Deep Navy / Gold)
            add_rounded_box(slide, 5.12, 1.12, 4.40, 4.02, fill_rgb=(255, 255, 255), line_rgb=(0, 48, 135), line_pt=2.2, radius=0.04)
            add_textbox(slide, 5.32, 1.24, 4.00, 0.35, rc["title"], font_size=14, bold=True, color=(0, 48, 135))
            add_rounded_box(slide, 5.32, 1.66, 4.00, 1.56, fill_rgb=(252, 232, 230), line_rgb=(217, 48, 37), line_pt=1, radius=0.03)
            add_textbox(slide, 5.44, 1.73, 3.76, 0.32, rc["trap1_title"], font_size=9.8, bold=True, color=(197, 34, 31))
            add_textbox(slide, 5.44, 2.05, 3.76, 0.24, rc["trap1_expected"], font_size=9.2, bold=True, color=(11, 128, 67))
            add_textbox(slide, 5.44, 2.31, 3.76, 0.82, rc["trap1_body"], font_size=9.0, bold=False, color=(16, 24, 40))

            add_rounded_box(slide, 5.32, 3.34, 4.00, 1.62, fill_rgb=(255, 248, 225), line_rgb=(255, 196, 57), line_pt=1.2, radius=0.03)
            add_textbox(slide, 5.44, 3.41, 3.76, 0.32, rc["trap2_title"], font_size=9.8, bold=True, color=(0, 48, 135))
            add_textbox(slide, 5.44, 3.73, 3.76, 0.24, rc["trap2_expected"], font_size=9.2, bold=True, color=(11, 128, 67))
            add_textbox(slide, 5.44, 3.99, 3.76, 0.85, rc["trap2_body"], font_size=9.0, bold=False, color=(16, 24, 40))

        set_slide_notes(slide, sdata["notes"])

    prs.save(output_path)
    print(f"Saved PayPal PPTX: {output_path} ({len(prs.slides)} slides)")


# ---------------------------------------------------------------------------
# PART 2: BUILD INTERACTIVE HTML PRESENTATION DECK (index.html)
# ---------------------------------------------------------------------------
def render_slide_inner_html(s):
    stype = s["type"]
    num = s["num"]
    timer_html = ""
    if s.get("timer_seconds"):
        mins = s["timer_seconds"] // 60
        secs = s["timer_seconds"] % 60
        timer_html = f"""
        <div class="lab-timer-widget" data-seconds="{s['timer_seconds']}" id="timer-{num}">
          <span class="timer-label">⏱️ Hands-On Lab Timer:</span>
          <span class="timer-display" id="timer-disp-{num}">{mins:02d}:{secs:02d}</span>
          <button class="timer-btn" onclick="toggleLabTimer({num})">▶ Start / Pause</button>
          <button class="timer-btn secondary" onclick="resetLabTimer({num})">↺ Reset</button>
        </div>
        """

    if stype == "cover":
        title_html = html.escape(s["title"]).replace("\n", "<br/>")
        return f"""
        <div class="slide-canvas slide-cover">
          <div class="pp-top-stripe"></div>
          <img class="gcl-logo" src="assets/logo_paypal_header.png" alt="PayPal AI &amp; Cloud TPU Engineering"/>
          <div class="cover-left">
            <div class="pill-badge">{html.escape(s.get('badge', 'PayPal AI Showcase'))}</div>
            <h1 class="cover-title">{title_html}</h1>
            <div class="pp-gold-bar"></div>
            <p class="cover-subtitle">{html.escape(s['subtitle'])}</p>
            <div class="cover-meta">Rabimba Karanjai • AI Systems &amp; Cloud Accelerator Engineering • PayPal</div>
          </div>
          <div class="cover-right">
            <img src="assets/bg_paypal_cover.png" alt="PayPal Cloud TPU Architecture"/>
          </div>
        </div>
        """

    if stype == "big_qr":
        badge = 'PayPal Internal • AI Engineering'
        wifi_html = ""
        if s.get("wifi_ssid"):
            wifi_html = f"""
            <div class="wifi-chip">Wi-Fi: <strong>{html.escape(s['wifi_ssid'])}</strong> &nbsp;·&nbsp; Password: <code>{html.escape(s['wifi_pass'])}</code></div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">{badge}</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="big-qr-wrap">
            <a href="{html.escape(s['url'])}" target="_blank" class="big-qr-card">
              <img src="assets/{html.escape(s['qr'])}" alt="QR code"/>
            </a>
            <a href="{html.escape(s['url'])}" target="_blank" class="big-qr-link">{html.escape(s['url_text'])}</a>
            <p class="big-qr-desc">{html.escape(s['desc'])}</p>
            {wifi_html}
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "qr_hub":
        cards_html = ""
        for c in s["cards"]:
            cards_html += f"""
            <div class="qr-card">
              <div class="qr-icon-badge">PP</div>
              <h3>{html.escape(c['title'])}</h3>
              <a href="{html.escape(c['url'])}" target="_blank" class="qr-link">{html.escape(c['url_text'])}</a>
              <p>{html.escape(c['desc'])}</p>
              <img class="qr-img" src="assets/{html.escape(c['qr'])}" alt="QR Code"/>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="qr-grid">{cards_html}</div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "speaker":
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="pp-top-stripe"></div>
          <div class="speaker-fan-bg">
            <img src="assets/bg_paypal_speaker.png" alt="PayPal Background"/>
          </div>
          <img class="gcl-logo" style="left:48%; top:4.5%;" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
          <span class="prop-badge-abs">PayPal Internal • AI Engineering</span>
          <div class="speaker-content">
            <div class="speaker-photo-wrap">
              <img src="assets/{html.escape(s['photo'])}" alt="Rabimba Karanjai"/>
            </div>
            <div class="speaker-Bio-text">
              <h1>Rabimba<br/>Karanjai</h1>
              <p class="role-line">AI Systems &amp; Cloud Accelerator Engineering • PayPal</p>
              <p class="role-line">Google Developer Expert — AI &amp; ML</p>
              <div class="speaker-tags">
                <span class="tag-chip">Native PyTorch on TPU</span>
                <span class="tag-chip">autokernel Pallas Fusion</span>
                <span class="tag-chip">PCI-DSS &amp; SecOps Guardrails</span>
              </div>
            </div>
          </div>
        </div>
        """

    if stype == "thank_you":
        mid_html = ""
        if s.get("qr_mid"):
            mid_html = f"""
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_mid'])}" alt="LinkedIn QR"/>
                <span>{html.escape(s['qr_mid_label'])}</span>
              </div>
            """
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="pp-top-stripe"></div>
          <div class="speaker-fan-bg">
            <img src="assets/bg_paypal_speaker.png" alt="PayPal Background"/>
          </div>
          <img class="gcl-logo" style="left:48%; top:4.5%;" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
          <span class="prop-badge-abs">PayPal Internal • AI Engineering</span>
          <div class="thankyou-right">
            <div class="thankyou-text">
              <h1>{html.escape(s['title'])}</h1>
              <p>{html.escape(s['subtitle']).replace(chr(10), '<br/>')}</p>
            </div>
            <div class="thankyou-qrs">
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_top'])}" alt="Codelab QR"/>
                <span>{html.escape(s['qr_top_label'])}</span>
              </div>
              {mid_html}
              <div class="ty-qr-box">
                <img src="assets/{html.escape(s['qr_bottom'])}" alt="GitHub QR"/>
                <span>{html.escape(s['qr_bottom_label'])}</span>
              </div>
            </div>
          </div>
        </div>
        """

    if stype == "section_poll":
        p = s["poll"]
        opts = "".join(f"<li onclick=\"this.classList.toggle('voted')\">{html.escape(o)} <span class='vote-pill'>Click to Vote</span></li>" for o in p["options"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="section-poll-wrap">
            <img class="section-robot-icon" src="assets/{html.escape(s['icon'])}" alt="PayPal Badge"/>
            <h2>{html.escape(s['title']).replace(chr(10), '<br/>')}</h2>
            <div class="interactive-poll-card">
              <div class="poll-q">{html.escape(p['question'])}</div>
              <ul class="poll-opts">{opts}</ul>
              <button class="reveal-btn" onclick="this.nextElementSibling.classList.toggle('visible')">✨ Reveal Takeaway</button>
              <div class="poll-answer">💡 {html.escape(p['answer'])}</div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "agent_triad":
        b0, b1, b2 = s["boxes"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="triad-headline">
            {html.escape(s['headline'])}
          </div>
          <div class="triad-row">
            <div class="triad-box">
              <img src="assets/{html.escape(b0['icon'])}" alt="Pillar 1"/>
              <h3>{html.escape(b0['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box triad-center">
              <img src="assets/{html.escape(b1['icon'])}" alt="Pillar 2"/>
              <h3>{html.escape(b1['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box">
              <img src="assets/{html.escape(b2['icon'])}" alt="Pillar 3"/>
              <h3>{html.escape(b2['label']).replace(chr(10), '<br/>')}</h3>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "objectives_card":
        b_html = "".join(f"<li><strong class='hl-blue'>• {html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="blue-outline-card">
            <p class="card-intro">{html.escape(s['intro'])}</p>
            <ul class="obj-list">{b_html}</ul>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "arch_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              <p class="body-p">{html.escape(s['intro'])}</p>
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right center-img-box">
              <img class="arch-img zoomable" src="assets/{html.escape(s['image'])}" alt="Architecture Diagram" onclick="openLightbox(this.src)"/>
              <span class="click-hint">🔍 Click diagram to enlarge full-screen</span>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "three_tech":
        cols_html = ""
        for c in s["cols"]:
            cols_html += f"""
            <div class="tech-col-card">
              <img src="assets/{html.escape(c['icon'])}" alt="Tech Icon"/>
              <h3>{html.escape(c['title']).replace(chr(10), '<br/>')}</h3>
              <p>{html.escape(c['body'])}</p>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="three-tech-grid">{cols_html}</div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "two_cards_quiz":
        lc, rc, q = s["left_card"], s["right_card"], s["quiz"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["items"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["items"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <h4>{html.escape(lc['subtitle'])}</h4>
              <ul class="clean-bullets">{li_l}</ul>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <h4>{html.escape(rc['subtitle'])}</h4>
              <ul class="clean-bullets">{li_r}</ul>
            </div>
          </div>
          <div class="quiz-banner">
            <div class="quiz-q-row">
              <span>{html.escape(q['question'])}</span>
              <button class="reveal-btn-sm" onclick="this.parentElement.nextElementSibling.classList.toggle('visible')">Reveal Answer</button>
            </div>
            <div class="quiz-ans-row">{html.escape(q['answer'])}</div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "lab_divider":
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="lab-divider-center">
            <h1>{html.escape(s['title'])}</h1>
            <div class="lab-sub-row">
              <img src="assets/paypal_monogram_badge.png" alt="PayPal"/>
              <span>{html.escape(s['subtitle'])}</span>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "code_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        intro_p = f"<p class='body-p'>{html.escape(s['intro'])}</p>" if s.get("intro") else ""
        shot_html = ""
        if s.get("screenshot"):
            shot_html = f"""
            <div class="shot-preview-box">
              <img class="zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Animated Mechanism Diagram" onclick="openLightbox(this.src)"/>
              <span class="click-hint">🔍 Click diagram to enlarge full-screen</span>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              {intro_p}
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right">
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s['code_title'])}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
              {shot_html}
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "stepper_split":
        steps_html = ""
        for snum, stitle, sdesc in s["steps"]:
            steps_html += f"""
            <div class="v-step-item">
              <div class="v-step-circle">{html.escape(snum)}</div>
              <div class="v-step-text">
                <h4>{html.escape(stitle)}</h4>
                <code>{html.escape(sdesc)}</code>
              </div>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left v-stepper-card">
              {steps_html}
            </div>
            <div class="col-right">
              <div class="callout-card">
                <span class="callout-pill">{html.escape(s['callout_badge'])}</span>
                <h4>{html.escape(s['callout_title'])}</h4>
                <p>{html.escape(s['callout_body'])}</p>
              </div>
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s['code_title'])}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "two_cards_code":
        lc, rc = s["left_card"], s["right_card"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["bullets"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <h4>{html.escape(lc['subtitle'])}</h4>
              <div class="terminal-card compact">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">Prompt / Snippet</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(lc['code'])}</code></pre>
              </div>
              <ul class="clean-bullets compact-list">{li_l}</ul>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <h4>{html.escape(rc['subtitle'])}</h4>
              <div class="terminal-card compact">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">Prompt / Snippet</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(rc['code'])}</code></pre>
              </div>
              <ul class="clean-bullets compact-list">{li_r}</ul>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "checkpoint_visual":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="split-2col">
            <div class="col-left">
              <ul class="clean-bullets">{b_html}</ul>
            </div>
            <div class="col-right center-img-box">
              <img class="arch-img zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Empirical Benchmark Plot" onclick="openLightbox(this.src)"/>
              <p class="img-caption">{html.escape(s.get('caption', ''))} (Click to zoom)</p>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "four_steps":
        steps_html = ""
        for st in s["steps"]:
            hi_cls = "step-card-hi" if st.get("highlight") else ""
            steps_html += f"""
            <div class="four-step-card {hi_cls}">
              <div class="step-num-circle">{html.escape(st['num'])}</div>
              <h4>{html.escape(st['title']).replace(chr(10), '<br/>')}</h4>
              <p>{html.escape(st['body'])}</p>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
          <p class="body-p">{html.escape(s['intro'])}</p>
          <div class="four-steps-grid">{steps_html}</div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """

    if stype == "verification_cards":
        lc, rc = s["left_card"], s["right_card"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="pp-top-stripe"></div>
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_paypal_header.png" alt="PayPal AI Engineering"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">PayPal Internal • AI Engineering</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <div class="query-box">
                <strong>Input Snippet:</strong><br/>
                <span>{html.escape(lc['query'])}</span>
              </div>
              <div class="grounded-box">
                <strong class="hl-green">{html.escape(lc['result_title'])}</strong>
                <p>{html.escape(lc['result_body'])}</p>
                <small><strong>Verification Goal:</strong> {html.escape(lc['goal'])}</small>
              </div>
            </div>
            <div class="bordered-card card-red">
              <h3>{html.escape(rc['title'])}</h3>
              <div class="trap-box trap-red">
                <strong>{html.escape(rc['trap1_title'])}</strong>
                <div class="hl-green">{html.escape(rc['trap1_expected'])}</div>
                <p>{html.escape(rc['trap1_body'])}</p>
              </div>
              <div class="trap-box trap-yellow">
                <strong>{html.escape(rc['trap2_title'])}</strong>
                <div class="hl-green">{html.escape(rc['trap2_expected'])}</div>
                <p>{html.escape(rc['trap2_body'])}</p>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_paypal_footer.png" alt="PayPal"/>
        </div>
        """
    return ""


def get_slide_title(s):
    if "title" in s:
        return s["title"].replace("\n", " ")
    if "headline" in s:
        return "The Three Engineering Pillars"
    if "left_card" in s and "right_card" in s:
        return f"{s['left_card']['title']} & {s['right_card']['title']}"
    return f"Slide {s['num']}"


def build_html_deck(output_path):
    slides_dom = []
    notes_json = []
    for s in SLIDES_DATA:
        active = "active" if s["num"] == 1 else ""
        stitle = get_slide_title(s)
        slides_dom.append(
            f'<section class="slide {active}" data-slide="{s["num"]}" data-title="{html.escape(stitle)}" data-module="{html.escape(s["module"])}" data-time="{html.escape(s["time"])}">'
            f'{render_slide_inner_html(s)}'
            f'</section>'
        )
        notes_json.append({
            "num": s["num"],
            "title": stitle,
            "module": s["module"],
            "time": s["time"],
            "notes": s["notes"],
        })

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PayPal AI Engineering Showcase — Full-Stack PyTorch on Cloud TPU (torch_tpu)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --g-blue: #0070BA;
      --g-blue-dark: #003087;
      --g-cyan: #009CDE;
      --g-blue-bg: #EBF4FF;
      --g-red: #D93025;
      --g-red-dark: #003087;
      --g-red-bg: #FCE8E6;
      --g-yellow: #FFC439;
      --g-yellow-bg: #FFF8E1;
      --g-green: #0B8043;
      --g-green-dark: #096B36;
      --g-dark: #001C64;
      --g-gray: #5A6474;
      --g-border: #D0D7E2;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Google Sans', 'Roboto', system-ui, sans-serif;
      background: #061233;
      color: #101828;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      display: flex;
      flex-direction: column;
    }}
    /* Main viewport scaling 16:9 canvas */
    #deck-viewport {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
      padding: 12px;
    }}
    .slide {{
      display: none;
      width: min(96vw, calc((100vh - 64px) * 16 / 9));
      aspect-ratio: 16 / 9;
      background: #FFFFFF;
      border-radius: 12px;
      box-shadow: 0 24px 68px rgba(0, 12, 48, 0.75);
      position: relative;
      overflow: hidden;
    }}
    body.notes-open .slide {{
      width: min(94vw, calc((100vh - 245px) * 16 / 9));
    }}
    .slide.active {{ display: block; }}
    .slide-canvas {{
      width: 100%;
      height: 100%;
      position: relative;
      padding: 2.5% 4.2% 2.2% 4.2%;
      display: flex;
      flex-direction: column;
    }}
    /* Signature PayPal 4-segment top bar */
    .pp-top-stripe {{
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 7px;
      background: linear-gradient(90deg, #003087 0%, #003087 38%, #0070BA 38%, #0070BA 70%, #009CDE 70%, #009CDE 88.5%, #FFC439 88.5%, #FFC439 100%);
      z-index: 10;
    }}
    .pp-gold-bar {{
      width: 120px;
      height: 6px;
      background: #FFC439;
      border-radius: 3px;
      margin: 4px 0 16px 0;
    }}
    /* Top & Bottom Master Branding */
    .slide-top-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.2%;
      min-height: 36px;
    }}
    .gcl-logo-sm {{ height: 34px; object-fit: contain; }}
    .gcl-logo {{ position: absolute; top: 4.5%; left: 4.5%; height: 46px; z-index: 5; }}
    .gcl-footer {{ position: absolute; bottom: 2.4%; left: 4.2%; height: 22px; opacity: 0.92; }}
    .prop-badge {{ font-size: 0.78rem; color: var(--g-blue-dark); font-weight: 600; }}
    .prop-badge-abs {{ position: absolute; top: 4.5%; right: 4.2%; font-size: 0.78rem; color: var(--g-blue-dark); font-weight: 600; z-index: 5; }}
    .module-pill {{
      background: var(--g-blue-bg);
      color: var(--g-blue-dark);
      border: 1px solid var(--g-blue);
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
    }}

    /* Cover Slide */
    .slide-cover {{
      padding: 0;
      flex-direction: row;
      align-items: center;
    }}
    .cover-left {{
      width: 52%;
      padding: 8% 3% 4% 4.8%;
      z-index: 3;
    }}
    .pill-badge {{
      display: inline-block;
      background: var(--g-blue-bg);
      color: var(--g-blue);
      font-weight: 700;
      font-size: 0.9rem;
      padding: 6px 16px;
      border-radius: 999px;
      border: 1.5px solid var(--g-blue);
      margin-bottom: 18px;
    }}
    .cover-title {{
      font-size: clamp(1.7rem, 3.1vw, 3.1rem);
      line-height: 1.16;
      font-weight: 700;
      color: var(--g-dark);
      margin-bottom: 18px;
    }}
    .cover-subtitle {{
      font-size: clamp(0.95rem, 1.35vw, 1.3rem);
      color: var(--g-gray);
      line-height: 1.45;
      margin-bottom: 22px;
    }}
    .cover-meta {{
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--g-blue-dark);
    }}
    .cover-right {{
      width: 48%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }}
    .cover-right img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    /* QR Hub Slide */
    .center-title {{ text-align: center; font-size: clamp(1.5rem, 2.5vw, 2.4rem); font-weight: 700; margin-bottom: 4px; }}
    .center-subtitle {{ text-align: center; font-size: 1rem; color: var(--g-gray); margin-bottom: 18px; }}
    .qr-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.6%;
      flex: 1;
      margin-bottom: 3.5%;
    }}
    .qr-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}
    .qr-icon-badge {{
      width: 40px; height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, #4285F4, #669DF6);
      color: #fff;
      font-family: 'Roboto Mono', monospace;
      font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      margin-bottom: 8px;
    }}
    .qr-card h3 {{ font-size: 1.05rem; margin-bottom: 4px; }}
    .qr-link {{ font-size: 0.84rem; color: var(--g-blue); font-weight: 600; text-decoration: underline; margin-bottom: 6px; word-break: break-all; }}
    .qr-card p {{ font-size: 0.82rem; color: var(--g-gray); margin-bottom: 10px; line-height: 1.35; }}
    .qr-img {{ width: 145px; height: 145px; object-fit: contain; margin-top: auto; border-radius: 8px; background: #fff; padding: 4px; border: 1px solid #eee; }}

    /* Big dedicated QR slide (credits redemption) */
    .big-qr-wrap {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2.2%; }}
    .big-qr-card {{
      background: #fff; border: 2px solid var(--g-border); border-radius: 20px;
      padding: 1.6%; box-shadow: 0 10px 30px rgba(32,33,36,.12);
      transition: transform .2s, box-shadow .2s, border-color .2s;
    }}
    .big-qr-card:hover {{ transform: scale(1.02); border-color: var(--g-blue); box-shadow: 0 16px 40px rgba(26,115,232,.22); }}
    .big-qr-card img {{ display: block; width: min(40vh, 340px); height: auto; aspect-ratio: 1; }}
    .big-qr-link {{
      font-size: clamp(1.25rem, 2.6vw, 1.9rem); font-weight: 700; color: var(--g-blue);
      text-decoration: none; letter-spacing: -0.01em;
    }}
    .big-qr-link:hover {{ text-decoration: underline; }}
    .big-qr-desc {{ max-width: 74%; text-align: center; color: var(--g-gray); font-size: 0.95rem; line-height: 1.55; }}

    .wifi-chip {{
      background: #F1F3F4; border: 1.5px solid var(--g-border); border-radius: 999px;
      padding: 8px 22px; font-size: 0.95rem; color: var(--g-dark); font-weight: 500;
    }}
    .wifi-chip code {{
      font-family: 'Roboto Mono', monospace; background: #fff; border: 1px solid var(--g-border);
      border-radius: 6px; padding: 2px 10px; font-weight: 700; color: var(--g-blue-dark);
    }}

    /* Speaker & Thank You Slide */
    .slide-speaker {{ padding: 0; flex-direction: row; align-items: center; }}
    .speaker-fan-bg {{ position: absolute; left: 0; top: 0; width: 48%; height: 100%; z-index: 1; }}
    .speaker-fan-bg img {{ width: 100%; height: 100%; object-fit: cover; }}
    .speaker-content {{
      position: relative; z-index: 3;
      display: flex; align-items: center;
      width: 100%; height: 100%;
      padding: 6% 5% 6% 7%;
      gap: 6%;
    }}
    .speaker-photo-wrap img {{
      width: clamp(200px, 27vw, 330px);
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 22px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.28);
      border: 4px solid #fff;
    }}
    .speaker-Bio-text h1 {{ font-size: clamp(2.2rem, 3.8vw, 3.8rem); line-height: 1.08; margin-bottom: 16px; }}
    .role-line {{ font-size: clamp(1.1rem, 1.6vw, 1.55rem); color: #3C4043; margin-bottom: 8px; font-weight: 500; }}
    .speaker-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }}
    .tag-chip {{ background: var(--g-blue-bg); color: var(--g-blue-dark); padding: 5px 12px; border-radius: 999px; font-size: 0.82rem; font-weight: 600; }}
    .thankyou-right {{
      margin-left: 46%;
      width: 54%;
      padding: 5% 4.5% 5% 2%;
      z-index: 3;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
    }}
    .thankyou-text h1 {{ font-size: clamp(2.4rem, 4.2vw, 4.2rem); margin-bottom: 12px; }}
    .thankyou-text p {{ font-size: 1.05rem; color: var(--g-gray); line-height: 1.5; }}
    .thankyou-qrs {{ display: flex; flex-direction: column; gap: 18px; }}
    .ty-qr-box {{ display: flex; flex-direction: column; align-items: center; text-align: center; background: #F8F9FA; padding: 10px; border-radius: 12px; border: 1px solid var(--g-border); width: 185px; }}
    .ty-qr-box img {{ width: 125px; height: 125px; margin-bottom: 6px; }}
    .ty-qr-box span {{ font-size: 0.72rem; color: var(--g-blue-dark); font-weight: 600; line-height: 1.25; }}

    /* Section Poll Slide */
    .section-poll-wrap {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; max-width: 88%; margin: 0 auto; }}
    .section-robot-icon {{ width: 64px; height: 64px; margin-bottom: 8px; }}
    .section-poll-wrap h2 {{ font-size: clamp(1.6rem, 2.6vw, 2.5rem); margin-bottom: 16px; line-height: 1.18; }}
    .interactive-poll-card {{
      width: 100%;
      background: var(--g-blue-bg);
      border: 2px solid var(--g-blue);
      border-radius: 14px;
      padding: 16px 22px;
      text-align: left;
    }}
    .poll-q {{ font-size: 1.05rem; font-weight: 700; color: var(--g-blue-dark); margin-bottom: 10px; }}
    .poll-opts {{ list-style: none; display: flex; flex-direction: column; gap: 7px; margin-bottom: 12px; }}
    .poll-opts li {{
      background: #fff;
      border: 1.5px solid #BBD6FB;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.94rem;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.15s;
    }}
    .poll-opts li:hover, .poll-opts li.voted {{ background: #D2E3FC; border-color: var(--g-blue); font-weight: 600; }}
    .vote-pill {{ font-size: 0.75rem; background: var(--g-blue); color: #fff; padding: 2px 9px; border-radius: 999px; }}
    .reveal-btn, .reveal-btn-sm {{
      background: var(--g-blue); color: #fff; border: none;
      padding: 7px 14px; border-radius: 8px; font-weight: 600;
      cursor: pointer; font-size: 0.85rem;
    }}
    .reveal-btn:hover, .reveal-btn-sm:hover {{ background: var(--g-blue-dark); }}
    .poll-answer, .quiz-ans-row {{
      display: none;
      margin-top: 10px;
      padding: 9px 12px;
      background: #E6F4EA;
      border-left: 4px solid var(--g-green);
      border-radius: 6px;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--g-green-dark);
    }}
    .poll-answer.visible, .quiz-ans-row.visible {{ display: block; }}

    /* Triad Slide */
    .triad-headline {{
      font-size: clamp(1.35rem, 2.2vw, 2.15rem);
      font-weight: 700;
      line-height: 1.28;
      max-width: 90%;
      margin: 1.5% auto 4% auto;
    }}
    .hl-blue {{ color: var(--g-blue); }}
    .hl-green {{ color: var(--g-green-dark); }}
    .triad-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex: 1;
      margin-bottom: 4%;
    }}
    .triad-box {{
      flex: 1;
      background: #F1F3F4;
      border: 1.5px solid var(--g-border);
      border-radius: 14px;
      padding: 28px 16px 22px 16px;
      text-align: center;
      position: relative;
    }}
    .triad-center {{ border: 2px solid var(--g-blue); background: var(--g-blue-bg); }}
    .triad-box img {{ width: 58px; height: 58px; margin-bottom: 10px; }}
    .triad-box h3 {{ font-size: 1.25rem; line-height: 1.3; }}
    .triad-arrow {{ font-size: 2rem; color: var(--g-gray); font-weight: 700; }}

    /* Standard Content & Split Layouts */
    .slide-h2 {{ font-size: clamp(1.35rem, 2.1vw, 2.05rem); font-weight: 700; margin-bottom: 8px; color: var(--g-dark); }}
    .sub-blue {{ font-size: clamp(1rem, 1.3vw, 1.22rem); color: var(--g-blue); font-weight: 700; margin-bottom: 8px; }}
    .body-p {{ font-size: 0.92rem; color: #3C4043; line-height: 1.45; margin-bottom: 10px; }}
    .blue-outline-card {{
      border: 2.5px solid var(--g-blue);
      border-radius: 16px;
      padding: 20px 26px;
      flex: 1;
      margin-bottom: 3.5%;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .card-intro {{ font-size: 1.05rem; font-weight: 500; margin-bottom: 14px; color: var(--g-dark); line-height: 1.4; }}
    .obj-list {{ list-style: none; display: flex; flex-direction: column; gap: 12px; font-size: 0.96rem; line-height: 1.42; }}
    .split-2col {{
      display: grid;
      grid-template-columns: 47% 51%;
      gap: 2%;
      flex: 1;
      margin-bottom: 3.2%;
      min-height: 0;
    }}
    .col-left, .col-right {{ display: flex; flex-direction: column; min-height: 0; }}
    .clean-bullets {{ list-style: none; display: flex; flex-direction: column; gap: 9px; font-size: 0.89rem; line-height: 1.38; color: #3C4043; }}
    .clean-bullets li strong {{ color: var(--g-blue-dark); }}
    .compact-list {{ gap: 6px; font-size: 0.84rem; margin-top: 8px; }}
    .center-img-box {{ align-items: center; justify-content: center; background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px; padding: 10px; }}
    .arch-img {{ max-width: 100%; max-height: 88%; object-fit: contain; border-radius: 8px; cursor: zoom-in; }}
    .click-hint, .img-caption {{ font-size: 0.76rem; color: var(--g-gray); margin-top: 5px; text-align: center; }}

    /* Three Tech Columns */
    .three-tech-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2.5%;
      flex: 1;
      margin: 1.5% 0 4% 0;
    }}
    .tech-col-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }}
    .tech-col-card img {{ width: 54px; height: 54px; object-fit: contain; margin-bottom: 14px; }}
    .tech-col-card h3 {{ font-size: 1.15rem; margin-bottom: 10px; line-height: 1.28; }}
    .tech-col-card p {{ font-size: 0.9rem; color: #3C4043; line-height: 1.45; }}

    /* Dual Cards & Quiz Banner */
    .dual-cards-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2.2%;
      flex: 1;
      min-height: 0;
      margin-bottom: 10px;
    }}
    .bordered-card {{
      border-radius: 14px;
      padding: 14px 18px;
      display: flex;
      flex-direction: column;
      min-height: 0;
      background: #fff;
    }}
    .card-blue {{ border: 2.5px solid var(--g-blue); }}
    .card-blue h3 {{ color: var(--g-blue); font-size: 1.18rem; margin-bottom: 2px; }}
    .card-red {{ border: 2.5px solid var(--g-red); }}
    .card-red h3 {{ color: var(--g-red-dark); font-size: 1.18rem; margin-bottom: 2px; }}
    .bordered-card h4 {{ font-size: 0.86rem; color: var(--g-gray); margin-bottom: 8px; font-weight: 600; }}
    .quiz-banner {{
      background: var(--g-yellow-bg);
      border: 1.5px solid var(--g-yellow);
      border-radius: 10px;
      padding: 8px 14px;
      margin-bottom: 2.8%;
    }}
    .quiz-q-row {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 0.86rem; font-weight: 700; color: #B06000; }}

    /* Lab Divider */
    .lab-divider-center {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .lab-divider-center h1 {{ font-size: clamp(2.4rem, 4vw, 3.8rem); margin-bottom: 18px; }}
    .lab-sub-row {{ display: flex; align-items: center; gap: 14px; font-size: 1.35rem; color: var(--g-blue); font-weight: 700; }}
    .lab-sub-row img {{ width: 36px; height: 36px; }}

    /* Terminal Code Box */
    .terminal-card {{
      background: var(--g-dark);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      border: 1px solid #3C4043;
      margin-bottom: 8px;
    }}
    .terminal-card.compact {{ max-height: 46%; }}
    .term-header {{
      background: #2D2E31;
      padding: 6px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .term-dots {{ display: flex; gap: 6px; }}
    .term-dots span {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    .dot-r {{ background: #EA4335; }}
    .dot-y {{ background: #FBBC04; }}
    .dot-g {{ background: #34A853; }}
    .term-title {{ font-family: 'Roboto Mono', monospace; font-size: 0.75rem; color: #9AA0A6; }}
    .copy-btn {{
      background: #3C4043; color: #E8EAED; border: 1px solid #5F6368;
      border-radius: 5px; padding: 2px 8px; font-size: 0.72rem; cursor: pointer;
    }}
    .copy-btn:hover {{ background: var(--g-blue); border-color: var(--g-blue); }}
    .term-body {{
      padding: 10px 14px;
      color: #E8EAED;
      font-family: 'Roboto Mono', monospace;
      font-size: 0.76rem;
      line-height: 1.38;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-y: auto;
    }}
    .shot-preview-box {{
      flex: 1;
      min-height: 0;
      background: #F8F9FA;
      border: 1px solid var(--g-border);
      border-radius: 8px;
      padding: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}
    .shot-preview-box img {{ max-width: 100%; max-height: 135px; object-fit: contain; border-radius: 4px; cursor: zoom-in; }}

    /* Vertical Stepper & Callout */
    .v-stepper-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      justify-content: space-around;
    }}
    .v-step-item {{ display: flex; align-items: flex-start; gap: 14px; }}
    .v-step-circle {{
      width: 36px; height: 36px; border-radius: 50%;
      background: var(--g-blue); color: #fff; font-weight: 700;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }}
    .v-step-text h4 {{ font-size: 1rem; margin-bottom: 3px; }}
    .v-step-text code {{ font-family: 'Roboto Mono', monospace; font-size: 0.82rem; color: var(--g-green-dark); }}
    .callout-card {{
      background: #fff; border: 1.5px solid var(--g-border);
      border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
    }}
    .callout-pill {{
      display: inline-block; background: var(--g-red-bg); color: var(--g-red-dark);
      font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; margin-bottom: 6px;
    }}
    .callout-card h4 {{ font-size: 0.98rem; margin-bottom: 4px; }}
    .callout-card p {{ font-size: 0.83rem; color: #3C4043; line-height: 1.36; }}

    /* Four Steps Grid */
    .four-steps-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.8%;
      flex: 1;
      margin-bottom: 3.5%;
    }}
    .four-step-card {{
      background: #F8F9FA;
      border: 1.5px solid var(--g-border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
    }}
    .four-step-card.step-card-hi {{ border: 2.5px solid var(--g-blue); background: #fff; }}
    .step-num-circle {{
      width: 36px; height: 36px; border-radius: 50%;
      background: var(--g-blue-bg); color: var(--g-blue);
      font-weight: 700; display: flex; align-items: center; justify-content: center;
      margin-bottom: 12px;
    }}
    .step-card-hi .step-num-circle {{ background: var(--g-blue); color: #fff; }}
    .four-step-card h4 {{ font-size: 0.98rem; margin-bottom: 8px; line-height: 1.28; }}
    .step-card-hi h4 {{ color: var(--g-blue); }}
    .four-step-card p {{ font-size: 0.83rem; color: #3C4043; line-height: 1.4; }}

    /* Verification Cards */
    .query-box {{ background: #F1F3F4; padding: 10px 12px; border-radius: 8px; font-size: 0.85rem; margin-bottom: 10px; }}
    .grounded-box {{ background: var(--g-blue-bg); border: 1px solid var(--g-blue); padding: 12px; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; flex: 1; display: flex; flex-direction: column; gap: 6px; }}
    .trap-box {{ padding: 10px 12px; border-radius: 8px; font-size: 0.83rem; line-height: 1.35; margin-bottom: 8px; flex: 1; }}
    .trap-red {{ background: var(--g-red-bg); border: 1px solid var(--g-red); }}
    .trap-yellow {{ background: var(--g-yellow-bg); border: 1px solid var(--g-yellow); }}

    /* Lab Timer Widget */
    .title-with-timer {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px; }}
    .lab-timer-widget {{
      display: flex; align-items: center; gap: 8px;
      background: var(--g-blue-bg); border: 1.5px solid var(--g-blue);
      padding: 4px 12px; border-radius: 999px; font-size: 0.82rem;
    }}
    .timer-label {{ font-weight: 700; color: var(--g-blue-dark); }}
    .timer-display {{ font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 0.95rem; color: var(--g-red-dark); min-width: 48px; }}
    .timer-btn {{
      background: var(--g-blue); color: #fff; border: none;
      border-radius: 999px; padding: 3px 10px; font-size: 0.74rem; font-weight: 600; cursor: pointer;
    }}
    .timer-btn.secondary {{ background: #5F6368; }}

    /* Speaker Notes Teleprompter Drawer (Press S) */
    #notes-drawer {{
      display: none;
      height: 185px;
      background: #1E2028;
      border-top: 2px solid var(--g-blue);
      color: #E8EAED;
      padding: 12px 24px;
      overflow-y: auto;
      font-size: 0.95rem;
      line-height: 1.5;
    }}
    body.notes-open #notes-drawer {{ display: block; }}
    #notes-drawer-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 6px; font-size: 0.8rem; color: #8AB4F8; font-weight: 700;
    }}
    #notes-drawer-content {{ white-space: pre-wrap; font-family: 'Roboto', sans-serif; }}

    /* Bottom Presenter Control Bar (hidden by default; press B to toggle; never in fullscreen) */
    #presenter-bar {{
      height: 46px;
      background: #181A20;
      border-top: 1px solid #2D3139;
      display: none;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      color: #E8EAED;
      font-size: 0.84rem;
      user-select: none;
    }}
    body.controls-visible #presenter-bar {{ display: flex; }}
    body.is-fullscreen #presenter-bar {{ display: none !important; }}
    body:not(.controls-visible) .slide {{ width: min(96vw, calc((100vh - 24px) * 16 / 9)); }}
    body:not(.controls-visible).notes-open .slide {{ width: min(94vw, calc((100vh - 200px) * 16 / 9)); }}
    .bar-group {{ display: flex; align-items: center; gap: 8px; }}
    .bar-btn {{
      background: #282C34; color: #E8EAED; border: 1px solid #3E4451;
      padding: 5px 11px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;
      cursor: pointer; transition: all 0.15s;
    }}
    .bar-btn:hover {{ background: var(--g-blue); border-color: var(--g-blue); }}
    .bar-btn.active-toggle {{ background: var(--g-blue); border-color: var(--g-blue); }}
    #progress-track {{ width: 140px; height: 6px; background: #2D3139; border-radius: 99px; overflow: hidden; }}
    #progress-fill {{ height: 100%; background: var(--g-blue); width: 3%; transition: width 0.2s; }}

    /* Slide Grid Modal (Press G) */
    #grid-modal, #lightbox-modal {{
      display: none;
      position: fixed; inset: 0;
      background: rgba(15, 17, 23, 0.92);
      z-index: 100;
      padding: 32px;
      overflow-y: auto;
    }}
    #grid-modal.open, #lightbox-modal.open {{ display: flex; flex-direction: column; }}
    .grid-cards {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .grid-item {{
      background: #20232A; border: 1.5px solid #3C4043; border-radius: 8px;
      padding: 12px; color: #E8EAED; cursor: pointer;
    }}
    .grid-item:hover, .grid-item.current {{ border-color: var(--g-blue); background: #263147; }}
    .grid-item-num {{ font-size: 0.75rem; color: #8AB4F8; font-weight: 700; margin-bottom: 4px; }}
    .grid-item-title {{ font-size: 0.88rem; font-weight: 600; }}
    #lightbox-modal {{ align-items: center; justify-content: center; cursor: zoom-out; }}
    #lightbox-img {{ max-width: 94vw; max-height: 90vh; border-radius: 10px; box-shadow: 0 12px 40px rgba(0,0,0,0.8); }}
  </style>
</head>
<body>
  <div id="deck-viewport">
    {''.join(slides_dom)}
  </div>

  <!-- On-Screen Speaker Notes Teleprompter Drawer (Toggle with 'S') -->
  <div id="notes-drawer">
    <div id="notes-drawer-header">
      <span id="notes-slide-meta">🎤 SPEAKER NOTES &amp; TALK SCRIPT</span>
      <span>Tip: <strong>P</strong> = Presenter Console | <strong>S</strong> = hide drawer | <strong>B</strong> = control bar</span>
    </div>
    <div id="notes-drawer-content"></div>
  </div>

  <!-- Bottom Presenter Toolbar -->
  <div id="presenter-bar">
    <div class="bar-group">
      <button class="bar-btn" onclick="prevSlide()">◀ Prev</button>
      <span id="slide-counter" style="min-width: 72px; text-align:center; font-weight:700;">1 / {len(SLIDES_DATA)}</span>
      <button class="bar-btn" onclick="nextSlide()">Next ▶</button>
      <div id="progress-track"><div id="progress-fill"></div></div>
      <span id="module-indicator" style="color:#9AA0A6; font-size:0.78rem; margin-left:8px;"></span>
    </div>
    <div class="bar-group">
      <span id="talk-clock" style="font-family:'Roboto Mono',monospace; color:#FBBC04; font-weight:700;">⏱️ Talk Clock: 00:00 / 75:00</span>
      <button class="bar-btn" onclick="toggleTalkClock()" id="clock-btn">Start Clock</button>
      <button class="bar-btn" onclick="toggleNotesDrawer()" id="notes-btn">📝 Speaker Notes (S)</button>
      <button class="bar-btn" onclick="openPresenterPopup()">🖥️ Presenter View (P)</button>
      <button class="bar-btn" onclick="toggleGrid()">⊞ All Slides (G)</button>
      <button class="bar-btn" onclick="toggleFullscreen()">⛶ Fullscreen (F)</button>
    </div>
  </div>

  <!-- All-Slides Overview Grid Modal -->
  <div id="grid-modal">
    <div style="display:flex; justify-content:space-between; align-items:center; color:#fff;">
      <h2>All Workshop Slides — Click Any Slide to Jump</h2>
      <button class="bar-btn" onclick="toggleGrid()">✕ Close (ESC)</button>
    </div>
    <div class="grid-cards" id="grid-cards-container"></div>
  </div>

  <!-- Lightbox Modal for Diagrams & Screenshots -->
  <div id="lightbox-modal" onclick="closeLightbox()">
    <img id="lightbox-img" src="" alt="Enlarged View"/>
  </div>

  <script>
    const SLIDE_NOTES = {json.dumps(notes_json)};
    const totalSlides = SLIDE_NOTES.length;
    let currentSlide = 1;
    const channel = new BroadcastChannel('paypal_torchtpu_showcase_sync');

    function showSlide(n, broadcast = true) {{
      if (n < 1) n = 1;
      if (n > totalSlides) n = totalSlides;
      currentSlide = n;
      document.querySelectorAll('.slide').forEach(el => {{
        el.classList.toggle('active', parseInt(el.dataset.slide) === currentSlide);
      }});
      document.getElementById('slide-counter').textContent = `${{currentSlide}} / ${{totalSlides}}`;
      document.getElementById('progress-fill').style.width = `${{(currentSlide / totalSlides) * 100}}%`;
      const meta = SLIDE_NOTES[currentSlide - 1];
      document.getElementById('module-indicator').textContent = `${{meta.module}} (${{meta.time}})`;
      document.getElementById('notes-slide-meta').textContent = `🎤 SLIDE ${{meta.num}}: ${{meta.title}} — ${{meta.time}}`;
      document.getElementById('notes-drawer-content').textContent = meta.notes;
      window.location.hash = `slide-${{currentSlide}}`;
      if (broadcast) {{
        channel.postMessage({{ type: 'SLIDE_CHANGE', slide: currentSlide }});
      }}
    }}

    function nextSlide() {{ showSlide(currentSlide + 1); }}
    function prevSlide() {{ showSlide(currentSlide - 1); }}

    function toggleNotesDrawer() {{
      document.body.classList.toggle('notes-open');
      document.getElementById('notes-btn').classList.toggle('active-toggle');
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen();
      }} else {{
        document.exitFullscreen();
      }}
    }}

    // Control bar: hidden by default, press B to toggle, force-hidden in fullscreen
    function toggleControlBar() {{ document.body.classList.toggle('controls-visible'); }}
    document.addEventListener('fullscreenchange', () => {{
      document.body.classList.toggle('is-fullscreen', !!document.fullscreenElement);
    }});

    function openLightbox(src) {{
      document.getElementById('lightbox-img').src = src;
      document.getElementById('lightbox-modal').classList.add('open');
    }}
    function closeLightbox() {{
      document.getElementById('lightbox-modal').classList.remove('open');
    }}

    function copyCode(btn) {{
      const code = btn.closest('.terminal-card').querySelector('code').innerText;
      navigator.clipboard.writeText(code);
      const old = btn.textContent;
      btn.textContent = '✅ Copied!';
      setTimeout(() => btn.textContent = old, 1500);
    }}

    // Lab Checkpoint Timers
    const labIntervals = {{}};
    function toggleLabTimer(slideNum) {{
      const widget = document.getElementById(`timer-${{slideNum}}`);
      const disp = document.getElementById(`timer-disp-${{slideNum}}`);
      if (labIntervals[slideNum]) {{
        clearInterval(labIntervals[slideNum]);
        delete labIntervals[slideNum];
        return;
      }}
      let remaining = parseInt(widget.dataset.remaining || widget.dataset.seconds);
      labIntervals[slideNum] = setInterval(() => {{
        if (remaining > 0) remaining--;
        widget.dataset.remaining = remaining;
        const m = String(Math.floor(remaining / 60)).padStart(2, '0');
        const s = String(remaining % 60).padStart(2, '0');
        disp.textContent = `${{m}}:${{s}}`;
        if (remaining === 0) {{
          clearInterval(labIntervals[slideNum]);
          delete labIntervals[slideNum];
        }}
      }}, 1000);
    }}
    function resetLabTimer(slideNum) {{
      if (labIntervals[slideNum]) {{
        clearInterval(labIntervals[slideNum]);
        delete labIntervals[slideNum];
      }}
      const widget = document.getElementById(`timer-${{slideNum}}`);
      const total = parseInt(widget.dataset.seconds);
      widget.dataset.remaining = total;
      const m = String(Math.floor(total / 60)).padStart(2, '0');
      const s = String(total % 60).padStart(2, '0');
      document.getElementById(`timer-disp-${{slideNum}}`).textContent = `${{m}}:${{s}}`;
    }}

    // 75-Minute Overall Talk Clock
    let talkSeconds = 0;
    let talkTimer = null;
    function toggleTalkClock() {{
      const btn = document.getElementById('clock-btn');
      if (talkTimer) {{
        clearInterval(talkTimer);
        talkTimer = null;
        btn.textContent = 'Resume Clock';
      }} else {{
        btn.textContent = 'Pause Clock';
        talkTimer = setInterval(() => {{
          talkSeconds++;
          const m = String(Math.floor(talkSeconds / 60)).padStart(2, '0');
          const s = String(talkSeconds % 60).padStart(2, '0');
          document.getElementById('talk-clock').textContent = `⏱️ Talk Clock: ${{m}}:${{s}} / 75:00`;
        }}, 1000);
      }}
    }}

    // Slide Grid Overview
    function toggleGrid() {{
      const modal = document.getElementById('grid-modal');
      const container = document.getElementById('grid-cards-container');
      container.innerHTML = '';
      SLIDE_NOTES.forEach(s => {{
        const div = document.createElement('div');
        div.className = 'grid-item' + (s.num === currentSlide ? ' current' : '');
        div.innerHTML = `<div class="grid-item-num">Slide ${{s.num}} • ${{s.time}}</div><div class="grid-item-title">${{s.title}}</div>`;
        div.onclick = () => {{ showSlide(s.num); modal.classList.remove('open'); }};
        container.appendChild(div);
      }});
      modal.classList.toggle('open');
    }}

    // Dual-Screen Synchronized Presenter Popup (Press P)
    function openPresenterPopup() {{
      const win = window.open('speaker-notes.html?mode=presenter', 'PresenterConsole', 'width=980,height=760');
      setTimeout(() => channel.postMessage({{ type: 'SLIDE_CHANGE', slide: currentSlide }}), 500);
    }}

    channel.onmessage = (ev) => {{
      if (ev.data && ev.data.type === 'SLIDE_CHANGE') {{
        showSlide(ev.data.slide, false);
      }}
    }};

    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{ e.preventDefault(); nextSlide(); }}
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); prevSlide(); }}
      else if (e.key === 's' || e.key === 'S') {{ toggleNotesDrawer(); }}
      else if (e.key === 'p' || e.key === 'P') {{ openPresenterPopup(); }}
      else if (e.key === 'g' || e.key === 'G') {{ toggleGrid(); }}
      else if (e.key === 'f' || e.key === 'F') {{ toggleFullscreen(); }}
      else if (e.key === 'b' || e.key === 'B') {{ toggleControlBar(); }}
      else if (e.key === 'Escape') {{
        document.getElementById('grid-modal').classList.remove('open');
        closeLightbox();
      }}
    }});

    // Initialize from URL hash if present
    const m = window.location.hash.match(/slide-(\\d+)/);
    showSlide(m ? parseInt(m[1]) : 1);
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print(f"Saved Interactive Web Deck: {output_path}")


# ---------------------------------------------------------------------------
# PART 3: BUILD STANDALONE SPEAKER NOTES CONSOLE (speaker-notes.html)
# ---------------------------------------------------------------------------
def build_speaker_notes_html(output_path):
    notes_cards_html = []
    notes_json = []
    for s in SLIDES_DATA:
        stitle = get_slide_title(s)
        code_val = s.get("code") or (s.get("left_card", {}).get("code", "") + ("\n\n" + s.get("right_card", {}).get("code", "") if s.get("right_card", {}).get("code") else ""))
        notes_json.append({
            "num": s["num"],
            "title": stitle,
            "module": s["module"],
            "time": s["time"],
            "notes": s["notes"],
            "code": code_val,
        })
        code_block = ""
        if code_val:
            code_block = f"""
            <div class="cmd-box">
              <div class="cmd-hdr"><span>Copyable Command / Prompt</span><button onclick="navigator.clipboard.writeText(this.parentElement.nextElementSibling.innerText); this.textContent='✅ Copied!';">📋 Copy</button></div>
              <pre>{html.escape(code_val)}</pre>
            </div>
            """
        notes_cards_html.append(f"""
        <div class="note-card" id="note-slide-{s['num']}">
          <div class="note-hdr">
            <span class="badge-num">Slide {s['num']} / {len(SLIDES_DATA)}</span>
            <span class="badge-mod">{html.escape(s['module'])}</span>
            <span class="badge-time">⏱️ {html.escape(s['time'])}</span>
            <button class="jump-btn" onclick="syncToSlide({s['num']})">Sync Projector Here ▶</button>
          </div>
          <h2>{html.escape(stitle)}</h2>
          <div class="note-body">{html.escape(s['notes'])}</div>
          {code_block}
        </div>
        """)

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PayPal Speaker Notes &amp; Teleprompter — Full-Stack PyTorch on Cloud TPU</title>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Google Sans', system-ui, sans-serif;
      background: #061233;
      color: #E8EAED;
      margin: 0;
      padding: 0;
    }}
    header {{
      position: sticky; top: 0; z-index: 50;
      background: #0A1B48;
      border-bottom: 3px solid #FFC439;
      padding: 12px 24px;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 12px;
    }}
    .ctrl-row {{ display: flex; align-items: center; gap: 10px; }}
    button {{
      background: #0070BA; color: #fff; border: none;
      padding: 7px 14px; border-radius: 6px; font-weight: 600; cursor: pointer;
    }}
    button:hover {{ background: #003087; }}
    #live-banner {{
      background: #0B215A; border: 2px solid #009CDE;
      margin: 18px 24px; padding: 18px 22px; border-radius: 12px;
    }}
    #live-banner h3 {{ color: #FFC439; margin-bottom: 6px; font-size: 1.2rem; }}
    #live-notes {{ white-space: pre-wrap; font-size: 1.15rem; line-height: 1.55; color: #FFF; }}
    #live-next {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid #23408C; color: #009CDE; font-weight: 600; }}
    .container {{ max-width: 980px; margin: 0 auto; padding: 12px 24px 60px 24px; }}
    .note-card {{
      background: #0A1B48; border: 1.5px solid #1C3578;
      border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
    }}
    .note-card.active-card {{ border-color: #FFC439; box-shadow: 0 0 0 2px rgba(255,196,57,0.35); }}
    .note-hdr {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }}
    .badge-num {{ background: #0070BA; color: #fff; padding: 3px 10px; border-radius: 99px; font-weight: 700; font-size: 0.8rem; }}
    .badge-mod {{ color: #009CDE; font-size: 0.85rem; font-weight: 600; }}
    .badge-time {{ color: #FFC439; font-size: 0.85rem; font-weight: 600; margin-left: auto; }}
    .jump-btn {{ background: #2D3242; font-size: 0.75rem; padding: 4px 10px; }}
    .note-card h2 {{ font-size: 1.25rem; margin-bottom: 10px; color: #fff; }}
    .note-body {{ white-space: pre-wrap; font-size: 1.02rem; line-height: 1.55; color: #D2D6DF; }}
    .cmd-box {{ margin-top: 12px; background: #0B0D12; border: 1px solid #3C4043; border-radius: 8px; overflow: hidden; }}
    .cmd-hdr {{ background: #20232D; padding: 5px 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #9AA0A6; }}
    .cmd-box pre {{ padding: 10px 12px; font-family: 'Roboto Mono', monospace; font-size: 0.82rem; white-space: pre-wrap; color: #81C995; margin: 0; }}
  </style>
</head>
<body>
  <header>
    <div>
      <strong>🎤 Live Speaker Console &amp; Full Talk Script</strong>
      <span style="color:#9AA0A6; font-size:0.85rem; margin-left:10px;">Synced with Main Presentation Window</span>
    </div>
    <div class="ctrl-row">
      <button onclick="stepSlide(-1)">◀ Prev Slide</button>
      <span id="console-counter" style="font-weight:700; min-width:80px; text-align:center;">Slide 1 / 32</span>
      <button onclick="stepSlide(1)">Next Slide ▶</button>
    </div>
  </header>

  <div id="live-banner">
    <h3 id="live-title">Current Slide: 1</h3>
    <div id="live-notes"></div>
    <div id="live-next">Next Slide: 2</div>
  </div>

  <div class="container">
    <h2 style="margin-bottom:14px; color:#8AB4F8;">All Slides — Continuous Speaker Script &amp; Copy-Paste Prompts</h2>
    {''.join(notes_cards_html)}
  </div>

  <script>
    const NOTES = {json.dumps(notes_json)};
    let cur = 1;
    const channel = new BroadcastChannel('paypal_torchtpu_showcase_sync');

    function updateConsole(n) {{
      if (n < 1) n = 1;
      if (n > NOTES.length) n = NOTES.length;
      cur = n;
      const item = NOTES[cur - 1];
      const nextItem = NOTES[cur] || null;
      document.getElementById('console-counter').textContent = `Slide ${{cur}} / ${{NOTES.length}}`;
      document.getElementById('live-title').textContent = `LIVE ON SCREEN — Slide ${{item.num}}: ${{item.title}} (${{item.time}})`;
      document.getElementById('live-notes').textContent = item.notes;
      document.getElementById('live-next').textContent = nextItem ? `⏭️ UP NEXT — Slide ${{nextItem.num}}: ${{nextItem.title}} (${{nextItem.time}})` : `🎉 End of Deck`;
      document.querySelectorAll('.note-card').forEach(c => c.classList.remove('active-card'));
      const activeEl = document.getElementById(`note-slide-${{cur}}`);
      if (activeEl) {{
        activeEl.classList.add('active-card');
        activeEl.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}

    function syncToSlide(n) {{
      updateConsole(n);
      channel.postMessage({{ type: 'SLIDE_CHANGE', slide: n }});
    }}

    function stepSlide(delta) {{
      syncToSlide(cur + delta);
    }}

    channel.onmessage = (ev) => {{
      if (ev.data && ev.data.type === 'SLIDE_CHANGE') {{
        updateConsole(ev.data.slide);
      }}
    }};

    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); stepSlide(1); }}
      else if (e.key === 'ArrowLeft') {{ e.preventDefault(); stepSlide(-1); }}
    }});

    updateConsole(1);
  </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Saved Speaker Notes Console: {output_path}")


# ---------------------------------------------------------------------------
# PART 4: BUILD MARKDOWN RUNBOOK & VERBATIM SCRIPT (SPEAKER_NOTES_AND_SCRIPT.md)
# ---------------------------------------------------------------------------
def build_markdown_runbook(output_path):
    lines = [
        "# 🎤 PayPal Speaker Notes, Facilitator Runbook & Verbatim Talk Script",
        "",
        "## **Full-Stack PyTorch on Cloud TPU (`torch_tpu`): Domain LoRA, `autokernel` Pallas Fusion & High-Throughput Serving**",
        "- **Format**: PayPal AI & Cloud Accelerator Engineering Showcase (1 hr 15 mins / 75 minutes)",
        "- **Speaker**: Rabimba Karanjai (AI Systems & Cloud Accelerator Engineering • PayPal | Google Developer Expert — AI/ML)",
        "- **Package, Notebooks & Code**: `autokernel/`, `torchtpu-inference-workshop-main/notebooks/04..06_*.ipynb` & `demos/05..07_*/`",
        "",
        "---",
        "",
        "## ⚡ How to Present Directly from This Folder",
        "",
        "1. **Option A — Interactive PayPal Web Deck + Dual-Screen Presenter Console (Recommended)**:",
        "   - Run `./present.sh` in this folder (or open `index.html` in Chrome).",
        "   - Press **`P`** to pop out the synchronized **PayPal Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!",
        "   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.",
        "   - The bottom control bar is hidden from the audience by default and in fullscreen. Press **`B`** to toggle it (all functions also work via hotkeys: `S`/`P`/`G`/`F`/arrows).",
        "   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.",
        "2. **Option B — PowerPoint / Google Slides Presenter View**:",
        "   - Open `PayPal_TorchTPU_FullStack_Showcase.pptx` in PowerPoint/Keynote or upload to Google Slides.",
        "   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.",
        "3. **Option C — Tablet / Phone Companion**:",
        "   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through every slide's verbatim notes and copy-paste prompts.",
        "",
        "---",
        "",
        "## ⏱️ 75-Minute Pacing Schedule & Checkpoints",
        "",
        "| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **00:00 – 00:06** | 6 min | **Module 0: Welcome, Speaker & Artifacts** | Slides 1–3 | `autokernel` Package, Notebooks (`04`–`06`) & Repo Links |",
        "| **00:06 – 00:23** | 17 min | **Module 1: Enterprise Story & Architecture** | Slides 4–8 | 🎤 Poll #1 + 4-Stage Architecture + `colab-mcp` + 🎯 Quiz |",
        "| **00:23 – 00:36** | 13 min | **Module 2: Multi-Model Domain LoRA on TPU** | Slides 9–12 | `Qwen3-0.6B` (SecOps) & `Qwen2.5-0.5B` (FinTech PCI-DSS) |",
        "| **00:36 – 00:50** | 14 min | **Module 3: `autokernel` Lab (XProf & Pallas)** | Slides 13–16 | How `autokernel` Works + 4-Mode XProf + 73-Submodule Patching |",
        "| **00:50 – 01:05** | 15 min | **Module 4: SpecGuard SGLang Serving & Playbook** | Slides 17–20 | `2.46x` Prefix Cache TTFT + 16-File Burst + Q&A |",
        "",
        "---",
        "",
        "## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts",
        "",
    ]

    for s in SLIDES_DATA:
        stitle = get_slide_title(s)
        lines.append(f"### Slide {s['num']}: {stitle}")
        lines.append(f"- **Module**: {s['module']}")
        lines.append(f"- **Pacing**: `{s['time']}`")
        lines.append("")
        lines.append("#### 🎙️ Speaker Notes:")
        lines.append("```text")
        lines.append(s["notes"])
        lines.append("```")
        code_val = s.get("code") or (s.get("left_card", {}).get("code", "") + ("\n\n" + s.get("right_card", {}).get("code", "") if s.get("right_card", {}).get("code") else ""))
        if code_val:
            lines.append("")
            lines.append(f"#### 💻 On-Slide Command / Prompt (`{s.get('code_title', 'Snippet')}`):")
            lines.append("```bash")
            lines.append(code_val)
            lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved Markdown Runbook: {output_path}")


if __name__ == "__main__":
    pptx_out = os.path.join(BASE_DIR, "PayPal_TorchTPU_FullStack_Showcase.pptx")
    html_out = os.path.join(BASE_DIR, "index.html")
    notes_html_out = os.path.join(BASE_DIR, "speaker-notes.html")
    md_out = os.path.join(BASE_DIR, "SPEAKER_NOTES_AND_SCRIPT.md")

    build_pptx(pptx_out)
    build_html_deck(html_out)
    build_speaker_notes_html(notes_html_out)
    build_markdown_runbook(md_out)
