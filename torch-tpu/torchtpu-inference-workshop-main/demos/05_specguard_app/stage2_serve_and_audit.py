# SpecGuard TPU - Stage 2 & 3: SGLang-TorchTPU Serving + Prefix-Cached Multi-Pass Audit & 16-File Burst
import asyncio
import importlib.util
import inspect
import json
import os
import shutil
import signal
import subprocess
import sys
import time

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


def ensure_sglang_venv():
    venv = os.environ.get("SGLANG_VENV_DIR", "/tmp/venv-sglang")
    py = os.path.join(venv, "bin", "python")
    rel = "https://github.com/sgl-project/sglang-torchtpu/releases/download/tpu-v0.1.0"
    uv = shutil.which("uv") or "/usr/local/bin/uv"
    if not os.path.exists(uv):
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "uv"], check=True)
        uv = shutil.which("uv") or os.path.join(os.path.dirname(sys.executable), "uv")
    if not os.path.exists(py):
        print(f"Creating {venv} (Python 3.12) and installing SGLang-TorchTPU...")
        subprocess.run([uv, "venv", "-q", "--python", "3.12", venv], check=True)
        subprocess.run(
            [
                uv,
                "pip",
                "install",
                "-q",
                "--python",
                py,
                "--index-strategy",
                "unsafe-best-match",
                "--extra-index-url",
                "https://download.pytorch.org/whl/cpu",
                f"{rel}/sglang-0.5.22-py3-none-any.whl",
                f"{rel}/sglang_tpu-0.1.0-py3-none-any.whl",
                "tpu-info",
            ],
            check=True,
        )
    return py


def build_shared_repo_context():
    import torch.nn.modules.transformer as tfm

    src = inspect.getsource(tfm)[:4500]
    vulnerable_service = '''
# --- FILE: app/tpu_inference_service.py ---
import os, pickle, subprocess
import torch
import torch_xla.core.xla_model as xm

API_SECRET = "SK_LIVE_DEMO_HARDCODED_PRODUCTION_KEY_998877"

def run_user_job(req_body, db_cursor, user_id):
    # Legacy TPU setup
    dev = xm.xla_device()
    db_cursor.execute(f"SELECT * FROM jobs WHERE owner = '{user_id}'")
    payload = pickle.loads(req_body)
    subprocess.run(f"python run_eval.py --cfg {payload['path']}", shell=True)
    x = torch.randn(payload["seq_len"], 1024).to(dev)
    t0 = time.perf_counter()
    y = x * 2.0
    xm.mark_step()
    return {"elapsed_ms": (time.perf_counter() - t0) * 1000}
'''
    return f"# AUDIT SESSION ID: {time.time()}\n{vulnerable_service}\n\n# --- REFERENCE MODULE ---\n{src}"


