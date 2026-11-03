"""Dependency-free checks for the portable skill contract."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def frontmatter():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise AssertionError("YAML frontmatter closing delimiter is missing")
    return text[4:end], text[end + 5 :]


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_identity_license_and_trigger_description(self):
        meta, body = frontmatter()
        self.assertRegex(meta, r"(?m)^name:\s*japan-travel-copilot\s*$")
        self.assertRegex(meta, r"(?m)^license:\s*Apache-2\.0\s*$")
        description = re.search(r"(?ms)^description:\s*>-\s*\n((?:\s{2,}.*\n?)+)", meta)
        self.assertIsNotNone(description)
        text = " ".join(line.strip() for line in description.group(1).splitlines())
        for trigger in ("Japan travel", "transit", "translation", "disrupted"):
            self.assertIn(trigger.lower(), text.lower())
        self.assertLess(len((ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()), 500)
        self.assertIn("## Modes", body)

    def test_references_exist_and_are_linked(self):
        _, body = frontmatter()
        linked = re.findall(r"\]\((references/[^)]+)\)", body)
        self.assertTrue(linked)
        for relative in linked:
            self.assertTrue((ROOT / relative).is_file(), relative)
        for filename in (
            "travel-state.md",
            "evidence-and-transit.md",
            "translation-patterns.md",
            "scenarios.md",
        ):
            self.assertTrue((ROOT / "references" / filename).is_file())

    def test_portability_privacy_and_capability_boundaries(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "background monitoring",
            "without explicit user approval",
            "does not itself provide",
            "Traditional Chinese",
        ):
            self.assertIn(phrase, skill)
        self.assertRegex(skill, r"(?is)never\s+hallucinate")
        self.assertIn("ChatGPT does not automatically install", readme)
        self.assertIn("local-directory skill import", readme)
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", ROOT / "README.md"]
            + list((ROOT / "references").glob("*.md"))
        )
        self.assertNotRegex(combined, r"/(?:Users|home)/[\w.-]+")
        self.assertNotIn("sk-", combined)

    def test_fictional_state_example_is_valid_and_has_provenance(self):
        doc = (ROOT / "references" / "travel-state.md").read_text(encoding="utf-8")
        match = re.search(r"```json\s*(\{.*?\})\s*```", doc, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(data["mode"], "on_trip")
        self.assertEqual(data["current_place"]["source"], "user")
        self.assertEqual(data["destination"]["source"], "user")
        self.assertIn("open_question", data)

    def test_scenarios_encode_no_guessing_and_estimate_label(self):
        cases = (ROOT / "references" / "scenarios.md").read_text(encoding="utf-8")
        for required in (
            "不能安全地猜",
            "不能確認是否含花生",
            "還沒有核實",
            "不是即時匯率報價",
        ):
            self.assertIn(required, cases)

    def test_release_basics_exist(self):
        for filename in ("LICENSE", "CONTRIBUTING.md", "CHANGELOG.md", ".gitignore"):
            self.assertTrue((ROOT / filename).is_file(), filename)
        self.assertIn("Apache License", (ROOT / "LICENSE").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
