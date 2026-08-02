# Verification, handoff, and public actions

## Verification evidence

Run focused checks that directly exercise the changed production path first. Then run the broader repository-native lint, type, build, and test commands required by repository rules or the requested `--full` scope. Do not substitute a stub, demo path, cached artifact, or unrelated package for the real path.

Record each exact command, exit status, meaningful count, skipped or failing cases, and environment limitation. Distinguish fresh results from prior evidence. Run `git diff --check` when Git is available and inspect the final diff for scope, secrets, generated noise, debug code, AI markers, and unrelated files.

## Review package

`wrap-it-up` is read-only and includes:

- issue or review-feedback target and repository rules consulted;
- current branch, base, exact full head SHA, and worktree status;
- file-by-file diff summary and why each change belongs;
- focused and broader verification commands with exact outcomes;
- residual risks, skipped checks, pre-existing failures, and evidence gaps;
- proposed short commit message, pull-request title, body, and any human follow-up text;
- SHA-256 fingerprint of the exact `git diff` bytes, with the command used to produce it.

Generate the fingerprint without changing the worktree. On a later action, recompute it using the same byte stream and require an exact match.

## Monitoring

Run `scripts/watch_pr.py <pr> --once` for one current snapshot. Without `--once`, default to `--interval 60` and report only meaningful state transitions. Monitoring remains read-only: never comment, review, rerun checks, merge, update metadata, or push.

## Narrow authorization

`send-it` accepts `commit`, `push`, `pr`, or `all`. Without `--yes`, show a preview only. With `--yes`, verify the selected action, target repository and branch, exact head, current diff fingerprint, review package, and absence of unrelated changes immediately before acting.

- `commit --yes` creates only the reviewed local commit.
- `push --yes` pushes only the named, reviewed branch and does not commit first.
- `pr --yes` opens or updates only the reviewed pull request and does not commit or push first.
- `all --yes` authorizes commit, push, and pull-request creation or update in that order, stopping on any mismatch or failure.

Refuse stale evidence, drift, ambiguous targets, detached or unexpected heads, unrelated files, secrets, missing required checks, or a fingerprint mismatch. Approval never covers comments, reviews, merges, check reruns, issue assignment, or other metadata changes.
