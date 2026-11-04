# skill-eval-starter

Did your agent actually get better? Test any skill with it and without it, on whatever stack you build with.

A skill is instruction text your agent loads: a `SKILL.md`, a system prompt, an n8n AI-node prompt, a LangGraph node prompt. This repo runs that text against three of your prompts, once with the skill and once without, and checks the answers against rules you write. No dependencies beyond Python 3.9.

## At the workshop: go at your own pace

You have 15 minutes for one full loop: measure, improve, measure again. Do the steps below yourself, or hand them to your coding agent (Claude Code, Codex, Cursor, …) with this prompt:

```text
Read README.md in this repo and run one full loop for me.
My skill: <path to your SKILL.md or system prompt file, or paste it here>.
1. Follow "Test your own skill": copy template/ to mine/, put the skill in
   mine/SKILL.md, write the three prompts and one rule.
2. Measure: run eval.py on mine/ with --reps 3 and the CLI you are running in
   (for Claude Code: --cmd "claude -p"). Show me the score and one failing
   output, and tell me whether the skill or the rule is at fault.
   If no skill already passes everything, the test is too easy: propose one
   harder prompt or a stricter rule, and measure again once I agree.
3. Improve: copy mine/SKILL.md to mine/SKILL.v1.md, then make ONE change to
   mine/SKILL.md aimed at the failures. Never edit prompts.csv, checks.txt
   or eval.py.
4. Measure again with --reps 3. Keep the change only if "Runs that pass"
   with the skill went up, or held with a shorter skill; otherwise copy
   SKILL.v1.md back.
Finish with three numbers from mine/results.tsv: no skill, skill, improved skill.
```

At the end, bring back three numbers: **no skill __ · skill __ · improved skill __** (runs that pass).

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
Runs that pass                with: 2/2   without: 0/2
Skill fired when it should    3/3
```

## Test your own skill (10 minutes)

```bash
cp -r template mine
```

1. **Pick one skill** (1 min). Paste it into `mine/SKILL.md`. Pick the one your agent uses most, or the last one you corrected by hand.
2. **Write three prompts** (3 min) in `mine/prompts.csv`:
   - one that names the skill (`should_trigger` true)
   - one that only describes the job (true): tests whether the description is good enough
   - one close to the skill's topic where it must stay off (false). Most people skip this one; it catches a skill that fires too eagerly.
3. **Write one rule** (1 min) in `mine/checks.txt`. "My skill is fuzzy" usually still has a rule: no em dashes, under 200 words, starts with a verb, no hashtags.
   | Rule | Example |
   |---|---|
   | `max_words N` | `max_words 200` |
   | `max_chars N` | `max_chars 280` |
   | `must_match REGEX` | `must_match ^Subject:` |
   | `must_not_match REGEX` | `must_not_match —` |
4. **Run it** (3 min): `python3 eval.py mine/ --reps 3 --cmd "claude -p"` (or your CLI / API).
5. **Read the score** (2 min). Then open `mine/runs/<time>/` and read the outputs: a number you haven't looked behind is a guess.

## Three ways the score fools you

- **No baseline.** If the skill and no skill both pass, the skill adds nothing for that prompt, or the test is too easy. Make the prompt harder or cut that part of the skill.
- **The test is wrong.** A rule your skill no longer promises makes a good skill lose. Before you trust a result, read one failing output and ask: is the skill wrong, or the rule? Example: a humanizer skill lost to no skill on the rule "no buzzwords". Its rewrite was clean, but it added a "Changes:" note quoting the buzzwords it had cut, and the rule checks the whole answer.
- **One run is noise.** A skill that passes 75% of the time passes three runs in a row only 42% of the time. Run `--reps 3` before you believe a difference, and count a prompt only when every run passes.

## Then: improve the skill, never the test (5 minutes)

1. Run `--reps 3` and note "Runs that pass" (`results.tsv` keeps a line per run with the skill's hash). If no skill already passes everything, your test is too easy and nothing can improve: make one prompt harder or one rule stricter first. That is your job, not the agent's.
2. Save the current version (`cp mine/SKILL.md mine/SKILL.v1.md`), then make one change to `SKILL.md`, or let your agent make it, aimed at the failing outputs.
3. Run again. Keep the change only if "Runs that pass" with the skill goes up, or holds with a shorter skill. Otherwise copy the old version back.
4. The agent may edit `SKILL.md`. It never edits `prompts.csv` or `checks.txt`: an agent that may change the test will make the test easier, not the skill better.

Start small: 5 prompts with an imperfect rule beat no test (Andrew Ng). Grow toward 10 to 20 from real failures: every manual fix is a future test case (OpenAI).

## What can be measured, and what can't

**Where the tests come from.** You write them. The prompts are real requests your skill gets (one that names it, one that only describes the job, one where it must stay off). The rules are what you would reject by hand: too long, an em dash, no subject line. A good source is your own corrections: every time you fixed an output by hand, that fix is a rule or a prompt.

**How the score is made.** Each prompt runs with the skill (as system prompt) and without it, `--reps` times each. Every answer is checked against your rules. "Runs that pass" counts single answers; "Prompts that pass every run" counts a prompt only when all its runs pass, the strict number for "can I rely on it".

**Checked by code (this repo).** Same answer every time, free, no judge to argue with:
- length (`max_words`, `max_chars`)
- words, characters or patterns that must or must not appear (`must_match`, `must_not_match`): banned phrases, em dashes, hashtags, a required format
- whether the skill fired, and whether it stayed off when it should

**Needs a model as judge (not in this repo).** Tone, "does it answer the question", "are these three ideas really different", "did it invent facts". A judge model can grade these, but it is a second model with its own noise: check it against your own verdict on about six outputs before you count it. On my LinkedIn skill a small judge agreed with me on 2 of 6, so it came out of the score.

**Can't be measured in a test at all.** Whether real people like the result: replies, sales, comments. A test only checks what you wrote down. Check now and then that the score still moves with what you actually care about; my "punch" score for posts turned out to run backwards against real comments.

**Noise.** The same prompt gives different answers each run. One run proves nothing: a skill that passes 75% of the time passes three runs in a row only 42% of the time. That is why the loop uses `--reps 3`.

## How it works

The "with" run gives the model your skill as a system prompt and asks it to write `[skill used]` on the first line when it applies the skill. That makes triggering visible on any model. The marker is stripped before your rules run. The "without" run sends the bare prompt. CLI runs happen in an empty temp folder, so the agent can't read the skill from disk. Rules are only checked on prompts where the skill should fire; the stay-off prompt passes when the skill stays off.

This tests the skill text, not your agent's own skill loader. To test the loader too, remove the skill from your agent's skills folder physically for the baseline run (a disable flag isn't enough: the agent can still find the file).

## Sources

- OpenAI, [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills): the `id,should_trigger,prompt` set and the four goal types (outcome, process, style, efficiency)
- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): pass@k vs pass^k
- Andrej Karpathy, [autoresearch](https://github.com/karpathy/autoresearch): the agent edits the code, never the eval
- Andrew Ng, [The Batch, issue 297](https://www.deeplearning.ai/the-batch/issue-297/): start evals early with a handful of examples

Built for the session "Did Your Agent Actually Get Better?" at ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
