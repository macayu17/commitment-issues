#!/usr/bin/env python3
"""Collect read-only GitHub evidence about whether an issue is available."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any


ISSUE_URL = re.compile(
    r"https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)(?:[/?#].*)?$"
)
ISSUE_SHORT = re.compile(r"([^/\s]+)/([^/#\s]+)#(\d+)$")


def parse_issue_ref(value: str) -> tuple[str, str, int]:
    match = ISSUE_URL.fullmatch(value.strip()) or ISSUE_SHORT.fullmatch(value.strip())
    if not match:
        raise ValueError("expected a GitHub issue URL or owner/repo#number")
    return match.group(1), match.group(2), int(match.group(3))


def _active_prs(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in items if item.get("state", "").upper() == "OPEN"]


def classify_issue(issue: dict[str, Any]) -> dict[str, Any]:
    blocked: list[str] = []
    review: list[str] = []

    if issue.get("state", "").upper() != "OPEN":
        blocked.append("issue is not open")
    if active := _active_prs(issue.get("linked_prs", [])):
        blocked.append(f"{len(active)} active closing pull request(s)")

    if not issue.get("evidence_complete", False):
        review.append("evidence collection was incomplete")
    if issue.get("assignees"):
        review.append("issue is assigned")
    if active := _active_prs(issue.get("cross_references", [])):
        review.append(f"{len(active)} active timeline pull request reference(s)")
    if active := _active_prs(issue.get("pr_mentions", [])):
        review.append(f"{len(active)} open pull request body mention(s)")

    labels = {
        label.get("name", "").casefold()
        for label in issue.get("labels", [])
        if isinstance(label, dict)
    }
    uncertain = labels.intersection({"needs triage", "discussion", "design"})
    if uncertain:
        review.append("triage/design label: " + ", ".join(sorted(uncertain)))

    if blocked:
        return {"status": "blocked", "reasons": blocked + review}
    if review:
        return {"status": "needs-review", "reasons": review}
    return {
        "status": "no-hard-blocker-detected",
        "reasons": ["manual duplicate and claim review is still required"],
    }


def exit_code(status: str) -> int:
    return {"no-hard-blocker-detected": 0, "blocked": 2, "needs-review": 3}.get(
        status, 1
    )


def _gh_json(args: list[str]) -> Any:
    try:
        process = subprocess.run(
            ["gh", *args], capture_output=True, text=True, encoding="utf-8"
        )
    except OSError as error:
        raise RuntimeError(f"unable to run gh: {error}") from error
    if process.returncode:
        message = process.stderr.strip() or process.stdout.strip() or "gh failed"
        raise RuntimeError(message)
    return json.loads(process.stdout or "null")


def flatten_pages(pages: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item for page in pages for item in page]


def _pr_from_issue(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": item.get("number"),
        "state": item.get("state", ""),
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "isDraft": item.get("isDraft", False),
    }


def collect_issue(owner: str, repo: str, number: int) -> dict[str, Any]:
    evidence_complete = True
    issue = _gh_json(["api", f"repos/{owner}/{repo}/issues/{number}"])

    linked: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    mentions: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []

    try:
        view = _gh_json(
            [
                "issue",
                "view",
                str(number),
                "--repo",
                f"{owner}/{repo}",
                "--json",
                "closedByPullRequestsReferences",
            ]
        )
        linked = [
            _pr_from_issue(item)
            for item in view.get("closedByPullRequestsReferences", [])
        ]
    except (RuntimeError, json.JSONDecodeError):
        evidence_complete = False

    try:
        event_pages = _gh_json(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{owner}/{repo}/issues/{number}/timeline?per_page=100",
            ]
        )
        events = flatten_pages(event_pages)
        for event in events or []:
            source = event.get("source", {}).get("issue", {})
            if event.get("event") == "cross-referenced" and source.get("pull_request"):
                timeline.append(
                    {
                        "number": source.get("number"),
                        "state": source.get("state", ""),
                        "title": source.get("title", ""),
                        "url": source.get("html_url", ""),
                    }
                )
    except (RuntimeError, json.JSONDecodeError):
        evidence_complete = False

    try:
        search = _gh_json(
            [
                "api",
                "-X",
                "GET",
                "search/issues",
                "-f",
                f"q=repo:{owner}/{repo} is:pr is:open {number} in:body",
            ]
        )
        mentions = [
            {
                "number": item.get("number"),
                "state": item.get("state", ""),
                "title": item.get("title", ""),
                "url": item.get("html_url", ""),
            }
            for item in search.get("items", [])
        ]
    except (RuntimeError, json.JSONDecodeError):
        evidence_complete = False

    try:
        comment_pages = _gh_json(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{owner}/{repo}/issues/{number}/comments?per_page=100",
            ]
        )
        raw_comments = flatten_pages(comment_pages)
        comments = [
            {
                "author": item.get("user", {}).get("login", ""),
                "authorAssociation": item.get("author_association", ""),
                "createdAt": item.get("created_at", ""),
                "body": item.get("body", ""),
            }
            for item in (raw_comments or [])[-20:]
        ]
    except (RuntimeError, json.JSONDecodeError):
        evidence_complete = False

    labels = [
        {"name": item.get("name", "")}
        for item in issue.get("labels", [])
        if isinstance(item, dict)
    ]
    return {
        "repository": f"{owner}/{repo}",
        "number": number,
        "title": issue.get("title", ""),
        "url": issue.get("html_url", ""),
        "state": issue.get("state", "").upper(),
        "author": issue.get("user", {}).get("login", ""),
        "authorAssociation": issue.get("author_association", ""),
        "createdAt": issue.get("created_at", ""),
        "updatedAt": issue.get("updated_at", ""),
        "labels": labels,
        "assignees": [
            {"login": item.get("login", "")} for item in issue.get("assignees", [])
        ],
        "linked_prs": linked,
        "cross_references": timeline,
        "pr_mentions": mentions,
        "recent_comments": comments,
        "evidence_complete": evidence_complete,
    }


def _print_human(issue: dict[str, Any], result: dict[str, Any]) -> None:
    print(f"{issue['repository']}#{issue['number']}: {issue['title']}")
    print(f"status: {result['status']}")
    print(f"author association: {issue.get('authorAssociation') or 'unknown'}")
    for reason in result["reasons"]:
        print(f"- {reason}")
    print(
        "evidence: "
        f"{len(issue['assignees'])} assignee(s), "
        f"{len(issue['linked_prs'])} closing PR(s), "
        f"{len(issue['cross_references'])} timeline PR reference(s), "
        f"{len(issue['pr_mentions'])} open PR body mention(s), "
        f"{len(issue['recent_comments'])} recent comment(s)"
    )
    for comment in issue["recent_comments"][-3:]:
        body = " ".join(comment.get("body", "").split())
        if len(body) > 160:
            body = body[:157] + "..."
        print(
            f"- {comment.get('author') or 'unknown'} "
            f"({comment.get('authorAssociation') or 'unknown'}): {body or '(empty)'}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("issue")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        owner, repo, number = parse_issue_ref(args.issue)
        issue = collect_issue(owner, repo, number)
        result = classify_issue(issue)
    except (ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    report = {**issue, "classification": result}
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_human(issue, result)
    return exit_code(result["status"])


if __name__ == "__main__":
    raise SystemExit(main())
