# Commitment Issues

A Codex plugin for finding, vetting, implementing, reviewing, publishing, and monitoring open-source contributions.

## Install

Requirements: [Codex CLI](https://developers.openai.com/codex/cli), [GitHub CLI](https://cli.github.com/), and Python 3. Authenticate GitHub once with `gh auth login`.

```powershell
codex plugin marketplace add macayu17/commitment-issues
codex plugin add commitment-issues@commitment-issues
```

Start a new Codex thread after installation.

## Commands

```text
/commitment-issues:window-shop [owner|owner/repo] [--since <days>]
/commitment-issues:background-check <issue-url|owner/repo#number>
/commitment-issues:cook [issue|pr]
/commitment-issues:vibe-check [--full]
/commitment-issues:wrap-it-up [issue|pr]
/commitment-issues:babysit <pr-url|owner/repo#number> [--once] [--interval <seconds>]
/commitment-issues:send-it <commit|push|pr|all> [--yes]
/commitment-issues:pulse-check [owner|owner/repo]
```

`window-shop`, `background-check`, `vibe-check`, `wrap-it-up`, `babysit`, and `pulse-check` are read-only. `cook` may edit local files but performs no public action. `send-it` previews public actions unless the selected action includes `--yes`.

Examples:

```text
/commitment-issues:window-shop open-telemetry --since 14
/commitment-issues:background-check open-telemetry/opentelemetry-kotlin#720
/commitment-issues:babysit https://github.com/pyenv/pyenv/pull/3498 --once
/commitment-issues:send-it push --yes
```

## Develop

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
Push-Location plugins/commitment-issues
python -m unittest discover -s tests -v
Pop-Location
```

Licensed under the [MIT License](LICENSE).
