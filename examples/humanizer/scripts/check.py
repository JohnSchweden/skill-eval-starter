#!/usr/bin/env python3
"""The humanizer's deterministic part: checks a rewrite on stdin, prints findings, exit 1 if any.

Everything a rule can decide lives here, so the model doesn't have to remember it.
What a rule can't decide (is the meaning kept? does it sound human?) stays in SKILL.md.
"""
import re
import sys

AI_WORDS = (r"\b(testament|showcas\w*|underscor\w*|pivotal|crucial|delv\w*|tapestry|vibrant|seamless\w*|"
            r"robust|landscape|foster\w*|additionally|furthermore)\b")
PHRASES = r"(?i)(in today's fast-paced world|in conclusion|it's worth noting|it is worth noting|^overall,|the future (is|looks) bright|not only\b.*\bbut also)"

text = sys.stdin.read().strip()
findings = []
for m in re.finditer(AI_WORDS, text, re.IGNORECASE):
    findings.append(f'AI word "{m.group(0)}": use a plain word')
for m in re.finditer(PHRASES, text, re.MULTILINE):
    findings.append(f'AI phrase "{m.group(0)[:40]}": cut or rephrase')
if re.search(r"[—–]", text):
    findings.append("em or en dash: replace with a period or a comma")
if re.search(r"(?im)^(changes|notes?|what i changed)\b", text):
    findings.append("a notes or changes section: output only the rewrite")
print("\n".join(f"- {f}" for f in findings))
sys.exit(1 if findings else 0)
