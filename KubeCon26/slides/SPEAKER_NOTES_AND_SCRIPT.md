# 🎤 Speaker Notes, Live Demo Runbook & Verbatim Talk Script

## **Defeating the Prefix-Cache Penalty: KV-Aware Routing and Disaggregated Serving for Agent Fleets on GKE**
- **Event**: KubeCon 2026 Technical Session (15 Minutes + Q&A)
- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)
- **Companion Repository**: [https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26](https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26)

---

## ⚡ How to Present Directly from This Folder

1. **Option A — Interactive Google-Branded Web Deck + Dual-Screen Presenter Console (Recommended)**:
   - Open `slides/index.html` in Chrome (or serve via `make slides-serve`).
   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** (`speaker-notes.html`) on your laptop screen while dragging the main slide window to the stage projector.
   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.
   - Press **`B`** to toggle the bottom presenter toolbar (includes the 15-minute talk clock).
   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.
2. **Option B — Google Slides / PowerPoint Presenter View**:
   - Open `slides/KubeCon26-FleetKV-GKE.pptx` in Google Slides, PowerPoint, or Keynote.
   - Every slide uses the Google Cloud Labs master layouts with complete speaker notes embedded in the native Speaker Notes pane.
3. **Option C — Slidev Markdown Deck**:
   - Run `npx @slidev/cli slides/slides.md` if you prefer the Slidev workflow.

---

## ⏱️ 15-Minute Pacing Schedule & Live Demo Cue Sheet

| Clock Time | Duration | Section | Slides | Stage Action / Key Proof Point |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 – 01:20** | 1m 20s | **Opening & Companion Repo** | Slides 1–3 | Frame stateless K8s vs. agent trees; share repo & slide QR codes |
| **01:20 – 03:20** | 2m 00s | **Part 1: Agent Trees & Fork-Storms** | Slides 4–5 | 20,480-token trunk (`80` blocks) + 8-way fork + `8,192`-tok log burst |
| **03:20 – 05:00** | 1m 40s | **Part 2: Two Routing Failure Modes** | Slide 6 | Failure Mode 1 (`1/N` scatter) vs. Failure Mode 2 (Prefix-Herd Trap) |
| **05:00 – 08:30** | 3m 30s | **Part 3: FleetKV + TorchTPU Disagg** | Slides 7–9 | HBM Fit Gate, staged prefill leases, `TPUConnectorHMA` Tier-2 DRAM |
| **08:30 – 11:45** | 3m 15s | **Part 4: Live 3-Stage Traffic Flip** | Slide 10 | Switch to `tmux`: flip `stage1` → `stage2` → `stage3` on 4-col TUI |
| **11:45 – 13:30** | 1m 45s | **Part 5 & 6: Scorecard & Invariants** | Slides 11–12 | Twin Gate G1 + GKE TPU v6e numbers; 3 CI-audited GKE invariants |
| **13:30 – 15:00** | 1m 30s | **Wrap-Up & Q&A** | Slides 13–14 | Copy-paste reproduction commands & Q&A |

---

## 📋 Slide-by-Slide Verbatim Speaker Script & Code Snippets

### Slide 1: Defeating the Prefix-Cache Penalty: KV-Aware Routing & Disaggregated Serving for Agent Fleets on GKE
- **Section**: Session Opening
- **Pacing**: `00:00 – 00:35`

#### 🎙️ Speaker Notes:
```text
[00:00 - 00:35]
Kubernetes services were built around a simple assumption: HTTP requests are independent, pods are interchangeable, and round-robin spreads load evenly.

When you run an autonomous SWE or SRE agent fleet behind a stateless Service, you spend most of your accelerator cycles recomputing identical prompt prefixes across replicas. And if you switch to naive longest-prefix sticky routing, parallel agent fan-out herds onto a single pod and makes P95 tail latency worse than round-robin.

In this session, we will walk through why both failures happen and how we fix them using Gateway API Inference Extension and disaggregated TorchTPU serving on GKE.
```

---

### Slide 2: Rabimba Karanjai
- **Section**: Speaker & Companion Artifact
- **Pacing**: `00:35 – 01:00`

