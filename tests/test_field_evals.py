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
            ROOT / "evaluations" / "fixtures" / "README.md",
        ]
        text = "\n".join(source.read_text(encoding="utf-8") for source in sources)
        # The public evaluation report filename contains a run date, not a trip
        # date. Exempt only that filename; keep scanning prose and other paths.
        text = text.replace("2026-11-04-acp-offline-smoke.md", "acp-offline-smoke.md")
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

    def test_airport_contract_rejects_fictitious_departures_and_foreign_constraints(self):
        # Structural regression only: guards the contract, not model compliance.
        airport = next(case for case in self.cases if case["id"] == "AIRPORT-BUFFER-05")
        prohibitions = " ".join(airport["must_not"]).lower()
        for phrase in (
            "departure times", "departure clock windows", "bus intervals",
            "without an actual timetable", "hypothetical",
            "accessibility constraints", "another case",
        ):
            self.assertIn(phrase, prohibitions)
        navigation = (ROOT / "references" / "live-navigation.md").read_text(encoding="utf-8")
        airport_rules = navigation.split("## Airport and other hard deadlines", 1)[1]
        for phrase in (
            "never invent departure clock times or clock windows",
            '"example", "if" or', '"hypothetical"', "not actual services",
            "unsupported clock windows", "operator timetable",
            "user-supplied or verified times",
        ):
            self.assertIn(phrase, airport_rules)
        self.assertIn("do not import", navigation)
        self.assertIn("user-required", navigation)

    def test_manual_protocol_requires_fresh_sessions_and_auditable_evidence(self):
        # Instruction presence cannot establish independent behavioral acceptance.
        protocol = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(protocol.split())
        for phrase in (
            "brand NEW session/conversation per case per host",
            "Never reuse a session", 'prompt-only "forget/reset"',
            "preliminary / contaminated", "do not claim an independent",
            "host/adapter configuration", "Skill version or revision",
            "accessible tools", "run timestamps", "every input/output",
            "P0 critical failure", "nonexistent service",
        ):
            self.assertIn(phrase, normalized)

    def test_synthetic_image_fixture_has_jpeg_bytes_and_source_documentation(self):
        # Byte/document checks do not evaluate OCR or a model's image handling.
        fixtures = ROOT / "evaluations" / "fixtures"
        jpeg = (fixtures / "synthetic-exit-guide.jpg").read_bytes()
        self.assertTrue(jpeg.startswith(b"\xff\xd8\xff"), "JPEG magic is required")
        self.assertTrue(jpeg.endswith(b"\xff\xd9"), "JPEG end marker is required")
        self.assertGreater(len(jpeg), 1024)
        self.assertLess(len(jpeg), 100_000, "Keep the single sign fixture small")
        readme = (fixtures / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        for phrase in (
            "synthetic-exit-guide.jpg", "source-generated", "not a user photo",
            "出口案内 / Exit Guide", "11番出口", "階段のみ / Stairs only",
            "15番出口", "エレベーター / Elevator", "Fictional sign",
            "no direction arrows", "actual JPEG bytes", "image content block",
            "text-only prompt is not an image-input test",
            "not a general OCR benchmark or field-safety sign-off",
        ):
            self.assertIn(phrase, normalized)

    def test_image_observations_keep_sample_counts_and_limitations_explicit(self):
        # Guard reporting distinctions; this is not a new live image/model test.
        report = (ROOT / "evaluations" / "runs" / "2026-11-04-acp-offline-smoke.md").read_text(encoding="utf-8")
        normalized = " ".join(report.split())
        for phrase in (
            "4 scenarios × 2 models = 8", "1 separate image case × 2 models = 2",
            "12 model/case samples", "6 samples were fresh/independent",
            "2 fresh airport regression reruns",
            "not part of the standardized 22-case JSON fixture suite",
            "actual JPEG image content blocks", "fresh independent sessions per provider",
            "Exact run timestamps and full raw outputs were not recorded",
            "observational summary", "no official transit sources",
            "gpt-6.1-sol", "gemini-3.8-flash", "much longer than necessary",
            "not a user photo", "neither general OCR/image performance",
            "no P0 sign-off",
        ):
            self.assertIn(phrase, normalized)
        protocol = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        self.assertIn("fixtures/README.md", protocol)
        self.assertIn("A text-only prompt is not an image test", protocol)

    def test_airport_shopping_uncertainty_and_narrow_rerun_are_explicit(self):
        # Structural guard only; no behavioral sign-off for the new instruction.
        navigation = (ROOT / "references" / "live-navigation.md").read_text(encoding="utf-8")
        rules = " ".join(navigation.split("## Airport and other hard deadlines", 1)[1].split())
        for phrase in (
            "When actual timing is missing",
            "do not guarantee either shopping time or lack of shopping time",
            "likely trade-offs rather than categorical claims",
            "shopping window remains unknown", "Preserve urgency",
            "carrier cutoff and operator timetable checks",
        ):
            self.assertIn(phrase, rules)
        report = (ROOT / "evaluations" / "runs" / "2026-11-04-acp-offline-smoke.md").read_text(encoding="utf-8")
        normalized = " ".join(report.split())
        for phrase in (
            "two NEW independent sessions", "2 actual traveler turns per session",
            "3 people / 3 huge suitcases", "Only local read-only Skill/reference-file access was used",
            "Passed the narrow no-invented-departure condition",
            "categorical denial of shopping time was unsupported",
            "distinct from the original fake-timetable bug",
            "shopping-certainty guard has not been behaviorally rerun",
            "Codex gpt-6.1-sol **high**", "gemini-3.8-flash **medium**",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
