---
description: Find recent, viable open-source issues without changing local or remote state.
argument-hint: '[owner|owner/repo] [--since <days>] [--limit <count>]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged and run `python "${CLAUDE_PLUGIN_ROOT}/scripts/find_issues.py" $ARGUMENTS`. With no arguments, it defaults to contributed repositories discovered from the authenticated user's pull-request history, issues from the last 7 days, and at most 3 results. Accept optional `--since` and `--limit` overrides.

Return only unassigned issues authored by an `OWNER`, `MEMBER`, `COLLABORATOR`, or `CONTRIBUTOR`, with maintainer-only comments and no linked, closing, cross-referenced, or open pull-request-body evidence. Before recommending each helper result, manually inspect maintainer comments for claims or reservations and search open pull-request titles and bodies for its URL, number, distinctive error or feature wording, and likely duplicate phrasing. Keep the entire operation read-only.
