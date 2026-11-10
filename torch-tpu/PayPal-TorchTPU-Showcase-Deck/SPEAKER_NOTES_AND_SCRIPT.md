# 🎤 PayPal Speaker Notes, Facilitator Runbook & Verbatim Talk Script

## **Full-Stack PyTorch on Cloud TPU (`torch_tpu`): Domain LoRA, `autokernel` Pallas Fusion & High-Throughput Serving**
- **Format**: PayPal AI & Cloud Accelerator Engineering Showcase (1 hr 15 mins / 75 minutes)
- **Speaker**: Rabimba Karanjai (AI Systems & Cloud Accelerator Engineering • PayPal | Google Developer Expert — AI/ML)
- **Package, Notebooks & Code**: `autokernel/`, `torchtpu-inference-workshop-main/notebooks/04..06_*.ipynb` & `demos/05..07_*/`

---

## ⚡ How to Present Directly from This Folder

1. **Option A — Interactive PayPal Web Deck + Dual-Screen Presenter Console (Recommended)**:
   - Run `./present.sh` in this folder (or open `index.html` in Chrome).
   - Press **`P`** to pop out the synchronized **PayPal Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!
   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.
   - The bottom control bar is hidden from the audience by default and in fullscreen. Press **`B`** to toggle it (all functions also work via hotkeys: `S`/`P`/`G`/`F`/arrows).
   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.
2. **Option B — PowerPoint / Google Slides Presenter View**:
   - Open `PayPal_TorchTPU_FullStack_Showcase.pptx` in PowerPoint/Keynote or upload to Google Slides.
   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.
3. **Option C — Tablet / Phone Companion**:
   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through every slide's verbatim notes and copy-paste prompts.

---

## ⏱️ 75-Minute Pacing Schedule & Checkpoints

| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 – 00:06** | 6 min | **Module 0: Welcome, Speaker & Artifacts** | Slides 1–3 | `autokernel` Package, Notebooks (`04`–`06`) & Repo Links |
| **00:06 – 00:23** | 17 min | **Module 1: Enterprise Story & Architecture** | Slides 4–8 | 🎤 Poll #1 + 4-Stage Architecture + `colab-mcp` + 🎯 Quiz |
| **00:23 – 00:36** | 13 min | **Module 2: Multi-Model Domain LoRA on TPU** | Slides 9–12 | `Qwen3-0.6B` (SecOps) & `Qwen2.5-0.5B` (FinTech PCI-DSS) |
| **00:36 – 00:50** | 14 min | **Module 3: `autokernel` Lab (XProf & Pallas)** | Slides 13–16 | How `autokernel` Works + 4-Mode XProf + 73-Submodule Patching |
| **00:50 – 01:05** | 15 min | **Module 4: SpecGuard SGLang Serving & Playbook** | Slides 17–20 | `2.46x` Prefix Cache TTFT + 16-File Burst + Q&A |

---

## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts

### Slide 1: Full-Stack PyTorch on Cloud TPU: Domain LoRA, AutoKernel Pallas Fusion & Prefix-Cached Serving
- **Module**: Module 0 • PayPal AI Infrastructure Showcase
- **Pacing**: `00:00 – 00:02 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Welcome the PayPal engineering & AI infrastructure audience. Ensure the PayPal cover slide is projected clearly.

🗣️ SAY VERBATIM:
"Welcome everyone! Today I am walking through an end-to-end production AI engineering playbook on Google Cloud TPU (`tpu7x`) built with native PyTorch (`torch_tpu`). Instead of looking at isolated micro-benchmarks, I will show how I start in a standard Google Colab notebook bridged over MCP to our Cloud TPU pod, specialize open-weight models for PayPal-grade FinTech PCI-DSS v4.0 payment compliance and SecOps code auditing using LoRA, diagnose HBM round-trip bottlenecks with XProf, hot-patch 73 Hugging Face submodules in memory with my `autokernel` Pallas library, and serve the merged checkpoints with SGLang RadixAttention prefix caching and continuous batching."
```

---

