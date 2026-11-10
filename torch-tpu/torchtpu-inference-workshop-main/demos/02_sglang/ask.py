import time
from openai import OpenAI

llm = OpenAI(base_url="http://localhost:30000/v1",
             api_key="none")

# PyTorch's nn.Transformer source, after the time,
# so the server has never seen this prompt before
doc = f"{time.time()}\n"
doc += open("transformer.py").read()

for q in ["What does norm_first do?",
          "What is the default activation?"]:
    print("\n>", q)
    t0, first = time.monotonic(), None
    stream = llm.chat.completions.create(
        model="Qwen/Qwen3-32B", max_tokens=64,
        messages=[{"role": "user", "content":
                   f"{doc}\n\nIn one sentence: {q}"}],
        stream=True,
        stream_options={"include_usage": True},
        extra_body={"chat_template_kwargs":
                    {"enable_thinking": False}})
    for chunk in stream:
        for c in chunk.choices:
            if first is None and c.delta.content:
                first = (time.monotonic() - t0) * 1000
            print(c.delta.content or "", end="")
    u = chunk.usage  # the last chunk has the usage
    d = u.prompt_tokens_details  # None: none cached
    cached = d.cached_tokens if d else 0
    print(f"\nfirst token: {first:.0f} ms, cached"
          f" {cached:,} of {u.prompt_tokens:,} tokens")
