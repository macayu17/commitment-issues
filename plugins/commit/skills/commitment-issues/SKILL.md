---
name: commitment-issues
description: Use when Codex is asked to discover current open-source issues, vet contribution viability, implement a minimal source-grounded fix, audit or package a local contribution, monitor a pull request, or perform narrowly approved Git actions.
---

# Commitment Issues

Route open-source contribution work through a source-grounded lifecycle. Keep discovery, review, and monitoring read-only. Treat every commit, push, pull request, comment, review, merge, or metadata change as a separate public action requiring explicit authorization.

## Load the right reference

- Read [discovery.md](references/discovery.md) for candidate search or issue vetting.
- Read [implementation.md](references/implementation.md) before editing code or addressing review feedback.
- Read [verification-and-handoff.md](references/verification-and-handoff.md) for audits, review packages, monitoring, or any proposed public action.

## Source hierarchy

Resolve conflicts in this order:

1. The user's current instruction and action boundary.
2. Repository-local `AGENTS.md`, contribution guides, and documented commands.
3. Live issue, pull-request, timeline, branch, and check state.
4. Current source, tests, callers, and existing helpers.
5. Historical notes and assumptions.

Never let cached or historical state override cheap live verification.

## Command router

| Command | Route | Mutation |
| --- | --- | --- |
| `shop` | Discover recent viable candidates from contributed repositories | Read-only |
| `vet` | Deeply vet one issue with `scripts/vet_issue.py` | Read-only |
| `cook` | Re-vet, implement, and test locally | Local files only |
| `vibe` | Audit diff and checks; `--full` adds the broad suite | Read-only |
| `wrap` | Build the review package and diff fingerprint | Read-only |
| `babysit` | Snapshot or monitor with `scripts/watch_pr.py` | Read-only |
| `send` | Preview or perform exactly one approved action set | Explicit gate |
| `pulse` | Summarize local and remote state | Read-only |

Pass command arguments exactly as received. Do not reinterpret a missing `--yes` as approval.

## Core workflow

1. Establish the repository, target, current branch, worktree state, and applicable rules. For implementation, clone when absent or create a clean issue-specific worktree or dedicated clone from the current upstream base.
2. Refresh live evidence before recommending or editing. Stop on active competing work, unclear ownership, or repository rules that prohibit the contribution mode.
3. Trace the real entrypoint through callers and existing helpers before selecting the change point.
4. Implement the smallest repository-native root-cause fix. Preserve unrelated user changes.
5. Run the smallest meaningful focused check, then every broader repository check required by local rules. Do not declare completion while a required check is unrun or failing.
6. Review the actual diff for scope, generated noise, secrets, AI markers, accidental files, and unsupported claims.
7. Produce a handoff bound to the exact head SHA and SHA-256 fingerprint of the current diff.
8. Leave all public actions unperformed unless `send` receives a matching narrow action plus `--yes`.

## Public-action gate

Preview is the default. Approval for `commit`, `push`, or `pr` authorizes only that named action; the actions never imply one another. `all --yes` is the only shorthand for all three, in order. Recompute state immediately before acting and refuse if the reviewed diff, fingerprint, head, branch, target, or scope has drifted. Never infer authorization for comments, reviews, merges, check reruns, issue assignment, or metadata edits.

## Red flags

- Stale issue state, an assignee or claim, a linked or cross-referenced active pull request, or an unresolved duplicate.
- Repository rules that require prior approval, prohibit autonomous contributions, or cap concurrent work.
- A fix chosen before tracing sibling callers or existing helpers.
- Tests that exercise a stub or alternate path instead of the changed production path.
- Unrelated cleanup, generated churn, secrets, AI markers, or claims unsupported by command output.
- A review package whose SHA, diff fingerprint, or verification evidence no longer matches.

## Common mistakes

- Treating an open issue as available without checking timelines and open pull-request bodies.
- Patching the reported symptom in one caller when a shared root-cause fix is smaller.
- Calling a build success a full verification result.
- Describing tests as passing when they were skipped, stale, or run against another head.
- Treating permission to commit as permission to push or open a pull request.

## Example

For `owner/repo#123`, read repository rules, run `scripts/vet_issue.py owner/repo#123`, manually settle any incomplete duplicate or claim evidence, create an isolated checkout, trace the affected production path and callers, make the minimal local fix, run focused and required broader checks, then generate a review package with the exact head SHA and diff fingerprint. Stop there unless a later `send <action> --yes` matches that package.