### Slide 2: Rabimba Karanjai
- **Module**: Module 0 • Speaker Intro
- **Pacing**: `00:02 – 00:04 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Introduce yourself and connect the talk to PayPal's high-throughput, strict-SLA FinTech workloads.

🗣️ SAY VERBATIM:
"I'm Rabimba Karanjai. Working on production LLM systems, payment compliance guardrails, and Cloud TPU acceleration at PayPal taught me one hard lesson: model accuracy, kernel latency, and serving economics cannot live in separate silos. If I fine-tune a PCI-DSS or ISO-20022 compliance model that triggers XLA recompilations on dynamic batch shapes or re-prefills 1,280 tokens of shared policy rubric on every pull request or settlement check, our p99 latency blows right past a 50-millisecond SLA. Today's showcase unifies domain LoRA, Pallas VMEM kernel fusion, and RadixAttention prefix caching into one repeatable engineering stack."
```

---

### Slide 3: Reusable `autokernel` Library, Colab Notebooks & Demos
- **Module**: Module 0 • Packages, Notebooks & Artifacts
- **Pacing**: `00:04 – 00:06 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Point the team to the reusable `autokernel` package, the three Colab notebooks, and the CLI scripts.

🗣️ SAY VERBATIM:
"Everything I am presenting today is packaged so any engineer can run it immediately: a pip-installable `autokernel` Python library (`pip install -e ./autokernel`) with 10 unit and hardware verification tests, three self-contained Colab notebooks (`04`, `05`, and `06`), and standalone CLI scripts under `demos/05_specguard_app`, `06_autokernel_app`, and `07_domain_adaptation_showcase`. Every number in this deck comes from live hardware runs on `tpu7x` Chip 0."
```

---

### Slide 4: Why Do FinTech & SecOps AI Guardrails Hit a Wall in Production?
- **Module**: Module 1 • The FinTech & SecOps Production Challenge
- **Pacing**: `00:06 – 00:09 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Ask engineers in the room to vote A, B, or C.

🗣️ SAY VERBATIM:
"Let's look at what actually happens when we deploy an AI compliance or code auditor in a FinTech environment like PayPal. First, off-the-shelf base models hallucinate generic advice instead of enforcing exact PCI-DSS v4.0 rules—like flagging unmasked PAN and CVV fields in `logger.info` under `PCI-DSS-3.3.1`—or catching `.item()` host-device sync stalls in an ISO-20022 settlement loop. Second, naive eager PyTorch dispatches 47 separate TPU programs for a 4-layer block, bouncing intermediate tensors back and forth to off-chip HBM. Third, when a PR scanner audits 16 files in a burst, it re-computes the same 1,280-token compliance rubric 16 times!"
```

---

### Slide 5: The Three Engineering Pillars
- **Module**: Module 1 • The Three Engineering Pillars
- **Pacing**: `00:09 – 00:12 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk across the three pillars on screen.

🗣️ SAY VERBATIM:
"I designed this stack around three pillars. Pillar 1 is native `torch_tpu`: the TPU is simply `torch.device('tpu')`, allowing me to run Hugging Face `peft` LoRA adaptation across multiple model architectures in static `bfloat16` with zero `torch_xla` boilerplate. Pillar 2 is `autokernel`: using XProf and `torch.tpu.pallas.jax_op` to fuse memory-bound normalization and gating ops in on-chip TPU VMEM and hot-patch 73 Hugging Face submodules in memory. Pillar 3 is high-throughput serving with `sglang-torchtpu` and `vllm-torchtpu`, keeping shared compliance prefixes resident in TPU HBM."
```

---

### Slide 6: The 4-Stage Full-Stack TorchTPU Architecture
- **Module**: Module 1 • End-to-End Architecture
- **Pacing**: `00:12 – 00:16 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Point to the 4-layer architecture diagram on the right (remind attendees they can click any chart in the web deck to zoom in full-screen).

🗣️ SAY VERBATIM:
"Look at how the four stages connect on the right. At the top, `colab-mcp` and `tpu-agent-suite@0.7.0` give both me and my AI coding agent direct execution access to the TPU pod. In Stage 2, I run multi-model LoRA fine-tuning in `bfloat16` on `torch.device('tpu')`. In Stage 3, I profile with XProf and use `autokernel` to hot-patch 73 submodules inside the Hugging Face model with custom Pallas kernels. And in Stage 4, I hand the merged checkpoint to SGLang and vLLM for high-throughput serving."
```

