---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

can you make me a tracker for this one, so i know whats left

LAB.2
Build a link shortener that never loses a link
faded
proves implement
Write the store behind the shortener and the checks that prove it: every code maps to one URL, a deleted code is never reused, expired links return 410, and each visit is counted once. Then load it at 10, 100 and 1000 links, checking the counts at each step.

repo: phase2-web/02-link-shortener
~60 min · ~2 h first pass
solution notes

the code is in labs/link-shortener in my repo

Input files: labs/link-shortener/src/store.py, labs/link-shortener/src/checks.py, labs/link-shortener/src/load.py, labs/link-shortener/tests/test_checks.py
