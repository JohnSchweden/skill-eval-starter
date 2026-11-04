# skill-eval-starter

Did your agent actually get better? Run a skill three ways and compare: without it, with it, and with a check that always runs.

- **Skill text**: the instructions your agent loads (`SKILL.md`, a system prompt, an n8n or LangGraph node prompt). The model may follow them, or not.
- **Skill + check**: the same text plus a script that checks every answer in code, like a hook. The model fixes what the script finds.

A note on words: a skill folder can already hold code (`scripts/`), docs (`references/`) and templates (`assets/`), per the [Agent Skills spec](https://agentskills.io/specification). But the model decides whether to run that code. A Claude Code **plugin** is a package around skills that can add **hooks**: code that runs every time, whether the model wants it or not. The third stage here tests that idea, "code that always runs", without needing a plugin.

No dependencies beyond Python 3.9.

## What's in here

```
eval.py                  the runner: same requests, three ways, scored against a fixed test
examples/post-writer/    example 1: writes a short LinkedIn post from notes
examples/humanizer/      example 2: rewrites AI-sounding text so it reads human
template/                empty copy for your own skill (homework)
```

Each example folder holds:

| File | What it is | Changes? |
|---|---|---|
| `SKILL.md` | the skill text: the part only a model can do | yes, this is what you improve |
| `scripts/check.py` | the check script: the part code can do | yes |
| `prompts.csv` | four test requests: three where the skill should fire, one where it must stay off | never |
| `checks.txt` | the test rules: code rules, plus one yes/no question for an AI judge | never |

## At the workshop (15 minutes)

You don't write anything. Clone, run both examples, read the results.

```bash
git clone https://github.com/JohnSchweden/skill-eval-starter && cd skill-eval-starter

python3 eval.py examples/post-writer --cmd "claude -p"
python3 eval.py examples/humanizer   --cmd "claude -p"
```

Any CLI that reads a prompt on stdin and prints the answer works (`--cmd "codex exec"`, `--cmd "ollama run llama3.2"`). Or any OpenAI-compatible API (OpenAI, OpenRouter, Ollama, LM Studio, Anthropic, Gemini):

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://openrouter.ai/api/v1   # leave unset for OpenAI
python3 eval.py examples/post-writer --model gpt-4o-mini
```

Each run makes about 70 small calls (3 runs per request and stage, plus judge calls and script fixes) and takes a few minutes. In a hurry: `--reps 1`.

Or hand it to your coding agent:

```text
Read README.md in this repo. Run eval.py on examples/post-writer and on
examples/humanizer with --cmd set to the CLI you are running in
(for Claude Code: --cmd "claude -p"). For each example, show me the table,
then open one failing output from runs/ and tell me whether the skill or
the test is at fault. Do not edit any file.
```

**Bring back three numbers per example** ("Runs that pass"): **no skill __ · skill __ · skill + check __**

### What the output looks like

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

### What to look at

1. **No skill vs. skill.** Does the skill add anything? If no skill already passes, the skill does nothing for that request, or the test is too easy.
2. **Skill vs. skill+check on "Code checks pass".** The script catches what code can check, and the model fixes it. Here skill+check should get close to 100%.
3. **Skill vs. skill+check on "Judge says yes".** The script can't help here: whether facts were kept or invented is not something code can decide. Only the skill text moves this number.
4. **Open one output** in `examples/<name>/runs/<time>/`. Each file starts with its verdict. A number you haven't looked behind is a guess.

## The three stages

| Stage | The model gets | Tests |
|---|---|---|
| no skill | the bare request | what the model does anyway: your baseline |
| skill | the request + `SKILL.md` as system prompt | what the text adds |
| skill+check | the same, then `scripts/check.py` checks every answer; the model fixes the findings, at most twice | what code adds on top of the text |

## What can be measured, and how

| What | Checked by | Example | Trust |
|---|---|---|---|
| Length, banned words, dashes, hashtags, a required format | code (`checks.txt` rules) | `max_words 120`, `must_not_match [—–]` | same answer every time, free |
| Did the skill fire, and stay off when it should | code (the `[skill used]` marker) | the stay-off request | same answer every time |
| Facts kept, nothing invented, tone, "does it answer the question" | an AI judge (`judge <question>` in `checks.txt`) | "Does the answer use only facts that are in the request?" | a second model with its own noise |
| Do real people like it | nothing in a test | replies, comments, sales | only the real world tells you |

**Deterministic vs. AI.** Everything a rule can decide belongs in code: in the test (`checks.txt`) and in the check script (`scripts/check.py`). That frees the skill text from rules the model may forget, and leaves it with the part only a model can do: the verdict, the wording, keeping the facts. The judge measures that part, but it can be wrong. Before you trust a judge, compare it with your own verdict on about six outputs.

**Noise.** The same request gives different answers each run. A skill that passes 75% of the time passes three runs in a row only 42% of the time. That's why the default is `--reps 3`. Small differences mean nothing until you add requests or runs.

## Three ways the score fools you

- **No baseline.** Skill and no skill both pass: the skill adds nothing, or the test is too easy.
- **The test is wrong.** A rule the skill no longer promises makes a good skill lose. Example from building this repo: the humanizer judge first asked "does the answer keep every fact *and claim*?". The skill is told to cut empty claims like "the future looks bright", so the judge failed every good rewrite. Read one failing output and ask: is the skill wrong, or the test?
- **One run is noise.** See above.

## Tonight: test your own skill

The runner is the same for every skill. Each skill needs its own test: its own requests, rules, judge question and script.

```bash
cp -r template mine
```

1. **The skill**: paste it into `mine/SKILL.md`.
2. **Requests**: three to five real requests in `mine/prompts.csv`. At least one names the skill, one only describes the job, and one is close to its topic but must stay off.
3. **Rules**: in `mine/checks.txt`, write what your skill promises: code rules for what code can decide, one `judge` question for what it can't. A good source is your own corrections: every output you fixed by hand is a rule or a request.
4. **Script** (optional): move the code rules your skill should enforce into `mine/scripts/check.py`. Without the folder, the skill+check stage is skipped.
5. **Run**: `python3 eval.py mine --cmd "claude -p"`.
6. **Improve**: change `SKILL.md` or the script, run again, keep the change only if "Runs that pass" went up. `results.tsv` keeps a line per run with a hash of the skill and script. Your agent may edit the skill and the script, never `prompts.csv` or `checks.txt`. An agent that may change the test will make the test easier, not the skill better.

Start small: five requests with an imperfect rule beat no test (Andrew Ng). Grow toward 10 to 20 from real failures (OpenAI).

## How it works

The skill and skill+check stages give the model `SKILL.md` as a system prompt. They ask it to write `[skill used]` on the first line when it applies the skill, which makes triggering visible on any model. The marker is stripped before the rules run. CLI runs happen in an empty temp folder, so the agent can't read the skill from disk. Rules are only checked on requests where the skill should fire; the stay-off request passes when the skill stays off. The judge uses the same backend as the run. Outputs go to `<folder>/runs/<time>/`, and one summary line per run is appended to `<folder>/results.tsv`.

This tests the skill text and its script, not your agent's own skill loader. To test the loader too, remove the skill from your agent's skills folder for the baseline run. A disable flag isn't enough: the agent can still find the file.

## Sources

- OpenAI, [Testing agent skills systematically with evals](https://developers.openai.com/blog/eval-skills): the `id,should_trigger,prompt` set
- Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): code graders vs. model graders, pass@k vs. pass^k
- Andrej Karpathy, [autoresearch](https://github.com/karpathy/autoresearch): the agent edits the code, never the eval
- Andrew Ng, [The Batch, issue 297](https://www.deeplearning.ai/the-batch/issue-297/): start evals early with a handful of examples

Built for the session "Did Your Agent Actually Get Better?" at ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
