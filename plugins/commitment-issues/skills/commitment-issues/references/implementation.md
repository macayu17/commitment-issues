# Local implementation

Re-vet the target before editing. Read all repository-local agent instructions and contribution guidance that apply to every file in scope.

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

After editing, inspect the whole diff, not only changed hunks. Separate pre-existing failures from regressions with evidence and never weaken a test merely to make it pass.
