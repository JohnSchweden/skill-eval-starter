---
name: humanizer
description: Rewrites text that sounds AI-generated so it reads like a person wrote it, keeping the meaning.
---
# Humanizer

Rewrite the user's text so it sounds like a person wrote it.

- Keep every fact: numbers, names, events. Add nothing.
- Cut empty claims that say nothing checkable: "the future is bright", "nothing short of transformative".
- Prefer short sentences and plain verbs. Keep the length about the same or shorter.
- Output only the rewritten text. No notes, no list of changes.

AI words, stock phrases and dashes are checked by `scripts/check.py`.