---

### Slide 7: Developer Workflow: Colab MCP + Single-Chip PJRT Sharing
- **Module**: Module 1 • Interactive Developer Setup
- **Pacing**: `00:16 – 00:20 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Highlight the PJRT initialization order in the code box on the right—this is a critical practical tip for engineers.

🗣️ SAY VERBATIM:
"Here is a critical engineering tip when combining `torch_tpu` and JAX Pallas on the same chip. Both PyTorch and JAX talk to the TPU through `libtpu` and PJRT. If I import `jax` before `torch_tpu` initializes its PJRT client, or if `TPU_VISIBLE_DEVICES` conflicts with `TPU_VISIBLE_CHIPS`, they fight over the `/dev/vfio` device lock. By popping `TPU_VISIBLE_DEVICES`, pinning `TPU_VISIBLE_CHIPS='0'`, and allocating one tensor on `torch.device('tpu:0')` followed by `torch.accelerator.synchronize()` before importing `jax`—which I packaged into `autokernel.init_tpu(chip=0)`—both frameworks share the chip cleanly!"
```

#### 💻 On-Slide Command / Prompt (`.opencode/opencode.jsonc & autokernel.init_tpu(chip=0)`):
```bash
// 1. .opencode/opencode.jsonc
{
  "mcp": {
    "colab-mcp": {
      "type": "local",
      "command": ["uvx", "colab-mcp"]
    }
  }
}

# 2. Single-Chip PJRT Sharing (encapsulated in autokernel)
os.environ.pop("TPU_VISIBLE_DEVICES", None)
os.environ["TPU_VISIBLE_CHIPS"] = "0"
os.environ["TPU_CHIPS_PER_HOST_BOUNDS"] = "1,1,1"
import torch, torch_tpu
_ = torch.ones(1, device="tpu:0")  # Acquire PJRT first!
torch.accelerator.synchronize()
import jax  # Shares PJRT client with torch_tpu
```

---

### Slide 8: Native PyTorch on TPU (torch_tpu) & What to Avoid on Cloud TPU
- **Module**: Module 1 • Native torch_tpu vs Legacy Stack
- **Pacing**: `00:20 – 00:23 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Contrast the PayPal Blue card (`torch_tpu` best practices) with the Coral Red card (anti-patterns).

🗣️ SAY VERBATIM:
"Let's align on the mental model of `torch_tpu`. First, `torch_xla` is deprecated—everything I build uses `import torch, torch_tpu` and `torch.device('tpu')`. Second, TPUs thrive on static shapes and `bfloat16`. When I pad my training batches to fixed buckets like `(4, 256)` or `(6, 128)` and mask padding tokens with `-100` in the cross-entropy loss, XLA compiles the training graph once on Step 0 and runs every subsequent step in 105 milliseconds with zero recompilation."
```

---

### Slide 9: Stage 1: Multi-Model Domain Adaptation
- **Module**: Module 2 • Multi-Model Domain Adaptation
- **Pacing**: `00:23 – 00:25 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Transition to Module 2—showing how domain adaptation works across two distinct model architectures and compliance domains.

🗣️ SAY VERBATIM:
"Now let's dive into Stage 1: Multi-Model Domain Adaptation on Cloud TPU. I wanted to prove that this workflow generalizes across both model families and enterprise compliance domains, so I trained two distinct architectures on `tpu7x` Chip 0: `Qwen/Qwen3-0.6B` for SecOps and TorchTPU migration auditing, and `Qwen/Qwen2.5-0.5B-Instruct` for FinTech PCI-DSS v4.0 and ISO-20022 payment guardrails."
```

---

