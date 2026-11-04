# How it works

## Skill text vs. skill + check

- **Skill text**: the instructions your agent loads (`SKILL.md`, a system prompt, an n8n or LangGraph node prompt). The model may follow them, or not.
- **Skill + check**: the same text plus a script that checks every answer in code, like a hook. The model fixes what the script finds.

A note on words: a skill folder can already hold code (`scripts/`), docs (`references/`) and templates (`assets/`), per the [Agent Skills spec](https://agentskills.io/specification). But the model decides whether to run that code. A Claude Code **plugin** is a package around skills that can add **hooks**: code that runs every time, whether the model wants it or not. The third stage here tests that idea, "code that always runs", without needing a plugin.

## The three stages

| Stage | The model gets | Tests |
|---|---|---|
| no skill | the bare request | what the model does anyway: your baseline |
| skill | the request + `SKILL.md` as system prompt | what the text adds |
| skill+check | the same, then `scripts/check.py` checks every answer; the model fixes the findings, at most twice | what code adds on top of the text |

## Test vs. eval

Each skill folder holds:

| File | What it is | Changes? |
|---|---|---|
| `SKILL.md` | the skill text: the part only a model can do | yes, this is what you improve |
| `scripts/check.py` | the check script: the part code can do (text on stdin, findings on stdout, exit 1 if any) | yes |
| `prompts.csv` | the test requests (`id,should_trigger,prompt`): some where the skill should fire, at least one where it must stay off | never |
| `checks.txt` | the test rules: code rules, plus one yes/no question for an AI judge | never |

**The test** is `prompts.csv` + `checks.txt`. **The eval** is `eval.py` running that test against the three stages. `scripts/check.py` belongs to the skill, not the test: it may change, the test may not.

Rules in `checks.txt`, one per line:

```
max_words 120
max_chars 1300
must_match ^[A-Z]
must_not_match [—–]
judge Does the answer use only facts that are in the request?
```

## What the runner does

1. The skill and skill+check stages give the model `SKILL.md` as a system prompt. They ask it to write `[skill used]` on the first line when it applies the skill, which makes triggering visible on any model. The marker is stripped before the rules run.
2. CLI runs happen in an empty temp folder, so the agent can't read the skill from disk.
3. Rules are only checked on requests where the skill should fire. The stay-off request passes when the skill stays off.
4. The judge uses the same backend as the run.
5. Every answer goes to `<folder>/runs/<time>/`, each file starting with its verdict. One summary line per run is appended to `<folder>/results.tsv`, with a hash of the skill and script, so you can see which version scored what.

## Example output

One run per request (`--reps 1`) of the post writer on `claude -p --model haiku`:

```
prompt          skill    no skill      skill skill+check
agent-eval      on            0/1        1/1        1/1
meeting-notes   on            0/1        1/1        1/1
first-talk      on            0/1        1/1        1/1
stay-off        off           1/1        1/1        1/1

Code checks pass              1/3        3/3        3/3   checked by code: same answer every time
Judge says yes                0/3        3/3        3/3   checked by a model: can be wrong
Runs that pass                0/3        3/3        3/3   all checks
Skill fired right               -        4/4        4/4   on when it should be, off when not
```

## What this does not test

This tests the skill text and its script, not your agent's own skill loader. To test the loader too, remove the skill from your agent's skills folder for the baseline run. A disable flag isn't enough: the agent can still find the file.
