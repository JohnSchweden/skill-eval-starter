#!/usr/bin/env python3
"""Run a skill with and without it, score both against your own rules.

Usage:
  python3 eval.py example/                      # uses OPENAI_BASE_URL / OPENAI_API_KEY / --model
  python3 eval.py example/ --cmd "claude -p"    # any CLI that reads the prompt on stdin
  python3 eval.py example/ --reps 3             # 3 runs per prompt and arm

A skill folder holds three files:
  SKILL.md     the instruction text under test (any skill or system prompt)
  prompts.csv  id,should_trigger,prompt
  checks.txt   one rule per line (see README)

No dependencies beyond Python 3.9+.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MARKER = "[skill used]"

SYSTEM = (
    "You can use the skill below. Use it only if the request matches what the skill is for. "
    f"If you use it, write {MARKER} alone on the first line, then answer as the skill says. "
    f"If you don't use it, answer normally and do not write {MARKER}.\n\n<skill>\n{{skill}}\n</skill>"
)


def load_checks(path):
    rules = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        kind, _, arg = line.partition(" ")
        if kind in ("max_words", "max_chars"):
            rules.append((kind, int(arg)))
        elif kind in ("must_match", "must_not_match"):
            rules.append((kind, re.compile(arg, re.MULTILINE)))
        else:
            sys.exit(f"{path}:{n}: unknown rule '{kind}' (use max_words, max_chars, must_match, must_not_match)")
    if not rules:
        sys.exit(f"{path}: no rules")
    return rules


def check(text, rules):
    """Return the list of rules the text fails."""
    failed = []
    for kind, arg in rules:
        if kind == "max_words" and len(text.split()) > arg:
            failed.append(f"{kind} {arg} (got {len(text.split())})")
        elif kind == "max_chars" and len(text) > arg:
            failed.append(f"{kind} {arg} (got {len(text)})")
        elif kind == "must_match" and not arg.search(text):
            failed.append(f"{kind} {arg.pattern}")
        elif kind == "must_not_match" and arg.search(text):
            failed.append(f"{kind} {arg.pattern}")
    return failed


def call_api(system, prompt, model):
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps({"model": model, "messages": messages}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def call_cmd(system, prompt, cmd):
    text = f"{system}\n\n---\n\n{prompt}" if system else prompt
    # Run in an empty folder so the agent can't pick up project files or the skill itself.
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(cmd, shell=True, input=text, capture_output=True, text=True, cwd=tmp, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="folder with SKILL.md, prompts.csv, checks.txt")
    ap.add_argument("--cmd", help='CLI that reads a prompt on stdin, e.g. "claude -p"')
    ap.add_argument("--model", default=os.environ.get("EVAL_MODEL", "gpt-4o-mini"), help="model for the API backend")
    ap.add_argument("--reps", type=int, default=1, help="runs per prompt and arm (3 to trust a result)")
    args = ap.parse_args()

    skill = (args.folder / "SKILL.md").read_text()
    rules = load_checks(args.folder / "checks.txt")
    with open(args.folder / "prompts.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["should_trigger"] = row["should_trigger"].strip().lower() in ("true", "yes", "1")

    if not args.cmd and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for a non-OpenAI endpoint), or pass --cmd.")
    backend = args.cmd or args.model

    def run(job):
        row, arm, rep = job
        system = SYSTEM.format(skill=skill) if arm == "with" else ""
        try:
            out = call_cmd(system, row["prompt"], args.cmd) if args.cmd else call_api(system, row["prompt"], args.model)
        except Exception as e:  # report and keep going; one bad call shouldn't sink the run
            return job, None, [f"error: {e}"]
        used = out.lstrip().startswith(MARKER)
        out = out.lstrip()[len(MARKER):].strip() if used else out.strip()
        return job, used, out

    jobs = [(row, arm, rep) for row in rows for arm in ("with", "without") for rep in range(args.reps)]
    print(f"{len(jobs)} runs on {backend} ...", file=sys.stderr)
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(run, jobs))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = args.folder / "runs" / stamp
    outdir.mkdir(parents=True)

    # Per row and arm: did every rep pass? Trigger rows are scored on the rules,
    # no-trigger rows on staying off (the skill must not fire).
    table, score = [], {"with": [0, 0], "without": [0, 0]}
    trigger_ok = trigger_n = 0
    for row in rows:
        line = [row["id"], "on" if row["should_trigger"] else "off"]
        for arm in ("with", "without"):
            passes = []
            for (r, a, rep), used, out in results:
                if r is not row or a != arm:
                    continue
                if used is None:
                    passes.append(False)
                    note = out[0]
                    out = ""
                elif row["should_trigger"]:
                    failed = check(out, rules)
                    passes.append(not failed)
                    note = "pass" if not failed else "FAIL " + "; ".join(failed)
                else:
                    ok = not used if arm == "with" else True
                    passes.append(ok)
                    note = "stayed off" if ok else "FIRED (should stay off)"
                if arm == "with" and used is not None:
                    trigger_n += 1
                    trigger_ok += used == row["should_trigger"]
                (outdir / f"{row['id']}-{arm}-{rep + 1}.md").write_text(f"<!-- {note} -->\n{out}\n")
            all_pass = all(passes)
            if row["should_trigger"]:
                score[arm][0] += all_pass
                score[arm][1] += 1
            line.append(f"{sum(passes)}/{len(passes)}")
        table.append(line)

    print(f"\nskill {hashlib.sha1(skill.encode()).hexdigest()[:7]}  {backend}  reps {args.reps}\n")
    print(f"{'id':<14}{'skill':<7}{'with':>6}{'without':>9}")
    for i, kind, w, wo in table:
        print(f"{i:<14}{kind:<7}{w:>6}{wo:>9}")
    pct = lambda a: f"{score[a][0]}/{score[a][1]}" + (f" ({100 * score[a][0] // score[a][1]}%)" if score[a][1] else "")
    print(f"\nPrompts that pass every run   with: {pct('with')}   without: {pct('without')}")
    print(f"Skill fired when it should    {trigger_ok}/{trigger_n}")
    print(f"Outputs in {outdir}/")

    with open(args.folder / "results.tsv", "a") as f:
        if f.tell() == 0:
            f.write("time\tskill_sha\tbackend\treps\twith\twithout\ttrigger\n")
        f.write(f"{stamp}\t{hashlib.sha1(skill.encode()).hexdigest()[:7]}\t{backend}\t{args.reps}\t"
                f"{score['with'][0]}/{score['with'][1]}\t{score['without'][0]}/{score['without'][1]}\t{trigger_ok}/{trigger_n}\n")


if __name__ == "__main__":
    main()
