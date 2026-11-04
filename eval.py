#!/usr/bin/env python3
"""Run the same prompts three ways and score each against fixed tests.

  no skill   the bare prompt
  skill      the skill text (SKILL.md) as system prompt
  skill+check  the skill text plus its script (scripts/check.py), enforced: the script
               checks every answer and the model fixes what it reports, at most twice.
               A script inside a skill runs only if the model decides to call it;
               here it always runs, like a hook.

Usage:
  python3 eval.py examples/post-writer --cmd "claude -p"   # any CLI that reads the prompt on stdin
  python3 eval.py examples/humanizer --model gpt-4o-mini   # or an OpenAI-compatible API
  python3 eval.py examples/post-writer --reps 3            # runs per prompt and stage (default 3)

A skill folder holds:
  SKILL.md           the instruction text (any skill or system prompt)
  scripts/check.py   optional: the skill's deterministic part (text on stdin, findings on stdout, exit 1 if any)
  prompts.csv        the test prompts: id,should_trigger,prompt
  checks.txt         the test rules: code rules, and `judge <question>` for a model judge

The skill and its script may change. prompts.csv and checks.txt are the test: they never change.
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
STAGES = ("none", "skill", "check")
LABEL = {"none": "no skill", "skill": "skill", "check": "skill+check"}

SYSTEM = (
    "You can use the skill below. Use it only if the request matches what the skill is for. "
    f"If you use it, write {MARKER} alone on the first line, then answer as the skill says. "
    f"If you don't use it, answer normally and do not write {MARKER}.\n\n<skill>\n{{skill}}\n</skill>"
)
FIX = (
    "{prompt}\n\nYour answer was:\n<answer>\n{answer}\n</answer>\n\n"
    "The skill's check script found these problems:\n{findings}\n\n"
    f"Write the corrected answer. Start with {MARKER} on the first line, then only the answer."
)
JUDGE = (
    "You are grading an answer. Reply with YES or NO only.\n\n"
    "Request:\n<request>\n{prompt}\n</request>\n\nAnswer:\n<answer>\n{answer}\n</answer>\n\nQuestion: {question}"
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
        elif kind == "judge":
            rules.append((kind, arg))
        else:
            sys.exit(f"{path}:{n}: unknown rule '{kind}' (use max_words, max_chars, must_match, must_not_match, judge)")
    if not rules:
        sys.exit(f"{path}: no rules")
    return rules


def code_check(text, rules):
    """Return the code rules the text fails."""
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


def call_api(prompt, model, system=""):
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps({"model": model, "messages": messages}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def call_cmd(prompt, cmd, system=""):
    text = f"{system}\n\n---\n\n{prompt}" if system else prompt
    # Run in an empty folder so the agent can't pick up project files or the skill itself.
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(cmd, shell=True, input=text, capture_output=True, text=True, cwd=tmp, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout


def strip_marker(out):
    out = out.strip()
    used = out.startswith(MARKER)
    return used, (out[len(MARKER):].strip() if used else out)


def run_script(script, text):
    r = subprocess.run([sys.executable, str(script)], input=text, capture_output=True, text=True, timeout=60)
    return r.stdout.strip() if r.returncode else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="skill folder (SKILL.md, prompts.csv, checks.txt, optional scripts/check.py)")
    ap.add_argument("--cmd", help='CLI that reads a prompt on stdin, e.g. "claude -p"')
    ap.add_argument("--model", default=os.environ.get("EVAL_MODEL", "gpt-4o-mini"), help="model for the API backend")
    ap.add_argument("--reps", type=int, default=3, help="runs per prompt and stage (default 3)")
    ap.add_argument("--workers", type=int, default=4, help="calls in parallel (default 4)")
    args = ap.parse_args()

    skill = (args.folder / "SKILL.md").read_text()
    script = args.folder / "scripts" / "check.py"
    stages = STAGES if script.exists() else STAGES[:2]
    rules = load_checks(args.folder / "checks.txt")
    code_rules = [r for r in rules if r[0] != "judge"]
    judges = [q for k, q in rules if k == "judge"]
    with open(args.folder / "prompts.csv", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["should_trigger"] = row["should_trigger"].strip().lower() in ("true", "yes", "1")

    if not args.cmd and not os.environ.get("OPENAI_API_KEY"):
        sys.exit("Set OPENAI_API_KEY (and OPENAI_BASE_URL for a non-OpenAI endpoint), or pass --cmd.")
    backend = args.cmd or args.model
    call = (lambda p, s="": call_cmd(p, args.cmd, s)) if args.cmd else (lambda p, s="": call_api(p, args.model, s))

    def run(job):
        row, stage, rep = job
        r = {"row": row, "stage": stage, "rep": rep, "used": None, "out": "", "code": [], "judge": [], "fixes": 0}
        try:
            system = SYSTEM.format(skill=skill) if stage != "none" else ""
            r["used"], r["out"] = strip_marker(call(row["prompt"], system))
            if stage == "none":
                r["used"] = None
            # Skill+check: the script checks the answer, the model fixes what it finds (at most twice).
            while stage == "check" and r["used"] and r["fixes"] < 2:
                findings = run_script(script, r["out"])
                if not findings:
                    break
                r["fixes"] += 1
                _, r["out"] = strip_marker(call(FIX.format(prompt=row["prompt"], answer=r["out"], findings=findings), system))
            if row["should_trigger"]:
                r["code"] = code_check(r["out"], code_rules)
                for q in judges:
                    verdict = call(JUDGE.format(prompt=row["prompt"], answer=r["out"], question=q)).strip().upper()
                    if not verdict.startswith("YES"):
                        r["judge"].append(f"judge: {q}")
        except Exception as e:  # report and keep going; one bad call shouldn't sink the run
            r["error"] = str(e)
        return r

    jobs = [(row, stage, rep) for row in rows for stage in stages for rep in range(args.reps)]
    n_trigger = sum(row["should_trigger"] for row in rows) * len(stages) * args.reps
    print(f"{len(jobs)} runs + {n_trigger * len(judges)} judge calls + script fixes, on {backend} ...", file=sys.stderr)
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(run, jobs))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = args.folder / "runs" / stamp
    outdir.mkdir(parents=True)

    # Score. Rows where the skill should fire: code checks and judge. Stay-off rows: the skill must not fire.
    tally = {s: {"code": [0, 0], "judge": [0, 0], "all": [0, 0], "fired": [0, 0]} for s in stages}
    table = []
    for row in rows:
        line = [row["id"], "on" if row["should_trigger"] else "off"]
        for stage in stages:
            ok = 0
            for r in results:
                if r["row"] is not row or r["stage"] != stage:
                    continue
                t = tally[stage]
                if "error" in r:
                    passed, note = False, "ERROR " + r["error"]
                elif row["should_trigger"]:
                    t["code"][0] += not r["code"]; t["code"][1] += 1
                    if judges:
                        t["judge"][0] += not r["judge"]; t["judge"][1] += 1
                    passed = not r["code"] and not r["judge"]
                    note = "pass" if passed else "FAIL " + "; ".join(r["code"] + r["judge"])
                else:
                    passed = not r["used"]
                    note = "stayed off" if passed else "FIRED (should stay off)"
                if row["should_trigger"]:
                    t["all"][0] += passed; t["all"][1] += 1
                if stage != "none" and r["used"] is not None:
                    t["fired"][0] += r["used"] == row["should_trigger"]; t["fired"][1] += 1
                if r["fixes"]:
                    note += f" (script fixes: {r['fixes']})"
                ok += passed
                (outdir / f"{row['id']}-{LABEL[stage].replace(' ', '-')}-{r['rep'] + 1}.md").write_text(f"{note}\n\n---\n\n{r['out']}\n")
            line.append(f"{ok}/{args.reps}")
        table.append(line)

    frac = lambda p: f"{p[0]}/{p[1]}" if p[1] else "-"
    w = 11
    print(f"\n{args.folder.name}  ·  {backend}  ·  {args.reps} runs per prompt\n")
    print(f"{'prompt':<16}{'skill':<6}" + "".join(f"{LABEL[s]:>{w}}" for s in stages))
    for i, kind, *cells in table:
        print(f"{i:<16}{kind:<6}" + "".join(f"{c:>{w}}" for c in cells))
    print()
    print(f"{'Code checks pass':<22}" + "".join(f"{frac(tally[s]['code']):>{w}}" for s in stages) + "   checked by code: same answer every time")
    if judges:
        print(f"{'Judge says yes':<22}" + "".join(f"{frac(tally[s]['judge']):>{w}}" for s in stages) + "   checked by a model: can be wrong")
    print(f"{'Runs that pass':<22}" + "".join(f"{frac(tally[s]['all']):>{w}}" for s in stages) + "   all checks")
    print(f"{'Skill fired right':<22}" + "".join(f"{frac(tally[s]['fired']):>{w}}" for s in stages) + "   on when it should be, off when not")
    print(f"\nOutputs in {outdir}/")

    sha = hashlib.sha1((skill + (script.read_text() if script.exists() else "")).encode()).hexdigest()[:7]
    with open(args.folder / "results.tsv", "a") as f:
        if f.tell() == 0:
            f.write("time\tskill_sha\tbackend\treps\t" + "\t".join(f"{s}_pass\t{s}_code\t{s}_judge" for s in STAGES) + "\n")
        cols = []
        for s in STAGES:
            t = tally.get(s)
            cols += [frac(t["all"]), frac(t["code"]), frac(t["judge"])] if t else ["-"] * 3
        f.write(f"{stamp}\t{sha}\t{backend}\t{args.reps}\t" + "\t".join(cols) + "\n")


if __name__ == "__main__":
    main()
