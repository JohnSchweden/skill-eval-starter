# skill-eval-starter

Did your agent actually get better? Run a skill three ways and compare: without it, with it, and with a check that always runs.

- **Skill text**: the instructions your agent loads. The model may follow them, or not.
- **Skill + check**: the same text plus a script that checks every answer in code, like a hook. The model fixes what the script finds.

Works with any agent CLI or model API. No dependencies beyond Python 3.9.

## What's in here

```
eval.py                  the runner: same requests, three ways, scored against a fixed test
examples/post-writer/    example 1: writes a short LinkedIn post from notes
examples/humanizer/      example 2: rewrites AI-sounding text so it reads human
template/                empty copy for your own skill
docs/                    how it works, what to trust, other CLIs, cost
```

**The test** is `prompts.csv` + `checks.txt` in each example folder; it never changes. **The eval** is `eval.py` running that test; results land in `runs/<time>/` and `results.tsv`. Details: [docs/how-it-works.md](docs/how-it-works.md).

## At the workshop (15 minutes)

You don't write anything. Clone, run both examples, read the results.

```bash
git clone https://github.com/JohnSchweden/skill-eval-starter && cd skill-eval-starter

AGENT='claude -p --model haiku --tools "" --setting-sources "" --system-prompt "Answer the request."'
python3 eval.py examples/post-writer --cmd "$AGENT"
python3 eval.py examples/humanizer   --cmd "$AGENT"
```

The extra flags keep Claude Code's own prompt, tools, hooks and settings out of the call: about 1,000 tokens instead of 22,000, and a "no skill" stage that is really bare.

**Not on Claude Code?** Set `AGENT` to your CLI's line from [docs/backends.md](docs/backends.md) (Codex, Gemini CLI, opencode, Cursor, Copilot, Ollama, `llm`), or use any OpenAI-compatible API:

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1   # leave unset for OpenAI
python3 eval.py examples/post-writer --model gpt-4o-mini
```

Each example makes about 25 small calls and takes a minute or two ([cost](docs/cost.md)).

Or hand it to your coding agent:

```text
Read README.md and docs/backends.md in this repo. Run eval.py on
examples/post-writer and on examples/humanizer with --cmd set to the line
for the CLI you are running in. For each example, show me the table,
then open one failing output from runs/ and tell me whether the skill or
the test is at fault. Do not edit any file.
```

**Bring back three numbers per example** ("Runs that pass"): **no skill __ · skill __ · skill + check __**

## What to look at

1. **No skill vs. skill.** Does the skill add anything? If no skill already passes, the skill does nothing for that request, or the test is too easy.
2. **Skill vs. skill+check on "Code checks pass".** The script catches what code can check, and the model fixes it. Here skill+check should get close to 100%.
3. **Skill vs. skill+check on "Judge says yes".** Whether facts were kept or invented is not something code can decide. Only the skill text moves this number.
4. **Open one output** in `examples/<name>/runs/<time>/`. Each file starts with its verdict. A number you haven't looked behind is a guess.

One run per request is noise; use `--reps 3` before you decide anything. Why, and two more ways the score fools you: [docs/measuring.md](docs/measuring.md).

## Tonight: test your own skill

```bash
cp -r template mine
python3 eval.py mine --cmd "$AGENT"
```

Six steps, from your skill to a number you can trust: [docs/your-own-skill.md](docs/your-own-skill.md).

## Docs

- [how-it-works.md](docs/how-it-works.md): the three stages, skill vs. plugin, test vs. eval, example output
- [measuring.md](docs/measuring.md): what code can check, what needs a judge, noise, three traps
- [backends.md](docs/backends.md): lines for each CLI, the API path, why the extra flags
- [your-own-skill.md](docs/your-own-skill.md): test your own skill in six steps
- [cost.md](docs/cost.md): measured tokens and cost per run

## Sources

- OpenAI, [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills): the `id,should_trigger,prompt` set
- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): code graders vs. model graders, pass@k vs. pass^k
- Andrej Karpathy, [autoresearch](https://github.com/karpathy/autoresearch): the agent edits the code, never the eval
- Andrew Ng, [The Batch, issue 297](https://www.deeplearning.ai/the-batch/issue-297/): start evals early with a handful of examples

Built for the session "Did Your Agent Actually Get Better?" at ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