#### 🎙️ Speaker Notes:
```text
[00:35 - 01:00]
I'm Rabimba Karanjai, a Google Developer Expert for AI/ML and ML Scientist at PayPal.

Everything we cover today—the Go 1.23 Envoy ext_proc router, the GKE Cloud TPU v6e and GAIE manifests, and the trace-calibrated local digital twin—is open-source under Apache-2.0 in our companion repository.
```

---

### Slide 3: Scan to Grab the Companion Artifact & Slides
- **Section**: Companion Repository & Resources
- **Pacing**: `01:00 – 01:20`

#### 🎙️ Speaker Notes:
```text
[01:00 - 01:20]
If you want to run the benchmark on your laptop or deploy the manifests on GKE, scan the left QR code for the companion repo, or the middle QR code for this interactive slide deck.
```

---

### Slide 4: Chatbots Are Lines. Agent Fleets Are Trees.
- **Section**: Part 1: The Agent Tree Workload
- **Pacing**: `01:20 – 02:30`

#### 🎙️ Speaker Notes:
```text
[01:20 - 02:30]
Why do agent fleets break standard serving pools? Because a chatbot is a line, whereas an agent workflow is a tree.

When an incident orchestrator triggers on an alert, it assembles a 20,480-token shared trunk—80 blocks of 256 tokens holding MCP tool schemas, repository structure, and alert state—and at millisecond zero spawns 8 parallel sub-agents. Each sub-agent pulls 8,192 tokens of pod logs and diffs before converging on a synthesis turn. Over the episode, 85.6% of tokens across those branches are shared prefix blocks.
```

---

### Slide 5: Anatomy of an 8-Way Incident Orchestrator Fork-Storm
- **Section**: Part 1: Fork-Storm Topology
- **Pacing**: `02:30 – 03:20`

#### 🎙️ Speaker Notes:
```text
[02:30 - 03:20]
Look at the token budget across a single orchestrator episode. Blocks 0 through 79 form the 20,480-token parent trunk. When the orchestrator forks 8 sub-agents simultaneously, all 8 child requests carry those exact 80 block hashes, followed by a 2-block role delta and a 32-block (8,192-token) log burst on Turn 2. Finally, the join turn reuses the original 80-block trunk.
```

---

### Slide 6: Failure Mode 1: Stateless K8s Round-Robin & Failure Mode 2: The Prefix-Herd Trap
- **Section**: Part 2: Two Routing Failure Modes
- **Pacing**: `03:20 – 05:00`

#### 🎙️ Speaker Notes:
```text
[03:20 - 05:00]
Behind a standard Kubernetes Service, round-robin scatters those 8 child branches across all replicas. Every replica misses on the parent trunk, recomputes 20,480 tokens of prefill, and stalls co-located decode streams past 133 milliseconds P99 ITL.

The natural next step is enabling longest-prefix sticky routing. That triggers a second failure mode during parallel agent fan-out: the Prefix-Herd Trap. At fork time, all 8 sub-agents match 80 out of 80 parent blocks on Pod 0. A router that maximizes prefix match sends all 8 concurrent branches to Pod 0 while Pods 1 through 3 sit idle. Worse, as those 8 branches append 8,192-token log bursts on Pod 0, they exceed Pod 0's 360-block HBM capacity and LRU-evict the shared parent trunk right before the synthesis join turn.
```

---

### Slide 7: Why KV-Aware Routing & Disaggregation Need Each Other
- **Section**: Part 3: Co-Designing Routing & Disaggregation
- **Pacing**: `05:00 – 06:15`

#### 🎙️ Speaker Notes:
```text
[05:00 - 06:15]
This is why routing and disaggregation have to work together. KV-aware routing on an aggregated pool ties compute affinity to memory residency, herding forked branches onto whichever pod holds the parent trunk. Disaggregation without KV-aware fit routing still recomputes shared prefixes.

When we combine them, Prefill pods compute the shared trunk once, pin evicted blocks in 48 GiB of host DRAM, compute only the branch delta, and stream KV blocks over gVNIC to whichever Decode pod has HBM headroom.
```

---

### Slide 8: Control Plane: Fit-Aware Tree Routing in GAIE ext_proc
- **Section**: Part 3: Control Plane (FleetKV EPP)
- **Pacing**: `06:15 – 07:30`

