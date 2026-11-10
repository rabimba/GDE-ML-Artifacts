"""The picture for burst.py: one bar per request, drawn in the 52 columns of the stage
pane. A bar is grey until its first token arrives, blue while it streams and green
when the answer is finished; its length is the number of tokens generated so far
(full width = max_tokens). Below the bars: tokens per second over the last second,
tokens so far and time since the first request. When every request has finished it
prints the summary: totals, and the median first-token time and streaming rate of
a single request. Every number is measured here, on the client.
"""
import statistics
import time

from rich.console import Console
from rich.live import Live
from rich.text import Text

WIDTH = 48
EIGHTHS = " ▏▎▍▌▋▊▉"


class Grid:
    def __init__(self, n, max_tokens=256):
        self.n, self.max = n, max_tokens
        self.tokens = [0] * n
        self.sent = [None] * n   # request sent
        self.first = [None] * n  # first token arrived
        self.end = [None] * n    # answer finished
        self.stamps = []         # arrival time of every token
        self.cols = 1 if n == 1 else min(n, 8 if n <= 64 else 16)
        self.cell = (WIDTH - (self.cols - 1)) // self.cols
        self.console = Console(highlight=False)

    # burst.py calls these for request i
    def start(self, i):
        self.sent[i] = time.monotonic()

    def add(self, i, chunk):
        now = time.monotonic()
        if chunk.choices and chunk.choices[0].delta.content:
            if self.first[i] is None:
                self.first[i] = now
            self.tokens[i] += 1
            self.stamps.append(now)
        if getattr(chunk, "usage", None):  # the server's exact count, at the end
            self.tokens[i] = chunk.usage.completion_tokens

    def done(self, i):
        self.end[i] = time.monotonic()

    def __enter__(self):
        self.t0 = time.monotonic()
        self.live = Live(console=self.console, get_renderable=self.render,
                         refresh_per_second=12, transient=False)
        self.live.__enter__()
        return self

    def __exit__(self, *exc):
        self.live.__exit__(*exc)
        if exc[0] is None:
            self.summary()
        return False

    def bar(self, i):
        if self.first[i] is None:
            return Text("·" * self.cell, style="grey50")
        filled = min(self.tokens[i], self.max) / self.max * self.cell
        full, part = int(filled), int((filled - int(filled)) * 8)
        s = ("█" * full + (EIGHTHS[part] if full < self.cell else "")).ljust(self.cell)
        return Text(s, style="green" if self.end[i] else "dodger_blue1")

    def render(self):
        now = time.monotonic()
        waiting = sum(f is None for f in self.first)
        done = sum(e is not None for e in self.end)
        t = Text()
        t.append(f"{self.n} request{'s' if self.n > 1 else ''}: ", style="bold")
        t.append(f"{waiting} waiting, {self.n - waiting - done} streaming, {done} done\n\n")
        for r in range(0, self.n, self.cols):
            for i in range(r, min(r + self.cols, self.n)):
                t.append_text(self.bar(i))
                t.append(" ")
            t.append("\n")
        while self.stamps and now - self.stamps[0] > 1.0:
            self.stamps.pop(0)
        t.append(f"\n{len(self.stamps):>6,} tokens/s", style="bold")
        t.append(f"   {sum(self.tokens):,} tokens   {now - self.t0:.1f} s")
        return t

    def summary(self):
        total = sum(self.tokens)
        span = max(self.end) - self.t0
        ttft = statistics.median(f - s for f, s in zip(self.first, self.sent) if f)
        rates = [k / (e - f) for k, f, e in zip(self.tokens, self.first, self.end)
                 if f and e > f]
        s = "s" if self.n > 1 else ""
        self.console.print(
            f"\n{self.n} request{s}, {total:,} tokens in {span:.1f} s:"
            f" [bold]{total / span:,.0f} tokens/s[/bold]\n"
            f"each request: first token after {ttft * 1000:,.0f} ms,\n"
            f"then {statistics.median(rates):,.0f} tokens/s"
            f"{' (medians)' if self.n > 1 else ''}")
