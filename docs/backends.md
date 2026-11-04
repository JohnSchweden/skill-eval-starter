# Run it on your CLI or API

`eval.py` needs one thing from a backend: a prompt goes in, an answer comes out. Two ways in:

- `--cmd "<command>"`: any CLI. The prompt arrives on stdin, the answer is read from stdout. The command runs through your shell in an empty temp folder.
- No `--cmd`: any OpenAI-compatible API, through `OPENAI_API_KEY`, `OPENAI_BASE_URL` and `--model`.

A CLI that takes the prompt only as an argument works too: `"$(cat)"` turns stdin into the argument. Put the whole command in single quotes so your own shell leaves `$(cat)` alone.

## CLI lines

Copy the line into a variable, then run `python3 eval.py examples/post-writer --cmd "$AGENT"`.

| CLI | Line | Tested |
|---|---|---|
| Claude Code | `AGENT='claude -p --model haiku --tools "" --setting-sources "" --system-prompt "Answer the request."'` | yes |
| Codex | `AGENT='codex exec --ephemeral --skip-git-repo-check -'` | no |
| Gemini CLI | `AGENT='gemini -m flash-lite -p "$(cat)"'` | no |
| opencode | `AGENT='OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode run --pure -m <provider/model> "$(cat)"'` | no |
| Cursor | `AGENT='cursor-agent -p --mode ask --output-format text "$(cat)"'` | no |
| GitHub Copilot | `AGENT='copilot -s --model claude-haiku-4.5 -p "$(cat)"'` | no |
| Ollama (local) | `AGENT='ollama run llama3.2'` | no |
| `llm` (any provider via plugins) | `AGENT='llm -m <model> --no-log'` | no |

"No" means the flags come from each tool's docs (November 2026) but nobody has run this line yet. If yours works or needs a fix, open an issue or a PR with the working line.

To choose a model, add the CLI's model flag (`-m`, `--model`). Pick the cheapest model it offers: the test is about the skill, not the model.

Aider is left out: it is built to edit files, has no stdin and prints its own banners around the answer.

## Why the extra flags

An agent CLI is not a bare model. It adds its own system prompt, tool definitions, project instruction files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`), settings and hooks. That has two costs:

- **Tokens.** A plain `claude -p` call carries about 22,000 tokens of Claude Code for a 400-token job (see [cost.md](cost.md)).
- **A baseline that isn't bare.** The "no skill" stage runs with everything your agent loads anyway. Your global instructions may already do what the skill does.

The flags strip what each CLI lets you strip. The empty temp folder keeps project files out for every CLI. What a CLI can't strip, like a built-in system prompt, stays in all three stages, so the comparison between stages is still fair. Numbers from two different CLIs are not comparable with each other.

## The barest option: an API

For the cleanest baseline, skip the agent and call a model directly. Any OpenAI-compatible endpoint works:

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1   # leave unset for OpenAI
python3 eval.py examples/post-writer --model gpt-4o-mini
```

OpenRouter reaches most providers with one key. Ollama (`http://localhost:11434/v1`) and LM Studio run locally; Anthropic and Gemini also offer OpenAI-compatible endpoints.

## Check your line first

Before a full run, send one prompt by hand and look at the output:

```bash
echo "Say hi in three words." | sh -c "$AGENT"
```

You should see only the answer. Logs, banners or a "thinking" block on stdout end up in the score: the rules check them like answer text.
