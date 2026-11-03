"""Static checks for synthetic travel-field evaluation coverage.

These tests deliberately do NOT run an LLM or simulate live transit.
"""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluations" / "scenarios.json"


class FieldEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.collection = json.loads(CASES.read_text(encoding="utf-8"))
        self.cases = self.collection["cases"]

    def test_fixture_is_portable_and_has_a_minimum_risk_set(self):
        self.assertEqual(self.collection["schema_version"], "1.0")
        self.assertGreaterEqual(len(self.cases), 22)
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(
            sum(case["priority"] == "P0" for case in self.cases), 10
        )
        self.assertGreaterEqual(
            sum(case["priority"] == "P1" for case in self.cases), 12
        )
        self.assertGreaterEqual(
            sum(len(case["turns"]) > 1 for case in self.cases), 10
        )

    def test_each_case_has_falsifiable_behavioral_contract(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(
                    set(case),
                    {"id", "priority", "workflow", "host_capabilities",
                     "turns", "must", "must_not"},
                )
                self.assertRegex(case["id"], r"^[A-Z][A-Z0-9-]+$")
                self.assertIn(case["priority"], ("P0", "P1", "P2"))
                self.assertIsInstance(case["host_capabilities"], list)
                self.assertGreaterEqual(len(case["turns"]), 1)
                self.assertGreaterEqual(len(case["must"]), 2)
                self.assertGreaterEqual(len(case["must_not"]), 1)
                for key in ("workflow",):
                    self.assertTrue(case[key].strip())
                for key in ("turns", "must", "must_not"):
                    self.assertTrue(
                        all(isinstance(x, str) and x.strip() for x in case[key])
                    )

    def test_representative_workflows_are_not_missing(self):
        workflows = {case["workflow"] for case in self.cases}
        for required in (
            "navigation", "deadline", "image", "correction", "trip_continuity",
            "shopping", "orders", "timed_event", "translation", "memory",
        ):
            self.assertIn(required, workflows)

    def test_documentation_and_entrypoint_have_safety_guidance(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in ("live-navigation.md", "trip-operations.md",
                     "photo-and-orders.md"):
            self.assertIn("references/" + name, skill)
            self.assertTrue((ROOT / "references" / name).is_file())
        navigation = (ROOT / "references" / "live-navigation.md").read_text(encoding="utf-8")
        continuity = (ROOT / "references" / "trip-operations.md").read_text(encoding="utf-8")
        photos = (ROOT / "references" / "photo-and-orders.md").read_text(encoding="utf-8")
        for phrase in (
            "07:22", "19:22", "step-free", "check-in", "airport",
            "withdraw", "source", "checkpoint",
        ):
            self.assertIn(phrase.lower(), navigation.lower())
        for phrase in (
            "Hard constraints", "confirmed", "tentative", "canceled",
            "purchased", "unavailable", "timed",
        ):
            self.assertIn(phrase.lower(), continuity.lower())
        for phrase in (
            "visible", "inference", "receipt", "requested", "served",
            "billed", "allergen",
        ):
            self.assertIn(phrase.lower(), photos.lower())

    def test_privacy_and_live_test_limitations(self):
        sources = [
            CASES, ROOT / "SKILL.md", ROOT / "README.md",
            *sorted((ROOT / "references").glob("*.md")),
            ROOT / "evaluations" / "README.md",
        ]
        text = "\n".join(source.read_text(encoding="utf-8") for source in sources)
        # Check for identifier *shapes*, not values from a real trip.
        for pattern in (
            r"\b[A-Z]{2}[0-9]{3,4}\b",  # Flight identifiers
            r"\b20[0-9]{2}-[01][0-9]-[0-3][0-9]\b",  # Trip dates
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",  # Email addresses
            r"/(?:Users|home)/[A-Za-z0-9._-]+",  # Local user paths
            r"\b(?:[0-9][ -]?){13,19}\b",  # Card-like sequences
            r"gho_[A-Za-z0-9]+",  # Credentials
        ):
            self.assertNotRegex(text, pattern)
        readme = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        self.assertIn("fictional and synthetic", readme)
        self.assertIn("does not run model inference", readme.lower())
        self.assertIn("Photo-themed cases are text-only stand-ins", readme)
        self.assertIn("automatic critical fail", readme)
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("evaluations/README.md", root_readme)

    def test_regression_prompts_do_not_accuse_well_behaved_agents(self):
        by_id = {case["id"]: case for case in self.cases}
        self.assertIn("19:22", by_id["NAV-TIME-02"]["turns"][0])
        self.assertIn("07:22", by_id["NAV-TIME-02"]["turns"][0])
        self.assertIn("舊路線筆記", by_id["NAV-SIGN-03"]["turns"][0])
        self.assertIn("範例機場第一航廈", by_id["AIRPORT-BUFFER-05"]["turns"][0])
        self.assertIn("沒附上照片", by_id["IMG-CONFLICT-07"]["turns"][0])
        self.assertIn("NAV-WRONGWAY-22", by_id)
        self.assertIn("FOOD-LEDGER-21", by_id)

    def test_accessibility_and_receipt_chain_are_explicit(self):
        navigation = (ROOT / "references" / "live-navigation.md").read_text(encoding="utf-8")
        orders = (ROOT / "references" / "photo-and-orders.md").read_text(encoding="utf-8")
        self.assertIn("Platform ↔ train carriage", navigation)
        self.assertIn("スロープ板", navigation)
        self.assertIn("requested", orders.lower())
        self.assertIn("served", orders.lower())
        self.assertIn("billed", orders.lower())


if __name__ == "__main__":
    unittest.main()
