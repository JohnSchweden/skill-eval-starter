# Cost

Measured 2026-11-05 on `claude-haiku` through `claude -p`, one call writing a post from `examples/post-writer`:

| Command | Input tokens | Output tokens | Cost per call |
|---|---|---|---|
| `claude -p --model haiku` | about 21,900 | about 890 | $0.0035 |
| `$AGENT` (the Claude Code line in the README) | about 955 | about 430 | $0.0004 |

About 95% of a plain `claude -p` call is Claude Code itself: its system prompt, tool definitions, your settings and hooks. The skill and request are about 400 tokens. Other agent CLIs add their own prompt and tools too, so use their slim flags where they have them (see [backends.md](backends.md)).

| Run (both examples) | Calls | Tokens with `$AGENT` | Cost |
|---|---|---|---|
| `--reps 1` | about 50 | about 70,000 | about $0.02 |
| `--reps 3` (default) | about 140 | about 195,000 | about $0.06 |

Calls per example: 4 requests × 3 stages × reps answers, plus 3 × 3 × reps judge calls, plus up to 2 script fixes per answer in the skill+check stage.
