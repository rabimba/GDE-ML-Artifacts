# 🎤 Speaker Notes, Facilitator Runbook & Verbatim Talk Script

## **Full-Stack PyTorch on Cloud TPU: Domain Adaptation, Pallas Kernel Fusion & High-Throughput Serving**
- **Format**: Interactive Hands-On Workshop (1 hr 15 mins / 75 minutes)
- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML)
- **Notebooks & Code**: `torchtpu-inference-workshop-main/notebooks/04..06_*.ipynb` & `demos/05..07_*/`

---

## ⚡ How to Present Directly from This Folder

1. **Option A — Interactive Web Deck + Dual-Screen Presenter Console (Recommended)**:
   - Run `./present.sh` in this folder (or open `index.html` in Chrome).
   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** on your laptop screen while dragging the main slide window to the projector!
   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.
   - The bottom control bar is hidden from the audience by default and in fullscreen. Press **`B`** to toggle it (all functions also work via hotkeys: `S`/`P`/`G`/`F`/arrows).
   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.
2. **Option B — Google Slides / PowerPoint Presenter View**:
   - Upload `TorchTPU_FullStack_Showcase_Workshop.pptx` to Google Slides (File → Import slides / Open) or open in PowerPoint/Keynote.
   - Every slide has the complete speaker notes embedded in the native Speaker Notes pane.
3. **Option C — Tablet / Phone Companion**:
   - Open `speaker-notes.html` or this `SPEAKER_NOTES_AND_SCRIPT.md` file to scroll through every slide's verbatim notes and copy-paste prompts.

---

## ⏱️ 75-Minute Pacing Schedule & Checkpoints

| Clock Time | Duration | Module | Slides | Interactive Element / Checkpoint |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 – 00:06** | 6 min | **Module 0: Welcome, Speaker & Artifacts** | Slides 1–3 | Notebooks (`04`–`06`), Demos & Repo Links |
| **00:06 – 00:23** | 17 min | **Module 1: Enterprise Story & Architecture** | Slides 4–8 | 🎤 Poll #1 + 4-Stage Architecture + `colab-mcp` + 🎯 Quiz |
| **00:23 – 00:36** | 13 min | **Module 2: Multi-Model Domain LoRA on TPU** | Slides 9–12 | `Qwen3-0.6B` (SecOps) & `Qwen2.5-0.5B` (FinTech PCI-DSS) |
| **00:36 – 00:50** | 14 min | **Module 3: AutoKernel Lab (XProf & Pallas)** | Slides 13–16 | 4-Mode XProf Waterfall + 73-Submodule HF Pallas Patching |
| **00:50 – 01:05** | 15 min | **Module 4: SpecGuard SGLang Serving & Playbook** | Slides 17–20 | `2.46x` Prefix Cache TTFT + 16-File Burst + Q&A |

---

## 📋 Slide-by-Slide Verbatim Speaker Script & Copy-Paste Prompts

### Slide 1: Full-Stack PyTorch on Cloud TPU: From Domain LoRA & Pallas Kernels to Prefix-Cached Serving
- **Module**: Module 0 • Welcome & Vision
- **Pacing**: `00:00 – 00:02 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Welcome the audience with high energy! Ensure the cover slide is projected clearly.

🗣️ SAY VERBATIM:
"Welcome everyone! Today we are going beyond isolated micro-benchmarks to walk through a complete, end-to-end production AI story on Google Cloud TPU using native PyTorch (`torch_tpu`). We will see how a developer or an AI coding agent can start in a standard Google Colab notebook connected over MCP to a live Cloud TPU (`tpu7x`), adapt multiple open-weight models to specialized enterprise domains like SecOps and FinTech PCI-DSS compliance using LoRA, inspect hardware bottlenecks with XProf, inject custom Pallas kernels directly into Hugging Face Transformer layers, and serve the merged checkpoints with SGLang RadixAttention prefix caching and continuous batching."
```

---

