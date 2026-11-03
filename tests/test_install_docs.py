"""Offline checks for public installation instructions and safety boundaries."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
SOURCE = "jacktdry/japan-travel-copilot"


class InstallationDocumentationTests(unittest.TestCase):
    def test_readme_exposes_one_command_at_top_in_both_languages(self):
        self.assertIn(f"npx skills add {SOURCE} -g", README[:1100])
        for title in ("## Install and compatibility", "## 安裝與相容性"):
            self.assertIn(title, README)
        self.assertIn("Node.js **22.20+**", README)
        self.assertIn("Node.js **22.20 以上**", README)

    def test_cli_commands_are_scoped_and_reversible(self):
        for command in (
            f"npx skills add {SOURCE} -g",
            f"npx skills add {SOURCE}\n",
            f"npx skills add {SOURCE} --list",
            "npx skills ls -g", "npx skills ls",
            "npx skills update japan-travel-copilot -g",
            "npx skills remove --global japan-travel-copilot",
        ):
            self.assertIn(command, README)
        self.assertIn("current project only", README)
        self.assertIn("全域安裝", README)
        self.assertIn("do not use unattended flags", README.lower())

    def test_agent_can_follow_readme_without_guessing_capabilities(self):
        for phrase in (
            "For installation-capable Agents: required workflow",
            "請 Agent 協助安裝", "給 Agent 的安裝與使用規則",
            "Inspect before modifying", "Check capabilities and existing installation",
            "Choose the scope", "Install and verify", "Start using it",
            "ask before executing them", "verify discovery",
            "cannot install", "manual ZIP installation",
        ):
            self.assertIn(phrase.lower(), README.lower())
        self.assertIn("README installation guide", SKILL)
        self.assertIn("Never claim installation", SKILL)
        self.assertNotRegex(README, r"(?m)^\s*(?:curl|wget) .+\|\s*(?:bash|sh)\s*$")

    def test_no_node_manual_install_keeps_all_relative_resources(self):
        self.assertIn("Manual ZIP (no Node.js required)", README)
        self.assertIn("下載 ZIP 手動安裝（不需要 Node.js）", README)
        for item in ("SKILL.md", "references/", "scripts/"):
            self.assertIn(item, README)
            self.assertTrue((ROOT / item).exists(), item)
        self.assertIn("<HOST_SKILLS_DIRECTORY>/japan-travel-copilot/SKILL.md", README)
        self.assertIn("session-only instructions", README)

    def test_install_does_not_enable_memory_and_usage_is_explained(self):
        for phrase in (
            "Do not activate file memory", "Never automatically read or write trip files",
            "Copying a Skill does not run", "first-trip onboarding",
            "不要啟用或保存旅程記憶", "安裝也不會自動寫入任何旅行資料",
        ):
            self.assertIn(phrase, README)
        self.assertIn("Installation is separate from invoking the Skill", SKILL)

    def test_repository_link_is_the_public_origin(self):
        self.assertIn("https://github.com/" + SOURCE, README)
        self.assertTrue(SKILL.startswith("---\nname: japan-travel-copilot\n"))
        self.assertLess(len(SKILL.splitlines()), 500)


if __name__ == "__main__":
    unittest.main()
