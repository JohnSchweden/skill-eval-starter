# skill-eval-starter

Did your agent actually get better? Test any skill with it and without it, on whatever stack you build with.

A skill is instruction text your agent loads: a `SKILL.md`, a system prompt, an n8n AI-node prompt, a LangGraph node prompt. This repo runs that text against three of your prompts, once with the skill and once without, and checks the answers against rules you write. No dependencies beyond Python 3.9.

## Try the example (2 minutes)

```bash
git clone https://github.com/JohnSchweden/skill-eval-starter && cd skill-eval-starter

# any CLI that reads a prompt on stdin
python3 eval.py example/ --cmd "claude -p"            # tested
python3 eval.py example/ --cmd "ollama run llama3.2"  # same idea, any CLI that prints the answer

# or any OpenAI-compatible API (OpenAI, OpenRouter, Ollama, LM Studio, Anthropic, Gemini)
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1   # leave unset for OpenAI
python3 eval.py example/ --model gpt-4o-mini
```

```
id            skill    with  without
names-it      on        1/1      0/1
describes-it  on        1/1      0/1
stay-off      off       1/1      1/1

Prompts that pass every run   with: 2/2 (100%)   without: 0/2 (0%)
Skill fired when it should    3/3
```

## Test your own skill (12 minutes)

```bash
cp -r template mine
```

1. **Pick one skill** (2 min). Paste it into `mine/SKILL.md`. Pick the one your agent uses most, or the last one you corrected by hand.
2. **Write three prompts** (4 min) in `mine/prompts.csv`:
   - one that names the skill (`should_trigger` true)
   - one that only describes the job (true): tests whether the description is good enough
   - one close to the skill's topic where it must stay off (false). Most people skip this one; it catches a skill that fires too eagerly.
3. **Write one rule** (2 min) in `mine/checks.txt`. "My skill is fuzzy" usually still has a rule: no em dashes, under 200 words, starts with a verb, no hashtags.
   | Rule | Example |
   |---|---|
   | `max_words N` | `max_words 200` |
   | `max_chars N` | `max_chars 280` |
   | `must_match REGEX` | `must_match ^Subject:` |
   | `must_not_match REGEX` | `must_not_match —` |
4. **Run it** (5 min): `python3 eval.py mine/ --cmd "claude -p"` (or your CLI / API).
5. **Read the score** (1 min). Then open `mine/runs/<time>/` and read the outputs: a number you haven't looked behind is a guess.

## Three ways the score fools you

- **No baseline.** If the skill and no skill both pass, the skill adds nothing for that prompt, or the test is too easy. Make the prompt harder or cut that part of the skill.
- **The test is wrong.** A rule your skill no longer promises makes a good skill lose. Before you trust a result, read one failing output and ask: is the skill wrong, or the rule?
- **One run is noise.** A skill that passes 75% of the time passes three runs in a row only 42% of the time. Run `--reps 3` before you believe a difference, and count a prompt only when every run passes.

## Then: let the agent improve the skill, but never the test

1. Run `--reps 3` and note the score (`results.tsv` keeps a line per run with the skill's hash).
2. Make one change to `SKILL.md` (or let your agent make it).
3. Run again. Keep the change only if the score rises beyond the noise, or holds with a shorter skill. Otherwise revert.
4. The agent may edit `SKILL.md`. It never edits `prompts.csv` or `checks.txt`.

Start small: 5 prompts with an imperfect rule beat no test (Andrew Ng). Grow toward 10 to 20 from real failures: every manual fix is a future test case (OpenAI).

## How it works

The "with" run gives the model your skill as a system prompt and asks it to write `[skill used]` on the first line when it applies the skill. That makes triggering visible on any model. The marker is stripped before your rules run. The "without" run sends the bare prompt. CLI runs happen in an empty temp folder, so the agent can't read the skill from disk. Rules are only checked on prompts where the skill should fire; the stay-off prompt passes when the skill stays off.

This tests the skill text, not your agent's own skill loader. To test the loader too, remove the skill from your agent's skills folder physically for the baseline run (a disable flag isn't enough: the agent can still find the file).

## Sources

- OpenAI, [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills): the `id,should_trigger,prompt` set and the four goal types (outcome, process, style, efficiency)
- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): pass@k vs pass^k
- Andrej Karpathy, [autoresearch](https://github.com/karpathy/autoresearch): the agent edits the code, never the eval
- Andrew Ng, [The Batch, issue 297](https://www.deeplearning.ai/the-batch/issue-297/): start evals early with a handful of examples

Built for the session "Did Your Agent Actually Get Better?" at ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