### Slide 2: Rabimba Karanjai
- **Module**: Module 0 • Speaker Intro
- **Pacing**: `00:02 – 00:04 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Briefly introduce yourself and why this workflow matters in production AI.

🗣️ SAY VERBATIM:
"I'm Rabimba Karanjai, a Google Developer Expert for AI/ML. Building production LLM systems, automated compliance auditors, and developer guardrails taught me one lesson: model quality, kernel latency, and serving economics cannot live in separate silos. If you fine-tune a domain model that triggers XLA recompilations or re-computes 1,200 tokens of policy context on every request, your tail latency explodes. Today's showcase unifies those layers into one repeatable playbook."
```

---

### Slide 3: Workshop Notebooks, Demos & Agent Suite
- **Module**: Module 0 • Notebooks & Artifacts
- **Pacing**: `00:04 – 00:06 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Point attendees to the three artifacts in the repository.

🗣️ SAY VERBATIM:
"All of today's code lives in three self-contained Colab notebooks (`04_specguard_e2e_app.ipynb`, `05_autokernel_pallas_lab.ipynb`, and our master notebook `06_end_to_end_showcase_and_domain_adaptation.ipynb`) plus standalone CLI scripts under `demos/05_specguard_app`, `06_autokernel_app`, and `07_domain_adaptation_showcase`. Every number on these slides was captured live on a Cloud TPU (`tpu7x` Chip 0)."
```

---

### Slide 4: Why Do Enterprise AI Guardrails Hit a Wall in Production?
- **Module**: Module 1 • The Enterprise Challenge
- **Pacing**: `00:06 – 00:09 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Ask the audience to raise hands for A, B, or C.

🗣️ SAY VERBATIM:
"Let's start with the real-world problem. Suppose you are building an automated compliance and code auditing platform for a FinTech or enterprise engineering org. First, base models don't know your strict output schema or domain rules—like flagging unmasked PANs under PCI-DSS 3.3.1 or catching deprecated `torch_xla` calls. Second, if you run naive eager PyTorch on TPU, every tiny op dispatches separately and hammers HBM. Third, when you audit 16 files in a pull request, you re-compute the exact same 1,280-token policy header 16 times!"
```

---

### Slide 5: Anatomy of an AI Coding Agent
- **Module**: Module 1 • The Three Pillars
- **Pacing**: `00:09 – 00:12 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk across the three pillars on screen.

🗣️ SAY VERBATIM:
"Our solution rests on three pillars. Pillar 1 is `torch_tpu`: the TPU is simply `torch.device('tpu')`, letting us run Hugging Face `peft` LoRA fine-tuning across multiple domain models with zero `torch_xla` boilerplate. Pillar 2 is hardware-aware optimization: using XProf and `torch.tpu.pallas.jax_op` to fuse memory-bound ops in TPU VMEM and hot-patch Hugging Face models in-place. Pillar 3 is production serving with `sglang-torchtpu` and `vllm-torchtpu`, exploiting RadixAttention prefix caching and continuous batching."
```

---

### Slide 6: The 4-Stage Full-Stack TorchTPU Architecture
- **Module**: Module 1 • End-to-End Architecture
- **Pacing**: `00:12 – 00:16 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Point to the 4-layer architecture diagram on the right (remind attendees they can click any chart in the web deck to zoom in full-screen).

🗣️ SAY VERBATIM:
"Look at how the four stages connect on the right. At the top, `colab-mcp` and `tpu-agent-suite@0.7.0` give both humans and AI agents direct execution access to the TPU pod. In Stage 2, we run multi-model LoRA fine-tuning in `bfloat16` on `torch.device('tpu')`. In Stage 3, we profile with XProf and hot-patch 73 submodules inside the Hugging Face model with custom Pallas kernels. And in Stage 4, we hand the merged checkpoint to SGLang and vLLM for high-throughput serving."
```

---

### Slide 7: Developer Workflow: Colab MCP + TPU Agent Suite
- **Module**: Module 1 • Interactive Developer Setup
- **Pacing**: `00:16 – 00:20 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Highlight the PJRT initialization order in the code box on the right—this is a critical practical tip for developers.

🗣️ SAY VERBATIM:
"Here is a golden developer tip when combining `torch_tpu` and JAX Pallas on the same chip. Both PyTorch and JAX talk to the TPU through `libtpu` and PJRT. If you import `jax` before `torch_tpu` initializes its PJRT client, or if `TPU_VISIBLE_DEVICES` conflicts with `TPU_VISIBLE_CHIPS`, they will fight over the `/dev/vfio` device lock. By popping `TPU_VISIBLE_DEVICES`, pinning `TPU_VISIBLE_CHIPS='0'`, and allocating one tensor on `torch.device('tpu')` followed by `torch.accelerator.synchronize()` before importing `jax`, both frameworks share the chip seamlessly!"
```

