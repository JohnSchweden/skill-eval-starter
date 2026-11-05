# skill-eval-starter

Did your agent actually get better? Test a skill three ways and compare the numbers.

Needs Python 3.9 and an agent CLI or a model API key. Nothing to install.

## 1. Clone the repo

```bash
git clone https://github.com/JohnSchweden/skill-eval-starter && cd skill-eval-starter
```

## 2. Run the post writer and the humanizer

Set your agent (Claude Code):

```bash
AGENT='claude -p --model haiku --tools "" --setting-sources "" --system-prompt "Answer the request."'
```

Let a stronger model grade the answers (optional, roughly 10 cents more per example):

```bash
export JUDGE='claude -p --model sonnet --tools "" --setting-sources "" --system-prompt "Answer the request."'
```

Without it, the model under test grades its own answers.

Not on Claude Code? Take your CLI's `AGENT=` line from [docs/backends.md](docs/backends.md) (Codex, Gemini, opencode, Cursor, Copilot, Ollama) or use an API key.

Run the post writer:

```bash
python3 eval.py examples/post-writer --cmd "$AGENT"
```

Run the humanizer:

```bash
python3 eval.py examples/humanizer --cmd "$AGENT"
```

On Windows, use PowerShell and `python` (not tested on Windows yet):

```powershell
$env:AGENT = 'claude -p --model haiku --tools "" --setting-sources "" --system-prompt "Answer the request."'
$env:JUDGE = 'claude -p --model sonnet --tools "" --setting-sources "" --system-prompt "Answer the request."'
python eval.py examples/post-writer
python eval.py examples/humanizer
```

Without `--cmd`, eval.py takes the agent from the `AGENT` variable, and without `--judge-cmd` the judge from `JUDGE`. That way PowerShell never has to pass the quotes on.

Each request runs three times per stage: about 70 small calls per example, a minute or two, about 3 cents with the line above.

## 3. Each runs three ways

| Stage | What the model gets |
|---|---|
| no skill | just the request |
| skill | the request + the skill text. The model may follow it. |
| skill + check | the same, plus a script that checks every answer. The model fixes what it finds. |

## 4. See what code caught, and the judge

```
                            no skill         skill   skill+check
Code checks pass       0% (0/9)     89% (8/9)    100% (9/9)   checked by code
Judge says yes         0% (0/9)    100% (9/9)    100% (9/9)   checked by a model
Runs that pass         0% (0/9)     89% (8/9)    100% (9/9)   all checks
Skill fired right             -  100% (12/12)  100% (12/12)   on when it should be, off when not
Script sent back              -             -      0% (0/9)   answers check.py sent back for a fix
```

- **Code checks**: length, dashes, banned words. Same answer, same result, every time.
- **Judge**: facts kept, nothing invented. A model decides, so it can be wrong: each output file shows its YES or NO and the reason.
- **Script sent back**: at 0%, the script changed nothing. Then skill and skill + check differ only by chance.
- **Open one output** in `examples/<name>/runs/`. A number you haven't looked behind is a guess.

**Bring back three percentages per example** (Runs that pass): no skill __% · skill __% · skill + check __%

## Homework: test your own skill

Fill in the four files in `mine/` before the run; the template has no test rules yet.

```bash
cp -r template mine
python3 eval.py mine --cmd "$AGENT"
```

Steps: [docs/your-own-skill.md](docs/your-own-skill.md)

## More

- [How it works](docs/how-it-works.md): the files, test vs. eval, skill vs. plugin, sources
- [What to trust](docs/measuring.md): code vs. judge, noise, four traps
- [Other CLIs and APIs](docs/backends.md)
- [Cost](docs/cost.md)

Built for "Did Your Agent Actually Get Better?", ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
