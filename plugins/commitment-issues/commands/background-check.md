---
description: Deeply vet one open-source issue for freshness, ownership, claims, duplicates, and competing work.
argument-hint: '<issue-url|owner/repo#number>'
disable-model-invocation: true
---

Use $commitment-issues to run its issue-vetting workflow with the raw `$ARGUMENTS` unchanged. Execute `python "${CLAUDE_PLUGIN_ROOT}/scripts/vet_issue.py" --json $ARGUMENTS` for deterministic evidence, inspect recent comment bodies and associations plus any evidence it cannot settle, and keep the operation read-only.
