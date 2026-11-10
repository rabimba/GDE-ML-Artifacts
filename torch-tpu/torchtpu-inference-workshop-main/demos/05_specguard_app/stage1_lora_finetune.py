# SpecGuard TPU - Stage 1: LoRA Fine-Tuning Qwen/Qwen3-0.6B on Cloud TPU (torch_tpu)
# Showcases:
#   - Native torch.device("tpu") in bfloat16 (no torch_xla)
#   - Static sequence length padding (pad_to_multiple_of=64, max_length=256) for zero XLA recompile
#   - PEFT LoRA adaptation on attention projections + checkpoint merge for SGLang serving
import json
import os
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

import torch
from torch_tpu import _loader

if not _loader._LOADED:
    _loader._init_device("tpu")

from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen3-0.6B"
MERGED_DIR = os.environ.get("SPECGUARD_MERGED_DIR", "/tmp/specguard-qwen3-0.6b-merged")
MAX_LEN = 256

AUDIT_EXAMPLES = [
    {
        "code": "import torch_xla.core.xla_model as xm\ndev = xm.xla_device()\nx = torch.randn(8, 8).to(dev)\nxm.mark_step()",
        "audit": "[CRITICAL | TPU-001] Deprecated torch_xla usage. Replace xm.xla_device() with torch.device('tpu') and remove xm.mark_step().",
    },
    {
        "code": "cursor.execute(f\"SELECT * FROM users WHERE username = '{user_input}'\")",
        "audit": "[CRITICAL | SEC-001] SQL Injection via f-string formatting. Use parameterized queries: cursor.execute('SELECT * FROM users WHERE username = ?', (user_input,)).",
    },
    {
        "code": "payload = pickle.loads(request.body)\nmodel_cfg = payload['config']",
        "audit": "[CRITICAL | SEC-002] Arbitrary code execution via unsafe pickle.loads on untrusted request body. Parse with json.loads and validate schema.",
    },
    {
        "code": "for seq in variable_len_batches:\n    ids = tokenizer(seq, padding=True, return_tensors='pt').to('tpu')\n    out = compiled_model(**ids)",
        "audit": "[HIGH | TPU-002] Dynamic batch sequence lengths trigger repeated XLA recompilations on TPU. Pad to static bucket (padding='max_length', max_length=256).",
    },
    {
        "code": "t0 = time.perf_counter()\ny = model(x_tpu)\nms = (time.perf_counter() - t0) * 1000",
        "audit": "[MEDIUM | TPU-003] Missing torch.accelerator.synchronize() before stopping timer; measures async host dispatch instead of TPU execution time.",
    },
    {
        "code": "subprocess.run(f'tar -xzf {uploaded_filename}', shell=True, check=True)",
        "audit": "[CRITICAL | SEC-003] Command injection via shell=True with unsanitized filename. Pass argument list ['tar', '-xzf', path] with shell=False.",
    },
    {
        "code": "API_TOKEN = 'SK_LIVE_DEMO_HARDCODED_SECRET_9876543210'\nheaders = {'Authorization': f'Bearer {API_TOKEN}'}",
        "audit": "[HIGH | SEC-004] Hardcoded API credential in source. Load secrets from environment variables or secret manager.",
    },
    {
        "code": "for step, batch in enumerate(loader):\n    loss = model(batch.to('tpu')).loss\n    loss.backward()\n    if step % 4 == 0:\n        print(loss.item())",
        "audit": "[MEDIUM | TPU-004] Calling loss.item() inside the inner step forces a host-device sync and breaks TPU execution pipelining. Log only at intervals.",
    },
]

SYSTEM_PROMPT = (
    "You are SpecGuard-TPU, an expert code security and PyTorch TPU auditor. "
    "Respond with a concise one-line finding formatted as [SEVERITY | CODE] Description and fix."
)


def format_chat(tokenizer, code_str, audit_str=None):
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Audit this Python snippet:\n```python\n{code_str}\n```"},
    ]
    if audit_str is not None:
        msgs.append({"role": "assistant", "content": audit_str})
        return tokenizer.apply_chat_template(
            msgs, tokenize=False, enable_thinking=False
        )
    return tokenizer.apply_chat_template(
        msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False
    )