#### 💻 On-Slide Command / Prompt (`.opencode/opencode.jsonc & TPU Chip 0 Isolation`):
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

# 2. Single-Chip PJRT Sharing (PyTorch + JAX Pallas)
os.environ.pop("TPU_VISIBLE_DEVICES", None)
os.environ["TPU_VISIBLE_CHIPS"] = "0"
os.environ["TPU_CHIPS_PER_HOST_BOUNDS"] = "1,1,1"
import torch, torch_tpu
_ = torch.ones(1, device="tpu")  # Acquire PJRT first!
torch.accelerator.synchronize()
import jax  # Shares PJRT client with torch_tpu
```

---

### Slide 8: Native PyTorch on TPU (torch_tpu) & What to Avoid on Cloud TPU
- **Module**: Module 1 • Native torch_tpu vs Legacy Stack
- **Pacing**: `00:20 – 00:23 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Contrast the blue card (`torch_tpu` best practices) with the red card (anti-patterns).

🗣️ SAY VERBATIM:
"Let's make sure everyone has the mental model of `torch_tpu`. First, `torch_xla` is deprecated—everything we do uses `import torch, torch_tpu` and `torch.device('tpu')`. Second, TPUs love static shapes and `bfloat16`. When we pad our batches to fixed buckets like `(4, 256)` or `(6, 128)` and mask padding tokens with `-100` in the loss, XLA compiles the training graph once on Step 0 and flies through the remaining steps without a single recompilation."
```

---

### Slide 9: Stage 1: Multi-Model Domain Adaptation
- **Module**: Module 2 • Multi-Model Domain Adaptation
- **Pacing**: `00:23 – 00:25 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Transition to Module 2—showing how domain adaptation works across multiple models and domains.

🗣️ SAY VERBATIM:
"Now let's dive into Stage 1 of our showcase: Multi-Model Domain Adaptation on Cloud TPU. A common question from engineering teams is: does this workflow only work for one toy model, or can we specialize multiple models for different enterprise compliance domains? Let's look at two distinct models and domains we trained on `tpu7x` Chip 0."
```

---

### Slide 10: Specializing Two Distinct Models on `torch.device('tpu')`
- **Module**: Module 2 • Two Models, Two Enterprise Domains
- **Pacing**: `00:25 – 00:29 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Compare Model A (`Qwen/Qwen3-0.6B`) on the left and Model B (`Qwen/Qwen2.5-0.5B-Instruct`) on the right.

🗣️ SAY VERBATIM:
"On the left, we adapted `Qwen/Qwen3-0.6B` to act as a SecOps and PyTorch-TPU Migration Auditor—catching SQL injection, hardcoded secrets, `.item()` sync stalls, and deprecated `torch_xla` code. In 40 steps at `181.7 ms/step`, loss dropped from `2.8536` to `0.0118` and perplexity collapsed from `17.35` to `1.01`. On the right, we took a different architecture—`Qwen/Qwen2.5-0.5B-Instruct`—and adapted it on FinTech PCI-DSS v4.0 and ISO-20022 payment compliance rules. In 30 steps at `105.2 ms/step`, loss dropped from `3.9182` to `0.0021` and domain perplexity collapsed from `50.31` to `1.00`, emitting exact rule citations like `PCI-DSS-3.3.1`!"
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
"Here is the empirical plot generated directly from `domain_adapt_and_pallas_patch.py` on `tpu7x` Chip 0. In Panel 1, you see the step-by-step loss curves for both `Qwen3-0.6B` and `Qwen2.5-0.5B`. In Panel 2, you see the dramatic collapse in domain perplexity—from `17.35` down to `1.01` and from `50.31` down to `1.00`. And in Panel 3, you see what happens when we hot-patch the adapted Hugging Face model in-place with custom Pallas kernels: a `4.81x` speedup across the 24-layer RMSNorm stack and a `1.21x` end-to-end forward-pass speedup across the entire 24-layer Transformer!"
```

---

### Slide 12: Qualitative Verification: Unadapted Base vs. TPU LoRA Adapted
- **Module**: Module 2 • Before vs After Domain Adaptation
- **Pacing**: `00:33 – 00:36 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Highlight the concrete before-and-after text outputs on both cards.

