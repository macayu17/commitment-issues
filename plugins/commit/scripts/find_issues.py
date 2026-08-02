#!/usr/bin/env python3
"""Find recent, unclaimed GitHub issues with no competing pull request."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import sys
from typing import Any

try:
    from scripts.vet_issue import _gh_json, classify_issue, collect_issue, flatten_pages
except ModuleNotFoundError:  # Direct execution from the plugin's scripts directory.
    from vet_issue import _gh_json, classify_issue, collect_issue, flatten_pages


DEFAULT_DAYS = 7
DEFAULT_LIMIT = 3
ISSUE_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"}
MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", help="owner or owner/repo")
    parser.add_argument("--since", type=positive_int, default=DEFAULT_DAYS)
    parser.add_argument("--limit", type=positive_int, default=DEFAULT_LIMIT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def contributed_repositories() -> list[str]:
    viewer = str(_gh_json(["api", "user"]).get("login", "")).casefold()
    pull_requests = _gh_json(
        [
            "search",
            "prs",
            "--author",
            "@me",
            "--visibility",
            "public",
            "--limit",
            "1000",
            "--sort",
            "updated",
            "--order",
            "desc",
            "--json",
            "repository",
        ]
    )
    repositories: list[str] = []
    seen: set[str] = set()
    for pull_request in pull_requests:
        name = pull_request.get("repository", {}).get("nameWithOwner", "")
        if not name or name.casefold() in seen:
            continue
        if name.split("/", 1)[0].casefold() == viewer:
            continue
        seen.add(name.casefold())
        repositories.append(name)
    return repositories


def _search_issues(target: str | None, cutoff: str) -> list[dict[str, Any]]:
    if target and "/" in target:
        view = _gh_json(["repo", "view", target, "--json", "visibility"])
        if view.get("visibility", "").upper() != "PUBLIC":
            raise RuntimeError(f"repository is not public: {target}")
        repositories = [target]
    elif target:
        repositories = [
            item["nameWithOwner"]
            for item in _gh_json(
                [
                    "repo",
                    "list",
                    target,
                    "--limit",
                    "1000",
                    "--source",
                    "--no-archived",
                    "--visibility",
                    "public",
                    "--json",
                    "nameWithOwner",
                ]
            )
        ]
    else:
        repositories = contributed_repositories()

    def fetch(repository: str) -> list[dict[str, Any]]:
        pages = _gh_json(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{repository}/issues?state=open&since={cutoff}T00:00:00Z&per_page=100",
            ]
        )
        candidates: list[dict[str, Any]] = []
        for item in flatten_pages(pages):
            if item.get("pull_request") or item.get("created_at", "")[:10] < cutoff:
                continue
            candidates.append(
                {
                    "number": item.get("number"),
                    "url": item.get("html_url", ""),
                    "repository": {"nameWithOwner": repository},
                    "authorAssociation": item.get("author_association", ""),
                    "assignees": item.get("assignees", []),
                    "createdAt": item.get("created_at", ""),
                }
            )
        return candidates

    candidates: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(8, len(repositories) or 1)) as executor:
        for repository_issues in executor.map(fetch, repositories):
            candidates.extend(repository_issues)

    unique = {item.get("url"): item for item in candidates if item.get("url")}
    return sorted(unique.values(), key=lambda item: item.get("createdAt", ""), reverse=True)


def candidate_is_available(issue: dict[str, Any]) -> bool:
    if issue.get("authorAssociation", "").upper() not in ISSUE_ASSOCIATIONS:
        return False
    if classify_issue(issue)["status"] != "no-hard-blocker-detected":
        return False
    if any(issue.get(key) for key in ("linked_prs", "cross_references", "pr_mentions")):
        return False
    return all(
        association.upper() in MAINTAINER_ASSOCIATIONS
        for association in issue.get("commentAuthorAssociations", [])
    )


def discover(target: str | None, days: int, limit: int) -> dict[str, Any]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    matches: list[dict[str, Any]] = []
    for candidate in _search_issues(target, cutoff):
        if candidate.get("authorAssociation", "").upper() not in ISSUE_ASSOCIATIONS:
            continue
        repository = candidate["repository"]["nameWithOwner"]
        owner, repo = repository.split("/", 1)
        issue = collect_issue(owner, repo, int(candidate["number"]))
        if candidate_is_available(issue):
            matches.append(issue)
            if len(matches) == limit:
                break
    return {
        "target": target or "previously-contributed repositories",
        "sinceDays": days,
        "limit": limit,
        "candidates": matches,
    }


def _print_human(report: dict[str, Any]) -> None:
    print(
        f"scope: {report['target']}; last {report['sinceDays']} day(s); "
        f"max {report['limit']} result(s)"
    )
    if not report["candidates"]:
        print("no matching issues found")
        return
    for issue in report["candidates"]:
        print(
            f"{issue['repository']}#{issue['number']} "
            f"[{issue['authorAssociation']}]: {issue['title']}"
        )
        print(issue["url"])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = discover(args.target, args.since, args.limit)
    except (KeyError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
