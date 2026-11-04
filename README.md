# skill-eval-starter

Did your agent actually get better? Test a skill three ways and compare the numbers.

Needs Python 3.9 and an agent CLI or a model API key. Nothing to install.

## 1. Clone the repo

```bash
git clone https://github.com/JohnSchweden/skill-eval-starter && cd skill-eval-starter
```

## 2. Run the post writer and the humanizer

```bash
AGENT='claude -p --model haiku --tools "" --setting-sources "" --system-prompt "Answer the request."'
python3 eval.py examples/post-writer --cmd "$AGENT"
python3 eval.py examples/humanizer   --cmd "$AGENT"
```

Not on Claude Code? Take your CLI's `AGENT=` line from [docs/backends.md](docs/backends.md) (Codex, Gemini, opencode, Cursor, Copilot, Ollama) or use an API key.

About 25 small calls per example: a minute or two, about one cent with the line above.

## 3. Each runs three ways

| Stage | What the model gets |
|---|---|
| no skill | just the request |
| skill | the request + the skill text. The model may follow it. |
| skill + check | the same, plus a script that checks every answer. The model fixes what it finds. |

## 4. See what code caught, and the judge

```
                       no skill      skill skill+check
Code checks pass            1/3        3/3        3/3   checked by code
Judge says yes              0/3        3/3        3/3   checked by a model
Runs that pass              0/3        3/3        3/3   all checks
```

- **Code checks**: length, dashes, banned words. The script moves this number.
- **Judge**: facts kept, nothing invented. Only the skill text moves this number.
- **Open one output** in `examples/<name>/runs/`. A number you haven't looked behind is a guess.

**Bring back three numbers per example:** no skill __ · skill __ · skill + check __

## Tonight: test your own skill

```bash
cp -r template mine
python3 eval.py mine --cmd "$AGENT"
```

Steps: [docs/your-own-skill.md](docs/your-own-skill.md)

## More

- [How it works](docs/how-it-works.md): the files, test vs. eval, skill vs. plugin, sources
- [What to trust](docs/measuring.md): code vs. judge, noise, three traps
- [Other CLIs and APIs](docs/backends.md)
- [Cost](docs/cost.md)

Built for "Did Your Agent Actually Get Better?", ClawCamp Berlin #2, 5 November 2026, by Yevgen Schweden.
