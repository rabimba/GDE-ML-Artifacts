# The Locality Trap: Surviving Agentic Fork Storms with KV-Tier-Aware Routing and Disaggregated Cloud TPUs on GKE

*Companion deep-dive to my KubeCon NA 2026 talk—why naive KV-sticky routing makes tail TTFT 2.7x worse than Round-Robin under parallel agent fan-out, how we built an Envoy ext_proc router and local TPU Digital Twin to fix it, and three distributed-systems bugs we squashed along the way.*

**By Rabimba Karanjai** · Interactive Slide Deck: [rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/](https://rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/) · Reference Source: [github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26](https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26)

---

At KubeCon NA 2026 in Salt Lake City, I presented a 15-minute case study on serving multi-agent workloads over Google Kubernetes Engine (GKE) and Cloud TPU v6e (Trillium). Fifteen minutes on a conference stage gives you just enough room to deliver the high-level architecture, flash the final scorecard, and show a terminal demo. It leaves zero room for the gnarly distributed-systems details: the wire-level Envoy `ext_proc` state machines, the ZeroMQ DNS discovery traps inside Kubernetes, or the debugging scars from tracking down why multi-turn prompt hashes drifted across container boundaries.

This post is the companion deep-dive. It documents the engineering mechanics behind **FleetKV**—an open-source, fit-aware KV router built for the Kubernetes Gateway API Inference Extension (GAIE v1)—and explains why the conventional wisdom around LLM prefix caching breaks down the moment sequential chat turns into parallel agentic execution trees.

All the code, Kubernetes manifests, and a trace-calibrated local Digital Twin are open-sourced in our Google Developer Expert (GDE) reference repository: [github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26](https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26).

---

## 1. When Chat Becomes a Tree: Why Naive Locality Fails

For the past two years, LLM serving teams have optimized for sequential conversational threads. In linear chat, context grows monotonically: turn 1 adds 500 tokens, turn 2 appends another 400 tokens, and turn 3 appends 300 tokens. The cache eviction horizon is predictable, and basic round-robin or least-request load balancing across identical model replicas works well enough.

Agentic systems change the geometry of inference traffic from a linear list into a rapidly branching tree. 

Consider a standard enterprise triage or coding agent:
1. An orchestrator receives a customer query or incident log. It builds a hefty, shared system prompt—retrieval context, API schemas, tool definitions, and few-shot examples—totaling 16,000 to 24,000 tokens (a "shared trunk").
2. Instead of waiting for one answer, the orchestrator spawns four to eight sub-agents concurrently: a query planner, a database extractor, a code runner, and an adversarial verification bot.
3. Each sub-agent inherits the exact same 20,480-token trunk, appends its own 1,000-to-2,000-token branch instruction, and fires a request into the serving cluster at the exact same millisecond.

```
                  [ Shared Trunk System Prompt: 20,480 Tokens ]
                                      │
        ┌───────────────┬─────────────┼───────────────┬───────────────┐
        ▼               ▼             ▼               ▼               ▼
   Branch 1        Branch 2      Branch 3        Branch 4        Branch 5..8
 (SQL Planner)   (Log Parser)   (API Runner)   (Code Sandbox)   (Verifier)
```

At `256 KiB` per token for a 32B model in `bfloat16`, caching that 20,480-token prefix preserves over **5 GiB of Key-Value tensor state**. Recomputing it from scratch on every branch burns tens of millions of systolic matrix multiply operations and spikes hardware Time to First Token (TTFT).

### The False-Obvious Fix and the Prefix-Herd Collapse

The obvious architectural reaction is simple: enable `--enable-prefix-caching` in vLLM and slap a prefix-sticky routing policy in front of the cluster. If Worker `agg-0` already holds the trunk in its High-Bandwidth Memory (HBM), route all matching requests to `agg-0`.

When you test that policy against a real multi-agent fork storm, your cluster suffers a catastrophic **Prefix-Herd Collapse**:

1. **Massive Tail TTFT Inflation**: Every concurrent sub-agent branch matches the same longest prefix on `agg-0`. Instead of distributing compute load, your ingress proxy queues all eight branches on the exact same worker. On our 4-replica benchmark cluster, Stage 1 (Kubernetes Round-Robin) produced a P95 TTFT of **12,497 ms**. Under Stage 2 (Naive KV-Sticky), P95 TTFT spiked to **33,375 ms**—a **2.7x degradation** under identical traffic.
2. **Self-Eviction Cascades**: Worker `agg-0` exhausts its available HBM block pool trying to allocate KV slots for eight concurrent branches. It starts evicting cached blocks—including the very 20,480-token trunk that attracted the traffic in the first place. Across a 416-request test wave, naive stickiness caused **9,931 HBM evictions**.
3. **Decode Starvation (Inter-Token Jitter)**: Because `agg-0` is an aggregated worker running both prefill and decode phases on the same chips, its Matrix Multiply Units (MXUs) freeze existing token-generation streams while crunching through queued 20K-token prefill chunks. P99 Inter-Token Latency (ITL) spiked to **156.5 ms**, well above acceptable streaming thresholds.

> **The Single-Variable Testbed:**
> Vendor benchmarks often disguise these bottlenecks by changing the model weights, using small 2K-token prompts, or ignoring tail latencies. In this work, we held every application variable constant:
> - **Model**: Qwen2.5-32B executed in `bfloat16` with a strict `--block-size 256`.
> - **Workload**: 2 waves of 8 concurrent orchestrators, each spawning an 8-way fork storm (64 active agent branches, 416 streaming requests per stage) sharing a 20,480-token trunk.
> - **Strict Production Goodput SLO**: TTFT ≤ 3,000 ms **AND** TPOT/ITL ≤ 50 ms. Any request missing either threshold counts as zero goodput.
> 
> To allow engineers to replicate these dynamics without spending hundreds of dollars on cloud accelerators, we built a trace-calibrated Python Digital Twin (`twin/tpu_worker_twin.py`) calibrated to real Cloud TPU v6e cycle times. Running `make gate-g1` executes all three stages on a standard developer workstation in under three minutes.

---

## 2. The Two-Plane Solution: FleetKV and Disaggregated TPUs

Solving the locality trap requires decoupling your routing intelligence from naive cache matching and splitting your accelerator topology into specialized hardware roles.

```
[ Ingress Client: 8-Way Fork Storm ]
                 │
                 ▼
     [ Envoy Gateway (:80) ]
                 │  gRPC ext_proc (:9002)
                 ▼
     [ fleetkv-epp Router ] ◄──── ZeroMQ KVEvents (:5557) ──── [ TPU Workers ]
                 │                (HBM + Host DRAM Index)
                 ▼
       x-target-pod Routing
                 │
       ┌─────────┴────────────────────────┐
       ▼                                  ▼
[ vLLM Prefill Pod ]              [ vLLM Decode Pod ]
  • Compute-Bound                   • Memory-Bandwidth-Bound
  • 256-tok Pallas Kernels          • Locked 27ms P99 ITL
  • 64 GiB /dev/shm HMA             • TPUConnectorHMA Transfer
```

### Plane 1: FleetKV Fit-Aware Envoy `ext_proc` Router

Instead of letting an ingress proxy guess worker state based on external HTTP response codes, FleetKV runs as a standalone Go service (`fleetkv-epp`) implementing the Envoy v3 `ExternalProcessor` gRPC protocol. It listens on port `:9002` and integrates directly with the GKE Gateway API Inference Extension via an `InferencePool` specification.

FleetKV maintains a lock-free, concurrency-safe in-memory Radix Tree (`router/pkg/radix/kv_tree.go`). It subscribes to real-time ZeroMQ event streams published by every vLLM worker on port `:5557`:
- `BlockStored`: Block hash inserted into HBM or Tier-2 Host DRAM.
- `BlockRemoved`: Block evicted due to memory pressure.
- `AllBlocksCleared`: Worker reboot or cache reset.

When an 8-way fork storm arrives at Envoy, FleetKV hashes the incoming prompt tokens in deterministic 256-token chunks (`router/pkg/hash/blockhash.go`) and evaluates every worker through its **Fit-Aware Scoring Engine** (`router/pkg/scorer/policies.go`):

```go
// 1. Hard HBM Fit Admission Gate: Reject pods that cannot fit the branch without eviction
if m.Pod.EffectiveFreeHBMBlocks() < estBlocks + cfg.SafetyReserveBlocks {
    continue
}

// 2. Peak Prefill Queue Gate: Shed load if pending prefill backlog exceeds throughput limits
if cfg.PeakPrefillThresholdTokens > 0 && m.Pod.InFlightPrefillTokens > cfg.PeakPrefillThresholdTokens {
    continue
}

// 3. Marginal Saved Prefill Cost minus Live Queue Wait Time
marginalSavedMs := float64(m.MatchedHBMBlocks) * hbmSavedPerBlock + 
                   float64(m.MatchedDRAMBlocks) * dramSavedPerBlock

queueWaitMs := (float64(m.Pod.InFlightPrefillTokens) / cfg.PodThroughputTokPerMs) +
               (float64(m.Pod.ActiveRequests) * cfg.ActiveDecodeWeightMs) +
               (float64(m.Pod.ReservedBlocks) * 0.05)

score := marginalSavedMs - queueWaitMs
```

If Worker `agg-0` already holds the 80-block prefix but is running out of headroom, its score drops immediately. FleetKV admits the first three branches to `agg-0` (maximizing cache reuse) and automatically spills branches 4 through 8 over to `agg-1` or Tier-2 Host DRAM before `agg-0` can trigger an eviction cascade.

### Plane 2: TorchTPU P/D Disaggregation and Tier-2 Memory

Routing alone cannot fix the fundamental hardware tension of aggregated serving: large, ragged prefill chunks require maximum compute throughput, while autoregressive decode loops are starved for memory bandwidth.

On Google Cloud TPU v6e (Trillium), we deploy a disaggregated architecture using GKE's `DisaggregatedSet` (`deploy/gke/02-disaggregatedset-torchtpu.yaml`):
1. **Prefill Workers (`role: prefill`)**: Sized for massive parallel matrix operations. Configured with `--block-size 256` to match the Scalar Memory (SMEM) limits of Pallas paged-attention kernels.
2. **Tier-2 Memory Spillover (`TPUConnectorHMA`)**: Each worker maps a 64 GiB `emptyDir: Memory` volume to `/dev/shm`. When TPU HBM fills, older KV blocks are copied via high-speed host DMA into host RAM rather than discarded. Loading a block from host RAM to HBM over PCIe takes a fraction of the time required to recompute 256 tokens through the systolic array.
3. **Decode Workers (`role: decode`)**: Dedicated exclusively to continuous token generation. Free from prefill interruptions, decode pods deliver a jitter-free streaming experience with a P99 ITL of **27 ms** on real TPU v6e chips (**33.1 ms** in our Digital Twin).

---

## 3. Where the Wheels Came Off: Three Distributed-Systems Bugs

Building a clean architecture on paper is straightforward; making it survive high-concurrency fork storms under live telemetry exposed three subtle bugs that required surgical fixes.

### Bug 1: Phantom Prefill Leases Cripple Upstream Routing

**The Failure:** When FleetKV routed a request, it reserved an `InFlightPrefillTokens` lease on the target worker to prevent subsequent requests from double-booking its compute pipeline. In our initial implementation, this lease was held until the entire HTTP request finished. 

For a streaming response generating 500 tokens, the request stays open for 10 to 15 seconds. Even though the worker completed the 20,480-token prefill in 300 milliseconds and transitioned immediately to low-overhead decode, FleetKV’s `queueWaitMs` formula continued to penalize the worker as if its prefill MXU pipeline was 100% saturated. As a result, the router refused to send new requests to perfectly idle prefill workers.

**The Fix:** We refactored `router/pkg/extproc/server.go` and `router/pkg/radix/kv_tree.go` into a two-stage lease lifecycle:
- `AcquireStagedLease(podID, estBlocks, unmatchedTokens)` returns two distinct release handles: `releasePrefillFn` and `releaseFn`.
- In the Envoy `ext_proc` event loop, FleetKV inspects downstream stream events. The exact moment Envoy receives `ResponseHeaders` from the backend worker (signaling that the first output token has been produced and prefill is finished), FleetKV calls `ReleasePrefill()`.
- The remaining lightweight `ActiveRequests` token lease is held until `ResponseBody.EndOfStream` or context cancellation.

```go
// router/pkg/extproc/server.go
case *extprocv3.ProcessingRequest_ResponseHeaders:
    // TTFT achieved! Backend produced first token; prefill phase complete.
    if ctx.routeDecision != nil {
        ctx.routeDecision.ReleasePrefill()
    }
    return &extprocv3.ProcessingResponse{...}
```

### Bug 2: The Kubernetes ClusterIP ZeroMQ Blackhole

**The Failure:** To discover TPU workers, `fleetkv-epp` was initially pointed at the Kubernetes Service DNS name: `tcp://vllm-prefill-service:5557`. In Kubernetes, standard Services use `ClusterIP` virtual IP addresses managed by `kube-proxy` (iptables or IPVS). 

ZeroMQ `SUB` sockets establish long-lived TCP connections. When `fleetkv-epp` initialized its subscriber socket, `kube-proxy` mapped that single TCP handshake to **one random prefill pod**. FleetKV successfully ingested cache events from `prefill-0`, but was completely blind to cache allocations on `prefill-1`, `prefill-2`, and `prefill-3`. The router's radix tree remained starved of cluster state, causing erratic routing decisions.

**The Fix:** We switched the Kubernetes Service definition to a **Headless Service** (`clusterIP: None` in `deploy/gke/03-fleetkv-epp-and-pool.yaml`):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fleetkv-prefill-headless
  namespace: fleetkv-serving
spec:
  clusterIP: None
  selector:
    llm-d.ai/role: prefill
  ports:
    - name: http-inference
      port: 8000
    - name: zmq-kvevents
      port: 5557
```

In the Go subscriber client (`router/pkg/zmqsub/subscriber.go`), we implemented periodic DNS SRV / multi-A record polling via `net.LookupHost`. FleetKV resolves every backing pod IP address and attaches distinct, parallel ZeroMQ TCP connections (`tcp://<pod-ip>:5557`) across the entire worker fleet.

### Bug 3: Multi-Turn Block Boundary Drift Spikes ITL

**The Failure:** In Stage 1 and Stage 2 testing, Turn 1 requests hit the cache cleanly, but Turn 2 and Turn 3 requests experienced unexpected cache misses, dropping the effective hit rate by over 30% and causing sudden P99 ITL spikes up to 173 ms.

**The Fix:** Digging into the block hashing logic revealed a token alignment mismatch. In vLLM, blocks are strictly allocated on 256-token multiples. If Turn 1 ends at token offset 20,600, that corresponds to 80 full blocks (20,480 tokens) plus 120 residual tokens. 

When Turn 2 added a 150-token user response, our initial router code hashed Turn 2 starting from index 0 of the new text. This created an artificial 150-token chunk that misaligned all subsequent 256-token boundaries with vLLM's internal KV allocator!

We updated `router/pkg/hash/blockhash.go` to support a `tail_tokens` carry-over buffer:
```go
// Carry over unaligned tail tokens from prior turns to maintain 256-token block parity
combined := append(tailTokens, newTokens...)
fullBlocks := len(combined) / blockSize
newTail := combined[fullBlocks*blockSize:]
```
We also enforced `PYTHONHASHSEED="0"` across all container environments to ensure Python's string hashing and Go's SHA-256 block hashing produced bit-identical keys across process boundaries.

---

## 4. Empirical Scorecard: Local Digital Twin vs. GKE Cloud TPU v6e

To quantify the impact of these optimizations, we ran our 64-branch fork-storm harness (2 waves of 8 orchestrators × 8 sub-agents, 416 streaming requests per stage) across three cluster configurations:
1. **Stage 1 (Baseline)**: Kubernetes Service Round-Robin over aggregated workers.
2. **Stage 2 (Naive Sticky)**: Longest-prefix matching without capacity gates over aggregated workers.
3. **Stage 3 (FleetKV + Disagg)**: Fit-aware routing + P/D disaggregated TPU v6e workers with `/dev/shm` Host DRAM spillover.

### Full Empirical Results

| Metric | Stage 1: Round-Robin | Stage 2: Naive Sticky | Stage 3: FleetKV + Disagg | Delta (S3 vs S1 Baseline) |
| :--- | :---: | :---: | :---: | :---: |
| **Local Twin: Prefix Hit Rate** | 30.79 % | 62.48 % *(thrashing)* | **86.07 %** | **+55.3 points** |
| **Local Twin: P50 TTFT** | 6,498.4 ms | 5,581.1 ms | **1,152.7 ms** | **-82.3 %** |
| **Local Twin: P95 Tail TTFT** | 12,082.8 ms | 33,376.6 ms *(herd)* | **2,507.1 ms** | **-79.2 %** |
| **Local Twin: P99 ITL (Jitter)** | 133.12 ms | 141.43 ms | **33.12 ms** | **-75.1 %** (< 40ms SLO) |
| **Local Twin: Cluster Goodput** | 31.6 tok/s (1.0x) | 18.5 tok/s (0.59x) | **134.7 tok/s** | **4.26x Goodput** |
| **Local Twin: Lost HBM Evictions**| 17,377 | 10,585 *(self-evict)* | **0 evictions** | **Zero Evictions** |
| | | | | |
| **GKE Hardware: Prefix Hit Rate** | 19.4 % | 52.8 % | **91.6 %** | **+72.2 points** |
| **GKE Hardware: P50 TTFT** | 2,710 ms | 1,180 ms | **315 ms** | **-88.4 %** |
| **GKE Hardware: P95 Tail TTFT** | 3,420 ms | 3,890 ms *(herd)* | **485 ms** | **-85.8 %** |
| **GKE Hardware: P99 ITL (Jitter)** | 116 ms | 98 ms | **27 ms** | **-76.7 %** |
| **GKE Hardware: Cluster Goodput** | 1.0x | 1.35x | **2.55x** | **2.55x Goodput** |

*Note: GKE hardware reference tests executed on an 8-chip Cloud TPU v6e budget (`2x ct6e-standard-4t`, 8 Trillium chips) evaluating Qwen2.5-32B in `bfloat16` with VPC `MTU=8896`.*

### Analyzing the Curves

The empirical data demonstrates why optimizing solely for cache hit rate is an operational trap:
- **Stage 2 Looks Good on Paper, Fails in Reality**: Naive sticky routing doubled the cache hit rate (from 30.8% to 62.5%), but its output goodput collapsed by **41%** (from 31.6 tok/s down to 18.5 tok/s). Because every branch stamped onto the same worker, P95 TTFT exploded to **33.4 seconds**. More than half the requests violated our 3,000 ms TTFT SLO.
- **Stage 3 Delivers True Production Goodput**: FleetKV combined with disaggregated serving achieved an **86.1% hit rate on the Digital Twin** and **91.6% on real TPU v6e hardware**. By shedding excess load to warm Tier-2 DRAM workers before HBM thrashing occurred, it eliminated evictions completely and drove P95 TTFT down to **2,507 ms (Twin) / 485 ms (Hardware)**.
- **Isolating Decode Unlocks Smooth Streaming**: Removing prefill workloads from decode chips lowered P99 ITL from 133 ms down to **33.1 ms on the Twin** and **27 ms on Cloud TPU v6e**, turning choppy, lagging token streams into a smooth, interactive experience.

---

## 5. Production Playbook and 5-Minute Reproduction

If you are running multi-agent workloads or large shared prompt prefixes on Kubernetes today, here is the production checklist:

1. **Never Deploy Naive Prefix-Sticky Routing Without Admission Gates**: If your ingress controller routes purely on longest-prefix matches without verifying target worker queue depths and remaining HBM capacity, a sudden surge of agent branches will herd onto a single pod and blow up your tail latency.
2. **Lock Step Block Sizes and Hash Seeds**: Ensure your router and inference workers agree on token chunking. On TPU v6e, always use `--block-size 256` to avoid Pallas kernel SMEM overflows, and export `PYTHONHASHSEED="0"` across all pods.
3. **Use Headless Services for Control-Plane Discovery**: Do not point ZeroMQ or stateful gRPC telemetry subscribers at standard Kubernetes `ClusterIP` VIPs. Use `clusterIP: None` so your control plane maintains independent connections to every individual worker pod.
4. **Size `/dev/shm` for Host DRAM Offloading**: In your GKE manifests, mount an `emptyDir` with `medium: Memory` to `/dev/shm` sized to at least 64 GiB. Enabling `TPUConnectorHMA` allows vLLM to stage KV blocks into host memory, preventing cold systolic recomputations when HBM fills.
5. **Release Ingress Leases at TTFT**: If you implement custom capacity accounting in Envoy or an API gateway, ensure prefill token leases are freed the millisecond `ResponseHeaders` are received. Holding prefill reservations during long decode loops will artificially throttle your cluster.

### Run the 3-Stage Benchmark on Your Laptop in 5 Minutes

You don't need a cloud TPU quota to explore these dynamics. The entire testbed—Envoy proxy, Go `fleetkv-epp` router, and multi-worker TPU digital twin—runs locally via Docker Compose or native Go/Python harnesses:

```bash
# Clone the repository
git clone https://github.com/rabimba/GDE-ML-Artifacts.git
cd GDE-ML-Artifacts/KubeCon26

# Run the complete verification suite (Go race tests + 3-stage physics + K8s manifest audits)
make gate-all

# Or run just the 3-stage fork-storm benchmark and print the live scorecard
make gate-g1
```

### Presentation Slides and Artifacts
- **Interactive Web Slide Deck**: [rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/](https://rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/)
- **Presenter Script & Teleprompter Notes**: [slides/SPEAKER_NOTES_AND_SCRIPT.md](https://github.com/rabimba/GDE-ML-Artifacts/blob/main/KubeCon26/slides/SPEAKER_NOTES_AND_SCRIPT.md)
- **PowerPoint Presentation (Google Cloud Labs Branded)**: [slides/KubeCon26-FleetKV-GKE.pptx](https://github.com/rabimba/GDE-ML-Artifacts/raw/main/KubeCon26/slides/KubeCon26-FleetKV-GKE.pptx)
- **Source Code & Manifests**: [github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26](https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26)

---
*Labels: AI Systems, Cloud TPU, Envoy, GKE, Google Developer Expert, KubeCon, Kubernetes, LLM Serving, OpenXLA, vLLM*
