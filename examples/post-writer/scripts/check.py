#!/usr/bin/env python3
"""The post-writer's deterministic part: checks a post on stdin, prints findings, exit 1 if any.

The request comes in as the first argument, so the script can spot numbers and names the notes don't have.
Everything a rule can decide lives here, and only here, so SKILL.md doesn't repeat it.
What a rule can't decide (is the first line a verdict? is an added sentence a made-up event?) stays in SKILL.md.
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


BUZZWORDS = r"\b(game[- ]changer|leverag\w*|unlock\w*|revolutioni[sz]\w*|synerg\w*|landscape|journey|delv\w*)\b"

text = sys.stdin.read().strip()
request = sys.argv[1] if len(sys.argv) > 1 else ""
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
for f in new_facts(text, request):
    findings.append(f'"{f}" is not in the request: remove it or use only what the request says')
print("\n".join(f"- {f}" for f in findings))
sys.exit(1 if findings else 0)
