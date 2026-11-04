# What can be measured, and how

| What | Checked by | Example | Trust |
|---|---|---|---|
| Length, banned words, dashes, hashtags, a required format | code (`checks.txt` rules) | `max_words 120`, `must_not_match [—–]` | same answer every time, free |
| Did the skill fire, and stay off when it should | code (the `[skill used]` marker) | the stay-off request | same answer every time |
| Facts kept, nothing invented, tone, "does it answer the question" | an AI judge (`judge <question>` in `checks.txt`) | "Does the answer use only facts that are in the request?" | a second model with its own noise |
| Do real people like it | nothing in a test | replies, comments, sales | only the real world tells you |

## Deterministic vs. AI

Everything a rule can decide belongs in code: in the test (`checks.txt`) and in the check script (`scripts/check.py`). That frees the skill text from rules the model may forget, and leaves it with the part only a model can do: the verdict, the wording, keeping the facts. The judge measures that part, but it can be wrong. Before you trust a judge, compare it with your own verdict on about six outputs.

## Noise

The same request gives different answers each run. A skill that passes 75% of the time passes three runs in a row only 42% of the time. The default is one run (`--reps 1`): enough to see the shape. Before you decide to keep a change, run `--reps 3`. Small differences mean nothing until you add requests or runs.

## Three ways the score fools you

- **No baseline.** Skill and no skill both pass: the skill adds nothing, or the test is too easy.
- **The test is wrong.** A rule the skill no longer promises makes a good skill lose. Example from building this repo: the humanizer judge first asked "does the answer keep every fact *and claim*?". The skill is told to cut empty claims like "the future looks bright", so the judge failed every good rewrite. Read one failing output and ask: is the skill wrong, or the test?
- **One run is noise.** See above.
