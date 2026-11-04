#!/usr/bin/env python3
"""Optional: your skill's deterministic part, enforced on every answer. Delete this folder to test the skill text only.

Reads the answer on stdin. Prints one "- finding" line per problem and exits 1 if there are any;
eval.py hands the findings back to the model to fix (at most twice).
Put here only what code can decide for sure: length, banned words, a required format.
"""
import re
import sys

text = sys.stdin.read().strip()
findings = []
if len(text.split()) > 200:
    findings.append(f"{len(text.split())} words: cut to at most 200")
if re.search(r"[—–]", text):
    findings.append("em or en dash: replace with a period or a comma")
print("\n".join(f"- {f}" for f in findings))
sys.exit(1 if findings else 0)
