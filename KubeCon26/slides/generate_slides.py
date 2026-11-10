#!/usr/bin/env python3
# Copyright 2026 Rabimba Karanjai & Contributors.
# Licensed under the Apache License, Version 2.0.
"""
Google-Branded Presentation Suite Generator for KubeCon 2026:
  "Defeating the Prefix-Cache Penalty: KV-Aware Routing and Disaggregated Serving for Agent Fleets on GKE"

Generates:
1. KubeCon26-FleetKV-GKE.pptx (Editable PowerPoint using Google Cloud Labs master layouts + speaker notes)
2. index.html (Interactive Web Presentation Deck: Presenter Console [P], Teleprompter [S], Grid [G], Fullscreen [F])
3. speaker-notes.html (Synchronized dual-screen Speaker Notes & Teleprompter Console)
4. SPEAKER_NOTES_AND_SCRIPT.md (Complete 15-Minute Speaker Script, Live Demo Runbook & Q&A Bank)
"""

from __future__ import annotations

import html
import json
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIDENTIAL_BADGE = False
REF_PPTX = os.path.join(
    os.path.dirname(os.path.dirname(BASE_DIR)),
    "Command-and-Control-Gemini-MCP-Workshop",
    "Command_and_Control_Gemini_MCP_Workshop.pptx",
)


