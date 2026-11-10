# Parses XProf (.pt.trace.json) traces from AutoKernel Lab and plots the 4-way TPU timeline.
import glob
import importlib.util
import json
import os
import re

_KV_LINE_RE = re.compile(r'^(\s*"[^"]+"\s*:\s*)"(.*)"(\s*,?\s*)$')


def _sanitize_line(line: str) -> str:
    m = _KV_LINE_RE.match(line)
    if not m:
        return line
    prefix, val, suffix = m.groups()
    if '"' not in val:
        return line
    # Check if quotes inside val are actual unescaped string quotes rather than JSON delimiters
    fixed_val = re.sub(r'(?<!\\)"', r'\\"', val)
    return f'{prefix}"{fixed_val}"{suffix}'


def load_trace_events(path):
    with open(path, errors="replace") as f:
        raw = f.read()
    try:
        return json.loads(raw).get("traceEvents", [])
    except json.JSONDecodeError:
        lines = [_sanitize_line(ln) for ln in raw.splitlines()]
        for _ in range(32):
            try:
                return json.loads("\n".join(lines)).get("traceEvents", [])
            except json.JSONDecodeError as err:
                idx = err.lineno - 1
                if 0 <= idx < len(lines):
                    lines[idx] = '""'
                else:
                    break
        return []


def tpu_programs(trace_dir, step_index=2):
    """Returns ([(start_ms, dur_ms, name)], step_ms, pallas_calls)."""
    candidates = glob.glob(f"{trace_dir}/*.pt.trace.json")
    if not candidates:
        return [], 0.0, 0
    path = max(candidates, key=os.path.getmtime)
    events = load_trace_events(path)
    threads = {
        (e.get("pid"), e.get("tid")): e.get("args", {}).get("name", "")
        for e in events
        if e.get("ph") == "M" and e.get("name") == "thread_name"
    }
    programs = [
        e
        for e in events
        if e.get("ph") == "X" and threads.get((e.get("pid"), e.get("tid"))) == "XLA Modules"
    ]
    steps = sorted(
        (
            e
            for e in events
            if e.get("ph") == "X" and str(e.get("name", "")).startswith("ProfilerStep#")
        ),
        key=lambda e: e["ts"],
    )
    if steps:
        s = steps[min(step_index, len(steps) - 1)]
        t0, t1 = s["ts"], s["ts"] + s["dur"]
    elif programs:
        t0 = min(e["ts"] for e in programs)
        t1 = max(e["ts"] + e["dur"] for e in programs)
    else:
        return [], 0.0, 0
    inside = sorted(
        (e for e in programs if t0 <= e["ts"] <= t1), key=lambda e: e["ts"]
    )
    pallas_calls = sum(
        1
        for e in events
        if e.get("ph") == "X"
        and t0 <= e.get("ts", 0) <= t1
        and (
            "pallas" in str(e.get("name", "")).lower()
            or "tpu_custom_call" in str(e.get("name", "")).lower()
            or "custom-call" in str(e.get("name", "")).lower()
        )
    )
    bars = [((e["ts"] - t0) / 1000.0, e["dur"] / 1000.0, e["name"]) for e in inside]
    return bars, (t1 - t0) / 1000.0, pallas_calls


def main():
    modes = [
        ("eager", "Eager (1 op/launch)", "#4285F4"),
        ("defer", "DeferAndFuse", "#F9AB00"),
        ("compiled", "torch.compile", "#34A853"),
        ("pallas", "Pallas Fused Kernels", "#A142F4"),
    ]
    summary = []
    rows_for_plot = []
    eager_steady = None

    print("\n" + "=" * 78)
    print(
        f"{'Mode':22s} | {'Steady ms':>10s} | {'Speedup':>8s} | {'TPU Progs/Step':>14s} | {'Trace Step ms':>13s}"
    )
    print("-" * 78)

    for key, label, color in modes:
        meta_path = f"traces/metrics_{key}.json"
        if not os.path.exists(meta_path):
            continue
        with open(meta_path) as f:
            meta = json.load(f)
        steady_ms = meta["median_steady_ms"]
        if eager_steady is None:
            eager_steady = steady_ms
        speedup = (eager_steady / steady_ms) if steady_ms > 0 else 1.0
        bars, trace_step_ms, pallas_cnt = tpu_programs(meta["trace_dir"])
        print(
            f"{label:22s} | {steady_ms:8.2f}ms | {speedup:7.2f}x | {len(bars):14d} | {trace_step_ms:11.2f}ms"
        )
        summary.append(
            {
                "mode": key,
                "label": label,
                "first_step_ms": round(meta.get("first_step_ms", 0.0), 2),
                "median_steady_ms": round(steady_ms, 3),
                "speedup_vs_eager": round(speedup, 2),
                "tpu_programs_per_step": len(bars),
                "trace_step_ms": round(trace_step_ms, 3),
                "pallas_events_in_step": pallas_cnt,
                "parity": meta.get("parity", {}),
            }
        )
        rows_for_plot.append((label, color, bars, trace_step_ms))

    print("=" * 78)
    os.makedirs("traces", exist_ok=True)
    with open("traces/autokernel_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    if rows_for_plot and importlib.util.find_spec("matplotlib") is not None:
        import matplotlib.pyplot as plt

        width = max(max(step_ms for _, _, _, step_ms in rows_for_plot), 0.1)
        fig, ax = plt.subplots(figsize=(14, 4.4))
        for y, (label, color, bars, step_ms) in enumerate(reversed(rows_for_plot)):
            ax.broken_barh(
                [(s, max(d, width / 1400.0)) for s, d, _ in bars],
                (y + 0.15, 0.7),
                facecolor=color,
                edgecolor="white",
                linewidth=0.8,
            )
            n_str = f"{len(bars)} TPU prog{'s' if len(bars) != 1 else ''}"
            ax.text(width * 1.01, y + 0.5, f"{n_str}, {step_ms:.2f} ms", va="center")
        ax.set_xlim(0, width)
        ax.set_yticks(
            [i + 0.5 for i in range(len(rows_for_plot))],
            [r[0] for r in reversed(rows_for_plot)],
        )
        ax.set_xlabel("ms from start of ProfilerStep (same scale across all 4 modes)")
        ax.set_title(
            "AutoKernel Lab: Eager vs DeferAndFuse vs torch.compile vs Custom Pallas Kernels"
        )
        plt.tight_layout()
        out_png = "traces/autokernel_xprof_waterfall.png"
        plt.savefig(out_png, dpi=150, bbox_inches="tight")
        print(f"Saved 4-way XProf waterfall chart to {out_png}")


if __name__ == "__main__":
    main()