#### 🎙️ Speaker Notes:
```text
[06:15 - 07:30]
Here is the scoring function inside fleetkv-epp. Every vllm-torchtpu prefill pod publishes BlockStored and BlockRemoved events over ZeroMQ on port 5557 as 256-token blocks enter HBM or spill to host DRAM.

When Envoy forwards a request over ext_proc, the router first checks the HBM Fit Gate: if admitting another branch plus our 24-block safety reserve would overflow the pod's free HBM blocks, it spills that branch to a peer pod instead of evicting the shared trunk. Second, notice our staged lease accounting: we release InFlightPrefillTokens as soon as ResponseHeaders arrive at TTFT, while holding the HBM block reservation until the SSE decode stream completes.
```

#### 💻 On-Slide Code / Command (`go (router/pkg/scorer/policies.go)`):
```bash
func ScoreEndpoint(pod *PodState, req *RouteInput) float64 {
    // 1. Hard HBM Fit Gate: spill to peer if branch horizon overflows HBM
    effectiveFree := pod.FreeHBMBlocks - pod.ReservedBlocks
    if effectiveFree < req.EstimatedBranchBlocks + SafetyReserveBlocks {
        return RejectOverflowSpillToPeer
    }
    // 2. Trade off ZMQ-indexed block hits against in-flight prefill queue
    savedMs   := float64(pod.MatchedHBMBlocks)*HBMBlockMs +
                 float64(pod.MatchedDRAMBlocks)*DRAMBlockMs
    queueWait := float64(pod.InFlightPrefillTokens) / PodTokPerMs
    return savedMs - queueWait
}
```

---

### Slide 9: Data Plane: vllm-torchtpu + TPUConnectorHMA on GKE
- **Section**: Part 3: Data Plane (vllm-torchtpu + HMA)
- **Pacing**: `07:30 – 08:30`

#### 🎙️ Speaker Notes:
```text
[07:30 - 08:30]
On the data plane, our DisaggregatedSet runs vllm-torchtpu on GKE Trillium ct6e-standard-4t node pools. Prefill pods mount a 64 GiB /dev/shm volume and allocate 48 GiB to TPUConnectorHMA as a Tier-2 host DRAM cache, keeping shared agent trunks warm even when active branch deltas cycle through HBM.

Once a prefill pod computes the branch delta, it transfers the KV blocks asynchronously over an MTU-8896 gVNIC network to the Decode pod selected by fleetkv-epp. Let's switch to the live terminal and watch all three stages under load.
```

---

### Slide 10: Live Demo: 3-Stage Traffic Flip Under 64-Branch Fork-Storm
- **Section**: Part 4: Live 3-Stage Traffic Flip Demo
- **Pacing**: `08:30 – 11:45`

#### 🎙️ Speaker Notes:
```text
[08:30 - 11:45]
[SWITCH TO TMUX TERMINAL]
1. Stage 1 (round_robin): Point out the 4-pod even traffic split (25% each), low cache hit rate (~30.8% in the local twin, ~19.4% on 8-chip GKE), and P99 decode ITL at 133 ms from prefill-decode interference.
2. Run ./bench/demo_ctl.sh stage2: Watch Stage 1 freeze in Column 1 while Stage 2 skews onto a single hot pod as all 8 forked branches match the 80-block trunk. HBM evictions climb past 10,500 blocks and P95 tail TTFT spikes to 33.4 seconds—worse than Stage 1.
3. Run ./bench/demo_ctl.sh stage3: Watch fleetkv-epp emit herd_spillover decisions, pinning the trunk in prefill HBM/DRAM while splitting decode streams evenly across decode-0 and decode-1. HBM evictions drop to 0, hit rate reaches 86.1% (91.6% on GKE), and P99 ITL drops to 33.1 ms (< 40 ms SLO).
```

#### 💻 On-Slide Code / Command (`Operator Shell — 3-Pane Conference TUI`):
```bash
# Launch 3-pane tmux layout (Scorecard TUI + EPP Route Stream + Shell)
./bench/demo_ctl.sh prep

# Flip live traffic across all 3 architectures:
./bench/demo_ctl.sh stage2   # Trigger single-pod herd & HBM thrash
./bench/demo_ctl.sh stage3   # Enable FleetKV Fit Gate + Disagg P/D
```

