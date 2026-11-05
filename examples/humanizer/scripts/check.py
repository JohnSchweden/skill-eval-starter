#!/usr/bin/env python3
"""The humanizer's deterministic part: checks a rewrite on stdin, prints findings, exit 1 if any.

The request comes in as the first argument, so the script can spot numbers and names the original doesn't have.
Everything a rule can decide lives here, and only here, so SKILL.md doesn't repeat it.
What a rule can't decide (is the meaning kept? does it sound human?) stays in SKILL.md.
"""
import re
import sys

def new_facts(text, request):
    """Numbers and names in the answer that the request doesn't contain: likely made up."""
    known = request.lower()
    found = [n for n in re.findall(r"\d+(?:[.,:]\d+)?", text) if n not in known]
    for sentence in re.split(r"[.!?:\n]+", text):
        for word in re.findall(r"[A-Za-z][\w'-]*", sentence)[1:]:  # skip the first word: capital anyway
            if word[0].isupper() and word not in ("I", "I'm", "I've", "I'd", "I'll") and word.lower() not in known:
                found.append(word)
    return list(dict.fromkeys(found))


AI_WORDS = (r"\b(testament|showcas\w*|underscor\w*|pivotal|crucial|delv\w*|tapestry|vibrant|seamless\w*|"
            r"robust|landscape|foster\w*|additionally|furthermore)\b")
PHRASES = r"(?i)(in today's fast-paced world|in conclusion|it's worth noting|it is worth noting|^overall,|the future (is|looks) bright|not only\b.*\bbut also|\b(isn't|is not|it's not|it is not) (just|only)\b)"

text = sys.stdin.read().strip()
request = sys.argv[1] if len(sys.argv) > 1 else ""
findings = []
for m in re.finditer(AI_WORDS, text, re.IGNORECASE):
    findings.append(f'AI word "{m.group(0)}": use a plain word')
for m in re.finditer(PHRASES, text, re.MULTILINE):
    findings.append(f'AI phrase "{m.group(0)[:40]}": cut or rephrase')
if re.search(r"[—–]", text):
    findings.append("em or en dash: replace with a period or a comma")
if re.search(r"(?im)^(changes|notes?|what i changed)\b", text):
    findings.append("a notes or changes section: output only the rewrite")
for f in new_facts(text, request):
    findings.append(f'"{f}" is not in the request: remove it or use only what the request says')
print("\n".join(f"- {f}" for f in findings))
sys.exit(1 if findings else 0)
