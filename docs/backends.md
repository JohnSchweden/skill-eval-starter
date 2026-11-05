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
| Codex | `AGENT='codex exec --ephemeral --skip-git-repo-check -'` | flags and error path |
| Gemini CLI | `AGENT='gemini --skip-trust -m flash-lite -p "$(cat)"'` | flags and error path |
| opencode | `AGENT='OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode run --pure -m <provider/model> "$(cat)"'` | yes |
| Cursor | `AGENT='cursor-agent -p --mode ask --output-format text "$(cat)"'` | no |
| GitHub Copilot | `AGENT='copilot -s --model claude-haiku-4.5 -p "$(cat)"'` | no |
| Ollama (local) | `AGENT='ollama run llama3.2'` | no |
| `llm` (any provider via plugins) | `AGENT='llm -m <model> --no-log'` | no |

"Yes" means a full run of both examples went through this line. "Flags and error path" means every flag exists in the current release and a call with a wrong key fails cleanly (exit code not 0, nothing on stdout), so `eval.py` reports it as an error; no logged-in run yet. "No" means the flags come from each tool's docs (November 2026) but nobody has run this line yet. If yours works or needs a fix, open an issue or a PR with the working line.

- **Gemini CLI** refuses to run in a folder it doesn't trust, and `eval.py` runs every call in a new empty folder. Without `--skip-trust` every call fails.
- **opencode** without a login: `-m opencode/big-pickle` is a free model that needs no key (tested 5 November 2026; other free models were often unavailable). Add `--workers 1` to the `eval.py` call: parallel opencode calls share one local database and some fail with "database is locked".
- **Hermes, OpenClaw** and other long-running agents: no tested line. Use the API route below with the provider key your agent already uses (OpenRouter, OpenAI, a local Ollama). It tests the skill text on the same model, without the agent around it.

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
python3 eval.py examples/post-writer --model openai/gpt-4o-mini   # plain gpt-4o-mini on OpenAI itself
```

OpenRouter reaches most providers with one key. Ollama (`http://localhost:11434/v1`) and LM Studio run locally; Anthropic and Gemini also offer OpenAI-compatible endpoints.

## Or let your coding agent run it

```text
Read README.md and docs/backends.md in this repo. Run eval.py on
examples/post-writer and on examples/humanizer with --cmd set to the line
for the CLI you are running in. For each example, show me the table,
then open one failing output from runs/ and tell me whether the skill or
the test is at fault. Do not edit any file.
```

## Check your line first

Before a full run, send one prompt by hand and look at the output:

```bash
echo "Say hi in three words." | sh -c "$AGENT"
```

You should see only the answer. Logs, banners or a "thinking" block on stdout end up in the score: the rules check them like answer text.
