import unittest
from unittest.mock import patch

from scripts.find_issues import (
    _search_issues,
    build_parser,
    candidate_is_available,
    contributed_repositories,
    discover,
)


class FindIssuesTests(unittest.TestCase):
    def issue(self, **overrides):
        data = {
            "state": "OPEN",
            "labels": [],
            "assignees": [],
            "linked_prs": [],
            "cross_references": [],
            "pr_mentions": [],
            "commentAuthorAssociations": [],
            "authorAssociation": "MEMBER",
            "evidence_complete": True,
        }
        data.update(overrides)
        return data

    def test_bare_command_defaults_to_seven_days_and_three_results(self):
        args = build_parser().parse_args([])
        self.assertIsNone(args.target)
        self.assertEqual(args.since, 7)
        self.assertEqual(args.limit, 3)

    @patch("scripts.find_issues._gh_json")
    def test_contributed_repositories_are_recent_unique_upstreams(self, gh_json):
        gh_json.side_effect = [
            {"login": "me"},
            [
                {"repository": {"nameWithOwner": "org/one"}},
                {"repository": {"nameWithOwner": "org/one"}},
                {"repository": {"nameWithOwner": "me/fork"}},
                {"repository": {"nameWithOwner": "org/two"}},
            ],
        ]
        self.assertEqual(contributed_repositories(), ["org/one", "org/two"])
        self.assertIn("--visibility", gh_json.call_args_list[1].args[0])
        self.assertIn("public", gh_json.call_args_list[1].args[0])

    def test_allowed_issue_author_associations_include_contributors(self):
        for association in ("OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"):
            with self.subTest(association=association):
                self.assertTrue(candidate_is_available(self.issue(authorAssociation=association)))

    def test_non_maintainer_comment_rejects_candidate(self):
        self.assertFalse(
            candidate_is_available(
                self.issue(commentAuthorAssociations=["MEMBER", "CONTRIBUTOR"])
            )
        )

    def test_needs_design_issue_is_not_available(self):
        self.assertFalse(
            candidate_is_available(self.issue(labels=[{"name": "Needs Design"}]))
        )

    def test_any_pull_request_evidence_rejects_candidate(self):
        for key in ("linked_prs", "cross_references", "pr_mentions"):
            with self.subTest(key=key):
                self.assertFalse(
                    candidate_is_available(
                        self.issue(**{key: [{"number": 9, "state": "CLOSED"}]})
                    )
                )

    @patch("scripts.find_issues.collect_issue")
    @patch("scripts.find_issues._search_issues")
    def test_discovery_respects_limit_after_strict_filtering(self, search, collect):
        search.return_value = [
            {
                "number": number,
                "authorAssociation": "MEMBER",
                "repository": {"nameWithOwner": "org/repo"},
            }
            for number in (1, 2, 3)
        ]
        collect.side_effect = [
            self.issue(number=1, linked_prs=[{"number": 5, "state": "OPEN"}]),
            self.issue(number=2),
            self.issue(number=3),
        ]
        report = discover(None, 7, 1)
        self.assertEqual([item["number"] for item in report["candidates"]], [2])
        self.assertEqual(collect.call_count, 2)

    @patch("scripts.find_issues.contributed_repositories", return_value=["org/repo"])
    @patch("scripts.find_issues._gh_json")
    def test_recent_issues_use_paginated_repo_api_without_search_ceiling(
        self, gh_json, _repos
    ):
        gh_json.return_value = [
            [
                {
                    "number": 1,
                    "html_url": "https://github.com/org/repo/issues/1",
                    "created_at": "2026-08-01T00:00:00Z",
                    "author_association": "MEMBER",
                    "assignees": [],
                }
            ]
        ]
        issues = _search_issues(None, "2026-07-26")
        args = gh_json.call_args.args[0]
        self.assertEqual(len(issues), 1)
        self.assertEqual(args[:3], ["api", "--paginate", "--slurp"])
        self.assertNotIn("--limit", args)


if __name__ == "__main__":
    unittest.main()
