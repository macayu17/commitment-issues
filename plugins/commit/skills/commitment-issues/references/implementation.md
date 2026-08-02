# Local implementation

Re-vet the target before editing. Read all repository-local agent instructions and contribution guidance that apply to every file in scope.

## Isolate the work

Read the issue discussion and repository structure before choosing files to change. Inspect the top-level layout, scoped rule files, contribution guide, manifests, CI configuration, production entrypoints, and test organization.

If the repository is not local, clone the issue's repository into a unique issue-specific directory. If a suitable clone already exists, fetch the current upstream default branch and create a clean issue-specific worktree; use a dedicated clone when a worktree is unsafe or unavailable. Never edit in a dirty or shared checkout. Do not stash, clean, reset, switch branches, or overwrite another task's files to create isolation.

## Trace before changing

1. Locate the runtime or build entrypoint that reaches the reported behavior.
2. Read the implementation fully enough to understand inputs, outputs, state, and error handling.
3. Find every caller of the function or component being changed.
4. Search for existing helpers, types, validation, fixtures, and nearby tests before adding anything.
5. Reproduce the failure or establish a source-backed invariant when reproduction is impractical.
6. Choose the shared root-cause boundary that fixes affected callers without widening behavior unnecessarily.

## Change policy

- Prefer deletion, an existing helper, standard library, native platform behavior, or an installed dependency before new code.
- Match repository naming, structure, error conventions, and test style.
- Keep the diff minimal and limited to the issue. Do not perform unrelated cleanup, formatting churn, dependency additions, speculative abstraction, or scaffolding for future work.
- Preserve user edits and generated-file policy. Never overwrite unrelated dirty state.
- Keep validation, data-loss prevention, security controls, and accessibility requirements intact.
- Add the smallest runnable regression check for non-trivial logic and make it exercise the real production path, not a mock-only or stub path.
- Do not add AI attribution, assistant markers, canned prose, decorative comments, or unexplained generated artifacts.

For pull-request feedback, read the exact current review thread, confirm the remote head and local branch match, classify the request as actionable or already resolved, then implement only the supported local change. Do not reply publicly from `cook`.

After editing, run the focused regression check, the affected package or module suite, and every broader lint, format, type, build, and test command required by repository rules. Do not trade required verification for a deadline. If a required check cannot run or does not pass, keep the task incomplete and report exact evidence; never weaken a test merely to make it pass.

Inspect the whole diff, not only changed hunks. Confirm the code matches maintainer style and contains no AI slop, speculative abstraction, unrelated cleanup, dependency churn, debug residue, or generated noise. Separate pre-existing failures from regressions with evidence.