🗣️ SAY VERBATIM:
"Numbers are great, but let's read the actual model outputs. Before LoRA fine-tuning, when we asked `Qwen3-0.6B` to audit a `torch_xla` snippet, it said: 'The use of xm.xla_device() may expose the code to potential security vulnerabilities, update the library.' It had no idea `torch_xla` was deprecated in favor of `torch_tpu`! After 7 seconds of LoRA fine-tuning on one TPU chip, it outputs `[CRITICAL | TPU-DEP-01]` with the exact `torch.device('tpu')` migration fix. And on the right, our adapted `Qwen2.5-0.5B` FinTech model pinpoints `PCI-DSS-3.3.1` PAN logging violations and `TPU-SYNC-02` settlement loop stalls."
```

---

### Slide 13: Stage 2: AutoKernel Lab (XProf & Pallas)
- **Module**: Module 3 • AutoKernel Lab & Pallas Fusion
- **Pacing**: `00:36 – 00:38 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Transition to Module 3—kernel engineering with XProf and Pallas.

🗣️ SAY VERBATIM:
"Once we have an adapted model, how do we make it run as fast as the hardware allows? Welcome to Stage 2: AutoKernel Lab. Here we use the PyTorch TPU profiler (`ProfilerActivity.TPU`) and XProf to see what happens on the chip across four execution modes, and then write custom Pallas kernels that fuse memory-bound operations inside TPU Vector Memory (VMEM)."
```

---

### Slide 14: Benchmarking 4 Execution Modes on a 4-Layer Decoder Stack
- **Module**: Module 3 • The 4 Execution Modes on TPU
- **Pacing**: `00:38 – 00:42 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk through the 4 cards from left to right, emphasizing the XProf program count drop (`47 -> 3 -> 1 -> 1`).

🗣️ SAY VERBATIM:
"Look at the progression across the four cards. In plain Eager mode, a 4-layer decoder block takes `3.591 ms` because it launches 47 separate TPU programs per step—every elementwise op reads and writes HBM. Turning on `TORCH_TPU_DEFER_AND_FUSE=1` cuts that to 3 TPU programs and `2.126 ms` (`1.69x`). `torch.compile(backend='tpu')` captures the whole graph into 1 TPU program at `1.579 ms` (`2.28x`). And with `torch.tpu.pallas.jax_op`, our custom Pallas kernels execute in 1 TPU program with `9.54e-07` numerical parity—and on the isolated 8-layer Residual+RMSNorm stack, Pallas hits `0.409 ms` versus `2.587 ms` eager: a massive `6.32x` kernel speedup!"
```

---

### Slide 15: Inside the XProf Trace: 47 Dispatches vs. 1 Fused Program
- **Module**: Module 3 • XProf Timeline & Pallas Parity
- **Pacing**: `00:42 – 00:46 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Click `autokernel_xprof_waterfall.png` to zoom in on the 4-row XProf waterfall chart.

