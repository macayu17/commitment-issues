---
description: Implement a vetted issue or address pull-request feedback locally, with repository-native tests.
argument-hint: '[issue|pr]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged. Re-vet the target, read repository rules, trace source entrypoints, callers, and existing helpers, then make the smallest root-cause fix and test it locally. For pull-request feedback, verify the current thread and head before editing. Do not commit, push, comment, or open or update a pull request.
