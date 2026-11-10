import asyncio
import sys
from openai import AsyncOpenAI
from grid import Grid  # draws one bar per request

n = int(sys.argv[1])  # how many requests at once
llm = AsyncOpenAI(base_url="http://localhost:8000/v1",
                  api_key="none")

# n different questions, with short and long answers
asks = ["Explain {} in detail.",
        "Define {} in one sentence.",
        "List five facts about {}.",
        "Explain {} in a short paragraph."]
topics = ["torch.compile", "autograd", "nn.Module",
          "DataLoader", "mixed precision", "LayerNorm",
          "the KV cache", "attention", "dropout", "Adam",
          "beam search", "top-p sampling", "RoPE",
          "quantization", "tokenizers", "batch norm"]

async def ask(i, grid):
    await asyncio.sleep(i / n)  # arrivals over 1 s
    q = asks[i % 4].format(topics[i // 4 % 16])
    grid.start(i)
    stream = await llm.chat.completions.create(
        model="Qwen/Qwen3-32B", max_tokens=256,
        messages=[{"role": "user", "content": q}],
        stream=True,
        stream_options={"include_usage": True},
        extra_body={"chat_template_kwargs":
                    {"enable_thinking": False}})
    async for chunk in stream:
        grid.add(i, chunk)
    grid.done(i)

async def main():
    with Grid(n) as grid:
        await asyncio.gather(
            *(ask(i, grid) for i in range(n)))

asyncio.run(main())
