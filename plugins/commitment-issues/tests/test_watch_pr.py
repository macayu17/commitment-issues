import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from scripts.watch_pr import compare_snapshots, main, make_snapshot, parse_pr_ref, should_stop


class WatchPrTests(unittest.TestCase):
    def test_parses_pull_request_references(self):
        self.assertEqual(parse_pr_ref("owner/repo#7"), ("owner", "repo", 7))
        self.assertEqual(
            parse_pr_ref("https://github.com/owner/repo/pull/7"),
            ("owner", "repo", 7),
        )

    def test_missing_gh_returns_invocation_error(self):
        with (
            patch("scripts.watch_pr.subprocess.run", side_effect=FileNotFoundError("gh")),
            redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(main(["owner/repo#1", "--once"]), 1)

    def snapshot(self, **overrides):
        pr = {
            "headRefOid": "new-sha",
            "state": "OPEN",
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "",
            "comments": [{"id": "c1"}],
            "reviews": [],
            "reviewComments": [],
        }
        pr.update(overrides)
        checks = [
            {
                "name": "tests",
                "state": "PENDING",
                "bucket": "pending",
                "headSha": "new-sha",
            },
            {
                "name": "old tests",
                "state": "FAILURE",
                "bucket": "fail",
                "headSha": "old-sha",
            },
        ]
        return make_snapshot(pr, checks)

    def test_ignores_checks_from_old_head(self):
        snapshot = self.snapshot()
        self.assertEqual([check["name"] for check in snapshot["checks"]], ["tests"])

    def test_reports_checks_finishing(self):
        before = self.snapshot()
        after = self.snapshot()
        after["checks"][0].update(state="SUCCESS", bucket="pass")
        self.assertIn("checks-finished", compare_snapshots(before, after))

    def test_reports_failed_current_check(self):
        before = self.snapshot()
        after = self.snapshot()
        after["checks"][0].update(state="FAILURE", bucket="fail")
        self.assertIn("check-failed", compare_snapshots(before, after))

    def test_duplicate_check_names_do_not_hide_new_failure(self):
        pr = {
            "headRefOid": "sha",
            "state": "OPEN",
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
            "comments": [],
            "reviews": [],
            "reviewComments": [],
        }
        before = make_snapshot(
            pr,
            [
                {"name": "tests", "conclusion": "SUCCESS", "detailsUrl": "one"},
                {"name": "tests", "conclusion": "FAILURE", "detailsUrl": "two"},
            ],
        )
        after = make_snapshot(
            pr,
            [
                {"name": "tests", "conclusion": "FAILURE", "detailsUrl": "one"},
                {"name": "tests", "conclusion": "FAILURE", "detailsUrl": "two"},
            ],
        )
        self.assertIn("check-failed", compare_snapshots(before, after))

    def test_github_check_conclusions_use_terminal_buckets(self):
        expected = {
            "SUCCESS": "pass",
            "NEUTRAL": "pass",
            "SKIPPED": "pass",
            "FAILURE": "fail",
            "TIMED_OUT": "fail",
            "CANCELLED": "fail",
            "ACTION_REQUIRED": "fail",
            "STALE": "fail",
            "STARTUP_FAILURE": "fail",
        }
        pr = {
            "headRefOid": "sha",
            "state": "OPEN",
            "comments": [],
            "reviews": [],
            "reviewComments": [],
        }
        for conclusion, bucket in expected.items():
            with self.subTest(conclusion=conclusion):
                snapshot = make_snapshot(
                    pr, [{"name": conclusion, "conclusion": conclusion}]
                )
                self.assertEqual(snapshot["checks"][0]["bucket"], bucket)

    def test_reports_new_feedback(self):
        before = self.snapshot()
        after = self.snapshot(
            comments=[{"id": "c1"}, {"id": "c2"}],
            reviews=[{"id": "r1", "state": "CHANGES_REQUESTED"}],
        )
        events = compare_snapshots(before, after)
        self.assertIn("new-comment", events)
        self.assertIn("new-review", events)
        self.assertIn("changes-requested", events)

    def test_reports_same_count_replacement_as_new_feedback(self):
        before = self.snapshot(comments=[{"id": "c1"}])
        after = self.snapshot(comments=[{"id": "c2"}])
        self.assertIn("new-comment", compare_snapshots(before, after))

    def test_prints_actionable_new_feedback(self):
        before = self.snapshot(comments=[])
        after = self.snapshot(
            comments=[
                {
                    "id": "c2",
                    "author": {"login": "octocat"},
                    "body": "Please add a regression test.",
                    "url": "https://github.com/owner/repo/pull/1#issuecomment-2",
                }
            ]
        )
        for snapshot in (before, after):
            snapshot.update(
                repository="owner/repo",
                number=1,
                title="Fix",
                url="https://github.com/owner/repo/pull/1",
            )

        output = io.StringIO()
        with (
            patch("scripts.watch_pr.collect_snapshot", side_effect=[before, after]),
            patch("scripts.watch_pr.time.sleep"),
            patch("sys.stdout", output),
        ):
            self.assertEqual(main(["owner/repo#1", "--interval", "10"]), 0)

        text = output.getvalue()
        self.assertIn("feedback: comment by octocat", text)
        self.assertIn("body: Please add a regression test.", text)
        self.assertIn(
            "url: https://github.com/owner/repo/pull/1#issuecomment-2", text
        )

    def test_reports_new_inline_review_comment(self):
        before = self.snapshot()
        after = self.snapshot(reviewComments=[{"id": 99}])
        self.assertIn("new-review-comment", compare_snapshots(before, after))

    def test_reports_head_change_and_conflict(self):
        before = self.snapshot()
        after = self.snapshot(
            headRefOid="next-sha",
            mergeable="CONFLICTING",
            mergeStateStatus="DIRTY",
        )
        events = compare_snapshots(before, after)
        self.assertIn("head-changed", events)
        self.assertIn("merge-conflict", events)

    def test_reports_terminal_state(self):
        before = self.snapshot()
        after = self.snapshot(state="MERGED")
        self.assertIn("merged", compare_snapshots(before, after))

    def test_merged_snapshot_stops_immediately(self):
        self.assertTrue(should_stop(self.snapshot(state="MERGED")))

    def test_closed_snapshot_stops_immediately(self):
        self.assertTrue(should_stop(self.snapshot(state="CLOSED")))

    def test_conflicting_snapshot_stops_immediately(self):
        self.assertTrue(should_stop(self.snapshot(mergeable="CONFLICTING")))

    def test_failed_current_head_check_stops_immediately(self):
        snapshot = self.snapshot()
        snapshot["checks"][0].update(state="FAILURE", bucket="fail")
        self.assertTrue(should_stop(snapshot))

    def test_completed_current_head_checks_stop_immediately(self):
        snapshot = self.snapshot()
        snapshot["checks"][0].update(state="SUCCESS", bucket="pass")
        self.assertTrue(should_stop(snapshot))

    def test_changes_requested_stops_immediately(self):
        self.assertTrue(
            should_stop(self.snapshot(reviewDecision="CHANGES_REQUESTED"))
        )

    def test_pending_clean_snapshot_keeps_watching(self):
        self.assertFalse(should_stop(self.snapshot()))


if __name__ == "__main__":
    unittest.main()