### Slide 10: Specializing Two Distinct Models on `torch.device('tpu')`
- **Module**: Module 2 • Two Models, Two Enterprise Domains
- **Pacing**: `00:25 – 00:29 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Compare Model A (`Qwen/Qwen3-0.6B`) on the left and Model B (`Qwen/Qwen2.5-0.5B-Instruct`) on the right.

🗣️ SAY VERBATIM:
"On the left, I adapted `Qwen/Qwen3-0.6B` as a SecOps and PyTorch-TPU Migration Auditor—catching SQL injection, hardcoded secrets, `.item()` sync stalls, and deprecated `torch_xla` code. In 40 steps at `181.7 ms/step`, loss dropped from `2.8536` to `0.0118` and perplexity collapsed from `17.35` to `1.01`. On the right, I adapted `Qwen/Qwen2.5-0.5B-Instruct` on FinTech PCI-DSS v4.0 and ISO-20022 payment compliance rules. In 30 steps at `105.2 ms/step`, loss dropped from `3.9182` to `0.0021` and domain perplexity collapsed from `50.31` to `1.00`, emitting exact rule citations like `PCI-DSS-3.3.1`!"
```

#### 💻 On-Slide Command / Prompt (`Snippet`):
```bash
# Prompt Input:
import torch_xla.core.xla_model as xm
dev = xm.xla_device()

# Adapted Model Output:
[CRITICAL | TPU-DEP-01] Deprecated torch_xla
import detected. Replace with:
import torch, torch_tpu; torch.device('tpu')

# Prompt Input:
logger.info(f'PAN={card_num} CVV={cvv}')

# Adapted Model Output:
SEVERITY: CRITICAL | RULE: PCI-DSS-3.3.1 |
VIOLATION: Full PAN and CVV logged in cleartext.
REMEDIATION: Mask PAN (`tokenize_pan(card_num)`)
```

---

### Slide 11: Empirical Results: Multi-Model LoRA & In-Model Pallas Patching
- **Module**: Module 2 • Empirical Convergence & Perplexity
- **Pacing**: `00:29 – 00:33 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Click on `domain_adaptation_showcase.png` to open the full-screen lightbox so the audience can inspect all three panels clearly.

🗣️ SAY VERBATIM:
"Here is the empirical plot generated directly from `domain_adapt_and_pallas_patch.py` on `tpu7x` Chip 0. In Panel 1, you see the step-by-step loss curves for both `Qwen3-0.6B` and `Qwen2.5-0.5B`. In Panel 2, you see the collapse in domain perplexity—from `17.35` down to `1.01` and from `50.31` down to `1.00`. And in Panel 3, you see what happens when I hot-patch the adapted Hugging Face model in-place with custom Pallas kernels: a `4.81x` to `5.47x` speedup across the 24-layer RMSNorm stack and a `1.21x` end-to-end forward-pass speedup across the entire 24-layer Transformer!"
```

---

### Slide 12: Qualitative Verification: Unadapted Base vs. TPU LoRA Adapted
- **Module**: Module 2 • Before vs After Domain Adaptation
- **Pacing**: `00:33 – 00:36 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Highlight the concrete before-and-after text outputs on both cards.

🗣️ SAY VERBATIM:
"Let's read the actual model outputs before and after LoRA adaptation. Before fine-tuning, when I asked `Qwen3-0.6B` to audit a `torch_xla` snippet, it gave generic boilerplate about updating external libraries. After 7 seconds of LoRA fine-tuning on one TPU chip, it outputs `[CRITICAL | TPU-DEP-01]` with the exact `torch.device('tpu')` migration fix. And on the right, my adapted `Qwen2.5-0.5B` FinTech model pinpoints `PCI-DSS-3.3.1` PAN logging violations and `TPU-SYNC-02` ISO-20022 settlement loop stalls."
```

---

### Slide 13: Stage 2: `autokernel` (XProf & Pallas)
- **Module**: Module 3 • AutoKernel Lab & Pallas VMEM Fusion
- **Pacing**: `00:36 – 00:38 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Transition to Module 3—kernel engineering with XProf, Pallas, and the `autokernel` library.

🗣️ SAY VERBATIM:
"Once I have an adapted model, how do I make it run as fast as the TPU hardware allows? Welcome to Stage 2: AutoKernel Lab and the `autokernel` package. Here I use the PyTorch TPU profiler (`ProfilerActivity.TPU`) and XProf to inspect the hardware timeline across four execution modes, and then write custom Pallas kernels that fuse memory-bound operations inside on-chip TPU Vector Memory (VMEM)."
```

