---
description: Implement a vetted issue or address pull-request feedback locally, with repository-native tests.
argument-hint: '[issue|pr]'
disable-model-invocation: true
---

Use $commitment-issues with the raw `$ARGUMENTS` unchanged, plus any attached issue images. Re-vet the live target before editing. If the repository is absent, clone it; otherwise create a clean isolated worktree or dedicated clone from the current upstream default branch. Never work in a dirty or shared checkout.

Study the issue discussion, repository structure, applicable rules, contribution guide, CI, production entrypoints, callers, existing helpers, and nearby tests. Reproduce the problem, then make the smallest root-cause fix in maintainer style. Add the smallest real regression test. Allow no AI slop, junk, speculative abstraction, unrelated cleanup, dependency churn, decorative comments, or generated noise.

Run focused tests followed by every repository-required check. Remain incomplete while any required check is unrun or failing; report genuine environment blockers and pre-existing failures without weakening tests. Inspect the complete diff and worktree before handing back the local changes. Do not commit, push, comment, or open or update a pull request. Do not claim or assign the issue.
