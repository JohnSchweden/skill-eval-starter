---
name: commit-message
description: Writes a git commit message from a short description of a code change.
---
# Commit message

Write one line in Conventional Commits form: `type(scope): summary`.

- type is one of feat, fix, docs, refactor, test, chore
- scope is optional, lowercase, one word
- summary is lowercase, imperative ("add", not "added"), no period at the end
- the whole line is at most 72 characters
- output only the line: no quotes, no code fences, no explanation
