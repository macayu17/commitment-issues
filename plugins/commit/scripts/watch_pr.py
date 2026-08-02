#!/usr/bin/env python3
"""Watch a pull request without mutating GitHub state."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from typing import Any


PR_URL = re.compile(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)(?:[/?#].*)?$")
PR_SHORT = re.compile(r"([^/\s]+)/([^/#\s]+)#(\d+)$")


def parse_pr_ref(value: str) -> tuple[str, str, int]:
    match = PR_URL.fullmatch(value.strip()) or PR_SHORT.fullmatch(value.strip())
    if not match:
        raise ValueError("expected a GitHub pull request URL or owner/repo#number")
    return match.group(1), match.group(2), int(match.group(3))


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


def _flatten_pages(pages: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item for page in pages for item in page]


def _normalise_check(check: dict[str, Any], head_sha: str) -> dict[str, Any]:
    state = (check.get("conclusion") or check.get("state") or check.get("status") or "").upper()
    if state in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
        bucket = "pass"
    elif state in {
        "FAILURE",
        "ERROR",
        "TIMED_OUT",
        "CANCELLED",
        "ACTION_REQUIRED",
        "STALE",
        "STARTUP_FAILURE",
    }:
        bucket = "fail"
    else:
        bucket = "pending"
    return {
        "name": check.get("name") or check.get("context") or check.get("workflowName") or "check",
        "state": state,
        "bucket": check.get("bucket", bucket),
        "headSha": check.get("headSha", head_sha),
        "link": check.get("detailsUrl") or check.get("targetUrl") or check.get("link") or "",
    }


def _normalise_feedback(item: dict[str, Any], kind: str) -> dict[str, Any]:
    author = item.get("author") or item.get("user") or {}
    if isinstance(author, dict):
        author = author.get("login", "")
    return {
        "id": item.get("id"),
        "kind": kind,
        "author": author or "unknown",
        "state": (item.get("state") or "").upper(),
        "body": item.get("body") or "",
        "url": item.get("url") or item.get("html_url") or "",
    }


def make_snapshot(pr: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    head_sha = pr.get("headRefOid", "")
    current_checks = []
    for sequence, check in enumerate(checks):
        if check.get("headSha") and check.get("headSha") != head_sha:
            continue
        normalised = _normalise_check(check, head_sha)
        normalised["identity"] = (
            f"{normalised['name']}\0{normalised['link']}"
            if normalised["link"]
            else f"{normalised['name']}\0{sequence}"
        )
        current_checks.append(normalised)
    return {
        "head_sha": head_sha,
        "state": pr.get("state", "").upper(),
        "mergeable": pr.get("mergeable", ""),
        "merge_state": pr.get("mergeStateStatus", ""),
        "review_decision": pr.get("reviewDecision") or "",
        "comments": [
            _normalise_feedback(item, "comment") for item in pr.get("comments", [])
        ],
        "reviews": [
            _normalise_feedback(item, "review") for item in pr.get("reviews", [])
        ],
        "review_states": [item.get("state", "") for item in pr.get("reviews", [])],
        "review_comments": [
            _normalise_feedback(item, "inline-comment")
            for item in pr.get("reviewComments", [])
        ],
        "checks": current_checks,
    }


def _record_id(item: Any) -> Any:
    return item.get("id") if isinstance(item, dict) else item


def _new_records(before: dict[str, Any], after: dict[str, Any], key: str) -> list[Any]:
    old_ids = {_record_id(item) for item in before[key]}
    return [item for item in after[key] if _record_id(item) not in old_ids]


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    events: list[str] = []
    if before["head_sha"] != after["head_sha"]:
        events.append("head-changed")
    if _new_records(before, after, "comments"):
        events.append("new-comment")
    if _new_records(before, after, "reviews"):
        events.append("new-review")
    if _new_records(before, after, "review_comments"):
        events.append("new-review-comment")
    if (
        after["review_decision"] == "CHANGES_REQUESTED"
        and before["review_decision"] != "CHANGES_REQUESTED"
    ) or (
        "CHANGES_REQUESTED" in after["review_states"]
        and "CHANGES_REQUESTED" not in before["review_states"]
    ):
        events.append("changes-requested")
    if (
        after["mergeable"] == "CONFLICTING" or after["merge_state"] == "DIRTY"
    ) and not (
        before["mergeable"] == "CONFLICTING" or before["merge_state"] == "DIRTY"
    ):
        events.append("merge-conflict")

    before_buckets = {
        item.get("identity", f"{item['name']}\0{sequence}"): item["bucket"]
        for sequence, item in enumerate(before["checks"])
    }
    after_buckets = {
        item.get("identity", f"{item['name']}\0{sequence}"): item["bucket"]
        for sequence, item in enumerate(after["checks"])
    }
    if any(
        bucket == "fail" and before_buckets.get(name) != "fail"
        for name, bucket in after_buckets.items()
    ):
        events.append("check-failed")
    if (
        any(bucket == "pending" for bucket in before_buckets.values())
        and after_buckets
        and all(bucket != "pending" for bucket in after_buckets.values())
    ):
        events.append("checks-finished")

    if after["state"] == "MERGED" and before["state"] != "MERGED":
        events.append("merged")
    elif after["state"] == "CLOSED" and before["state"] != "CLOSED":
        events.append("closed")
    return events


def _print_new_feedback(before: dict[str, Any], after: dict[str, Any]) -> None:
    for key in ("comments", "reviews", "review_comments"):
        for item in _new_records(before, after, key):
            if not isinstance(item, dict):
                continue
            print(f"feedback: {item['kind']} by {item['author']}")
            if item["state"]:
                print(f"state: {item['state']}")
            print(f"body: {item['body'] or '(empty)'}")
            print(f"url: {item['url'] or 'unavailable'}")


def should_stop(snapshot: dict[str, Any]) -> bool:
    buckets = [check["bucket"] for check in snapshot["checks"]]
    return (
        snapshot["state"] in {"MERGED", "CLOSED"}
        or snapshot["mergeable"] == "CONFLICTING"
        or snapshot["merge_state"] == "DIRTY"
        or snapshot["review_decision"] == "CHANGES_REQUESTED"
        or "fail" in buckets
        or bool(buckets) and "pending" not in buckets
    )


def collect_snapshot(owner: str, repo: str, number: int) -> dict[str, Any]:
    pr = _gh_json(
        [
            "pr",
            "view",
            str(number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "number,title,url,state,headRefOid,mergeable,mergeStateStatus,reviewDecision,comments,reviews,statusCheckRollup",
        ]
    )
    review_comment_pages = _gh_json(
        [
            "api",
            "--paginate",
            "--slurp",
            f"repos/{owner}/{repo}/pulls/{number}/comments?per_page=100",
        ]
    )
    pr["reviewComments"] = _flatten_pages(review_comment_pages)
    snapshot = make_snapshot(pr, pr.get("statusCheckRollup", []))
    snapshot.update(
        repository=f"{owner}/{repo}",
        number=number,
        title=pr.get("title", ""),
        url=pr.get("url", ""),
    )
    return snapshot


def _summary(snapshot: dict[str, Any]) -> str:
    counts = {"pass": 0, "fail": 0, "pending": 0}
    for check in snapshot["checks"]:
        counts[check["bucket"]] = counts.get(check["bucket"], 0) + 1
    return (
        f"{snapshot['repository']}#{snapshot['number']} {snapshot['state']}\n"
        f"head: {snapshot['head_sha']}\n"
        f"checks: {counts['pass']} passed, {counts['fail']} failed, "
        f"{counts['pending']} pending\n"
        f"review: {snapshot['review_decision'] or 'none'}; "
        f"merge: {snapshot['mergeable']}/{snapshot['merge_state']}\n"
        f"feedback: {len(snapshot['comments'])} comment(s), "
        f"{len(snapshot['reviews'])} review(s), "
        f"{len(snapshot['review_comments'])} inline comment(s)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args(argv)
    if args.interval < 10:
        parser.error("--interval must be at least 10 seconds")

    try:
        owner, repo, number = parse_pr_ref(args.pr)
        previous = collect_snapshot(owner, repo, number)
        print(_summary(previous), flush=True)
        if args.once or should_stop(previous):
            return 0
        while True:
            time.sleep(args.interval)
            current = collect_snapshot(owner, repo, number)
            events = compare_snapshots(previous, current)
            if events:
                print("events: " + ", ".join(events))
                _print_new_feedback(previous, current)
                print(_summary(current))
                return 0
            previous = current
    except (ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
