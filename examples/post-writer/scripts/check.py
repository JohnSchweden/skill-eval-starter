#!/usr/bin/env python3
"""The post-writer's deterministic part: checks a post on stdin, prints findings, exit 1 if any.

Everything a rule can decide lives here, so the model doesn't have to remember it.
What a rule can't decide (is the first line a verdict? are the facts real?) stays in SKILL.md.
"""
import re
import sys

BUZZWORDS = r"\b(game[- ]changer|leverag\w*|unlock\w*|revolutioni[sz]\w*|synerg\w*|landscape|journey|delv\w*)\b"

text = sys.stdin.read().strip()
last = text.splitlines()[-1].strip() if text else ""
findings = []
words = len(text.split())
if words > 120:
    findings.append(f"{words} words: cut to at most 120")
if re.search(r"[—–]", text):
    findings.append("em or en dash: replace with a period or a comma")
if re.search(r"(^|\s)#\w", text):
    findings.append("hashtag: remove all hashtags")
if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", text):
    findings.append("emoji: remove all emojis")
for m in re.finditer(BUZZWORDS, text, re.IGNORECASE):
    findings.append(f'buzzword "{m.group(0)}": use a plain word')
if last.endswith("?"):
    findings.append(f'closes with a question ("{last[:60]}"): end on a statement')
print("\n".join(f"- {f}" for f in findings))
sys.exit(1 if findings else 0)