---

### Slide 11: Benchmark Scorecard: Gate G1 Twin & GKE Cloud TPU v6e
- **Section**: Part 5: Empirical Benchmark Scorecard
- **Pacing**: `11:45 – 12:30`

#### 🎙️ Speaker Notes:
```text
[11:45 - 12:30]
Here are both sets of numbers side by side: the local trace-calibrated twin verified by make gate-g1 on 416 requests per stage, and the 8-chip GKE TPU v6e hardware reference (2x ct6e-standard-4t).

In both environments, Stage 2's naive sticky routing makes P95 tail TTFT worse than stateless round-robin—33.4 seconds in the 4-pod twin and 3.89 seconds on GKE—because all 8 forked branches queue on a single replica and evict over 10,500 HBM blocks. Stage 3 cuts median TTFT by 82 to 88 percent, eliminates HBM evictions, and keeps P99 decode ITL at 27 to 33 milliseconds.
```

---

### Slide 12: Three Production Invariants (Audited in CI by Gate G2)
- **Section**: Part 6: Production GKE Invariants
- **Pacing**: `12:30 – 13:30`

#### 🎙️ Speaker Notes:
```text
[12:30 - 13:30]
Three operational invariants before you deploy this on GKE—all enforced by tests/test_g3_k8s_manifests.py in CI.

First, set PYTHONHASHSEED="0" on every container; otherwise Python's per-process hash randomization causes block hash mismatches across workers. Second, set --block-size 256 on both vllm-torchtpu and fleetkv-epp so Pallas paged-attention kernels fit inside TPU v6e Scalar Memory. Third, use a Kubernetes Headless Service (clusterIP: None) filtered to llm-d.ai/role=prefill so the router subscribes to every prefill pod's ZMQ socket individually, and configure mtu: 8896 on your gVNIC VPC.
```

---

### Slide 13: Reproduce Locally in 60 Seconds or Deploy on GKE TPU v6e
- **Section**: Reference: GKE & Local Commands
- **Pacing**: `13:30 – 14:00`

#### 🎙️ Speaker Notes:
```text
[13:30 - 14:00]
Here is the complete command reference for both environments. On the left, make gate-all runs our Go race-detector unit tests, cross-language SHA-256 block-hash parity checks, the 3-stage end-to-end fork-storm benchmark, and the Kubernetes manifest audit. On the right are the four commands to bootstrap the MTU-8896 GKE cluster, apply the DisaggregatedSet and InferencePool manifests, and run the exact same stage controller against a live GKE Gateway VIP.
```

#### 💻 On-Slide Code / Command (`Snippet`):
```bash
# Run all verification gates (Go race + E2E SLOs + K8s YAML)
make gate-all

# Launch interactive 3-pane conference TUI
./bench/demo_ctl.sh prep
./bench/demo_ctl.sh stage2
./bench/demo_ctl.sh stage3

./deploy/gke/00-bootstrap-gke-tpu.sh
kubectl apply -f deploy/gke/01-baseline-agg-service.yaml
kubectl apply -f deploy/gke/02-disaggregatedset-torchtpu.yaml
kubectl apply -f deploy/gke/03-fleetkv-epp-and-pool.yaml

FLEETKV_GATEWAY_URL="http://${GATEWAY_VIP}" \
  ./bench/demo_ctl.sh stage3 --target=gke
```

---

### Slide 14: Thank You!
- **Section**: Closing & Q&A
- **Pacing**: `14:00 – 15:00`

#### 🎙️ Speaker Notes:
```text
[14:00 - 15:00]
To wrap up: agent fleets generate tree-structured bursts, not independent linear turns. By combining a fit-aware GAIE ext_proc router with disaggregated vllm-torchtpu and Tier-2 host DRAM on GKE, you keep shared trunks warm without herding parallel sub-agents onto a single pod.

The Go router, GKE manifests, local digital twin, and automated test gates are all in the companion repository. Thank you—happy to take questions!
```

---