---

### Slide 14: Benchmarking 4 Execution Modes on a 4-Layer Decoder Stack
- **Module**: Module 3 • The 4 Execution Modes on TPU
- **Pacing**: `00:38 – 00:42 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk through the 4 cards from left to right, emphasizing the XProf program count drop (`47 -> 3 -> 1 -> 1`).

🗣️ SAY VERBATIM:
"Look at the progression across the four cards. In plain Eager mode, a 4-layer decoder block takes `3.591 ms` because it launches 47 separate TPU programs per step—every elementwise op reads and writes HBM. Turning on `TORCH_TPU_DEFER_AND_FUSE=1` cuts that to 3 TPU programs and `2.126 ms` (`1.69x`). `torch.compile(backend='tpu')` captures the whole graph into 1 TPU program at `1.579 ms` (`2.28x`). And with `torch.tpu.pallas.jax_op`, my custom Pallas kernels execute in 1 TPU program with `9.54e-07` numerical parity—and on the isolated 8-layer Residual+RMSNorm stack, Pallas hits `0.409 ms` versus `2.587 ms` eager: a `6.32x` kernel speedup!"
```

---

### Slide 15: Inside the XProf Trace: 47 Dispatches vs. 1 Fused Program
- **Module**: Module 3 • XProf Timeline & Pallas Parity
- **Pacing**: `00:42 – 00:46 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Click `autokernel_xprof_waterfall.png` to zoom in on the 4-row XProf waterfall chart.

🗣️ SAY VERBATIM:
"This visualization from `autokernel_lab.py` makes the hardware story unmistakable. Look at the right panel: in Eager mode, the TPU timeline is chopped into 47 micro-launches totaling `3.59 ms`. With `DeferAndFuse`, `torch.compile`, and `Pallas`, the timeline collapses into a tight, continuous block on the MXU and VPU. Even better, Pallas gives me explicit control over VMEM tiling (`BlockSpec((128, d), lambda i: (i, 0))`) and `float32` accumulation precision."
```

---

### Slide 16: How `autokernel` Replaces 5 HBM Trips & Patches 73 HF Submodules
- **Module**: Module 3 • How autokernel Hot-Patches Hugging Face
- **Pacing**: `00:46 – 00:50 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk through the 3-line `autokernel` snippet on the top right and click the animated mechanism diagram below it to open the full-screen lightbox!

🗣️ SAY VERBATIM:
"Look at how `autokernel` works under the hood. In stock eager PyTorch, a single RMSNorm layer executes 5 separate operators that read and write off-chip HBM 5 times—across 49 RMSNorms in Qwen2.5-0.5B, that is 245 off-chip HBM round-trips per forward pass! With `autokernel`, I tile the batch dimension via `solve_tile_size(N)`, DMA each `(128, 896)` block into on-chip VMEM once, fuse the entire `float32` variance reduction and weight scaling inside VPU registers, and DMA the `bfloat16` output back once. Calling `autokernel.patch_hf(merged_model)` swaps all 73 `RMSNorm` and `SwiGLU` submodules in memory without copying a single weight byte—delivering a `4.81x` to `5.47x` 24-layer RMSNorm speedup and a `1.21x` end-to-end Transformer speedup with `99.74%` top-1 token agreement!"
```

#### 💻 On-Slide Command / Prompt (`autokernel — 3-Line Reusable HF Model Patcher`):
```bash
import autokernel

# 1. Isolate Chip 0 & wake up torch_tpu BEFORE JAX loads
autokernel.init_tpu(chip=0, defer_and_fuse=True)

# 2. Hot-swap 49 RMSNorm + 24 SwiGLU MLP layers in memory
report = autokernel.patch_hf(merged_model)
print(report.total_patched)  # -> 73 (0 weight bytes copied)

# 3. Verify speedup, max_abs_diff, and top-1 agreement
bench = autokernel.verify_parity_and_speedup(
    stock_fn, patched_fn, sample_input
)
# Reversible anytime: autokernel.unpatch_hf(merged_model)
```

