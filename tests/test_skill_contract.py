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
            "onboarding.md",
            "memory.md",
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
        self.assertIn("vendor-neutral", readme)
        self.assertIn("Host support for Agent Skills", readme)
        self.assertIn("host policy", skill)
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", ROOT / "README.md"]
            + list((ROOT / "references").glob("*.md"))
        )
        self.assertNotRegex(combined, r"/(?:Users|home)/[\w.-]+")
        self.assertNotIn("sk-", combined)
        self.assertNotRegex(combined, r"(?i)ChatGPT|OpenAI|AgentDock")

    def test_source_dates_require_per_source_mapping_without_invented_dates(self):
        # Static instruction regression only: this cannot prove model compliance.
        # Check the entrypoint and both transit references so the rule survives
        # hosts loading only the entrypoint or the relevant navigation reference.
        for filename in ("SKILL.md", "references/evidence-and-transit.md",
                         "references/live-navigation.md"):
            with self.subTest(filename=filename):
                text = " ".join((ROOT / filename).read_text(encoding="utf-8").split())
                for clause in (
                    "source-backed time-sensitive transit/airport or accessibility choice",
                    "each decision-relevant source name + effective date",
                    "effective date not supplied",
                    "Separately state `observed_at` / access date, timezone and recorded precision",
                    "never invent an effective date",
                    "exact access clock time",
                    "source validity, access date, service date and live operating status",
                    "map date does not prove current elevator operation",
                    "compact line or table",
                    "across turns as needed",
                    "simple unrelated queries",
                    "immediate safety action",
                ):
                    self.assertIn(clause, text)
        evidence = " ".join((ROOT / "references/evidence-and-transit.md").read_text(
            encoding="utf-8").split())
        for clause in ("`effective_on`, as-of or validity wording and precision",
                       "including `null`", "never invent an effective date or substitute the access date",
                       "If only a date was recorded, say date-only",
                       "inspection date is not a new check by the assistant",
                       "leave an unknown trip date and service-day applicability unresolved"):
            self.assertIn(clause, evidence)

    def test_fictional_state_example_is_valid_and_has_provenance(self):
        doc = (ROOT / "references" / "travel-state.md").read_text(encoding="utf-8")
        match = re.search(r"```json\s*(\{.*?\})\s*```", doc, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(data["mode"], "on_trip")
        self.assertEqual(data["schema_version"], "0.2")
        self.assertEqual(data["profile"]["current_place"]["source"], "user")
        self.assertEqual(data["profile"]["destination"]["source"], "user")
        self.assertIn("open_question", data["profile"])
        self.assertIn("raw_snapshot", data)

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
