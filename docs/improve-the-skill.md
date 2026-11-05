# Improve the skill: three rounds

Measuring a skill is half the job. The other half is the loop: read the fails, change the skill text, run again, compare. Each round takes about two minutes and roughly 20 cents (Haiku answers, Sonnet judges, `--reps 5`). It fits into the workshop, or try it at home.

Your agent may change `SKILL.md` and `scripts/check.py`. It must never change `prompts.csv` or `checks.txt`: an agent that may change the test will make the test easier, not the skill better.

## 0. Work on a copy and get a baseline

```bash
cp -r examples/humanizer my-humanizer
mkdir my-humanizer/versions && cp my-humanizer/SKILL.md my-humanizer/versions/v0.md
python3 eval.py my-humanizer --cmd "$AGENT" --reps 5
```

Use `--reps 5`, not the default 3: 15 graded answers per stage instead of 9. Even so, the same text can move about 20 points from one run to the next. Write down "Runs that pass" for the skill and skill + check columns.

## 1. Read the fails, not the percentages

```bash
cd my-humanizer/runs/<time>
grep -l '^FAIL' *-skill-[0-9]*.md
```

Each file starts with the rule that failed and the judge's reason. Read every skill-stage fail and put it in one of two groups:

- **The same fail in several runs** (or in an earlier run): a real gap in the skill. Fix this one.
- **A fail that shows up once**: maybe noise. Leave it until it comes back.

Before you blame the skill, ask whether the test is wrong (see [measuring.md](measuring.md)).

## 2. One line per pattern

Add or change one line in `SKILL.md` for each real pattern. Two rules:

- **Name the behaviour, not the test.** Don't copy the held-out words from `checks.txt` into the skill. The score would go up and you would learn nothing: the held-out rules are there to see whether the skill works beyond its own word list. Give your own examples.
- **Keep a copy of each version**: `cp SKILL.md versions/v1.md`. `results.tsv` keeps a line per run with a hash of the skill, so you can see which version scored what.

## 3. Run again, and check every request

```bash
python3 eval.py my-humanizer --cmd "$AGENT" --reps 5
```

Look at the per-request table, not just the total. A rule that is too broad fixes one request and breaks another. Keep a change when the fail it targets is gone and no other request got worse. Otherwise narrow the line and run again.

Repeat steps 1 to 3 three times.

## Our run, 5 November 2026

| Version | Change | Skill | Skill + check | Script sent back |
|---|---|---|---|---|
| v0 | starter text | 73% (11/15) | 93% | 20% |
| v1 | + keep the verb of a fact; + drop "isn't just" frames | 80% (12/15) | 100% | 20% |
| v2 | verb rule narrowed to events; decorative verbs swapped | 93% (14/15) | 93% | 0% |
| v3 | + don't connect facts the original keeps apart | 100% (15/15) | 100% | 7% |

- **v0**: "Relay isn't just another app" survived in 3 of 5 product-launch answers, and the team update turned "onboarded 3 new customers" into "signed". Both fails had already shown up in earlier 3-run results, so they were real.
- **v1** fixed both, and the cover letter fell from 5/5 to 2/5. "Keep the verb that carries a fact" made Haiku keep "foster", "delved" and "showcase": they are verbs too. Only running every request each round caught this.
- **v2** limited the rule to verbs that say what happened. One fail was left: the rewrite gave the planning session an agenda the original never mentions. The no-skill answers fail the same way ("I'll send details soon").
- **v3** added a line against new links between facts. 15 of 15 passed.

The no-skill column ran the same requests every time and still moved between 33% and 53%. v0 to v3 is 27 points, and every fail along the way had a reason, so the gain is real. v2 to v3 on its own is a single answer. v3 was tuned on the same three texts it was scored on: a new request it has never seen shows whether the rules carry over.

<details>
<summary>Try it yourself first. Then compare with v3.</summary>

```markdown
- Keep every fact: numbers, names, events. Add nothing.
- Keep the verb of each event, what actually happened: "hired" stays "hired", not "recruited"; a different event is a different claim. Verbs that only decorate ("spearhead", "harness") are not events: swap them for plain ones.
- Don't connect facts the original keeps apart. "So", "because", "we'll discuss" or "I'll send details" each add a claim: a cause, a purpose, an agenda, a promise.
- Drop contrast frames like "X isn't just Y" or "not only A but also B". Say what X does.
- Cut empty claims that say nothing checkable: "the future is bright", "nothing short of transformative".
- Prefer short sentences and plain verbs. Keep the length about the same or shorter.
- Output only the rewritten text. No notes, no list of changes.
```

</details>

## Let your agent run the loop

You can hand the loop to your agent. Paste this into Claude Code (or any agent CLI) from the repo folder:

> Improve `my-humanizer/SKILL.md` in three rounds. Each round: run `python3 eval.py my-humanizer --cmd "$AGENT" --reps 5`, read every FAIL file of the skill stage in the new run folder, find the fails that repeat, change or add one line in SKILL.md per pattern, save the version to `my-humanizer/versions/vN.md`. Never edit `prompts.csv`, `checks.txt` or `scripts/check.py`, and never copy words from `checks.txt` into the skill. If a change makes another request worse, narrow it. At the end, show a table: version, change, skill %, skill + check %.

Read the fails yourself as well. The agent's summary of why a run failed is a claim. The FAIL files show what actually happened.
