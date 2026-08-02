import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    "shop": "[owner|owner/repo] [--since <days>]",
    "vet": "<issue-url|owner/repo#number>",
    "cook": "[issue|pr]",
    "vibe": "[--full]",
    "wrap": "[issue|pr]",
    "babysit": "<pr-url|owner/repo#number> [--once] [--interval <seconds>]",
    "send": "<commit|push|pr|all> [--yes]",
    "pulse": "[owner|owner/repo]",
}
READ_ONLY_COMMANDS = {
    "shop": "read-only",
    "vet": "read-only",
    "vibe": "make no edits and perform no public action",
    "wrap": "do not modify local or remote state",
    "babysit": "never comment, review, rerun checks, merge, or otherwise mutate github",
    "pulse": "read-only",
}


class PluginLayoutTests(unittest.TestCase):
    def test_command_directory_contains_only_planned_commands(self):
        command_names = {path.name for path in (ROOT / "commands").glob("*.md")}
        self.assertEqual(command_names, {f"{name}.md" for name in COMMANDS})

    def test_manifest_names_the_plugin_and_skill_directory(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "commit")
        self.assertEqual(manifest["version"], "0.1.2")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["author"]["name"], "macayu17")
        self.assertEqual(manifest["interface"]["developerName"], "macayu17")
        for unsupported_key in ("apps", "mcpServers", "hooks"):
            self.assertNotIn(unsupported_key, manifest)
        for unsupported_key in ("composerIcon", "logo", "logoDark", "screenshots"):
            self.assertNotIn(unsupported_key, manifest["interface"])

    def test_all_commands_are_user_only_and_delegate_to_skill(self):
        for name, hint in COMMANDS.items():
            with self.subTest(command=name):
                text = (ROOT / "commands" / f"{name}.md").read_text(encoding="utf-8")
                self.assertIn(f"argument-hint: '{hint}'", text)
                self.assertIn("disable-model-invocation: true", text)
                self.assertIn("Use $commitment-issues", text)
                self.assertIn("raw `$ARGUMENTS` unchanged", text)

    def test_read_only_commands_explicitly_forbid_mutation(self):
        for name, prohibition in READ_ONLY_COMMANDS.items():
            with self.subTest(command=name):
                text = (ROOT / "commands" / f"{name}.md").read_text(encoding="utf-8")
                self.assertIn(prohibition, text.casefold())

    def test_cook_forbids_public_actions(self):
        text = (ROOT / "commands" / "cook.md").read_text(encoding="utf-8").casefold()
        self.assertIn(
            "do not commit, push, comment, or open or update a pull request",
            text,
        )

    def test_cook_requires_isolation_repo_study_and_complete_checks(self):
        command = (ROOT / "commands" / "cook.md").read_text(encoding="utf-8").casefold()
        implementation = (
            ROOT
            / "skills"
            / "commitment-issues"
            / "references"
            / "implementation.md"
        ).read_text(encoding="utf-8").casefold()

        self.assertIn("clone", command)
        self.assertIn("isolated worktree or dedicated clone", command)
        self.assertIn("repository structure", command)
        self.assertIn("maintainer style", command)
        self.assertIn("no ai slop", command)
        self.assertIn("every repository-required check", command)
        self.assertIn("remain incomplete", command)
        self.assertIn("never edit in a dirty or shared checkout", implementation)
        self.assertIn("read the issue discussion and repository structure", implementation)
        self.assertIn("do not trade required verification for a deadline", implementation)

    def test_babysit_is_read_only_and_uses_the_watcher(self):
        text = (ROOT / "commands" / "babysit.md").read_text(encoding="utf-8")
        self.assertIn('${CLAUDE_PLUGIN_ROOT}/scripts/watch_pr.py', text)
        self.assertIn("--once", text)
        self.assertIn("read-only", text.casefold())

    def test_vet_uses_plugin_relative_helper(self):
        text = (ROOT / "commands" / "vet.md").read_text(encoding="utf-8")
        self.assertIn('${CLAUDE_PLUGIN_ROOT}/scripts/vet_issue.py', text)
        self.assertIn(
            'python "${CLAUDE_PLUGIN_ROOT}/scripts/vet_issue.py" --json $ARGUMENTS',
            text,
        )

    def test_send_it_requires_narrow_confirmation(self):
        text = (ROOT / "commands" / "send.md").read_text(encoding="utf-8")
        self.assertIn("--yes", text)
        self.assertIn("preview", text.casefold())
        self.assertIn("never imply", text.casefold())
        self.assertIn("authorize only the selected action", text.casefold())
        self.assertIn("only `all --yes` authorizes all three", text.casefold())

    def test_skill_has_discoverable_trigger_metadata(self):
        text = (
            ROOT / "skills" / "commitment-issues" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("name: commitment-issues", text)
        self.assertIn("description: Use when", text)


if __name__ == "__main__":
    unittest.main()
