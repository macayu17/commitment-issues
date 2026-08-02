# Commitment Issues

A Codex plugin for finding, vetting, implementing, reviewing, publishing, and monitoring open-source contributions.

## Install

Requirements: [Codex CLI](https://developers.openai.com/codex/cli), [GitHub CLI](https://cli.github.com/), and Python 3. Authenticate GitHub once with `gh auth login`.

```powershell
codex plugin marketplace add macayu17/commitment-issues
codex plugin add commit@commitment-issues
```

Start a new Codex thread after installation.

## Commands

```text
/commit:shop [owner|owner/repo] [--since <days>] [--limit <count>]
/commit:vet <issue-url|owner/repo#number>
/commit:cook [issue|pr]
/commit:vibe [--full]
/commit:wrap [issue|pr]
/commit:babysit <pr-url|owner/repo#number> [--once] [--interval <seconds>]
/commit:send <commit|push|pr|all> [--yes]
/commit:pulse [owner|owner/repo]
```

`shop`, `vet`, `vibe`, `wrap`, `babysit`, and `pulse` are read-only. `cook` may edit local files but performs no public action. `send` previews public actions unless the selected action includes `--yes`.

Examples:

```text
/commit:shop open-telemetry --since 14
/commit:vet open-telemetry/opentelemetry-kotlin#720
/commit:babysit https://github.com/pyenv/pyenv/pull/3498 --once
/commit:send push --yes
```

Bare `/commit:shop` searches public upstream repositories from your 1,000 most recently updated authored pull requests, defaults to issues created within 7 days, and returns at most 3 strict matches. Use `--since` or `--limit` only when you want different bounds.

## Develop

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
Push-Location plugins/commit
python -m unittest discover -s tests -v
Pop-Location
```

Licensed under the [MIT License](LICENSE).
