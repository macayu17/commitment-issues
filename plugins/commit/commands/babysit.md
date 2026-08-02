---
description: Watch pull-request state and report meaningful changes without mutating GitHub.
argument-hint: '<pr-url|owner/repo#number> [--once] [--interval <seconds>]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged and run `python "${CLAUDE_PLUGIN_ROOT}/scripts/watch_pr.py" $ARGUMENTS`. `--once` returns one read-only snapshot; otherwise monitor state with a default 60-second interval. Never comment, review, rerun checks, merge, or otherwise mutate GitHub.
