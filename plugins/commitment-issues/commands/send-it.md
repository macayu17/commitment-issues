---
description: Preview or narrowly authorize selected commit, push, and pull-request actions.
argument-hint: '<commit|push|pr|all> [--yes]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged. Without `--yes`, preview the selected action only. With `--yes`, authorize only the selected action after matching the review package, diff fingerprint, exact head, branch, and scope. Refuse drift, stale evidence, ambiguous intent, or unrelated changes. `commit`, `push`, and `pr` never imply one another; only `all --yes` authorizes all three in order.
