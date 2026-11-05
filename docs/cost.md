# Cost

Measured 2026-11-05 on `claude-haiku` through `claude -p`, one call writing a post from `examples/post-writer`:

| Command | Input tokens | Output tokens | Cost per call |
|---|---|---|---|
| `claude -p --model haiku` | about 21,900 | about 890 | $0.0035 |
| `$AGENT` (the Claude Code line in the README) | about 955 | about 430 | $0.0004 |

About 95% of a plain `claude -p` call is Claude Code itself: its system prompt, tool definitions, your settings and hooks. The skill and request are about 400 tokens. Other agent CLIs add their own prompt and tools too, so use their slim flags where they have them (see [backends.md](backends.md)).

| Run (both examples) | Calls | Tokens with `$AGENT` | Cost |
|---|---|---|---|
| `--reps 1` | about 30 | about 45,000 | about $0.01 |
| `--reps 3` (default) | about 90 | about 125,000 | about $0.04 |

Calls per example: 4 requests × 2 stages × reps answers, plus 3 × 2 × reps judge calls. The skill+check stage reuses the skill's answers: it adds a call only for each script fix (at most 2 per answer) and a judge call per fixed answer.