def generate_audit(model, tokenizer, device, code_snippet):
    prompt = format_chat(tokenizer, code_snippet, None)
    enc = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **enc,
            max_new_tokens=48,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    gen_ids = out[0][enc["input_ids"].shape[1] :]
    return tokenizer.decode(gen_ids, skip_special_tokens=True).strip()


def main():
    device = torch.device("tpu")
    print(f"Initializing SpecGuard Stage 1 on device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch.bfloat16
    ).to(device)
    base_model.eval()

    test_snippet = (
        "import torch_xla.core.xla_model as xm\n"
        "dev = xm.xla_device()\n"
        "q = f\"SELECT token FROM keys WHERE id = '{req_id}'\""
    )
    print("\n--- Pre-LoRA Baseline Output ---")
    before_text = generate_audit(base_model, tokenizer, device, test_snippet)
    print(before_text)

    # Configure PEFT LoRA
    lora_cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    model = get_peft_model(base_model, lora_cfg)
    model.print_trainable_parameters()
    model.train()

    # Pre-tokenize static-shape batches (B=4, L=256) to prevent XLA recompilation
    texts = [format_chat(tokenizer, ex["code"], ex["audit"]) for ex in AUDIT_EXAMPLES]
    prompts_only = [format_chat(tokenizer, ex["code"], None) for ex in AUDIT_EXAMPLES]
    enc = tokenizer(
        texts,
        padding="max_length",
        max_length=MAX_LEN,
        truncation=True,
        return_tensors="pt",
    )
    input_ids = enc["input_ids"].to(device)
    attention_mask = enc["attention_mask"].to(device)
    labels = input_ids.clone()
    labels[attention_mask == 0] = -100
    for i, p_txt in enumerate(prompts_only):
        p_len = len(tokenizer(p_txt, add_special_tokens=False)["input_ids"])
        labels[i, :p_len] = -100

    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=0.01)

    batch_size = 4
    n_steps = 40
    losses = []
    step_ms_list = []

    print(f"\n--- Running {n_steps} LoRA Fine-Tuning Steps on TPU (static shape {batch_size}x{MAX_LEN}) ---")
    for step in range(1, n_steps + 1):
        idx = ((step - 1) * batch_size) % len( AUDIT_EXAMPLES )
        b_ids = input_ids[idx : idx + batch_size]
        b_mask = attention_mask[idx : idx + batch_size]
        b_lbls = labels[idx : idx + batch_size]

        t0 = time.perf_counter()
        optimizer.zero_grad()
        out = model(input_ids=b_ids, attention_mask=b_mask, labels=b_lbls)
        loss = out.loss
        loss.backward()
        optimizer.step()
        torch.accelerator.synchronize()
        ms = (time.perf_counter() - t0) * 1000.0

        loss_val = float(loss.detach().cpu().item())
        losses.append(loss_val)
        step_ms_list.append(ms)
        if step == 1 or step % 5 == 0 or step == n_steps:
            tok_s = (batch_size * MAX_LEN) / (ms / 1000.0)
            print(
                f"Step {step:2d}/{n_steps} | loss: {loss_val:.4f} | step_time: {ms:6.1f} ms | {tok_s:6.0f} tok/s"
            )

    model.eval()
    print("\n--- Post-LoRA Adapted Output ---")
    after_text = generate_audit(model, tokenizer, device, test_snippet)
    print(after_text)

    print(f"\nMerging LoRA adapter and saving checkpoint to {MERGED_DIR} ...")
    merged_model = model.merge_and_unload()
    merged_model.save_pretrained(MERGED_DIR)
    tokenizer.save_pretrained(MERGED_DIR)

    metrics = {
        "model_id": MODEL_ID,
        "merged_dir": MERGED_DIR,
        "initial_loss": round(losses[0], 4),
        "final_loss": round(losses[-1], 4),
        "loss_history": [round(x, 4) for x in losses],
        "median_step_ms": round(sorted(step_ms_list[2:])[len(step_ms_list[2:]) // 2], 2),
        "before_audit_sample": before_text,
        "after_audit_sample": after_text,
    }
    os.makedirs("traces", exist_ok=True)
    with open("traces/specguard_stage1_lora.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Stage 1 complete. Saved metrics to traces/specguard_stage1_lora.json")


if __name__ == "__main__":
    main()