🗣️ SAY VERBATIM:
"This visualization from `autokernel_lab.py` makes the hardware story unmistakable. Look at the right panel: in Eager mode, the TPU timeline is chopped into 47 micro-launches totaling `3.59 ms`. With `DeferAndFuse`, `torch.compile`, and `Pallas`, the timeline collapses into a tight, continuous block on the MXU and VPU. Even better, Pallas gives us explicit control over VMEM tiling (`BlockSpec((128, d), lambda i: (i, 0))`) and `float32` accumulation precision."
```

---

### Slide 16: How Developers Hot-Patch a Hugging Face Model with Pallas
- **Module**: Module 3 • Hot-Patching Hugging Face with Pallas
- **Pacing**: `00:46 – 00:50 (4m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Walk through the 15-line Python snippet on the right.

🗣️ SAY VERBATIM:
"Developers often ask: 'Once I write a Pallas kernel, how do I actually plug it into a Hugging Face `AutoModelForCausalLM` that I just fine-tuned with PEFT?' Look at the code on the right—it takes 15 lines of Python! We register `pallas_rmsnorm_jax` with `torch.tpu.pallas.jax_op`, wrap it in `PallasPatchedRMSNorm` holding the original parameter tensor `orig_norm.weight`, and loop over `merged_model.model.layers`. In `Qwen2.5-0.5B`, that replaces 73 submodules in-place, cutting 24-layer RMSNorm time by `4.81x` (`4.73 ms -> 0.98 ms`) and full-model forward time from `29.74 ms` to `24.66 ms` (`1.21x`) with `99.74%` top-1 token agreement!"
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
"Now let's complete the story in Stage 3: serving our merged checkpoint in production with `sglang-torchtpu`. In a real repository or payment compliance audit, every query shares a long prefix—your organization's security rubric, rule definitions, and shared AST header (~1,357 tokens). On Pass 1 (Cold Cache), SGLang computes the prefill in `102.86 ms`. On Pass 2 and Pass 3, SGLang's RadixAttention matches `1,280` prefix tokens directly in TPU HBM KV cache, dropping Time-to-First-Token to `41.80 ms`—a `2.46x` TTFT speedup! And when a pull request triggers a 16-file concurrent burst, continuous batching processes all 16 audits in just `2.05 seconds`!"
```

---

### Slide 18: How Developers Adopt This Stack in 3 Steps
- **Module**: Module 4 • The Developer Adoption Playbook
- **Pacing**: `00:55 – 00:58 (3m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Summarize the 3-step adoption path for engineering teams.

🗣️ SAY VERBATIM:
"If you want to bring this exact workflow back to your team tomorrow, here is the 3-step playbook. Step 1: configure `tpu-agent-suite` and `colab-mcp` against your TPU VM or GKE TPU pod. Step 2: run static-shape `bfloat16` LoRA adaptation on `torch.device('tpu')` and use XProf + `torch.tpu.pallas.jax_op` to fuse any memory-bound custom ops. Step 3: merge the checkpoint and serve with `sglang-torchtpu` or `vllm-torchtpu` with prefix caching enabled."
```

#### 💻 On-Slide Command / Prompt (`End-to-End Reproduction Commands`):
```bash
# 1. Run 4-way AutoKernel Lab (Eager / DAF / Compile / Pallas)
python demos/06_autokernel_app/autokernel_lab.py all

# 2. Run Multi-Model Domain LoRA + 73-Submodule Pallas Patching
python demos/07_domain_adaptation_showcase/domain_adapt_and_pallas_patch.py

# 3. Run SpecGuard LoRA + SGLang Prefix Cache & 16-File Burst
python demos/05_specguard_app/stage1_lora_finetune.py
python demos/05_specguard_app/stage2_serve_and_audit.py
```

---

### Slide 19: Executive Summary: Verified Cloud TPU (`tpu7x`) Results
- **Module**: Module 4 • Summary of Empirical Benchmarks
- **Pacing**: `00:58 – 01:00 (2m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Leave this executive summary card up for a moment so attendees can photograph the complete benchmark table.

🗣️ SAY VERBATIM:
"Here is the complete scoreboard from our live runs on `tpu7x` Chip 0. Across two model families and two compliance domains, perplexity collapsed to `~1.00` in under 40 steps; our Pallas kernels delivered `4.81x` to `6.32x` operator speedups and a `1.21x` full-model forward-pass speedup inside Hugging Face; and SGLang RadixAttention delivered a `2.46x` Warm TTFT speedup while auditing 16 concurrent files in `2.05 seconds`."
```

---

### Slide 20: Thank You!
- **Module**: Module 4 • Wrap-Up & Q&A
- **Pacing**: `01:00 – 01:05 (5m)`

#### 🎙️ Speaker Notes:
```text
🎬 [STAGE DIRECTION]: Thank the audience and open the floor for questions!

🗣️ SAY VERBATIM:
"Thank you all for joining! Scan the QR codes on the right to grab the master Colab notebooks, the Pallas kernel patchers, and this slide deck from `github.com/rabimba/GDE-ML-Artifacts`. I would love to hear what models and custom kernels you build on Cloud TPU—what questions can I answer?"
```

---
