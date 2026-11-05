"""Static evidence-contract checks only; no network or model inference."""

import json
from datetime import date
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evaluations/source-backed-airport.json"


class SourceBackedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.card = self.data["evidence_card"]

    def test_separate_unrun_fixture_has_complete_behavioral_contract(self):
        self.assertEqual(self.data["schema_version"], "1.0")
        self.assertEqual(self.data["id"], "SOURCE-AIRPORT-P0-01")
        self.assertEqual(self.data["priority"], "P0")
        self.assertEqual(self.data["kind"], "source-backed-static-evidence-exercise")
        self.assertEqual(self.data["model_evaluation_status"], "not_run")
        offline = json.loads((ROOT / "evaluations/scenarios.json").read_text())
        self.assertEqual(len(offline["cases"]), 22)
        self.assertNotIn(self.data["id"], {c["id"] for c in offline["cases"]})
        self.assertEqual(len(self.data["turns"]), 2)
        for key in ("turns", "must", "must_not"):
            self.assertGreaterEqual(len(self.data[key]), 2)
            self.assertTrue(all(isinstance(s, str) and s.strip()
                                for s in self.data[key]))
        # This is an exercise definition, never an automatically fabricated run.
        for key in ("answers", "results", "scores", "passed", "runs"):
            self.assertNotIn(key, self.data)
        self.assertIn("NOT live browsing", self.card["scope"])
        self.assertEqual(set(self.card), {"scope", "sources"})
        self.assertNotIn("reviewer_expectations", self.card)

    def test_official_provenance_and_date_precision_are_preserved(self):
        provenance = self.data["provenance"]
        self.assertEqual(date.fromisoformat(provenance["observed_at"]),
                         date(2026, 11, 5))
        self.assertEqual(provenance["timezone"], "Asia/Tokyo")
        self.assertEqual(provenance["precision"], "date_only")
        self.assertEqual(provenance["inspector"], "upstream orchestrator")
        self.assertIn("did not browse", provenance["note"])
        expected = {
            "kate-uh": ("https://www.kate.co.jp/en/timetable/detail/UH", None),
            "kintetsu-uehommachi": (
                "https://www.kintetsu.co.jp/foreign/english/about/station/yard/uehommachi.html",
                "2026-08-01"),
            "kintetsu-tsuruhashi": (
                "https://www.kintetsu.co.jp/foreign/english/about/station/yard/tsuruhashi.html",
                "2026-03-14"),
        }
        sources = self.card["sources"]
        self.assertEqual(len(sources), len(expected))
        self.assertEqual({s["id"] for s in sources}, set(expected))
        for source in sources:
            with self.subTest(source=source["id"]):
                url, effective = expected[source["id"]]
                self.assertEqual(source["url"], url)
                parsed = urlsplit(source["url"])
                self.assertEqual(parsed.scheme, "https")
                self.assertIsNone(parsed.username)
                self.assertFalse(parsed.query or parsed.fragment)
                self.assertEqual(source["effective_on"], effective)
                self.assertTrue(source["publisher"].strip())
                self.assertTrue(all(s.strip() for s in source["facts"]))
                if effective:
                    self.assertLess(date.fromisoformat(effective),
                                    date.fromisoformat(provenance["observed_at"]))
        by_id = {s["id"]: s for s in sources}
        self.assertEqual(by_id["kate-uh"]["timetable_entries"], [
            {"departure": "07:10", "scheduled_arrival_t1": "08:01"},
            {"departure": "07:50", "scheduled_arrival_t1": "08:41"},
        ])
        self.assertIn("SECOND-FLOOR", " ".join(by_id["kate-uh"]["facts"]))
        self.assertEqual(by_id["kintetsu-uehommachi"]["platform_transfer_guide_minutes"], 6)
        self.assertIn("ground-platform to underground-platform", " ".join(
            by_id["kintetsu-uehommachi"]["facts"]))

    def test_unknowns_cannot_be_resolved_by_static_maps_or_timetables(self):
        unknowns = self.data["reviewer_expectations"]["unsupported_facts"]
        for key, phrase in {
            "service_day": "date-scoped applicability",
            "rail_departure": "precise Tsuruhashi rail departure",
            "accessible_path": "second-floor-bus-terminal",
            "elevator_status": "Current elevator operation",
            "group_transfer_duration": "two people with large bags",
            "bus_operation_and_capacity": "seats",
            "flight_and_cutoffs": "bag-drop or gate cutoff",
            "deadline_and_shopping_margin": "having or lacking shopping time",
        }.items():
            self.assertIn(phrase, unknowns[key])
        recheck = " ".join(self.data["reviewer_expectations"]["freshness_and_recheck"])
        for phrase in ("effective_on", "observed_at", "service date",
                       "date-scoped", "staff", "carrier", "Without capable tools"):
            self.assertIn(phrase, recheck)
        requirements = " ".join(self.data["must"])
        for phrase in ("07:10 -> T1 08:01", "07:50 -> T1 08:41",
                       "two travelers", "step-free", "6-minute",
                       "cutoffs", "Shopping time remains unknown"):
            self.assertIn(phrase, requirements)
        prohibitions = " ".join(self.data["must_not"])
        for phrase in ("rail departures", "date-scoped official timetable",
                       "6-minute", "elevator status", "realtime",
                       "seating", "check-in", "lack of shopping time",
                       "agent live browsing"):
            self.assertIn(phrase, prohibitions)

    def test_traveler_prompts_are_independent_and_have_no_trip_identifiers(self):
        turns = " ".join(self.data["turns"])
        for phrase in ("虛構練習", "未來某天", "日期與航班時間尚未設定",
                       "兩人", "大型行李", "全程需要無階梯", "六分鐘"):
            self.assertIn(phrase, turns)
        for pattern in (r"\b20\d{2}-\d{2}-\d{2}\b", r"\b\d{1,2}:\d{2}\b",
                        r"\b[A-Z]{2}\d{3,4}\b", r"/(?:Users|home)/",
                        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                        r"gh[opusr]_[A-Za-z0-9]+"):
            self.assertNotRegex(turns, pattern)
        # All public dates belong to provenance, not traveler prompts/history.
        raw = FIXTURE.read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", raw)),
                         {"2026-11-05", "2026-08-01", "2026-03-14"})

    def test_manual_protocol_and_references_keep_proof_boundaries(self):
        protocol = (ROOT / "evaluations/README.md").read_text(encoding="utf-8")
        section = " ".join(protocol.split(
            "## Source-backed P0 static evidence exercise", 1)[1].split(
            "## Manual model/host evaluation", 1)[0].split())
        for phrase in (FIXTURE.name, self.data["id"], "Not run yet",
                       "outside the 22 text-only fictional/offline cases",
                       "source-injection/tool-equivalent", "not agent live browsing",
                       "current-timetable test", "NEW isolated session",
                       "disable dynamic lookup", "separate dynamic-update variant",
                       "exact inspection clock time is unrecorded",
                       "Do not inject `must`/`must_not`", "reviewer_expectations", "full replies",
                       "SHA-256", "P0 automatic critical fail",
                       "unassessed until an actual run", "No result establishes live operational safety"):
            self.assertIn(phrase, section)
        evidence = " ".join((ROOT / "references/evidence-and-transit.md").read_text().split())
        for phrase in ("effective date", "access date", "timezone",
                       "scheduled arrival is not a realtime arrival",
                       "group-and-baggage accessible", "endpoints and conditions"):
            self.assertIn(phrase, evidence)
        navigation = " ".join((ROOT / "references/live-navigation.md").read_text().split())
        for phrase in ("not realtime guarantees", "match its endpoints",
                       "arrival-platform-to-bus-terminal", "elevator operation",
                       "normal transfer guide cannot prove a tight bus connection"):
            self.assertIn(phrase, navigation)
        for filename in ("README.md", "CHANGELOG.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("evaluations/" + FIXTURE.name, text)
            self.assertIn("not run yet", text.lower())


if __name__ == "__main__":
    unittest.main()