def main():
    py312 = ensure_sglang_venv()
    candidates = [
        os.environ.get("SPECGUARD_MERGED_DIR", ""),
        os.path.abspath("specguard-qwen3-0.6b-merged"),
        "/tmp/specguard-qwen3-0.6b-merged",
    ]
    model_path = next((c for c in candidates if c and os.path.exists(c)), "Qwen/Qwen3-0.6B")
    port = int(os.environ.get("SPECGUARD_PORT", "30100"))
    log_path = os.path.abspath("sglang_specguard.log")

    fix_dir = os.path.abspath("tpu_sitecustomize")
    os.makedirs(fix_dir, exist_ok=True)
    with open(os.path.join(fix_dir, "sitecustomize.py"), "w") as f:
        f.write(
            "import os\n"
            "os.environ.pop('TPU_VISIBLE_DEVICES', None)\n"
            "os.environ['TPU_VISIBLE_CHIPS'] = '0'\n"
            "os.environ['TPU_CHIPS_PER_HOST_BOUNDS'] = '1,1,1'\n"
            "os.environ['TPU_HOST_BOUNDS'] = '1,1,1'\n"
            "try:\n"
            "    import torch, torch_tpu\n"
            "    from torch_tpu import _loader\n"
            "    if not _loader._LOADED:\n"
            "        _loader._init_device('tpu')\n"
            "except Exception:\n"
            "    pass\n"
        )

    env = dict(
        os.environ,
        PYTHONUNBUFFERED="1",
        SGLANG_PLATFORM="tpu",
        SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN="1",
        TORCH_TPU_INTERNAL_MATERIALIZE_COLLECTIVE_TENSORS="false",
        PYTHONPATH=fix_dir
        + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else ""),
    )

    cmd = [
        py312,
        "-m",
        "sglang.launch_server",
        "--model-path",
        model_path,
        "--device",
        "tpu",
        "--tp-size",
        "1",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--context-length",
        "8192",
        "--max-running-requests",
        "8",
        "--page-size",
        "128",
        "--mem-fraction-static",
        "0.80",
        "--enable-torch-compile",
        "--enable-cache-report",
    ]

    print(f"Starting SGLang-TorchTPU server on model: {model_path}")
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    import requests
    from openai import AsyncOpenAI, OpenAI

    try:
        t0 = time.time()
        ready = False
        last_print = -30
        while time.time() - t0 < 1800:
            if proc.poll() is not None:
                break
            try:
                if requests.get(f"http://127.0.0.1:{port}/health", timeout=2).status_code == 200:
                    ready = True
                    break
            except requests.RequestException:
                pass
            if time.time() - t0 - last_print >= 30:
                last_print = time.time() - t0
                with open(log_path) as lf:
                    lines = lf.read().splitlines()
                print(f"[{last_print:5.0f}s] {lines[-1][:100] if lines else 'starting...'}")
            time.sleep(1)

        if not ready:
            with open(log_path) as lf:
                print("Server failed to start:\n" + "".join(lf.readlines()[-40:]))
            raise RuntimeError("SGLang server did not become ready")

        startup_s = time.time() - t0
        print(f"SGLang server ready in {startup_s:.1f}s (pid={proc.pid})")

        client = OpenAI(base_url=f"http://127.0.0.1:{port}/v1", api_key="none")

        # Warm-up request (triggers decode compilation bucket)
        client.chat.completions.create(
            model=model_path,
            max_tokens=16,
            messages=[{"role": "user", "content": "Say ready."}],
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

        # Experiment 1: Multi-Turn Codebase Audit with Prefix Cache
        repo_doc = build_shared_repo_context()
        audit_questions = [
            ("Pass 1 (Cold): SQL & Deserialization", "Identify any SQL injection or pickle vulnerabilities in run_user_job."),
            ("Pass 2 (Warm Cache): TorchTPU Migration", "Identify deprecated torch_xla usage and how to replace it with torch_tpu."),
            ("Pass 3 (Warm Cache): Dynamic Shapes & Sync", "Identify dynamic shape recompilation and timing sync bugs on TPU."),
            ("Pass 4 (Warm Cache): Remediation Patch", "Provide a 3-bullet remediation checklist for app/tpu_inference_service.py."),
        ]

        prefix_results = []
        print("\n=== Experiment 1: Multi-Pass Codebase Audit (RadixAttention Prefix Cache) ===")
        for label, question in audit_questions:
            t_req = time.monotonic()
            ttft_ms = None
            text_out = []
            stream = client.chat.completions.create(
                model=model_path,
                max_tokens=64,
                messages=[
                    {
                        "role": "system",
                        "content": "You are SpecGuard-TPU, an expert code security and PyTorch TPU auditor.",
                    },
                    {
                        "role": "user",
                        "content": f"{repo_doc}\n\nAudit Task: {question} Answer concisely in 1-2 sentences.",
                    },
                ],
                stream=True,
                stream_options={"include_usage": True},
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
            usage = None
            for chunk in stream:
                for choice in chunk.choices:
                    if ttft_ms is None and choice.delta.content:
                        ttft_ms = (time.monotonic() - t_req) * 1000.0
                    if choice.delta.content:
                        text_out.append(choice.delta.content)
                if getattr(chunk, "usage", None) is not None:
                    usage = chunk.usage

            total_ms = (time.monotonic() - t_req) * 1000.0
            prompt_toks = getattr(usage, "prompt_tokens", 0) if usage else 0
            details = getattr(usage, "prompt_tokens_details", None) if usage else None
            cached_toks = getattr(details, "cached_tokens", 0) if details else 0
            ans = "".join(text_out).strip().replace("\n", " ")
            print(
                f"{label:38s} | TTFT: {ttft_ms:6.1f} ms | Total: {total_ms:6.1f} ms | "
                f"Cached: {cached_toks}/{prompt_toks} toks"
            )
            print(f"   -> {ans[:140]}")
            prefix_results.append(
                {
                    "label": label,
                    "ttft_ms": round(ttft_ms or 0.0, 2),
                    "total_ms": round(total_ms, 2),
                    "prompt_tokens": prompt_toks,
                    "cached_tokens": cached_toks,
                    "response": ans,
                }
            )

        # Experiment 2: 16-File Concurrent Repo Scan (Continuous Batching)
        print("\n=== Experiment 2: 16-File Concurrent Repository Scan (Continuous Batching) ===")
        file_snippets = [
            ("auth_db.py", "cursor.execute(f\"SELECT * FROM accounts WHERE email='{email}'\")"),
            ("legacy_tpu.py", "import torch_xla.core.xla_model as xm; dev = xm.xla_device()"),
            ("loader.py", "data = pickle.loads(socket.recv(4096))"),
            ("bench.py", "t0 = time.time(); out = model(x_tpu); dt = time.time() - t0"),
            ("runner.py", "subprocess.Popen(f'bash {user_script}', shell=True)"),
            ("config.py", "GCP_API_KEY = 'SK_LIVE_DEMO_SECRET_TOKEN_VALUE_12345'"),
            ("train_loop.py", "for s in steps: loss = model(x).loss; print(loss.item())"),
            ("dynamic_pad.py", "tok(batch, padding=True, return_tensors='pt').to('tpu')"),
        ] * 2  # 16 files total

        async def run_burst():
            aclient = AsyncOpenAI(base_url=f"http://127.0.0.1:{port}/v1", api_key="none")
            t_start_all = time.monotonic()
            records = [None] * len(file_snippets)

            async def scan_one(idx, fname, snippet):
                await asyncio.sleep(idx / len(file_snippets) * 0.4)
                req_start = time.monotonic() - t_start_all
                first_tok_t = None
                tok_count = 0
                out_chars = []
                s = await aclient.chat.completions.create(
                    model=model_path,
                    max_tokens=48,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are SpecGuard-TPU. Output a one-line finding: [SEVERITY | CODE] fix.",
                        },
                        {
                            "role": "user",
                            "content": f"File `{fname}`:\n```python\n{snippet}\n```",
                        },
                    ],
                    stream=True,
                    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                )
                async for ch in s:
                    for c in ch.choices:
                        if c.delta.content:
                            if first_tok_t is None:
                                first_tok_t = time.monotonic() - t_start_all
                            tok_count += 1
                            out_chars.append(c.delta.content)
                req_end = time.monotonic() - t_start_all
                records[idx] = {
                    "idx": idx,
                    "file": fname,
                    "start_s": round(req_start, 3),
                    "first_token_s": round(first_tok_t or req_end, 3),
                    "end_s": round(req_end, 3),
                    "ttft_ms": round(((first_tok_t or req_end) - req_start) * 1000.0, 1),
                    "chunks": tok_count,
                    "finding": "".join(out_chars).strip().replace("\n", " "),
                }

            await asyncio.gather(
                *(scan_one(i, f, s) for i, (f, s) in enumerate(file_snippets))
            )
            await aclient.close()
            return records, time.monotonic() - t_start_all

        burst_records, burst_wall_s = asyncio.run(run_burst())
        total_chunks = sum(r["chunks"] for r in burst_records)
        print(
            f"Scanned {len(burst_records)} files concurrently in {burst_wall_s:.2f}s "
            f"({total_chunks / burst_wall_s:.1f} streamed chunks/s)"
        )
        for r in burst_records[:6]:
            print(f"  [{r['idx']:02d}] {r['file']:14s} | TTFT {r['ttft_ms']:5.0f}ms | {r['finding'][:80]}")

        os.makedirs("traces", exist_ok=True)
        out_json = "traces/specguard_stage2_serving.json"
        cold_ttft = prefix_results[0]["ttft_ms"]
        warm_ttft = min(r["ttft_ms"] for r in prefix_results[1:])
        with open(out_json, "w") as f:
            json.dump(
                {
                    "model_path": model_path,
                    "server_startup_s": round(startup_s, 1),
                    "prefix_cache_audit": prefix_results,
                    "prefix_cache_ttft_speedup": round(cold_ttft / max(warm_ttft, 1.0), 2),
                    "burst_wall_s": round(burst_wall_s, 2),
                    "burst_records": burst_records,
                },
                f,
                indent=2,
            )
        print(f"Saved SpecGuard serving results to {out_json}")

        # Plot 3-panel dashboard if matplotlib is available
        if importlib.util.find_spec("matplotlib") is not None:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))

            # Panel 1: Stage 1 LoRA Loss Curve (if available)
            stage1_path = "traces/specguard_stage1_lora.json"
            if os.path.exists(stage1_path):
                with open(stage1_path) as sf:
                    s1 = json.load(sf)
                losses = s1.get("loss_history", [])
                axes[0].plot(range(1, len(losses) + 1), losses, marker="o", color="#4285F4", linewidth=2)
                axes[0].set_title("Stage 1: Qwen3-0.6B LoRA Loss on TPU")
                axes[0].set_xlabel("Training Step (Static 4x256)")
                axes[0].set_ylabel("Cross-Entropy Loss")
                axes[0].grid(True, alpha=0.3)

            # Panel 2: Prefix Cache Cold vs Warm TTFT
            labels = [f"Pass {i+1}\n({'Cold' if i==0 else 'Cached'})" for i in range(len(prefix_results))]
            ttfts = [r["ttft_ms"] for r in prefix_results]
            colors = ["#EA4335"] + ["#34A853"] * (len(prefix_results) - 1)
            axes[1].bar(labels, ttfts, color=colors)
            axes[1].set_title("Stage 2: SGLang Prefix Cache TTFT (ms)")
            axes[1].set_ylabel("Time to First Token (ms)")
            axes[1].grid(True, axis="y", alpha=0.3)

            # Panel 3: 16-Request Continuous Batching Timeline
            for r in burst_records:
                y = r["idx"]
                axes[2].barh(y, r["first_token_s"] - r["start_s"], left=r["start_s"], color="#F9AB00", height=0.6)
                axes[2].barh(y, r["end_s"] - r["first_token_s"], left=r["first_token_s"], color="#34A853", height=0.6)
            axes[2].set_title("Stage 3: 16-File Continuous Batching Scan")
            axes[2].set_xlabel("Seconds from Burst Start (Yellow=Wait, Green=Stream)")
            axes[2].set_ylabel("Concurrent Request #")
            axes[2].invert_yaxis()

            plt.tight_layout()
            dash_png = "traces/specguard_dashboard.png"
            plt.savefig(dash_png, dpi=150, bbox_inches="tight")
            print(f"Saved SpecGuard 3-stage dashboard to {dash_png}")

    finally:
        print("Stopping SGLang server and releasing TPU chip...")
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=15)
        except Exception:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
        print("TPU chip released.")


if __name__ == "__main__":
    main()
