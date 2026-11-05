# What can be measured, and how

| What | Checked by | Example | Trust |
|---|---|---|---|
| Length, banned words, dashes, hashtags, a required format | code (`checks.txt` rules) | `max_words 120`, `must_not_match [—–]` | same answer every time, free |
| Did the skill fire, and stay off when it should | code (the `[skill used]` marker) | the stay-off request | same answer every time |
| Facts kept, nothing invented, tone, "does it answer the question" | an AI judge (`judge <question>` in `checks.txt`) | "Does the answer use only facts that are in the request?" | a second model with its own noise |
| Do real people like it | nothing in a test | replies, comments, sales | only the real world tells you |

## Deterministic vs. AI

Everything a rule can decide belongs in code: in the test (`checks.txt`) and in the check script (`scripts/check.py`). That frees the skill text from rules the model may forget, and leaves it with the part only a model can do: the verdict, the wording, keeping the facts. The judge measures that part, but it can be wrong. Before you trust a judge, compare it with your own verdict on about six outputs. Each output file shows the judge's YES or NO and its reason. Example from the humanizer: the cover letter says "foster data-driven decisions", the rewrite says "help teams make better decisions", and the judge fails it for adding "teams". If you agree, fix the skill. If you don't, fix the question.

## Noise

The same request gives different answers each run. A skill that passes 75% of the time passes three runs in a row only 42% of the time. The default is three runs (`--reps 3`). One run (`--reps 1`) is quicker but only shows the shape: in testing, one run gave the humanizer 0% where three runs gave 22%. Small differences mean nothing until you add requests or runs.

## Five ways the score fools you

- **No baseline.** Skill and no skill both pass: the skill adds nothing, or the test is too easy.
- **The test is wrong.** A rule the skill no longer promises makes a good skill lose. Example from building this repo: the humanizer judge first asked "does the answer keep every fact *and claim*?". The skill is told to cut empty claims like "the future looks bright", so the judge failed every good rewrite. Read one failing output and ask: is the skill wrong, or the test?
- **The skill makes it worse.** The same conflict sat in the skill text: "keep every fact and claim". The model obeyed, kept "the future is bright" and reworded it to "the future looks bright". Without the skill, it dropped the line. No check caught it until an outside AI-writing detector scanned the outputs. If no skill beats skill on a pattern, read the skill text for the line that asks for it.
- **The test copies the skill.** The humanizer's first test banned exactly the words its skill banned, in three-sentence texts. Haiku passed every code check with no skill at all. With two full-length texts and held-out rules (AI tells the skill doesn't list), no skill dropped to 33%.
- **One run is noise.** See above.
