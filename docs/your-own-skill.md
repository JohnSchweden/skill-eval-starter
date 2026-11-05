# Test your own skill

The runner is the same for every skill. Each skill needs its own test: its own requests, rules, judge question and script.

```bash
cp -r template mine
```

1. **The skill**: paste it into `mine/SKILL.md`.
2. **Requests**: three to five real requests in `mine/prompts.csv`. At least one names the skill, one only describes the job, and one is close to its topic but must stay off. Use full-length texts like the ones you really give it: in three sentences most problems have no room to show.
3. **Rules**: in `mine/checks.txt`, write what your skill promises: code rules for what code can decide, one `judge` question for what it can't. A good source is your own corrections: every output you fixed by hand is a rule or a request. Add a few rules the skill text doesn't list (held out). If the test only bans the words the skill already bans, any model passes and the test shows nothing.
4. **Script** (optional): move the code rules your skill should enforce into `mine/scripts/check.py`. Without the folder, the skill+check stage is skipped.
5. **Run**: `python3 eval.py mine --cmd "$AGENT"` (your CLI line, see [backends.md](backends.md)). It runs each request three times; add requests before you trust a small difference.
6. **Improve**: change `SKILL.md` or the script, run again, keep the change only if "Runs that pass" went up. `results.tsv` keeps a line per run with a hash of the skill and script.

Your agent may edit the skill and the script, never `prompts.csv` or `checks.txt`. An agent that may change the test will make the test easier, not the skill better.

Start small: five requests with an imperfect rule beat no test (Andrew Ng). Grow toward 10 to 20 from real failures (OpenAI).

Before you trust the numbers, read [measuring.md](measuring.md): what code can check, what needs a judge, and five ways the score fools you.
