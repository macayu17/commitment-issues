import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from scripts.vet_issue import (
    _print_human,
    classify_issue,
    exit_code,
    flatten_pages,
    main,
    parse_issue_ref,
)


class ParseIssueRefTests(unittest.TestCase):
    def test_parses_shorthand(self):
        self.assertEqual(
            parse_issue_ref("open-telemetry/opentelemetry-go#123"),
            ("open-telemetry", "opentelemetry-go", 123),
        )

    def test_parses_github_url(self):
        self.assertEqual(
            parse_issue_ref("https://github.com/owner/repo/issues/42"),
            ("owner", "repo", 42),
        )

    def test_rejects_unknown_input(self):
        with self.assertRaises(ValueError):
            parse_issue_ref("repo#42")

    def test_flattens_paginated_api_arrays(self):
        self.assertEqual(flatten_pages([[{"id": 1}], [{"id": 2}]]), [{"id": 1}, {"id": 2}])

    def test_missing_gh_returns_invocation_error(self):
        with (
            patch("scripts.vet_issue.subprocess.run", side_effect=FileNotFoundError("gh")),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(main(["owner/repo#1"]), 1)


class ClassifyIssueTests(unittest.TestCase):
    def issue(self, **overrides):
        data = {
            "state": "OPEN",
            "labels": [],
            "assignees": [],
            "linked_prs": [],
            "cross_references": [],
            "pr_mentions": [],
            "evidence_complete": True,
        }
        data.update(overrides)
        return data

    def test_closed_issue_is_blocked(self):
        result = classify_issue(self.issue(state="CLOSED"))
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(exit_code(result["status"]), 2)

    def test_active_closing_pr_is_blocked(self):
        result = classify_issue(
            self.issue(linked_prs=[{"number": 9, "state": "OPEN"}])
        )
        self.assertEqual(result["status"], "blocked")

    def test_cross_reference_requires_review(self):
        result = classify_issue(
            self.issue(cross_references=[{"number": 8, "state": "OPEN"}])
        )
        self.assertEqual(result["status"], "needs-review")
        self.assertEqual(exit_code(result["status"]), 3)

    def test_assignment_requires_review(self):
        result = classify_issue(self.issue(assignees=[{"login": "someone"}]))
        self.assertEqual(result["status"], "needs-review")

    def test_incomplete_evidence_never_looks_clear(self):
        result = classify_issue(self.issue(evidence_complete=False))
        self.assertEqual(result["status"], "needs-review")

    def test_clear_means_only_no_hard_blocker_detected(self):
        result = classify_issue(self.issue())
        self.assertEqual(result["status"], "no-hard-blocker-detected")
        self.assertEqual(exit_code(result["status"]), 0)

    def test_human_output_includes_concise_recent_comment_context(self):
        issue = {
            "repository": "owner/repo",
            "number": 1,
            "title": "Issue",
            "authorAssociation": "NONE",
            "assignees": [],
            "linked_prs": [],
            "cross_references": [],
            "pr_mentions": [],
            "recent_comments": [
                {
                    "author": "maintainer",
                    "authorAssociation": "MEMBER",
                    "body": "  This is claimed.  Please coordinate.  ",
                }
            ],
        }
        output = io.StringIO()
        with patch("sys.stdout", output):
            _print_human(issue, {"status": "needs-review", "reasons": []})
        self.assertIn(
            "maintainer (MEMBER): This is claimed. Please coordinate.",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
