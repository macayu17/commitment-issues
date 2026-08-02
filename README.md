# Commitment Issues

A Codex plugin for finding, vetting, implementing, reviewing, publishing, and monitoring open-source contributions.

## Install

Requirements: [Codex CLI](https://developers.openai.com/codex/cli), [GitHub CLI](https://cli.github.com/), and Python 3. Authenticate GitHub once with `gh auth login`.

```powershell
codex plugin marketplace add macayu17/commitment-issues
codex plugin add commit@commitment-issues
```

Start a new Codex thread after installation. Type `$commit`, select
`commitment-issues [Skill]`, then add a route and its arguments:

```text
$commitment-issues cook https://github.com/owner/repo/issues/123
```

Codex plugins do not register their Markdown command files as custom
`/commit:*` slash commands. Use `$commitment-issues`, or run `/skills` and
select the skill.

## Routes

| Route | What it does | Changes state? |
| --- | --- | --- |
| `shop [owner\|owner/repo] [--since <days>] [--limit <count>]` | Finds recent, unassigned issues from maintainers or trusted contributors, then rejects candidates with claims, non-maintainer discussion, duplicates, or competing pull requests. With no arguments it searches repositories you previously contributed to, looks back 7 days, and returns at most 3 matches. | No |
| `vet <issue-url\|owner/repo#number>` | Checks one issue's live state, author relationship, assignees, discussion, linked work, duplicate signals, open pull requests, and repository contribution rules before recommending whether to proceed. | No |
| `cook <issue-url\|owner/repo#number>` | Re-vets the issue, clones the repository when needed, creates an isolated checkout, studies the repository and maintainer style, implements the smallest root-cause fix, and runs focused plus repository-required tests. It stops before any public action. | Local files only |
| `vibe [--full]` | Reviews the current diff for correctness, scope, generated noise, secrets, AI markers, and test evidence. `--full` also runs the broader repository suite. | No |
| `wrap [issue\|pr]` | Produces a review-ready handoff tied to the exact head commit and diff fingerprint. | No |
| `babysit <pr-url\|owner/repo#number> [--once] [--interval <seconds>]` | Reports pull-request checks, reviews, comments, merge state, and new activity. `--once` takes one snapshot; otherwise it keeps watching at the requested interval. | No |
| `send <commit\|push\|pr\|all> [--yes]` | Previews a selected public action. Adding `--yes` authorizes only that action after the reviewed state is rechecked. `commit`, `push`, and `pr` never imply one another; `all --yes` is the only combined authorization. | Only with `--yes` |
| `pulse [owner\|owner/repo]` | Summarizes the current local branch, worktree, issue, pull request, and checks without changing them. | No |

## Typical workflow

Check an issue before investing time:

```text
$commitment-issues vet https://github.com/owner/repo/issues/123
```

Start working immediately when you already intend to proceed. `cook` includes a
fresh vetting pass, so running `vet` first is optional:

```text
$commitment-issues cook https://github.com/owner/repo/issues/123
```

You can attach issue screenshots alongside the command, but include the GitHub
issue URL whenever possible so the skill can inspect live discussion, links,
and repository state.

Other examples:

```text
$commitment-issues shop
$commitment-issues shop open-telemetry --since 14 --limit 5
$commitment-issues vibe --full
$commitment-issues babysit https://github.com/pyenv/pyenv/pull/3498 --once
$commitment-issues send push
$commitment-issues send push --yes
```

The first `send push` only previews the push. The second performs it after
rechecking that the branch, reviewed diff, and handoff still match.

## Develop

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
Push-Location plugins/commit
python -m unittest discover -s tests -v
Pop-Location
```

Licensed under the [MIT License](LICENSE).