---

### Slide 17: Stage 3: SpecGuard TPU — SGLang Prefix Cache & 16-File Burst
- **Module**: Module 4 • SpecGuard TPU Serving & Audit
- **Pacing**: `00:50 – 00:55 (5m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Click `specguard_dashboard.png` to show the 3-panel SpecGuard TPU results.

🗣️ SAY VERBATIM:
"Now let's complete the story in Stage 3: serving our merged checkpoint in production with `sglang-torchtpu`. In a real repository or payment compliance audit, every query shares a long prefix—our organization's security rubric, PCI-DSS / TorchTPU rule definitions, and shared AST header (~1,357 tokens). On Pass 1 (Cold Cache), SGLang computes the prefill in `102.86 ms`. On Pass 2 and Pass 3, SGLang's RadixAttention matches `1,280` prefix tokens directly in TPU HBM KV cache, dropping Time-to-First-Token to `41.80 ms`—a `2.46x` TTFT speedup! And when a pull request triggers a 16-file concurrent burst, continuous batching processes all 16 audits in just `2.05 seconds`!"
```

---

### Slide 18: How Engineering Teams Adopt This Stack in 3 Steps
- **Module**: Module 4 • The Engineering Adoption Playbook
- **Pacing**: `00:55 – 00:58 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Summarize the 3-step adoption path for PayPal engineering teams.

🗣️ SAY VERBATIM:
"To bring this exact workflow into your service tomorrow, here is the 3-step playbook. Step 1: install `autokernel` (`pip install -e ./autokernel`) and connect `tpu-agent-suite` and `colab-mcp` to your TPU pod. Step 2: run static-shape `bfloat16` LoRA adaptation on `torch.device('tpu')` and call `autokernel.patch_hf(model)` to fuse memory-bound RMSNorm and SwiGLU ops in VMEM. Step 3: serve the merged checkpoint with `sglang-torchtpu` or `vllm-torchtpu` with RadixAttention prefix caching enabled."
```

#### 💻 On-Slide Command / Prompt (`End-to-End Reproduction Commands`):
```bash
# 0. Install & test reusable autokernel package (10/10 PASS)
pip install -e ./autokernel && pytest autokernel/tests/

# 1. Run 4-way AutoKernel Lab (Eager / DAF / Compile / Pallas)
python demos/06_autokernel_app/autokernel_lab.py all

# 2. Run Multi-Model Domain LoRA + 73-Submodule Pallas Patching
python demos/07_domain_adaptation_showcase/domain_adapt_and_pallas_patch.py

# 3. Run SpecGuard LoRA + SGLang Prefix Cache & 16-File Burst
python demos/05_specguard_app/stage2_serve_and_audit.py
```

---

### Slide 19: Executive Summary: Verified Cloud TPU (`tpu7x`) Results
- **Module**: Module 4 • Summary of Empirical Benchmarks
- **Pacing**: `00:58 – 01:00 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Leave this executive summary card up for a moment so attendees can capture the complete benchmark table.

🗣️ SAY VERBATIM:
"Here is the complete scoreboard from my live runs on `tpu7x` Chip 0. Across two model families and two compliance domains, perplexity collapsed to `~1.00` in under 40 steps; my `autokernel` Pallas library delivered `4.81x` to `6.32x` operator speedups and a `1.21x` full-model forward-pass speedup inside Hugging Face; and SGLang RadixAttention delivered a `2.46x` Warm TTFT speedup while auditing 16 concurrent files in `2.05 seconds`."
```

---

### Slide 20: Thank You!
- **Module**: Module 4 • Wrap-Up & Q&A
- **Pacing**: `01:00 – 01:05 (5m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Thank the team and open the floor for engineering questions!

🗣️ SAY VERBATIM:
"Thank you all for joining! Scan the QR codes on the right to grab the master Colab notebooks, the pip-installable `autokernel` package, and this slide deck. What questions can I answer about running PyTorch, LoRA, Pallas kernels, or SGLang on Cloud TPU?"
```

---