def ensure_generated_assets() -> None:
    """Generates QR codes and high-DPI architecture/benchmark visuals in slides/assets/."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    try:
        import qrcode
        qrs = {
            "qr_kubecon26_repo.png": "https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26",
            "qr_kubecon26_slides.png": "https://rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/index.html",
            "qr_gaie_docs.png": "https://gateway-api-inference-extension.sigs.k8s.io/",
        }
        for fname, url in qrs.items():
            out_p = os.path.join(ASSETS_DIR, fname)
            if not os.path.exists(out_p):
                img = qrcode.make(url)
                img.save(out_p)
    except Exception:
        pass

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch

        # 1. Fork-Storm Tree vs Linear Chatbot visual
        tree_path = os.path.join(ASSETS_DIR, "fork_storm_tree.png")
        fig, ax = plt.subplots(figsize=(9.2, 6.2), dpi=180)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7)
        ax.axis("off")
        fig.patch.set_facecolor("#F8F9FA")

        def draw_box(x, y, w, h, title, sub, bg="#FFFFFF", edge="#1A73E8", tc="#202124", lw=2.0):
            p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.18", facecolor=bg, edgecolor=edge, linewidth=lw)
            ax.add_patch(p)
            ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color=tc, family="sans-serif")
            ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=8.5, color="#5F6368", family="sans-serif")

        ax.text(5.0, 6.65, "Incident Orchestrator Fork-Storm Episode (85.6% Shared Prefix Tokens)", ha="center", va="center", fontsize=12, fontweight="bold", color="#174EA6")
        draw_box(0.4, 2.6, 2.5, 1.8, "Shared Trunk\n20,480 Tokens", "80 x 256-tok Blocks\n120 MCP Tools + AST", bg="#E8F0FE", edge="#1A73E8", tc="#174EA6", lw=2.5)

        branches = [
            (3.7, 5.1, "Sub-Agent 1..2", "+8,192 tok Log Burst\n(32 Blocks)"),
            (3.7, 3.6, "Sub-Agent 3..4", "+8,192 tok Git/Trace\n(32 Blocks)"),
            (3.7, 2.1, "Sub-Agent 5..6", "+8,192 tok Envoy Dump\n(32 Blocks)"),
            (3.7, 0.6, "Sub-Agent 7..8", "+8,192 tok TPU Profile\n(32 Blocks)"),
        ]
        for bx, by, bt, bs in branches:
            draw_box(bx, by, 2.6, 1.15, bt, bs, bg="#FFFFFF", edge="#34A853", tc="#137333", lw=1.8)
            ax.annotate("", xy=(bx, by + 0.57), xytext=(2.92, 3.5), arrowprops=dict(arrowstyle="->", color="#1A73E8", lw=1.8))
            ax.annotate("", xy=(7.1, 3.5), xytext=(bx + 2.62, by + 0.57), arrowprops=dict(arrowstyle="->", color="#34A853", lw=1.8))

        draw_box(7.1, 2.6, 2.5, 1.8, "Synthesis Join\n26,624 Tokens", "Reuses 20,480-tok Trunk\n+ 6,144-tok Summary", bg="#FEF7E0", edge="#FBBC04", tc="#B06000", lw=2.5)
        plt.tight_layout()
        fig.savefig(tree_path, dpi=180)
        plt.close(fig)

        # 2. FleetKV + TorchTPU Disaggregated Architecture diagram
        arch_path = os.path.join(ASSETS_DIR, "fleetkv_architecture.png")
        fig, ax = plt.subplots(figsize=(9.2, 6.2), dpi=180)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7)
        ax.axis("off")
        fig.patch.set_facecolor("#F8F9FA")

        ax.text(5.0, 6.65, "FleetKV GAIE Router + vllm-torchtpu Disaggregated Serving on GKE", ha="center", va="center", fontsize=12, fontweight="bold", color="#174EA6")
        draw_box(0.35, 4.3, 2.5, 1.6, "GKE Gateway (Envoy)", "InferencePool v1\ngRPC ext_proc (:9002)", bg="#FFFFFF", edge="#1A73E8", tc="#174EA6", lw=2.2)
        draw_box(0.35, 1.1, 2.5, 2.2, "FleetKV EPP (Go 1.23)", "256-Tok SHA-256 Hasher\nRadix Tree + HBM Fit Gate\nStaged Prefill Lease", bg="#E8F0FE", edge="#1A73E8", tc="#174EA6", lw=2.5)
        ax.annotate("", xy=(1.6, 3.35), xytext=(1.6, 4.28), arrowprops=dict(arrowstyle="<->", color="#1A73E8", lw=2.2))

        draw_box(3.75, 4.1, 2.75, 1.8, "Prefill Pool (TPU v6e)", "vllm-torchtpu (TP=4)\nPallas --block-size 256", bg="#FFFFFF", edge="#FBBC04", tc="#B06000", lw=2.2)
        draw_box(3.75, 1.1, 2.75, 1.9, "Tier-2 Host DRAM", "TPUConnectorHMA\n48 GiB /dev/shm (1,024+ Blks)", bg="#FEF7E0", edge="#FBBC04", tc="#B06000", lw=2.2)
        ax.annotate("", xy=(5.12, 3.05), xytext=(5.12, 4.08), arrowprops=dict(arrowstyle="<->", color="#B06000", lw=2.0))
        ax.annotate("ZMQ PUB :5557\nBlockStored/Removed", xy=(2.88, 2.2), xytext=(3.72, 4.4), fontsize=8, color="#174EA6", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#1A73E8", lw=1.6, ls="--"))

        draw_box(7.2, 4.2, 2.45, 1.7, "Decode Pod 0 (TPU v6e)", "Branches 1..4\nP99 ITL < 35 ms", bg="#E6F4EA", edge="#34A853", tc="#137333", lw=2.2)
        draw_box(7.2, 1.3, 2.45, 1.7, "Decode Pod 1 (TPU v6e)", "Branches 5..8 (Spillover)\nZero HBM Evictions", bg="#E6F4EA", edge="#34A853", tc="#137333", lw=2.2)
        ax.annotate("", xy=(7.18, 5.05), xytext=(6.52, 5.05), arrowprops=dict(arrowstyle="->", color="#137333", lw=2.2))
        ax.annotate("Async KV DMA\n(MTU 8896 gVNIC)", xy=(7.18, 2.15), xytext=(6.52, 4.5), fontsize=8, color="#137333", fontweight="bold", arrowprops=dict(arrowstyle="->", color="#34A853", lw=2.2))
        plt.tight_layout()
        fig.savefig(arch_path, dpi=180)
        plt.close(fig)

        # 3. 3-Stage Benchmark Scorecard Chart
        chart_path = os.path.join(ASSETS_DIR, "stage_scorecard_visual.png")
        fig, axes = plt.subplots(1, 3, figsize=(9.4, 5.4), dpi=180)
        fig.patch.set_facecolor("#F8F9FA")
        stages = ["Stage 1\nRound-Robin", "Stage 2\nNaive Sticky", "Stage 3\nFleetKV+Disagg"]
        colors = ["#EA4335", "#FBBC04", "#34A853"]

        # Panel 1: Hit Rate (%)
        vals1 = [30.8, 62.5, 86.1]
        bars1 = axes[0].bar(stages, vals1, color=colors, width=0.58)
        axes[0].set_title("Prefix Cache Hit Rate (%)\n(Higher is Better)", fontsize=10, fontweight="bold")
        axes[0].set_ylim(0, 105)
        for b, v in zip(bars1, vals1):
            axes[0].text(b.get_x() + b.get_width() / 2, v + 2.5, f"{v:.1f}%", ha="center", fontweight="bold", fontsize=9)

        # Panel 2: P95 Fork-Burst TTFT (seconds)
        vals2 = [12.08, 33.38, 2.51]
        bars2 = axes[1].bar(stages, vals2, color=colors, width=0.58)
        axes[1].set_title("P95 Fork-Burst TTFT (sec)\n(Lower is Better)", fontsize=10, fontweight="bold")
        axes[1].set_ylim(0, 38)
        for b, v in zip(bars2, vals2):
            axes[1].text(b.get_x() + b.get_width() / 2, v + 0.9, f"{v:.2f}s", ha="center", fontweight="bold", fontsize=9)

        # Panel 3: Decode Jitter P99 ITL (ms)
        vals3 = [133.1, 141.4, 33.1]
        bars3 = axes[2].bar(stages, vals3, color=colors, width=0.58)
        axes[2].axhline(40.0, color="#1A73E8", linestyle="--", linewidth=1.4, label="40ms SLO")
        axes[2].set_title("Decode Jitter P99 ITL (ms)\n(< 40 ms SLO)", fontsize=10, fontweight="bold")
        axes[2].set_ylim(0, 165)
        axes[2].legend(loc="upper right", fontsize=8)
        for b, v in zip(bars3, vals3):
            axes[2].text(b.get_x() + b.get_width() / 2, v + 3.5, f"{v:.1f}ms", ha="center", fontweight="bold", fontsize=9)

        for ax in axes:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(axis="x", labelsize=8.5)
        plt.suptitle("Verified Gate G1 Benchmark Scorecard (8 Orchestrators x 8-Way Fork = 416 Req/Stage)", fontsize=11, fontweight="bold", color="#174EA6")
        plt.tight_layout()
        fig.savefig(chart_path, dpi=180)
        plt.close(fig)
    except Exception as exc:
        print(f"Warning: asset generation skipped: {exc}")


# ---------------------------------------------------------------------------
# MASTER SLIDE DECK DATA (14 Slides — 15-Minute KubeCon 2026 Technical Session)
# ---------------------------------------------------------------------------
SLIDES_DATA = [
    {
        "num": 1,
        "module": "Session Opening",
        "time": "00:00 – 00:35",
        "type": "cover",
        "badge": "KubeCon 2026 • GKE Cloud TPU & GAIE",
        "title": "Defeating the Prefix-Cache Penalty:\nKV-Aware Routing & Disaggregated Serving\nfor Agent Fleets on GKE",
        "subtitle": "Gateway API Inference Extension (v1) • llm-d DisaggregatedSet • vllm-torchtpu • Cloud TPU v6e",
        "notes": (
            "[00:00 - 00:35]\n"
            "Kubernetes services were built around a simple assumption: HTTP requests are independent, pods are interchangeable, and round-robin spreads load evenly.\n\n"
            "When you run an autonomous SWE or SRE agent fleet behind a stateless Service, you spend most of your accelerator cycles recomputing identical prompt prefixes across replicas. And if you switch to naive longest-prefix sticky routing, parallel agent fan-out herds onto a single pod and makes P95 tail latency worse than round-robin.\n\n"
            "In this session, we will walk through why both failures happen and how we fix them using Gateway API Inference Extension and disaggregated TorchTPU serving on GKE."
        ),
    },
    {
        "num": 2,
        "module": "Speaker & Companion Artifact",
        "time": "00:35 – 01:00",
        "type": "speaker",
        "photo": "ref_slide4_pic2.jpg",
        "title": "Rabimba\nKaranjai",
        "subtitle": "Google Developer Expert — AI & ML\nML Scientist — PayPal",
        "tags": ["GKE Cloud TPU v6e", "Gateway API Inference Extension", "vllm-torchtpu & llm-d"],
        "notes": (
            "[00:35 - 01:00]\n"
            "I'm Rabimba Karanjai, a Google Developer Expert for AI/ML and ML Scientist at PayPal.\n\n"
            "Everything we cover today—the Go 1.23 Envoy ext_proc router, the GKE Cloud TPU v6e and GAIE manifests, and the trace-calibrated local digital twin—is open-source under Apache-2.0 in our companion repository."
        ),
    },
    {
        "num": 3,
        "module": "Companion Repository & Resources",
        "time": "01:00 – 01:20",
        "type": "qr_hub",
        "title": "Scan to Grab the Companion Artifact & Slides",
        "subtitle": "Every GKE manifest, Go ext_proc router package, and automated test gate (make gate-all) is in the repo.",
        "cards": [
            {
                "title": "KubeCon 2026 Repo",
                "url": "https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26",
                "url_text": "github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26",
                "desc": "Go 1.23 FleetKV EPP router, TPU v6e DisaggregatedSet YAML & Digital Twin.",
                "qr": "qr_kubecon26_repo.png",
            },
            {
                "title": "Interactive Web Deck",
                "url": "https://rabimba.github.io/GDE-ML-Artifacts/KubeCon26/slides/index.html",
                "url_text": "rabimba.github.io/.../KubeCon26/slides",
                "desc": "Follow along with live speaker notes (press S) and copyable YAML/Go snippets.",
                "qr": "qr_kubecon26_slides.png",
            },
            {
                "title": "GAIE Upstream Docs",
                "url": "https://gateway-api-inference-extension.sigs.k8s.io/",
                "url_text": "gateway-api-inference-extension.sigs.k8s.io",
                "desc": "Kubernetes SIG Networking Gateway API Inference Extension v1 specification.",
                "qr": "qr_gaie_docs.png",
            },
        ],
        "notes": (
            "[01:00 - 01:20]\n"
            "If you want to run the benchmark on your laptop or deploy the manifests on GKE, scan the left QR code for the companion repo, or the middle QR code for this interactive slide deck."
        ),
    },
    {
        "num": 4,
        "module": "Part 1: The Agent Tree Workload",
        "time": "01:20 – 02:30",
        "type": "split_worlds",
        "title": "Chatbots Are Lines. Agent Fleets Are Trees.",
        "left": {
            "color": "blue",
            "icon": "icon_gemini.png",
            "heading": "Linear Chatbot Traffic",
            "points": [
                "Single user typing one turn every 15 to 30 seconds",
                "Short system prompt (~1,024 tokens)",
                "Predictable, incremental KV cache growth per session",
                "Independent sessions rarely share 20K-token prefixes at millisecond zero",
            ],
        },
        "bridge": "t = 0 ms\n8-Way Fork\n20,480-Tok\nShared Trunk",
        "right": {
            "color": "green",
            "icon": "icon_adk.png",
            "heading": "SWE / SRE Agent Fleet (Fork-Storm)",
            "points": [
                "20,480-Token Trunk: 120 MCP tool schemas + repo AST + alert state (80 x 256-tok blocks)",
                "8-Way Parallel Fork: Orchestrator spawns 8 specialist sub-agents at t = 0 ms",
                "Log Bursts: Each sub-agent appends +8,192 tokens of kubectl logs / diffs on Turn 2",
                "Synthesis Join: Orchestrator merges all 8 sub-agent findings (85.6% prefix overlap)",
            ],
        },
        "notes": (
            "[01:20 - 02:30]\n"
            "Why do agent fleets break standard serving pools? Because a chatbot is a line, whereas an agent workflow is a tree.\n\n"
            "When an incident orchestrator triggers on an alert, it assembles a 20,480-token shared trunk—80 blocks of 256 tokens holding MCP tool schemas, repository structure, and alert state—and at millisecond zero spawns 8 parallel sub-agents. Each sub-agent pulls 8,192 tokens of pod logs and diffs before converging on a synthesis turn. Over the episode, 85.6% of tokens across those branches are shared prefix blocks."
        ),
    },
    {
        "num": 5,
        "module": "Part 1: Fork-Storm Topology",
        "time": "02:30 – 03:20",
        "type": "arch_split",
        "title": "Anatomy of an 8-Way Incident Orchestrator Fork-Storm",
        "subtitle": "20,480-Token Shared Parent Trunk -> 8 Concurrent Sub-Agent Branches -> Join",
        "intro": "Every 256-token block hash in the 80-block parent trunk is identical across all 8 child sub-agents:",
        "bullets": [
            ("Blocks 0..1 (512 tok)", "Global MCP tool bootstrap shared across all cluster orchestrators."),
            ("Blocks 2..79 (19,968 tok)", "Incident repository AST + active alert context (80 blocks total trunk)."),
            ("Turn 1..4 Branch Deltas", "8 parallel specialists append +512 tok role, +8,192 tok log burst, +1,024 tok config/patch."),
            ("Synthesis Join (26,624 tok)", "Orchestrator re-attaches the 80-block trunk plus a 24-block branch synthesis."),
        ],
        "image": "fork_storm_tree.png",
        "notes": (
            "[02:30 - 03:20]\n"
            "Look at the token budget across a single orchestrator episode. Blocks 0 through 79 form the 20,480-token parent trunk. When the orchestrator forks 8 sub-agents simultaneously, all 8 child requests carry those exact 80 block hashes, followed by a 2-block role delta and a 32-block (8,192-token) log burst on Turn 2. Finally, the join turn reuses the original 80-block trunk."
        ),
    },
    {
        "num": 6,
        "module": "Part 2: Two Routing Failure Modes",
        "time": "03:20 – 05:00",
        "type": "two_cards_quiz",
        "left_card": {
            "color": "blue",
            "title": "Failure Mode 1: Stateless K8s Round-Robin",
            "subtitle": "Standard ClusterIP Service (1/N Scatter Misses)",
            "items": [
                ("1/N Cache Scatter", "Pods 0..3 each recompute the same 20,480-token parent trunk on their MXUs (~30.8% hit rate)."),
                ("Duplicate HBM Residency", "Identical 20,480-token FP8 KV blocks occupy N x High-Bandwidth Memory across the pool."),
                ("Prefill-Decode Interference", "Co-located 8,192-token log-burst prefills stall active decode streams past 133 ms P99 ITL."),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "Failure Mode 2: The Prefix-Herd Trap",
            "subtitle": "Naive Longest-Prefix Sticky Routing (argmax MatchedBlocks)",
            "items": [
                ("Single-Pod Stampede", "All 8 forked sub-agents match 80/80 trunk blocks on Pod 0; naive routing herds 8/8 branches onto Pod 0."),
                ("Serial MXU Queueing", "Pod 0 queues all 8 bursts serially while Pods 1..3 sit idle, spiking P95 TTFT to 33.4s (worse than Round-Robin!)."),
                ("HBM Self-Eviction", "8 diverging branches exceed Pod 0's 360-block HBM budget and LRU-evict their own parent trunk before Join."),
            ],
        },
        "quiz": {
            "question": "🎯 Pop Quiz: Why does Naive KV-Sticky routing make P95 Fork-Burst TTFT worse than Stateless Round-Robin?",
            "answer": "Because all 8 parallel sub-agents share the exact 80-block parent trunk on Pod 0—serializing 8 prefill bursts on one MXU and overflowing Pod 0's HBM!",
        },
        "notes": (
            "[03:20 - 05:00]\n"
            "Behind a standard Kubernetes Service, round-robin scatters those 8 child branches across all replicas. Every replica misses on the parent trunk, recomputes 20,480 tokens of prefill, and stalls co-located decode streams past 133 milliseconds P99 ITL.\n\n"
            "The natural next step is enabling longest-prefix sticky routing. That triggers a second failure mode during parallel agent fan-out: the Prefix-Herd Trap. At fork time, all 8 sub-agents match 80 out of 80 parent blocks on Pod 0. A router that maximizes prefix match sends all 8 concurrent branches to Pod 0 while Pods 1 through 3 sit idle. Worse, as those 8 branches append 8,192-token log bursts on Pod 0, they exceed Pod 0's 360-block HBM capacity and LRU-evict the shared parent trunk right before the synthesis join turn."
        ),
    },
    {
        "num": 7,
        "module": "Part 3: Co-Designing Routing & Disaggregation",
        "time": "05:00 – 06:15",
        "type": "objectives_card",
        "title": "Why KV-Aware Routing & Disaggregation Need Each Other",
        "intro": "Solving both 1/N scatter misses and fork-storm herding requires coordinating the GAIE control plane with a disaggregated Prefill/Decode data plane:",
        "bullets": [
            ("1. Compute the Shared Trunk Once on Prefill TPUs", "Prefill pods compute the 20,480-token trunk once and back their 360-block HBM cache with 48 GiB of Tier-2 Host DRAM (/dev/shm via TPUConnectorHMA)."),
            ("2. Gate Admission on HBM Block Fit", "Before routing a forked branch, FleetKV checks whether the branch horizon + 24-block safety reserve fits in free HBM; overflow branches spill cleanly to peer pods."),
            ("3. Isolate Log-Burst Prefills from Decode ITL", "8,192-token Turn 2 log bursts execute on dedicated Prefill MXUs so Decode TPUs stream tokens uninterrupted at 27–33 ms P99 ITL (< 40 ms SLO)."),
            ("4. Stream KV Blocks Over MTU-8896 gVNIC", "TPUConnectorHMA transfers delta KV blocks asynchronously over jumbo-frame gVNIC from Prefill TPUs to whichever Decode pod has HBM headroom."),
        ],
        "notes": (
            "[05:00 - 06:15]\n"
            "This is why routing and disaggregation have to work together. KV-aware routing on an aggregated pool ties compute affinity to memory residency, herding forked branches onto whichever pod holds the parent trunk. Disaggregation without KV-aware fit routing still recomputes shared prefixes.\n\n"
            "When we combine them, Prefill pods compute the shared trunk once, pin evicted blocks in 48 GiB of host DRAM, compute only the branch delta, and stream KV blocks over gVNIC to whichever Decode pod has HBM headroom."
        ),
    },
    {
        "num": 8,
        "module": "Part 3: Control Plane (FleetKV EPP)",
        "time": "06:15 – 07:30",
        "type": "code_focus",
        "title": "Control Plane: Fit-Aware Tree Routing in GAIE ext_proc",
        "subtitle": "router/pkg/scorer/policies.go — Hard HBM Fit Gate + Staged Prefill Leases",
        "lang": "go (router/pkg/scorer/policies.go)",
        "code": (
            "func ScoreEndpoint(pod *PodState, req *RouteInput) float64 {\n"
            "    // 1. Hard HBM Fit Gate: spill to peer if branch horizon overflows HBM\n"
            "    effectiveFree := pod.FreeHBMBlocks - pod.ReservedBlocks\n"
            "    if effectiveFree < req.EstimatedBranchBlocks + SafetyReserveBlocks {\n"
            "        return RejectOverflowSpillToPeer\n"
            "    }\n"
            "    // 2. Trade off ZMQ-indexed block hits against in-flight prefill queue\n"
            "    savedMs   := float64(pod.MatchedHBMBlocks)*HBMBlockMs +\n"
            "                 float64(pod.MatchedDRAMBlocks)*DRAMBlockMs\n"
            "    queueWait := float64(pod.InFlightPrefillTokens) / PodTokPerMs\n"
            "    return savedMs - queueWait\n"
            "}"
        ),
        "callouts": [
            ("ZeroMQ KV Indexer (:5557)", "Subscribes to vllm-torchtpu BlockStored & BlockRemoved events across HBM and Tier-2 Host DRAM."),
            ("Hard HBM Fit Gate", "Rejects pods where admitting the branch horizon (+24 safety blocks) would evict warm parent trunks."),
            ("Staged Lease Accounting", "AcquireStagedLease releases InFlightPrefillTokens on ResponseHeaders (TTFT) while holding ReservedBlocks until stream EOF."),
        ],
        "notes": (
            "[06:15 - 07:30]\n"
            "Here is the scoring function inside fleetkv-epp. Every vllm-torchtpu prefill pod publishes BlockStored and BlockRemoved events over ZeroMQ on port 5557 as 256-token blocks enter HBM or spill to host DRAM.\n\n"
            "When Envoy forwards a request over ext_proc, the router first checks the HBM Fit Gate: if admitting another branch plus our 24-block safety reserve would overflow the pod's free HBM blocks, it spills that branch to a peer pod instead of evicting the shared trunk. Second, notice our staged lease accounting: we release InFlightPrefillTokens as soon as ResponseHeaders arrive at TTFT, while holding the HBM block reservation until the SSE decode stream completes."
        ),
    },
    {
        "num": 9,
        "module": "Part 3: Data Plane (vllm-torchtpu + HMA)",
        "time": "07:30 – 08:30",
        "type": "arch_split",
        "title": "Data Plane: vllm-torchtpu + TPUConnectorHMA on GKE",
        "subtitle": "DisaggregatedSet on Trillium ct6e-standard-4t (2x2) with 48 GiB Tier-2 Host DRAM",
        "intro": "Upstream PyTorch models lowered via torch.compile(backend='tpu') onto Pallas paged-attention kernels:",
        "bullets": [
            ("Pallas 256-Token Blocks", "vllm-torchtpu runs Qwen/Qwen3-30B-A3B-FP8 with --block-size 256 so block tables fit in TPU v6e Scalar Memory (SMEM)."),
            ("Tier-2 Host DRAM (/dev/shm)", "Prefill pods mount a 64 GiB memory volume and allocate 48 GiB (1,024+ blocks) to TPUConnectorHMA so trunks never recompute."),
            ("Async KV DMA (MTU 8896)", "Delta KV blocks stream over jumbo-frame gVNIC from the selected Prefill pod (x-fleetkv-prefill-endpoint) to Decode TPUs."),
            ("GAIE Endpoint Picker Headers", "fleetkv-epp sets x-gateway-destination-endpoint and ClearRouteCache=true on Envoy v3 BodyResponse."),
        ],
        "image": "fleetkv_architecture.png",
        "notes": (
            "[07:30 - 08:30]\n"
            "On the data plane, our DisaggregatedSet runs vllm-torchtpu on GKE Trillium ct6e-standard-4t node pools. Prefill pods mount a 64 GiB /dev/shm volume and allocate 48 GiB to TPUConnectorHMA as a Tier-2 host DRAM cache, keeping shared agent trunks warm even when active branch deltas cycle through HBM.\n\n"
            "Once a prefill pod computes the branch delta, it transfers the KV blocks asynchronously over an MTU-8896 gVNIC network to the Decode pod selected by fleetkv-epp. Let's switch to the live terminal and watch all three stages under load."
        ),
    },
    {
        "num": 10,
        "module": "Part 4: Live 3-Stage Traffic Flip Demo",
        "time": "08:30 – 11:45",
        "type": "stepper_split",
        "title": "Live Demo: 3-Stage Traffic Flip Under 64-Branch Fork-Storm",
        "steps": [
            ("1", "Stage 1: Stateless K8s Round-Robin", "./bench/demo_ctl.sh stage1"),
            ("2", "Stage 2: Naive Longest-Prefix Sticky", "./bench/demo_ctl.sh stage2"),
            ("3", "Stage 3: FleetKV Fit + Disagg P/D", "./bench/demo_ctl.sh stage3"),
        ],
        "callout_badge": "LIVE ON STAGE • 4-COLUMN TUI",
        "callout_title": "Watch Completed Stages Freeze Side-by-Side",
        "callout_body": (
            "As demo_ctl.sh hot-swaps policies via POST /admin/policy (or patches the GKE HTTPRoute), "
            "bench/stage_tui.py freezes the completed stage's 10-second sliding-window telemetry so all 3 stages remain visible side-by-side."
        ),
        "code_title": "Operator Shell — 3-Pane Conference TUI",
        "code": (
            "# Launch 3-pane tmux layout (Scorecard TUI + EPP Route Stream + Shell)\n"
            "./bench/demo_ctl.sh prep\n\n"
            "# Flip live traffic across all 3 architectures:\n"
            "./bench/demo_ctl.sh stage2   # Trigger single-pod herd & HBM thrash\n"
            "./bench/demo_ctl.sh stage3   # Enable FleetKV Fit Gate + Disagg P/D"
        ),
        "notes": (
            "[08:30 - 11:45]\n"
            "[SWITCH TO TMUX TERMINAL]\n"
            "1. Stage 1 (round_robin): Point out the 4-pod even traffic split (25% each), low cache hit rate (~30.8% in the local twin, ~19.4% on 8-chip GKE), and P99 decode ITL at 133 ms from prefill-decode interference.\n"
            "2. Run ./bench/demo_ctl.sh stage2: Watch Stage 1 freeze in Column 1 while Stage 2 skews onto a single hot pod as all 8 forked branches match the 80-block trunk. HBM evictions climb past 10,500 blocks and P95 tail TTFT spikes to 33.4 seconds—worse than Stage 1.\n"
            "3. Run ./bench/demo_ctl.sh stage3: Watch fleetkv-epp emit herd_spillover decisions, pinning the trunk in prefill HBM/DRAM while splitting decode streams evenly across decode-0 and decode-1. HBM evictions drop to 0, hit rate reaches 86.1% (91.6% on GKE), and P99 ITL drops to 33.1 ms (< 40 ms SLO)."
        ),
    },
    {
        "num": 11,
        "module": "Part 5: Empirical Benchmark Scorecard",
        "time": "11:45 – 12:30",
        "type": "checkpoint_visual",
        "title": "Benchmark Scorecard: Gate G1 Twin & GKE Cloud TPU v6e",
        "bullets": [
            ("Effective Prefix Hit Rate", "30.8% (S1) -> 62.5% (S2 thrashing) -> 86.1% Twin / 91.6% GKE (S3 HBM + Tier-2 DRAM)."),
            ("Median TTFT (P50)", "6,498 ms (S1) -> 5,581 ms (S2) -> 1,153 ms Twin (-82.3%) / 315 ms GKE (-88%)."),
            ("Fork-Burst Tail TTFT (P95)", "12,083 ms (S1) -> 33,377 ms (S2 herd stall!) -> 2,507 ms Twin (-79.2%) / 485 ms GKE (-86%)."),
            ("Decode Jitter (P99 ITL)", "133.1 ms (S1) -> 141.4 ms (S2) -> 33.1 ms Twin / 27 ms GKE (< 40 ms interactive SLO)."),
            ("Cluster Output Goodput", "31.6 tok/s (1.0x S1) -> 18.5 tok/s (0.59x S2) -> 134.7 tok/s (4.26x Twin / 2.55x GKE)."),
            ("Lost HBM Block Evictions", "17,377 (S1) -> 10,585 (S2 self-eviction) -> 0 in Stage 3 (pinned in 48 GiB Host DRAM)."),
        ],
        "screenshot": "stage_scorecard_visual.png",
        "caption": "Verified Gate G1 run (`make gate-g1`, 416 streaming requests/stage) & 8-chip GKE TPU v6e (`2x ct6e-standard-4t`) reference.",
        "notes": (
            "[11:45 - 12:30]\n"
            "Here are both sets of numbers side by side: the local trace-calibrated twin verified by make gate-g1 on 416 requests per stage, and the 8-chip GKE TPU v6e hardware reference (2x ct6e-standard-4t).\n\n"
            "In both environments, Stage 2's naive sticky routing makes P95 tail TTFT worse than stateless round-robin—33.4 seconds in the 4-pod twin and 3.89 seconds on GKE—because all 8 forked branches queue on a single replica and evict over 10,500 HBM blocks. Stage 3 cuts median TTFT by 82 to 88 percent, eliminates HBM evictions, and keeps P99 decode ITL at 27 to 33 milliseconds."
        ),
    },
    {
        "num": 12,
        "module": "Part 6: Production GKE Invariants",
        "time": "12:30 – 13:30",
        "type": "three_tech",
        "title": "Three Production Invariants (Audited in CI by Gate G2)",
        "cols": [
            {
                "icon": "icon_gemini.png",
                "title": "1. Pin PYTHONHASHSEED=\"0\"\nAcross Every Pod",
                "body": (
                    "Python randomizes process hash seeds by default. Set PYTHONHASHSEED=\"0\" on every vllm-torchtpu worker and "
                    "fleetkv-epp container so chained 256-token block hashes match across processes."
                ),
            },
            {
                "icon": "icon_adk.png",
                "title": "2. Match --block-size 256\non TPU v6e Pallas",
                "body": (
                    "GPU pools often default to block size 64. On Trillium TPU v6e, 64-token blocks overflow Scalar Memory (SMEM) "
                    "in Pallas paged-attention kernels. Set --block-size 256 in both vLLM and fleetkv-epp."
                ),
            },
            {
                "icon": "icon_mcp.png",
                "title": "3. Headless ZMQ Service +\nMTU-8896 gVNIC VPC",
                "body": (
                    "Expose ports 8000 and 5557 via Headless Services (clusterIP: None) so fleetkv-epp resolves every pod IP via DNS, "
                    "filter ZMQ to llm-d.ai/role=prefill, and set VPC mtu: 8896 for TPUConnectorHMA."
                ),
            },
        ],
        "notes": (
            "[12:30 - 13:30]\n"
            "Three operational invariants before you deploy this on GKE—all enforced by tests/test_g3_k8s_manifests.py in CI.\n\n"
            "First, set PYTHONHASHSEED=\"0\" on every container; otherwise Python's per-process hash randomization causes block hash mismatches across workers. Second, set --block-size 256 on both vllm-torchtpu and fleetkv-epp so Pallas paged-attention kernels fit inside TPU v6e Scalar Memory. Third, use a Kubernetes Headless Service (clusterIP: None) filtered to llm-d.ai/role=prefill so the router subscribes to every prefill pod's ZMQ socket individually, and configure mtu: 8896 on your gVNIC VPC."
        ),
    },
    {
        "num": 13,
        "module": "Reference: GKE & Local Commands",
        "time": "13:30 – 14:00",
        "type": "two_cards_code",
        "title": "Reproduce Locally in 60 Seconds or Deploy on GKE TPU v6e",
        "left_card": {
            "color": "blue",
            "title": "Local Digital Twin & CI Gates",
            "subtitle": "Runs on macOS / Linux without TPU hardware",
            "code": (
                "# Run all verification gates (Go race + E2E SLOs + K8s YAML)\n"
                "make gate-all\n\n"
                "# Launch interactive 3-pane conference TUI\n"
                "./bench/demo_ctl.sh prep\n"
                "./bench/demo_ctl.sh stage2\n"
                "./bench/demo_ctl.sh stage3"
            ),
            "bullets": [
                ("Gate G0", "Go 1.23 race tests + cross-language SHA-256 & ZMQ parity"),
                ("Gate G1", "Full 416-request/stage Envoy ext_proc + Twin SLO verification"),
            ],
        },
        "right_card": {
            "color": "red",
            "title": "GKE Cloud TPU v6e Production Stack",
            "subtitle": "2x ct6e-standard-4t + GAIE v1 + DisaggregatedSet",
            "code": (
                "./deploy/gke/00-bootstrap-gke-tpu.sh\n"
                "kubectl apply -f deploy/gke/01-baseline-agg-service.yaml\n"
                "kubectl apply -f deploy/gke/02-disaggregatedset-torchtpu.yaml\n"
                "kubectl apply -f deploy/gke/03-fleetkv-epp-and-pool.yaml\n\n"
                "FLEETKV_GATEWAY_URL=\"http://${GATEWAY_VIP}\" \\\n"
                "  ./bench/demo_ctl.sh stage3 --target=gke"
            ),
            "bullets": [
                ("Gate G2", "Audits PYTHONHASHSEED=0, --block-size 256, Headless ZMQ & MTU=8896"),
                ("Zero Client Changes", "Same Go EPP binary & OpenAI benchmark client across Twin and GKE"),
            ],
        },
        "notes": (
            "[13:30 - 14:00]\n"
            "Here is the complete command reference for both environments. On the left, make gate-all runs our Go race-detector unit tests, cross-language SHA-256 block-hash parity checks, the 3-stage end-to-end fork-storm benchmark, and the Kubernetes manifest audit. On the right are the four commands to bootstrap the MTU-8896 GKE cluster, apply the DisaggregatedSet and InferencePool manifests, and run the exact same stage controller against a live GKE Gateway VIP."
        ),
    },
    {
        "num": 14,
        "module": "Closing & Q&A",
        "time": "14:00 – 15:00",
        "type": "thank_you",
        "title": "Thank You!",
        "subtitle": (
            "Defeating the Prefix-Cache Penalty on GKE\n"
            "• Agent trees fork in bursts: gate KV routing on HBM fit\n"
            "• Release prefill leases on ResponseHeaders (TTFT)\n"
            "• Disaggregate Prefill & Decode with Tier-2 Host DRAM"
        ),
        "qr_top": "qr_kubecon26_repo.png",
        "qr_top_label": "Companion GitHub Repo (Apache-2.0)",
        "qr_mid": "qr_linkedin.png",
        "qr_mid_label": "Connect on LinkedIn",
        "qr_bottom": "qr_kubecon26_slides.png",
        "qr_bottom_label": "Interactive Slide Deck & Script",
        "notes": (
            "[14:00 - 15:00]\n"
            "To wrap up: agent fleets generate tree-structured bursts, not independent linear turns. By combining a fit-aware GAIE ext_proc router with disaggregated vllm-torchtpu and Tier-2 host DRAM on GKE, you keep shared trunks warm without herding parallel sub-agents onto a single pod.\n\n"
            "The Go router, GKE manifests, local digital twin, and automated test gates are all in the companion repository. Thank you—happy to take questions!"
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
        if b_title is None:
            r1 = p.add_run()
            r1.text = "• "
            r1.font.name = "Google Sans"
            r1.font.size = Pt(bullet_size)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(26, 115, 232)
        else:
            r1 = p.add_run()
            r1.text = f"• {b_title}: "
            r1.font.name = "Google Sans"
            r1.font.size = Pt(bullet_size)
            r1.font.bold = True
            r1.font.color.rgb = RGBColor(26, 115, 232)
        r2 = p.add_run()
        r2.text = b_body
        r2.font.name = "Google Sans"
        r2.font.size = Pt(bullet_size)
        r2.font.color.rgb = RGBColor(32, 33, 36)
    return tb


def add_image_fit(slide, img_path, left, top, max_w, max_h):
    from PIL import Image
    full_path = os.path.join(ASSETS_DIR, img_path)
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


def build_pptx(output_path):
    prs = pptx.Presentation(REF_PPTX)

    # Map required slide layouts from the reference presentation
    layouts = {l.name: l for m in prs.slide_masters for l in m.slide_layouts}
    layout_cover = layouts["CUSTOM_6_1_3_3_1"]
    layout_qr = layouts["TITLE_AND_BODY_1"]
    layout_speaker = layouts["CUSTOM_6_1_3_2_1_1_4"]
    layout_content = layouts["CUSTOM_6_1_3_2_1_1_3_1_1_1_1_1_2_1"]

    # Remove existing slides from prs
    xml_slides = prs.slides._sldIdLst
    for sldId in list(xml_slides):
        rId = sldId.rId
        prs.part.drop_rel(rId)
        xml_slides.remove(sldId)

    for sdata in SLIDES_DATA:
        stype = sdata["type"]
        if stype == "cover":
            slide = prs.slides.add_slide(layout_cover)
            clear_slide_shapes(slide)
            add_rounded_box(slide, 0.45, 1.35, 2.75, 0.36, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=1, radius=0.45)
            add_textbox(slide, 0.50, 1.39, 2.65, 0.28, sdata.get("badge", "Workshop"), font_size=11, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.85, 5.10, 2.10, sdata["title"], font_size=28, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.45, 4.05, 5.00, 0.85, sdata["subtitle"], font_size=13, bold=False, color=(95, 99, 104))

        elif stype == "big_qr":
            slide = prs.slides.add_slide(layout_qr)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.50, 0.40, 9.00, 0.58, sdata["title"], font_size=28, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_rounded_box(slide, 3.42, 1.08, 3.16, 2.88, fill_rgb=(255, 255, 255), line_rgb=(218, 220, 224), line_pt=1.5, radius=0.03)
            add_image_fit(slide, sdata["qr"], 3.56, 1.22, 2.88, 2.60)
            add_textbox(slide, 0.50, 4.04, 9.00, 0.40, sdata["url_text"], font_size=20, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)
            add_textbox(slide, 1.30, 4.48, 7.40, 0.55, sdata["desc"], font_size=10, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            if sdata.get("wifi_ssid"):
                add_rounded_box(slide, 2.75, 5.12, 4.50, 0.34, fill_rgb=(241, 243, 244), line_rgb=(218, 220, 224), line_pt=1, radius=0.5)
                add_textbox(slide, 2.80, 5.17, 4.40, 0.24, f"Wi-Fi: {sdata['wifi_ssid']}    •    Password: {sdata['wifi_pass']}", font_size=10, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)

        elif stype == "qr_hub":
            slide = prs.slides.add_slide(layout_qr)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.50, 0.45, 9.00, 0.55, sdata["title"], font_size=28, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.50, 1.00, 9.00, 0.35, sdata["subtitle"], font_size=13, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            for idx, c in enumerate(sdata["cards"]):
                cx = 0.55 + idx * 3.05
                add_rounded_box(slide, cx, 1.50, 2.80, 3.70, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_textbox(slide, cx + 0.14, 1.64, 2.52, 0.45, c["title"], font_size=13, bold=True, color=(32, 33, 36))
                add_textbox(slide, cx + 0.14, 2.08, 2.52, 0.36, c["url_text"], font_size=9.5, bold=True, color=(26, 115, 232))
                add_textbox(slide, cx + 0.14, 2.45, 2.52, 0.65, c["desc"], font_size=9.5, bold=False, color=(95, 99, 104))
                add_image_fit(slide, c["qr"], cx + 0.45, 3.15, 1.90, 1.90)

        elif stype == "speaker":
            slide = prs.slides.add_slide(layout_speaker)
            clear_slide_shapes(slide)
            add_image_fit(slide, sdata["photo"], 0.65, 1.15, 3.55, 3.55)
            add_textbox(slide, 4.75, 1.50, 4.75, 1.45, sdata["title"], font_size=40, bold=True, color=(32, 33, 36))
            add_textbox(slide, 4.75, 3.10, 4.75, 1.25, sdata["subtitle"], font_size=18, bold=False, color=(60, 64, 67))

        elif stype == "thank_you":
            slide = prs.slides.add_slide(layout_speaker)
            clear_slide_shapes(slide)
            add_textbox(slide, 4.80, 1.85, 3.30, 1.10, sdata["title"], font_size=44, bold=True, color=(32, 33, 36))
            add_textbox(slide, 4.80, 2.95, 3.30, 1.10, sdata["subtitle"], font_size=14, bold=False, color=(60, 64, 67))
            # Data-driven QR stack: 2 QRs (legacy roomy) or 3 QRs (with LinkedIn)
            qrs = [(sdata["qr_top"], sdata["qr_top_label"])]
            if sdata.get("qr_mid"):
                qrs.append((sdata["qr_mid"], sdata["qr_mid_label"]))
            qrs.append((sdata["qr_bottom"], sdata["qr_bottom_label"]))
            if len(qrs) == 2:
                geom = [(8.15, 0.45, 1.45, 1.92), (8.15, 3.35, 1.45, 4.82)]
                fsz = 8.5
            else:
                geom = [(8.25, 0.28, 1.22, 1.52), (8.25, 2.02, 1.22, 3.26), (8.25, 3.76, 1.22, 5.00)]
                fsz = 8
            for (qimg, qlabel), (qx, qy, qs, ly) in zip(qrs, geom):
                add_image_fit(slide, qimg, qx, qy, qs, qs)
                add_textbox(slide, 7.70, ly, 2.35, 0.45, qlabel, font_size=fsz, bold=True, color=(26, 115, 232), align=PP_ALIGN.CENTER)

        elif stype == "section_poll":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_image_fit(slide, sdata["icon"], 4.62, 0.90, 0.75, 0.75)
            add_textbox(slide, 1.00, 1.72, 8.00, 1.05, sdata["title"], font_size=28, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            poll = sdata["poll"]
            add_rounded_box(slide, 0.75, 2.88, 8.50, 2.20, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=2, radius=0.04)
            add_textbox(slide, 0.95, 2.98, 8.10, 0.62, poll["question"], font_size=12.5, bold=True, color=(23, 78, 166))
            opts_text = "\n".join(f"• {o}" for o in poll["options"])
            add_textbox(slide, 1.05, 3.62, 7.90, 0.75, opts_text, font_size=11, bold=False, color=(32, 33, 36))
            add_textbox(slide, 0.95, 4.42, 8.10, 0.58, f"💡 Key Insight: {poll['answer']}", font_size=10.5, bold=True, color=(19, 115, 51))

        elif stype == "agent_triad":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.45, 0.65, 7.60, 2.10, sdata["headline"], font_size=23, bold=True, color=(32, 33, 36))
            coords = [(0.35, 3.40, 2.75, 1.85), (3.55, 3.40, 2.90, 1.85), (6.90, 3.40, 2.75, 1.85)]
            for idx, box in enumerate(sdata["boxes"]):
                bx, by, bw, bh = coords[idx]
                add_rounded_box(slide, bx, by, bw, bh, fill_rgb=(241, 243, 244), line_rgb=(218, 220, 224), line_pt=1.5, radius=0.05)
                add_image_fit(slide, box["icon"], bx + bw / 2 - 0.35, by - 0.38, 0.70, 0.70)
                add_textbox(slide, bx + 0.12, by + 0.48, bw - 0.24, 1.15, box["label"], font_size=18, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)

        elif stype == "objectives_card":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.82, 9.10, 0.55, sdata["title"], font_size=26, bold=True, color=(32, 33, 36))
            add_rounded_box(slide, 0.45, 1.48, 9.10, 3.60, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.5, radius=0.04)
            add_bullet_list_box(slide, 0.68, 1.64, 8.64, 3.30, sdata["intro"], sdata["bullets"], intro_size=12.5, bullet_size=11)

        elif stype == "arch_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.78, 9.10, 0.52, sdata["title"], font_size=26, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.45, 1.32, 4.45, 0.36, sdata["subtitle"], font_size=13.5, bold=True, color=(26, 115, 232))
            add_bullet_list_box(slide, 0.45, 1.72, 4.35, 3.40, sdata["intro"], sdata["bullets"], intro_size=10.5, bullet_size=10)
            add_image_fit(slide, sdata["image"], 4.88, 1.35, 4.75, 3.70)

        elif stype == "three_tech":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.50, 0.90, 7.00, 0.50, sdata["title"], font_size=22, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            for idx, col in enumerate(sdata["cols"]):
                cx = 0.75 + idx * 2.95
                add_rounded_box(slide, cx, 1.65, 2.65, 3.40, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_image_fit(slide, col["icon"], cx + 0.18, 1.82, 0.68, 0.68)
                add_textbox(slide, cx + 0.16, 2.62, 2.33, 0.62, col["title"], font_size=13.5, bold=True, color=(32, 33, 36))
                add_textbox(slide, cx + 0.16, 3.30, 2.33, 1.60, col["body"], font_size=10.5, bold=False, color=(60, 64, 67))

        elif stype == "two_cards_quiz":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (26, 115, 232) if card["color"] == "blue" else (234, 67, 53)
                add_rounded_box(slide, cx, 0.82, 4.40, 3.32, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 0.94, 4.04, 0.36, card["title"], font_size=15.5, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.30, 4.04, 0.28, card["subtitle"], font_size=10.5, bold=True, color=(95, 99, 104))
                add_bullet_list_box(slide, cx + 0.16, 1.62, 4.08, 2.42, None, card["items"], bullet_size=9.8)
            quiz = sdata["quiz"]
            add_rounded_box(slide, 0.48, 4.24, 9.04, 0.92, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.8, radius=0.03)
            add_textbox(slide, 0.64, 4.28, 8.72, 0.42, quiz["question"], font_size=9.8, bold=True, color=(176, 96, 0))
            add_textbox(slide, 0.64, 4.70, 8.72, 0.42, quiz["answer"], font_size=9.5, bold=False, color=(32, 33, 36))

        elif stype == "lab_divider":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 1.00, 1.95, 8.00, 0.80, sdata["title"], font_size=36, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_image_fit(slide, "ref_slide11_pic4.png", 1.85, 2.95, 0.42, 0.42)
            add_textbox(slide, 2.40, 2.96, 6.20, 0.50, sdata["subtitle"], font_size=16, bold=True, color=(26, 115, 232))

        elif stype == "code_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.78, 9.04, 0.48, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.48, 1.26, 4.40, 0.32, sdata["subtitle"], font_size=12, bold=True, color=(26, 115, 232))
            add_bullet_list_box(slide, 0.48, 1.60, 4.35, 3.55, sdata.get("intro"), sdata["bullets"], intro_size=10, bullet_size=9.6)
            if sdata.get("screenshot"):
                add_terminal_box(slide, 4.98, 1.28, 4.58, 2.15, sdata["code_title"], sdata["code"], font_size=8.5)
                add_image_fit(slide, sdata["screenshot"], 4.98, 3.52, 4.58, 1.62)
            else:
                add_terminal_box(slide, 4.98, 1.28, 4.58, 3.85, sdata["code_title"], sdata["code"], font_size=8.8)

        elif stype == "stepper_split":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.55, 0.78, 8.90, 0.50, sdata["title"], font_size=24, bold=True, color=(32, 33, 36))
            add_rounded_box(slide, 0.55, 1.38, 4.10, 3.75, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.5, radius=0.04)
            for idx, (snum, stitle, sdesc) in enumerate(sdata["steps"]):
                sy = 1.52 + idx * 0.92
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.78), Inches(sy), Inches(0.40), Inches(0.40))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(26, 115, 232)
                pill.line.fill.background()
                add_textbox(slide, 0.78, sy + 0.05, 0.40, 0.30, snum, font_size=11, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)
                add_textbox(slide, 1.32, sy - 0.06, 3.15, 0.28, stitle, font_size=12, bold=True, color=(32, 33, 36))
                add_textbox(slide, 1.32, sy + 0.20, 3.15, 0.40, sdesc, font_size=9, bold=False, color=(19, 115, 51), font_name="Roboto Mono")
            # Top-right callout card
            add_rounded_box(slide, 4.88, 1.38, 4.64, 1.62, fill_rgb=(255, 255, 255), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
            add_rounded_box(slide, 5.06, 1.50, 2.65, 0.26, fill_rgb=(252, 232, 230), line_rgb=None, radius=0.3)
            add_textbox(slide, 5.10, 1.52, 2.55, 0.22, sdata["callout_badge"], font_size=8, bold=True, color=(197, 34, 31))
            add_textbox(slide, 5.06, 1.80, 4.30, 0.30, sdata["callout_title"], font_size=12, bold=True, color=(32, 33, 36))
            add_textbox(slide, 5.06, 2.10, 4.30, 0.82, sdata["callout_body"], font_size=9.5, bold=False, color=(60, 64, 67))
            # Bottom-right terminal card
            add_terminal_box(slide, 4.88, 3.12, 4.64, 2.02, sdata["code_title"], sdata["code"], font_size=8.5)

        elif stype == "two_cards_code":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.74, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(32, 33, 36))
            for idx, key in enumerate(["left_card", "right_card"]):
                card = sdata[key]
                cx = 0.48 if idx == 0 else 5.12
                border_rgb = (26, 115, 232) if card["color"] == "blue" else (234, 67, 53)
                add_rounded_box(slide, cx, 1.22, 4.40, 3.92, fill_rgb=(255, 255, 255), line_rgb=border_rgb, line_pt=2.2, radius=0.04)
                add_textbox(slide, cx + 0.18, 1.32, 4.04, 0.34, card["title"], font_size=14.5, bold=True, color=border_rgb)
                add_textbox(slide, cx + 0.18, 1.64, 4.04, 0.26, card["subtitle"], font_size=10, bold=False, color=(95, 99, 104))
                add_terminal_box(slide, cx + 0.18, 1.96, 4.04, 1.72, "snippet / command", card["code"], font_size=8.2)
                add_bullet_list_box(slide, cx + 0.16, 3.74, 4.08, 1.32, None, card["bullets"], bullet_size=9.5)

        elif stype == "checkpoint_visual":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.78, 9.04, 0.48, sdata["title"], font_size=21, bold=True, color=(32, 33, 36))
            add_bullet_list_box(slide, 0.48, 1.35, 4.35, 3.75, None, sdata["bullets"], bullet_size=10.2)
            add_rounded_box(slide, 4.98, 1.35, 4.55, 3.40, fill_rgb=(248, 249, 250), line_rgb=(26, 115, 232), line_pt=1.8, radius=0.03)
            add_image_fit(slide, sdata["screenshot"], 5.08, 1.45, 4.35, 3.20)
            add_textbox(slide, 4.98, 4.80, 4.55, 0.35, sdata.get("caption", ""), font_size=9, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "four_steps":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.52, 0.76, 8.96, 0.48, sdata["title"], font_size=24, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.52, 1.24, 8.96, 0.32, sdata["subtitle"], font_size=13, bold=True, color=(26, 115, 232))
            add_textbox(slide, 0.52, 1.60, 8.96, 0.62, sdata["intro"], font_size=11, bold=False, color=(60, 64, 67))
            for idx, st in enumerate(sdata["steps"]):
                sx = 0.52 + idx * 2.28
                is_hi = st.get("highlight", False)
                border_rgb = (26, 115, 232) if is_hi else (218, 220, 224)
                add_rounded_box(slide, sx, 2.32, 2.12, 2.80, fill_rgb=(248, 249, 250), line_rgb=border_rgb, line_pt=2.2 if is_hi else 1.2, radius=0.04)
                pill = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(sx + 0.18), Inches(2.50), Inches(0.42), Inches(0.42))
                pill.fill.solid()
                pill.fill.fore_color.rgb = RGBColor(26, 115, 232) if is_hi else RGBColor(232, 240, 254)
                pill.line.fill.background()
                add_textbox(slide, sx + 0.18, 2.55, 0.42, 0.32, st["num"], font_size=12, bold=True, color=(255, 255, 255) if is_hi else (26, 115, 232), align=PP_ALIGN.CENTER)
                add_textbox(slide, sx + 0.14, 3.02, 1.84, 0.58, st["title"], font_size=11.5, bold=True, color=(26, 115, 232) if is_hi else (32, 33, 36))
                add_textbox(slide, sx + 0.14, 3.64, 1.84, 1.38, st["body"], font_size=9.6, bold=False, color=(60, 64, 67))

        elif stype == "verification_cards":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.74, 9.04, 0.42, sdata["title"], font_size=20, bold=True, color=(32, 33, 36))
            lc = sdata["left_card"]
            rc = sdata["right_card"]
            # Left card (Blue)
            add_rounded_box(slide, 0.48, 1.20, 4.40, 3.95, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.2, radius=0.04)
            add_textbox(slide, 0.68, 1.32, 4.00, 0.35, lc["title"], font_size=14, bold=True, color=(26, 115, 232))
            add_rounded_box(slide, 0.68, 1.75, 4.00, 0.85, fill_rgb=(241, 243, 244), line_rgb=None, radius=0.03)
            add_textbox(slide, 0.80, 1.80, 3.76, 0.25, "User Query:", font_size=10, bold=True, color=(26, 115, 232))
            add_textbox(slide, 0.80, 2.05, 3.76, 0.50, lc["query"], font_size=9.5, bold=False, color=(32, 33, 36))
            add_rounded_box(slide, 0.68, 2.72, 4.00, 2.25, fill_rgb=(232, 240, 254), line_rgb=(26, 115, 232), line_pt=1.2, radius=0.03)
            add_textbox(slide, 0.80, 2.82, 3.76, 0.28, lc["result_title"], font_size=10.5, bold=True, color=(19, 115, 51))
            add_textbox(slide, 0.80, 3.12, 3.76, 1.05, lc["result_body"], font_size=9.5, bold=False, color=(32, 33, 36))
            add_textbox(slide, 0.80, 4.22, 3.76, 0.65, f"Verification Goal: {lc['goal']}", font_size=8.8, bold=False, color=(95, 99, 104))

            # Right card (Red)
            add_rounded_box(slide, 5.12, 1.20, 4.40, 3.95, fill_rgb=(255, 255, 255), line_rgb=(234, 67, 53), line_pt=2.2, radius=0.04)
            add_textbox(slide, 5.32, 1.32, 4.00, 0.35, rc["title"], font_size=14, bold=True, color=(197, 34, 31))
            add_rounded_box(slide, 5.32, 1.75, 4.00, 1.52, fill_rgb=(252, 232, 230), line_rgb=(234, 67, 53), line_pt=1, radius=0.03)
            add_textbox(slide, 5.44, 1.82, 3.76, 0.32, rc["trap1_title"], font_size=9.8, bold=True, color=(197, 34, 31))
            add_textbox(slide, 5.44, 2.14, 3.76, 0.24, rc["trap1_expected"], font_size=9.2, bold=True, color=(19, 115, 51))
            add_textbox(slide, 5.44, 2.40, 3.76, 0.80, rc["trap1_body"], font_size=9.0, bold=False, color=(32, 33, 36))

            add_rounded_box(slide, 5.32, 3.40, 4.00, 1.56, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1, radius=0.03)
            add_textbox(slide, 5.44, 3.47, 3.76, 0.32, rc["trap2_title"], font_size=9.8, bold=True, color=(176, 96, 0))
            add_textbox(slide, 5.44, 3.79, 3.76, 0.24, rc["trap2_expected"], font_size=9.2, bold=True, color=(19, 115, 51))
            add_textbox(slide, 5.44, 4.05, 3.76, 0.82, rc["trap2_body"], font_size=9.0, bold=False, color=(32, 33, 36))

        # ---- NEW TYPES (Location Intelligence deck) ----

        elif stype == "hero_media":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.55, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.10, 9.10, 0.32, sdata["subtitle"], font_size=12, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            # pptx can't animate the gif; use the extracted still frame
            still = sdata.get("image_still", sdata["image"])
            add_rounded_box(slide, 1.15, 1.55, 7.70, 3.05, fill_rgb=(13, 17, 23), line_rgb=None, radius=0.03)
            add_image_fit(slide, still, 1.20, 1.60, 7.60, 2.95)
            add_textbox(slide, 0.45, 4.70, 9.10, 0.35, sdata.get("caption", ""), font_size=8.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)

        elif stype == "diagram_build":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.52, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.05, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            n = len(sdata["build_steps"])
            top = 1.45
            row_h = 2.95 / n
            for i, st in enumerate(sdata["build_steps"]):
                y = top + i * row_h
                add_rounded_box(slide, 1.10, y, 7.80, row_h - 0.10, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.05)
                add_image_fit(slide, st["icon"], 1.28, y + 0.08, 0.46, 0.46)
                add_textbox(slide, 1.90, y + 0.02, 2.05, 0.34, st["label"], font_size=13, bold=True, color=(23, 78, 166))
                add_textbox(slide, 3.95, y + 0.02, 4.80, row_h - 0.12, st["desc"], font_size=9.5, bold=False, color=(60, 64, 67))
            add_rounded_box(slide, 1.10, 4.55, 7.80, 0.50, fill_rgb=(230, 244, 234), line_rgb=None, radius=0.3)
            add_textbox(slide, 1.10, 4.62, 7.80, 0.36, sdata["summary"], font_size=12, bold=True, color=(19, 115, 51), align=PP_ALIGN.CENTER)

        elif stype == "split_worlds":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.60, 9.10, 0.55, sdata["title"], font_size=26, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            specs = [("left", 0.55, (26, 115, 232), (232, 240, 254)), ("right", 6.05, (19, 115, 51), (230, 244, 234))]
            for key, cx, line, fill in specs:
                w = sdata[key]
                add_rounded_box(slide, cx, 1.45, 3.40, 3.30, fill_rgb=fill, line_rgb=line, line_pt=2.2, radius=0.04)
                add_image_fit(slide, w["icon"], cx + 0.18, 1.62, 0.55, 0.55)
                add_textbox(slide, cx + 0.82, 1.72, 2.40, 0.40, w["heading"], font_size=13.5, bold=True, color=line)
                add_bullet_list_box(slide, cx + 0.20, 2.30, 3.00, 2.30, None, [(None, p) for p in w["points"]], bullet_size=10.5)
            add_rounded_box(slide, 4.05, 2.55, 1.90, 1.20, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.8, radius=0.06)
            add_textbox(slide, 4.12, 2.66, 1.76, 1.00, sdata["bridge"], font_size=8.8, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)

        elif stype == "nxm":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.52, sdata["title"], font_size=24, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.05, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            for ci, (cx, cap) in enumerate([(0.55, sdata["left_caption"]), (5.15, sdata["right_caption"])]):
                add_rounded_box(slide, cx, 1.50, 4.30, 3.55, fill_rgb=(248, 249, 250), line_rgb=(218, 220, 224), line_pt=1.2, radius=0.04)
                add_textbox(slide, cx + 0.10, 1.58, 4.10, 0.30, cap, font_size=10.5, bold=True, color=(95, 99, 104), align=PP_ALIGN.CENTER)
                for ri, a in enumerate(sdata["agents"]):
                    add_rounded_box(slide, cx + 0.25, 2.05 + ri * 0.92, 1.45, 0.72, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=1.5, radius=0.08)
                    add_textbox(slide, cx + 0.25, 2.22 + ri * 0.92, 1.45, 0.40, a, font_size=9.5, bold=True, color=(23, 78, 166), align=PP_ALIGN.CENTER)
                for ri, sv in enumerate(sdata["servers"]):
                    add_rounded_box(slide, cx + 2.60, 2.05 + ri * 0.92, 1.45, 0.72, fill_rgb=(255, 255, 255), line_rgb=(19, 115, 51), line_pt=1.5, radius=0.08)
                    add_textbox(slide, cx + 2.60, 2.22 + ri * 0.92, 1.45, 0.40, sv, font_size=9.5, bold=True, color=(19, 115, 51), align=PP_ALIGN.CENTER)
                if ci == 0:
                    add_textbox(slide, cx + 1.80, 2.40, 0.70, 1.60, "✕\n✕\n✕", font_size=20, bold=True, color=(234, 67, 53), align=PP_ALIGN.CENTER)
                else:
                    hub = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx + 1.80), Inches(2.75), Inches(0.72), Inches(0.72))
                    hub.fill.solid(); hub.fill.fore_color.rgb = RGBColor(26, 115, 232); hub.line.fill.background()
                    add_textbox(slide, cx + 1.80, 2.93, 0.72, 0.36, "MCP", font_size=10, bold=True, color=(255, 255, 255), align=PP_ALIGN.CENTER)

        elif stype == "tool_catalog":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            accent = sdata.get("accent", "blue")
            ac = (23, 78, 166) if accent == "blue" else (19, 115, 51)
            add_image_fit(slide, sdata["icon"], 0.55, 0.55, 0.55, 0.55)
            add_textbox(slide, 1.25, 0.60, 8.20, 0.40, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 1.25, 1.02, 8.20, 0.28, sdata["subtitle"], font_size=11, bold=False, color=(95, 99, 104))
            n = len(sdata["tools"])
            top = 1.50
            row_h = 2.85 / n
            for i, (t, d) in enumerate(sdata["tools"]):
                y = top + i * row_h
                add_rounded_box(slide, 0.55, y, 8.90, row_h - 0.08, fill_rgb=(255, 255, 255), line_rgb=(218, 220, 224), line_pt=1, radius=0.05)
                add_rounded_box(slide, 0.72, y + 0.06, 2.95, row_h - 0.20, fill_rgb=(241, 243, 244), line_rgb=None, radius=0.05)
                add_textbox(slide, 0.80, y + 0.09, 2.80, row_h - 0.24, t, font_size=11, bold=True, color=ac, font_name="Roboto Mono")
                add_textbox(slide, 3.85, y + 0.05, 5.45, row_h - 0.14, d, font_size=10, bold=False, color=(32, 33, 36))
            add_rounded_box(slide, 0.55, 4.50, 8.90, 0.62, fill_rgb=(254, 247, 224), line_rgb=(251, 188, 4), line_pt=1.2, radius=0.04)
            add_textbox(slide, 0.72, 4.55, 8.60, 0.52, sdata["callout"], font_size=9.2, bold=True, color=(32, 33, 36))

        elif stype == "code_focus":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.48, 0.70, 9.04, 0.45, sdata["title"], font_size=22, bold=True, color=(32, 33, 36))
            add_textbox(slide, 0.48, 1.16, 5.30, 0.30, sdata["subtitle"], font_size=11.5, bold=True, color=(26, 115, 232))
            add_terminal_box(slide, 0.48, 1.52, 5.35, 3.55, sdata.get("lang", "python"), sdata["code"], font_size=8.8)
            add_rounded_box(slide, 6.02, 1.52, 3.50, 3.55, fill_rgb=(255, 255, 255), line_rgb=(26, 115, 232), line_pt=2.2, radius=0.04)
            add_textbox(slide, 6.22, 1.66, 3.10, 0.30, "The three control surfaces:", font_size=11, bold=True, color=(32, 33, 36))
            add_bullet_list_box(slide, 6.20, 2.02, 3.14, 2.95, None, [(k, v) for k, v in sdata["callouts"]], bullet_size=10)

        elif stype == "journey_storyboard":
            slide = prs.slides.add_slide(layout_content)
            clear_slide_shapes(slide)
            add_textbox(slide, 0.45, 0.55, 9.10, 0.50, sdata["title"], font_size=23, bold=True, color=(32, 33, 36), align=PP_ALIGN.CENTER)
            add_textbox(slide, 0.45, 1.04, 9.10, 0.30, sdata["subtitle"], font_size=11.5, bold=False, color=(95, 99, 104), align=PP_ALIGN.CENTER)
            n = len(sdata["steps"])
            top = 1.48
            row_h = 3.55 / n
            cmap = {"blue": (26, 115, 232), "green": (19, 115, 51), "yellow": (176, 96, 0)}
            for i, (tag, q, tool, res, color) in enumerate(sdata["steps"]):
                y = top + i * row_h
                line = cmap.get(color, (218, 220, 224))
                add_rounded_box(slide, 0.55, y, 8.90, row_h - 0.10, fill_rgb=(255, 255, 255), line_rgb=line, line_pt=1.5, radius=0.05)
                add_textbox(slide, 0.70, y + 0.04, 0.62, row_h - 0.18, tag, font_size=15, bold=True, color=line)
                add_textbox(slide, 1.38, y + 0.04, 4.05, row_h - 0.18, q, font_size=10.3, bold=True, color=(32, 33, 36))
                add_textbox(slide, 5.50, y + 0.04, 2.05, row_h - 0.18, tool, font_size=8.6, bold=False, color=(95, 99, 104), font_name="Roboto Mono")
                add_textbox(slide, 7.62, y + 0.04, 1.72, row_h - 0.18, res, font_size=8.8, bold=True, color=(32, 33, 36), align=PP_ALIGN.RIGHT)

        set_slide_notes(slide, sdata["notes"])

    prs.save(output_path)
    print(f"Saved PPTX: {output_path} ({len(prs.slides)} slides)")


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
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <div class="cover-left">
            <div class="pill-badge">{html.escape(s.get('badge', 'Workshop'))}</div>
            <h1 class="cover-title">{title_html}</h1>
            <p class="cover-subtitle">{html.escape(s['subtitle'])}</p>
            <div class="cover-meta">Rabimba Karanjai • Google Developer Expert (AI/ML)</div>
          </div>
          <div class="cover-right">
            <img src="assets/bg_cover_layers_cropped.png" alt="Google Cloud Layers"/>
          </div>
        </div>
        """

    if stype == "big_qr":
        badge = 'Proprietary + Confidential' if CONFIDENTIAL_BADGE else 'Google Developer Expert'
        wifi_html = ""
        if s.get("wifi_ssid"):
            wifi_html = f"""
            <div class="wifi-chip">Wi-Fi: <strong>{html.escape(s['wifi_ssid'])}</strong> &nbsp;·&nbsp; Password: <code>{html.escape(s['wifi_pass'])}</code></div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">{badge}</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="big-qr-wrap">
            <a href="{html.escape(s['url'])}" target="_blank" class="big-qr-card">
              <img src="assets/{html.escape(s['qr'])}" alt="Credit redemption QR code"/>
            </a>
            <a href="{html.escape(s['url'])}" target="_blank" class="big-qr-link">{html.escape(s['url_text'])}</a>
            <p class="big-qr-desc">{html.escape(s['desc'])}</p>
            {wifi_html}
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "qr_hub":
        cards_html = ""
        for c in s["cards"]:
            cards_html += f"""
            <div class="qr-card">
              <div class="qr-icon-badge">&lt;/&gt;</div>
              <h3>{html.escape(c['title'])}</h3>
              <a href="{html.escape(c['url'])}" target="_blank" class="qr-link">{html.escape(c['url_text'])}</a>
              <p>{html.escape(c['desc'])}</p>
              <img class="qr-img" src="assets/{html.escape(c['qr'])}" alt="QR Code"/>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="qr-grid">{cards_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "speaker":
        return f"""
        <div class="slide-canvas slide-speaker">
          <div class="speaker-fan-bg">
            <img src="assets/bg_speaker_fan.png" alt="Fan Background"/>
          </div>
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <span class="prop-badge-abs">Google Developer Expert</span>
          <div class="speaker-content">
            <div class="speaker-photo-wrap">
              <img src="assets/{html.escape(s['photo'])}" alt="Rabimba Karanjai"/>
            </div>
            <div class="speaker-Bio-text">
              <h1>Rabimba<br/>Karanjai</h1>
              <p class="role-line">Google Developer Expert — AI &amp; ML</p>
              <p class="role-line">ML Scientist — PayPal</p>
              <div class="speaker-tags">
                <span class="tag-chip">GKE Cloud TPU v6e</span>
                <span class="tag-chip">Gateway API Inference Extension</span>
                <span class="tag-chip">vllm-torchtpu &amp; llm-d</span>
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
          <div class="speaker-fan-bg">
            <img src="assets/bg_speaker_fan.png" alt="Fan Background"/>
          </div>
          <img class="gcl-logo" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
          <span class="prop-badge-abs">Google Developer Expert</span>
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
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="section-poll-wrap">
            <img class="section-robot-icon" src="assets/{html.escape(s['icon'])}" alt="Agent Icon"/>
            <h2>{html.escape(s['title']).replace(chr(10), '<br/>')}</h2>
            <div class="interactive-poll-card">
              <div class="poll-q">{html.escape(p['question'])}</div>
              <ul class="poll-opts">{opts}</ul>
              <button class="reveal-btn" onclick="this.nextElementSibling.classList.toggle('visible')">✨ Reveal Takeaway</button>
              <div class="poll-answer">💡 {html.escape(p['answer'])}</div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "agent_triad":
        b0, b1, b2 = s["boxes"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="triad-headline">
            An AI coding agent is a system that uses a <span class="hl-blue">model</span> to reason, an <span class="hl-blue">agent harness</span> to plan &amp; execute, and <span class="hl-blue">MCP &amp; skills</span> to access authoritative knowledge and tools.
          </div>
          <div class="triad-row">
            <div class="triad-box">
              <img src="assets/{html.escape(b0['icon'])}" alt="Tools"/>
              <h3>{html.escape(b0['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box triad-center">
              <img src="assets/{html.escape(b1['icon'])}" alt="Agent"/>
              <h3>{html.escape(b1['label']).replace(chr(10), '<br/>')}</h3>
            </div>
            <div class="triad-arrow">⟷</div>
            <div class="triad-box">
              <img src="assets/{html.escape(b2['icon'])}" alt="Model"/>
              <h3>{html.escape(b2['label']).replace(chr(10), '<br/>')}</h3>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "objectives_card":
        b_html = "".join(f"<li><strong class='hl-blue'>• {html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="blue-outline-card">
            <p class="card-intro">{html.escape(s['intro'])}</p>
            <ul class="obj-list">{b_html}</ul>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "arch_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
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
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="three-tech-grid">{cols_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "two_cards_quiz":
        lc, rc, q = s["left_card"], s["right_card"], s["quiz"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["items"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["items"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "lab_divider":
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="lab-divider-center">
            <h1>{html.escape(s['title'])}</h1>
            <div class="lab-sub-row">
              <img src="assets/ref_slide11_pic4.png" alt="Google G"/>
              <span>{html.escape(s['subtitle'])}</span>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "code_split":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        intro_p = f"<p class='body-p'>{html.escape(s['intro'])}</p>" if s.get("intro") else ""
        shot_html = ""
        if s.get("screenshot"):
            shot_html = f"""
            <div class="shot-preview-box">
              <img class="zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Codelab Screenshot" onclick="openLightbox(this.src)"/>
              <span class="click-hint">🔍 Click screenshot to zoom</span>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
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
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "two_cards_code":
        lc, rc = s["left_card"], s["right_card"]
        li_l = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in lc["bullets"])
        li_r = "".join(f"<li><strong>{html.escape(t)}:</strong> {html.escape(b)}</li>" for t, b in rc["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "checkpoint_visual":
        b_html = "".join(f"<li><strong>{html.escape(bt)}:</strong> {html.escape(bb)}</li>" for bt, bb in s["bullets"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
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
              <img class="arch-img zoomable" src="assets/{html.escape(s['screenshot'])}" alt="Codelab Screenshot" onclick="openLightbox(this.src)"/>
              <p class="img-caption">{html.escape(s.get('caption', ''))} (Click to zoom)</p>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
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
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
          <p class="body-p">{html.escape(s['intro'])}</p>
          <div class="four-steps-grid">{steps_html}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "verification_cards":
        lc, rc = s["left_card"], s["right_card"]
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="title-with-timer">
            <h2 class="slide-h2">{html.escape(s['title'])}</h2>
            {timer_html}
          </div>
          <div class="dual-cards-row">
            <div class="bordered-card card-blue">
              <h3>{html.escape(lc['title'])}</h3>
              <div class="query-box">
                <strong>User Query:</strong><br/>
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
            <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    # ---- NEW TYPES (Location Intelligence deck) ----

    if stype == "hero_media":
        media = s["image"]
        is_gif = media.lower().endswith(".gif")
        tag = f'<img src="assets/{html.escape(media)}" alt="demo"/>' if True else ""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="hero-media-wrap">
            {tag}
          </div>
          <p class="hero-caption">{html.escape(s.get('caption',''))}</p>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "diagram_build":
        steps_html = ""
        for i, st in enumerate(s["build_steps"]):
            steps_html += f"""
            <div class="build-step" data-step="{i}">
              <img src="assets/{html.escape(st['icon'])}" alt="icon"/>
              <div class="build-step-text"><h3>{html.escape(st['label'])}</h3><p>{html.escape(st['desc'])}</p></div>
            </div>
            """
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="build-col">{steps_html}</div>
          <div class="build-summary">{html.escape(s['summary'])}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "split_worlds":
        def _world(w):
            pts = "".join(f"<li>{html.escape(p)}</li>" for p in w["points"])
            return f"""
            <div class="world-card world-{w['color']}">
              <img src="assets/{html.escape(w['icon'])}" alt="icon"/>
              <h3>{html.escape(w['heading'])}</h3>
              <ul>{pts}</ul>
            </div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <div class="worlds-row">
            {_world(s['left'])}
            <div class="worlds-bridge">{html.escape(s['bridge'])}</div>
            {_world(s['right'])}
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "nxm":
        agents = "".join(f'<div class="nxm-node nxm-agent">{html.escape(a)}</div>' for a in s["agents"])
        servers = "".join(f'<div class="nxm-node nxm-server">{html.escape(x)}</div>' for x in s["servers"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="nxm-cols">
            <div class="nxm-col">
              <div class="nxm-caption">{html.escape(s['left_caption'])}</div>
              <div class="nxm-mesh">
                <div class="nxm-side">{agents}</div>
                <div class="nxm-tangle">✕ ✕ ✕<br/>✕ ✕ ✕</div>
                <div class="nxm-side">{servers}</div>
              </div>
            </div>
            <div class="nxm-col">
              <div class="nxm-caption">{html.escape(s['right_caption'])}</div>
              <div class="nxm-mesh">
                <div class="nxm-side">{agents}</div>
                <div class="nxm-hub">MCP</div>
                <div class="nxm-side">{servers}</div>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "tool_catalog":
        accent = s.get("accent","blue")
        rows = "".join(
            f'<div class="tool-row"><code class="tool-name">{html.escape(t)}</code><span class="tool-desc">{html.escape(d)}</span></div>'
            for t, d in s["tools"]
        )
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <div class="tool-cat-head">
            <img src="assets/{html.escape(s['icon'])}" alt="icon"/>
            <div><h2 class="slide-h2">{html.escape(s['title'])}</h2><p class="body-p">{html.escape(s['subtitle'])}</p></div>
          </div>
          <div class="tool-list tool-accent-{accent}">{rows}</div>
          <div class="tool-callout">{html.escape(s['callout'])}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "code_focus":
        callouts = "".join(f"<li><code>{html.escape(k)}</code> — {html.escape(v)}</li>" for k, v in s["callouts"])
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="slide-h2">{html.escape(s['title'])}</h2>
          <div class="split-2col">
            <div class="col-left">
              <h3 class="sub-blue">{html.escape(s['subtitle'])}</h3>
              <div class="terminal-card">
                <div class="term-header">
                  <div class="term-dots"><span class="dot-r"></span><span class="dot-y"></span><span class="dot-g"></span></div>
                  <span class="term-title">{html.escape(s.get('lang','python'))}</span>
                  <button class="copy-btn" onclick="copyCode(this)">📋 Copy</button>
                </div>
                <pre class="term-body"><code>{html.escape(s['code'])}</code></pre>
              </div>
            </div>
            <div class="col-right">
              <div class="blue-outline-card">
                <p class="card-intro">The three control surfaces:</p>
                <ul class="obj-list">{callouts}</ul>
              </div>
            </div>
          </div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    if stype == "journey_storyboard":
        rows = ""
        for tag, q, tool, res, color in s["steps"]:
            rows += f"""
            <div class="journey-row journey-{color}">
              <span class="journey-tag">{html.escape(tag)}</span>
              <span class="journey-q">{html.escape(q)}</span>
              <span class="journey-tool">{html.escape(tool)}</span>
              <span class="journey-res">{html.escape(res)}</span>
            </div>"""
        return f"""
        <div class="slide-canvas slide-standard">
          <div class="slide-top-bar">
            <img class="gcl-logo-sm" src="assets/logo_gcloud_labs.png" alt="Google Cloud Labs"/>
            <span class="module-pill">{html.escape(s['module'])} • {html.escape(s['time'])}</span>
            <span class="prop-badge">Google Developer Expert</span>
          </div>
          <h2 class="center-title">{html.escape(s['title'])}</h2>
          <p class="center-subtitle">{html.escape(s['subtitle'])}</p>
          <div class="journey-table">{rows}</div>
          <img class="gcl-footer" src="assets/logo_gcloud_footer.png" alt="Google Cloud"/>
        </div>
        """

    return ""


def get_slide_title(s):
    if "title" in s:
        return s["title"].replace("\n", " ")
    if "headline" in s:
        return "Anatomy of an AI Coding Agent"
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
  <title>Defeating the Prefix-Cache Penalty: KV-Aware Routing &amp; Disaggregated Serving on GKE — KubeCon 2026</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --g-blue: #1A73E8;
      --g-blue-dark: #174EA6;
      --g-blue-bg: #E8F0FE;
      --g-red: #EA4335;
      --g-red-dark: #C5221F;
      --g-red-bg: #FCE8E6;
      --g-yellow: #FBBC04;
      --g-yellow-bg: #FEF7E0;
      --g-green: #34A853;
      --g-green-dark: #137333;
      --g-dark: #202124;
      --g-gray: #5F6368;
      --g-border: #DADCE0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Google Sans', 'Roboto', system-ui, sans-serif;
      background: #111318;
      color: var(--g-dark);
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
    /* Slides lay out once on a fixed 1600x900 design canvas; JS sets --deck-scale
       so the whole slide scales uniformly to fit any window size or browser zoom. */
    .slide {{
      display: none;
      width: 1600px;
      height: 900px;
      background: #FFFFFF;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.55);
      position: absolute;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%) scale(var(--deck-scale, 0.9));
      transform-origin: center center;
      overflow: hidden;
    }}
    .slide.active {{ display: block; }}
    .slide-canvas {{
      width: 100%;
      height: 100%;
      position: relative;
      padding: 2.2% 4.2%;
      display: flex;
      flex-direction: column;
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
    .gcl-footer {{ position: absolute; bottom: 2.8%; left: 4.2%; height: 15px; opacity: 0.85; }}
    .prop-badge {{ font-size: 0.78rem; color: var(--g-gray); font-weight: 500; }}
    .prop-badge-abs {{ position: absolute; top: 4.5%; right: 4.2%; font-size: 0.78rem; color: var(--g-gray); z-index: 5; }}
    .module-pill {{
      background: #F1F3F4;
      color: var(--g-gray);
      padding: 4px 14px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
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
      font-size: 3.1rem;
      line-height: 1.16;
      font-weight: 700;
      color: var(--g-dark);
      margin-bottom: 18px;
    }}
    .cover-subtitle {{
      font-size: 1.3rem;
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
    .center-title {{ text-align: center; font-size: 2.4rem; font-weight: 700; margin-bottom: 4px; }}
    .center-subtitle {{ text-align: center; font-size: 1rem; color: var(--g-gray); margin-bottom: 18px; }}
    .qr-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 2.2%;
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
    .big-qr-card img {{ display: block; width: 340px; height: auto; aspect-ratio: 1; }}
    .big-qr-link {{
      font-size: 1.9rem; font-weight: 700; color: var(--g-blue);
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
      width: 330px;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 22px;
      box-shadow: 0 12px 32px rgba(0,0,0,0.28);
      border: 4px solid #fff;
    }}
    .speaker-Bio-text h1 {{ font-size: 3.8rem; line-height: 1.12; margin-bottom: 16px; }}
    .role-line {{ font-size: 1.55rem; color: #3C4043; margin-bottom: 8px; font-weight: 500; }}
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
    .thankyou-text h1 {{ font-size: 4.2rem; margin-bottom: 12px; }}
    .thankyou-text p {{ font-size: 1.05rem; color: var(--g-gray); line-height: 1.5; }}
    .thankyou-qrs {{ display: flex; flex-direction: column; gap: 18px; }}
    .ty-qr-box {{ display: flex; flex-direction: column; align-items: center; text-align: center; background: #F8F9FA; padding: 10px; border-radius: 12px; border: 1px solid var(--g-border); width: 185px; }}
    .ty-qr-box img {{ width: 125px; height: 125px; margin-bottom: 6px; }}
    .ty-qr-box span {{ font-size: 0.72rem; color: var(--g-blue-dark); font-weight: 600; line-height: 1.25; }}

    /* Section Poll Slide */
    .section-poll-wrap {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; max-width: 88%; margin: 0 auto; }}
    .section-robot-icon {{ width: 64px; height: 64px; margin-bottom: 8px; }}
    .section-poll-wrap h2 {{ font-size: 2.5rem; margin-bottom: 16px; line-height: 1.18; }}
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
      font-size: 2.15rem;
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
    .slide-h2 {{ font-size: 2.05rem; font-weight: 700; margin-bottom: 8px; color: var(--g-dark); }}
    .sub-blue {{ font-size: 1.22rem; color: var(--g-blue); font-weight: 700; margin-bottom: 8px; }}
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
    .lab-divider-center h1 {{ font-size: 3.8rem; margin-bottom: 18px; }}
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

    /* ---- NEW slide types (Location Intelligence) ---- */
    .hero-media-wrap {{
      flex: 1; display: flex; align-items: center; justify-content: center;
      background: #0d1117; border-radius: 12px; overflow: hidden; margin: 1% 0;
    }}
    .hero-media-wrap img {{ width: 100%; height: 100%; object-fit: contain; }}
    .hero-caption {{ text-align: center; font-size: 0.8rem; color: var(--g-gray); margin-bottom: 2%; }}

    .build-col {{ display: flex; flex-direction: column; gap: 2.2%; flex: 1; margin-top: 1%; }}
    .build-step {{
      display: flex; align-items: center; gap: 18px;
      background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px;
      padding: 2.4% 3%;
    }}
    .build-step img {{ width: 46px; height: 46px; object-fit: contain; flex: 0 0 auto; }}
    .build-step-text h3 {{ font-size: 1.1rem; font-weight: 700; color: var(--g-blue-dark); margin-bottom: 2px; }}
    .build-step-text p {{ font-size: 0.92rem; color: var(--g-gray); line-height: 1.35; }}
    .build-summary {{
      margin-top: 2%; margin-bottom: 2.5%; text-align: center; font-weight: 700; font-size: 1.05rem;
      color: var(--g-green-dark); background: #E6F4EA; border-radius: 999px; padding: 10px 18px;
    }}

    .worlds-row {{ display: flex; align-items: stretch; gap: 2%; flex: 1; margin-top: 2%; }}
    .world-card {{
      flex: 1; border-radius: 14px; padding: 3%; border: 2px solid var(--g-border);
      display: flex; flex-direction: column;
    }}
    .world-card img {{ width: 52px; height: 52px; object-fit: contain; margin-bottom: 10px; }}
    .world-card h3 {{ font-size: 1.15rem; margin-bottom: 10px; }}
    .world-card ul {{ margin-left: 18px; font-size: 0.95rem; color: var(--g-dark); line-height: 1.6; }}
    .world-blue {{ border-color: var(--g-blue); background: var(--g-blue-bg); }}
    .world-blue h3 {{ color: var(--g-blue-dark); }}
    .world-green {{ border-color: var(--g-green); background: #E6F4EA; }}
    .world-green h3 {{ color: var(--g-green-dark); }}
    .worlds-bridge {{
      align-self: center; flex: 0 0 16%; text-align: center; font-weight: 700;
      font-size: 0.9rem; color: var(--g-dark);
      background: var(--g-yellow-bg); border: 2px dashed var(--g-yellow);
      border-radius: 12px; padding: 12px;
    }}

    .nxm-cols {{ display: flex; gap: 3%; flex: 1; margin-top: 1%; }}
    .nxm-col {{ flex: 1; display: flex; flex-direction: column; }}
    .nxm-caption {{ text-align: center; font-size: 0.9rem; font-weight: 600; color: var(--g-gray); margin-bottom: 8px; }}
    .nxm-mesh {{
      flex: 1; display: flex; align-items: center; justify-content: space-between;
      background: #F8F9FA; border: 1.5px solid var(--g-border); border-radius: 12px; padding: 4%;
    }}
    .nxm-side {{ display: flex; flex-direction: column; gap: 12px; }}
    .nxm-node {{
      padding: 10px 14px; border-radius: 10px; font-weight: 600; font-size: 0.85rem; text-align: center;
      border: 1.5px solid var(--g-border); background: #fff;
    }}
    .nxm-agent {{ border-color: var(--g-blue); color: var(--g-blue-dark); }}
    .nxm-server {{ border-color: var(--g-green); color: var(--g-green-dark); }}
    .nxm-tangle {{ color: var(--g-red); font-size: 1.4rem; text-align: center; line-height: 1.1; }}
    .nxm-hub {{
      align-self: center; background: var(--g-blue); color: #fff; font-weight: 700;
      padding: 16px 22px; border-radius: 999px; font-size: 1.1rem;
      box-shadow: 0 6px 18px rgba(26,115,232,0.35);
    }}

    .tool-cat-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 1%; }}
    .tool-cat-head img {{ width: 54px; height: 54px; object-fit: contain; }}
    .tool-list {{ display: flex; flex-direction: column; gap: 10px; margin-top: 1%; }}
    .tool-row {{
      display: flex; align-items: center; gap: 16px;
      background: #fff; border: 1.5px solid var(--g-border); border-radius: 10px; padding: 10px 2%;
    }}
    .tool-name {{
      font-family: 'Roboto Mono', monospace; font-weight: 700; font-size: 0.95rem;
      background: #F1F3F4; padding: 4px 10px; border-radius: 6px; flex: 0 0 34%;
    }}
    .tool-accent-blue .tool-name {{ color: var(--g-blue-dark); }}
    .tool-accent-green .tool-name {{ color: var(--g-green-dark); }}
    .tool-desc {{ font-size: 0.9rem; color: var(--g-dark); }}
    .tool-callout {{
      margin-top: 2%; font-size: 0.92rem; font-weight: 600; color: var(--g-dark);
      background: var(--g-yellow-bg); border-left: 4px solid var(--g-yellow);
      border-radius: 8px; padding: 12px 16px;
    }}

    .journey-table {{ display: flex; flex-direction: column; gap: 1.6%; flex: 1; margin-top: 1%; }}
    .journey-row {{
      display: grid; grid-template-columns: 7% 44% 26% 23%; align-items: center;
      gap: 1.5%; padding: 1.5% 2%; border-radius: 10px; border: 1.5px solid var(--g-border); background: #fff;
    }}
    .journey-tag {{ font-weight: 800; font-size: 1rem; }}
    .journey-blue .journey-tag {{ color: var(--g-blue); }}
    .journey-green .journey-tag {{ color: var(--g-green); }}
    .journey-yellow .journey-tag {{ color: #B06000; }}
    .journey-q {{ font-size: 0.92rem; font-weight: 600; color: var(--g-dark); }}
    .journey-tool {{ font-family: 'Roboto Mono', monospace; font-size: 0.8rem; color: var(--g-gray); }}
    .journey-res {{ font-size: 0.82rem; font-weight: 700; color: var(--g-dark); text-align: right; }}
    .journey-blue {{ border-left: 5px solid var(--g-blue); }}
    .journey-green {{ border-left: 5px solid var(--g-green); }}
    .journey-yellow {{ border-left: 5px solid var(--g-yellow); }}
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
      <span id="talk-clock" style="font-family:'Roboto Mono',monospace; color:#FBBC04; font-weight:700;">⏱️ Talk Clock: 00:00 / 15:00</span>
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
    const channel = new BroadcastChannel('kubecon26_fleetkv_sync');

    // Scale the fixed 1600x900 slide canvas to fit the available viewport.
    // Must run before the first showSlide() so initial measurements are correct.
    function fitDeck() {{
      const vp = document.getElementById('deck-viewport');
      const s = Math.min((vp.clientWidth - 24) / 1600, (vp.clientHeight - 24) / 900);
      document.documentElement.style.setProperty('--deck-scale', Math.max(0.1, s).toFixed(4));
    }}
    new ResizeObserver(fitDeck).observe(document.getElementById('deck-viewport'));
    window.addEventListener('resize', fitDeck);
    fitDeck();

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
      fitDeck();
      if (broadcast) {{
        channel.postMessage({{ type: 'SLIDE_CHANGE', slide: currentSlide }});
      }}
    }}

    function nextSlide() {{ showSlide(currentSlide + 1); }}
    function prevSlide() {{ showSlide(currentSlide - 1); }}

    function toggleNotesDrawer() {{
      document.body.classList.toggle('notes-open');
      document.getElementById('notes-btn').classList.toggle('active-toggle');
      fitDeck();
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen();
      }} else {{
        document.exitFullscreen();
      }}
    }}

    // Control bar: hidden by default, press B to toggle, force-hidden in fullscreen
    function toggleControlBar() {{ document.body.classList.toggle('controls-visible'); fitDeck(); }}
    document.addEventListener('fullscreenchange', () => {{
      document.body.classList.toggle('is-fullscreen', !!document.fullscreenElement);
      fitDeck();
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
          document.getElementById('talk-clock').textContent = `⏱️ Talk Clock: ${{m}}:${{s}} / 15:00`;
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
  <title>Speaker Notes &amp; Teleprompter — KubeCon 2026 FleetKV &amp; GKE</title>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Google Sans', system-ui, sans-serif;
      background: #0F1117;
      color: #E8EAED;
      margin: 0;
      padding: 0;
    }}
    header {{
      position: sticky; top: 0; z-index: 50;
      background: #181B24;
      border-bottom: 2px solid #1A73E8;
      padding: 12px 24px;
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 12px;
    }}
    .ctrl-row {{ display: flex; align-items: center; gap: 10px; }}
    button {{
      background: #1A73E8; color: #fff; border: none;
      padding: 7px 14px; border-radius: 6px; font-weight: 600; cursor: pointer;
    }}
    button:hover {{ background: #174EA6; }}
    #live-banner {{
      background: #1E2436; border: 2px solid #4285F4;
      margin: 18px 24px; padding: 18px 22px; border-radius: 12px;
    }}
    #live-banner h3 {{ color: #8AB4F8; margin-bottom: 6px; font-size: 1.2rem; }}
    #live-notes {{ white-space: pre-wrap; font-size: 1.15rem; line-height: 1.55; color: #FFF; }}
    #live-next {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid #3C4043; color: #FBBC04; font-weight: 600; }}
    .container {{ max-width: 980px; margin: 0 auto; padding: 12px 24px 60px 24px; }}
    .note-card {{
      background: #181B24; border: 1.5px solid #2D3242;
      border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
    }}
    .note-card.active-card {{ border-color: #4285F4; box-shadow: 0 0 0 2px rgba(66,133,244,0.35); }}
    .note-hdr {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px; }}
    .badge-num {{ background: #1A73E8; color: #fff; padding: 3px 10px; border-radius: 99px; font-weight: 700; font-size: 0.8rem; }}
    .badge-mod {{ color: #8AB4F8; font-size: 0.85rem; font-weight: 600; }}
    .badge-time {{ color: #FBBC04; font-size: 0.85rem; font-weight: 600; margin-left: auto; }}
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
      <span id="console-counter" style="font-weight:700; min-width:80px; text-align:center;">Slide 1 / 14</span>
      <button onclick="stepSlide(1)">Next Slide ▶</button>
    </div>
  </header>

  <div id="live-banner">
    <h3 id="live-title">Current Slide: 1</h3>
    <div id="live-notes"></div>
    <div id="live-next">Next Slide: 2</div>
  </div>

  <div class="container">
    <h2 style="margin-bottom:14px; color:#8AB4F8;">All 14 Slides — Continuous Speaker Script &amp; Copy-Paste Snippets</h2>
    {''.join(notes_cards_html)}
  </div>

  <script>
    const NOTES = {json.dumps(notes_json)};
    let cur = 1;
    const channel = new BroadcastChannel('kubecon26_fleetkv_sync');

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
        "# 🎤 Speaker Notes, Live Demo Runbook & Verbatim Talk Script",
        "",
        "## **Defeating the Prefix-Cache Penalty: KV-Aware Routing and Disaggregated Serving for Agent Fleets on GKE**",
        "- **Event**: KubeCon 2026 Technical Session (15 Minutes + Q&A)",
        "- **Speaker**: Rabimba Karanjai (Google Developer Expert — AI/ML | ML Scientist — PayPal)",
        "- **Companion Repository**: [https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26](https://github.com/rabimba/GDE-ML-Artifacts/tree/main/KubeCon26)",
        "",
        "---",
        "",
        "## ⚡ How to Present Directly from This Folder",
        "",
        "1. **Option A — Interactive Google-Branded Web Deck + Dual-Screen Presenter Console (Recommended)**:",
        "   - Open `slides/index.html` in Chrome (or serve via `make slides-serve`).",
        "   - Press **`P`** to pop out the synchronized **Speaker Notes & Teleprompter Console** (`speaker-notes.html`) on your laptop screen while dragging the main slide window to the stage projector.",
        "   - Press **`S`** to toggle the inline Speaker Notes drawer at the bottom of the screen.",
        "   - Press **`B`** to toggle the bottom presenter toolbar (includes the 15-minute talk clock).",
        "   - Press **`G`** for the all-slides grid overview, **`F`** for Fullscreen, and **`←` / `→` / `Space`** to advance slides.",
        "2. **Option B — Google Slides / PowerPoint Presenter View**:",
        "   - Open `slides/KubeCon26-FleetKV-GKE.pptx` in Google Slides, PowerPoint, or Keynote.",
        "   - Every slide uses the Google Cloud Labs master layouts with complete speaker notes embedded in the native Speaker Notes pane.",
        "3. **Option C — Slidev Markdown Deck**:",
        "   - Run `npx @slidev/cli slides/slides.md` if you prefer the Slidev workflow.",
        "",
        "---",
        "",
        "## ⏱️ 15-Minute Pacing Schedule & Live Demo Cue Sheet",
        "",
        "| Clock Time | Duration | Section | Slides | Stage Action / Key Proof Point |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **00:00 – 01:20** | 1m 20s | **Opening & Companion Repo** | Slides 1–3 | Frame stateless K8s vs. agent trees; share repo & slide QR codes |",
        "| **01:20 – 03:20** | 2m 00s | **Part 1: Agent Trees & Fork-Storms** | Slides 4–5 | 20,480-token trunk (`80` blocks) + 8-way fork + `8,192`-tok log burst |",
        "| **03:20 – 05:00** | 1m 40s | **Part 2: Two Routing Failure Modes** | Slide 6 | Failure Mode 1 (`1/N` scatter) vs. Failure Mode 2 (Prefix-Herd Trap) |",
        "| **05:00 – 08:30** | 3m 30s | **Part 3: FleetKV + TorchTPU Disagg** | Slides 7–9 | HBM Fit Gate, staged prefill leases, `TPUConnectorHMA` Tier-2 DRAM |",
        "| **08:30 – 11:45** | 3m 15s | **Part 4: Live 3-Stage Traffic Flip** | Slide 10 | Switch to `tmux`: flip `stage1` → `stage2` → `stage3` on 4-col TUI |",
        "| **11:45 – 13:30** | 1m 45s | **Part 5 & 6: Scorecard & Invariants** | Slides 11–12 | Twin Gate G1 + GKE TPU v6e numbers; 3 CI-audited GKE invariants |",
        "| **13:30 – 15:00** | 1m 30s | **Wrap-Up & Q&A** | Slides 13–14 | Copy-paste reproduction commands & Q&A |",
        "",
        "---",
        "",
        "## 📋 Slide-by-Slide Verbatim Speaker Script & Code Snippets",
        "",
    ]

    for s in SLIDES_DATA:
        stitle = get_slide_title(s)
        lines.append(f"### Slide {s['num']}: {stitle}")
        lines.append(f"- **Section**: {s['module']}")
        lines.append(f"- **Pacing**: `{s['time']}`")
        lines.append("")
        lines.append("#### 🎙️ Speaker Notes:")
        lines.append("```text")
        lines.append(s["notes"])
        lines.append("```")
        code_val = s.get("code") or (s.get("left_card", {}).get("code", "") + ("\n\n" + s.get("right_card", {}).get("code", "") if s.get("right_card", {}).get("code") else ""))
        if code_val:
            lines.append("")
            lines.append(f"#### 💻 On-Slide Code / Command (`{s.get('code_title', s.get('lang', 'Snippet'))}`):")
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
    ensure_generated_assets()
    pptx_out = os.path.join(BASE_DIR, "KubeCon26-FleetKV-GKE.pptx")
    html_out = os.path.join(BASE_DIR, "index.html")
    notes_html_out = os.path.join(BASE_DIR, "speaker-notes.html")
    md_out = os.path.join(BASE_DIR, "SPEAKER_NOTES_AND_SCRIPT.md")

    build_pptx(pptx_out)
    build_html_deck(html_out)
    build_speaker_notes_html(notes_html_out)
    build_markdown_runbook(md_out)
