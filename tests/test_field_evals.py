"""Static checks for synthetic travel-field evaluation coverage.

These tests deliberately do NOT run an LLM or simulate live transit.
"""

import hashlib
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
        # Public report filenames contain run dates, not trip dates. Exempt
        # only those filenames; keep scanning prose and other paths.
        for filename in ("2026-11-04-acp-offline-smoke.md",
                         "2026-11-04-p0-fresh-session-review.md",
                         "2026-11-04-nav-checkpoint-postfix-transcripts.json",
                         "2026-11-04-p0-remaining-review.md",
                         "2026-11-04-p0-remaining-transcripts.json",
                         "2026-11-04-p0-remaining-postfix-transcripts.json"):
            text = text.replace(filename, filename.removeprefix("2026-11-04-"))
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

    def test_transfer_checkpoint_requires_grounded_gate_instructions(self):
        # Static contract only: these assertions do not prove model compliance.
        case = next(case for case in self.cases if case["id"] == "NAV-CHECKPOINT-04")
        self.assertEqual(case["turns"], [
            "我要從範例站搭火車到範例港，還沒上車。",
            "現在上車了，車門關了。",
            "已經到轉乘站。",
        ])
        requirements = " ".join(case["must"]).lower()
        for phrase in (
            "actual transfer station", "on-train versus off-train",
            "next appropriate line/direction", "one safe next action",
            "gate/ticket", "operator, lines and station", "before directing passage",
        ):
            self.assertIn(phrase, requirements)
        prohibitions = " ".join(case["must_not"]).lower()
        for phrase in (
            "entirely within the paid area", "not to exit gates",
            "without grounded operator, lines and station",
            "exit/re-entry", "without verified operator-specific transfer evidence",
        ):
            self.assertIn(phrase, prohibitions)
        navigation = (ROOT / "references" / "live-navigation.md").read_text(encoding="utf-8")
        rules = " ".join(navigation.split("## Time, boarding and travel checkpoints", 1)[1]
                         .split("## Step-free", 1)[0].split())
        for phrase in (
            "confirm the actual station", "still on the train or has alighted",
            "next appropriate line/direction from evidence", "one safe next action",
            "Gate and ticket arrangements depend on the operator",
            "Without grounded operator, lines and station",
            "do not presume", "paid area", "not to exit gates", "require exit/re-entry",
            "Verify the applicable gate/ticket procedure before directing passage",
        ):
            self.assertIn(phrase, rules)

    def test_postfix_gate_evidence_structure_quotes_and_privacy(self):
        # Artifact checks only; no LLM call or independent behavioral validation.
        path = ROOT / "evaluations" / "runs" / "2026-11-04-nav-checkpoint-postfix-transcripts.json"
        text = path.read_text(encoding="utf-8")
        evidence = json.loads(text)
        self.assertEqual(set(evidence), {
            "schema_version", "case_id", "date_local", "timezone",
            "precommit_head", "navigation_reference_sha256", "note", "runs",
        })
        self.assertEqual(evidence["schema_version"], "1.0")
        self.assertEqual(evidence["case_id"], "NAV-CHECKPOINT-04")
        digest = evidence["navigation_reference_sha256"]
        # Historical run snapshot: later guidance edits must not rewrite evidence
        # or imply that the current reference has already been behaviorally tested.
        self.assertEqual(digest,
                         "be740984415f7b8ef97258bfa725449dad07d3193be47d24eea7954dda50c3f8")
        self.assertEqual(len(evidence["runs"]), 2)
        final_answers = {}
        fixture = next(case for case in self.cases if case["id"] == evidence["case_id"])
        for run in evidence["runs"]:
            self.assertEqual(set(run), {
                "adapter", "model", "effort", "fresh_session", "source", "messages",
            })
            self.assertIs(run["fresh_session"], True)
            self.assertEqual(run["effort"], "medium")
            users = []
            for message in run["messages"]:
                self.assertEqual(set(message), {"role", "text"})
                self.assertIn(message["role"], ("user", "assistant"))
                self.assertTrue(message["text"].strip())
                if message["role"] == "user":
                    users.append(message["text"])
            self.assertEqual(len(users), 3)
            self.assertTrue(users[0].endswith(fixture["turns"][0]))
            self.assertEqual(users[1:], fixture["turns"][1:])
            self.assertEqual(run["messages"][-1]["role"], "assistant")
            final_answers[run["model"]] = run["messages"][-1]["text"]
        self.assertEqual(set(final_answers), {"gpt-6.1-sol", "gemini-3.8-flash"})
        for phrase in ("你到的是哪一站", "還在車上，還是已經下車", "是否需要出閘"):
            self.assertIn(phrase, final_answers["gpt-6.1-sol"])
        for phrase in (
            "站名是什麼", "還是仍在車廂內", "有些可在站內付費區",
            "有些則需出閘門", "請勿自行穿過閘門或認定不用出站",
            "改札を出る必要がありますか？",
        ):
            self.assertIn(phrase, final_answers["gemini-3.8-flash"])
        for answer in final_answers.values():
            self.assertNotIn("請勿走出驗票閘門", answer)
            self.assertNotIn("留在付費區內", answer)
        # Shape guards complement synthetic provenance; they cannot prove privacy.
        for pattern in (
            r"/(?:Users|home)/[A-Za-z0-9._-]+",
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
            r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
            r"gh[opusr]_[A-Za-z0-9]+",
            r'"(?:session_id|host_id|device_id|native_id)"\s*:',
            r"\b(?:[0-9][ -]?){13,19}\b",
        ):
            self.assertNotRegex(text, pattern)

    def test_postfix_report_keeps_outcome_narrow_and_provenance_explicit(self):
        # Documentation contract only, not an LLM validation.
        runs = ROOT / "evaluations" / "runs"
        report = (runs / "2026-11-04-p0-fresh-session-review.md").read_text(encoding="utf-8")
        section = " ".join(report.split("## Post-fix gate regression", 1)[1].split())
        evidence = json.loads((runs / "2026-11-04-nav-checkpoint-postfix-transcripts.json").read_text(encoding="utf-8"))
        for phrase in (
            "two fresh independent ACP sessions, 3 traveler turns each",
            "2026-11-04-nav-checkpoint-postfix-transcripts.json",
            evidence["navigation_reference_sha256"], "complete run event stream",
            "original first-turn harness wrapper excluded",
            "not original travel usage logs", "observed fixed for both providers",
            "one synthetic offline rerun per model", "not full P0 acceptance",
            "no live station verification", "do not run an LLM",
        ):
            self.assertIn(phrase, section)
        self.assertNotIn("No actual post-fix model rerun has been", report)
        self.assertIn("Critical substantive grounding failure", report)
        protocol = (ROOT / "evaluations" / "README.md").read_text(encoding="utf-8")
        self.assertIn("runs/2026-11-04-nav-checkpoint-postfix-transcripts.json", protocol)

    def test_remaining_case_contracts_preserve_source_boundaries_and_prompts(self):
        # Contract presence only, not a test of model decision-making.
        by_id = {case["id"]: case for case in self.cases}
        navigation = " ".join((ROOT / "references/live-navigation.md").read_text().split())
        photos = " ".join((ROOT / "references/photo-and-orders.md").read_text().split())
        for phrase in (
            "next actually scheduled express stop", "If that stop is unknown",
            "Safe stopping is separate from return-route feasibility",
            "first scheduled stop is not necessarily the best reverse transfer",
            "do not assume all local trains serve the desired station",
            "wrong-direction recovery, return trips and transfer decisions",
            "specific actual station, operator, lines and ticket/transfer rules",
            "must stay inside fare gates or must exit/re-enter",
            "opposite platform is the return route",
            "missing elevator icon, absent display or incomplete photo does not prove",
            "unverified", "station map or station staff",
        ):
            self.assertIn(phrase, navigation)
        for phrase in (
            "no image was received", "explicitly say that no image is attached/received",
            "attached image cannot be read", "explicitly say it is unreadable",
            "user report", "not direct observation of pixels",
        ):
            self.assertIn(phrase, photos)
        for case_id, phrases in {
            "NAV-WRONGWAY-22": (
                "stay inside fare gates or exit/re-enter", "ticket/transfer rules",
                "opposite platform", "first scheduled express stop",
                "best reverse transfer", "all local trains", "verified stop pattern",
            ),
            "NAV-STEPFREE-01": (
                "missing elevator icon", "absent display", "incomplete photo",
                "proof that the route is inaccessible",
            ),
        }.items():
            prohibitions = " ".join(by_id[case_id]["must_not"])
            for phrase in phrases:
                self.assertIn(phrase, prohibitions)
        blur = " ".join(by_id["IMG-BLUR-08"]["must"])
        for phrase in ("no image was attached/received", "user report", "not observed pixels"):
            self.assertIn(phrase, blur)
        # Pin every existing fictional turn, independently of changing rubrics.
        prompts = {case["id"]: case["turns"] for case in self.cases}
        self.assertEqual(hashlib.sha256(json.dumps(
            prompts, ensure_ascii=False, sort_keys=True
        ).encode()).hexdigest(),
            "d44cace3da29fe5cd57eaaf9303e1dd3567aa2ae28a7d8f5fe5d0f8967f4020f")

    def test_remaining_artifact_completeness_provenance_and_immutability(self):
        # Supplied artifact assertions, not independent session/freshness proof.
        path = ROOT / "evaluations/runs/2026-11-04-p0-remaining-transcripts.json"
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "501b8e62f0845d87580fe513d2f22eb7e6f30fe3bdf073e5bb07ad42f9166361")
        evidence = json.loads(raw)
        self.assertEqual(evidence["schema_version"], "1.0")
        self.assertEqual(evidence["skill_revision"],
                         "fe71d16f7d9da1aaa4083ff8284406bc5fffd436")
        self.assertIn("synthetic, offline, text-only", evidence["environment"])
        self.assertIn("Original first-turn test harness wrapper omitted", evidence["provenance"])
        models = {"gpt-6.1-sol": "Codex ACP read-only",
                  "gemini-3.8-flash": "Antigravity ACP plan"}
        ids = {"NAV-WRONGWAY-22", "NAV-STEPFREE-01", "IMG-BLUR-08",
               "IMG-CONFLICT-07", "LOC-CORRECT-09"}
        expected = {(case_id, model) for case_id in ids for model in models}
        samples = evidence["completed_samples"]
        self.assertEqual(len(samples), 10)
        self.assertEqual({(r["case_id"], r["model"]) for r in samples}, expected)
        fixtures = {c["id"]: c for c in self.cases}
        for run in samples:
            with self.subTest(case=run["case_id"], model=run["model"]):
                self.assertIs(run["fresh_independent_session"], True)
                self.assertEqual(run["host"], models[run["model"]])
                self.assertEqual(run["reasoning_effort"], "medium")
                self.assertEqual([turn["user"] for turn in run["turns"]],
                                 fixtures[run["case_id"]]["turns"])
                self.assertTrue(all(turn["assistant"].strip() for turn in run["turns"]))
                recovered = (run["model"] == "gemini-3.8-flash" and
                             run["case_id"] in {"IMG-CONFLICT-07", "LOC-CORRECT-09", "IMG-BLUR-08"})
                if recovered:
                    self.assertIn("nontruncated ACP run events (session/load empty)", run["source"])
                    self.assertIn("traveler prompts taken from public fixture", run["source"])
                else:
                    self.assertIn("ACP adapter session/load", run["source"])
        self.assertEqual(len(evidence["incomplete_attempts"]), 1)
        attempt = evidence["incomplete_attempts"][0]
        self.assertEqual((attempt["case_id"], attempt["model"]),
                         ("IMG-BLUR-08", "gemini-3.8-flash"))
        self.assertIs(attempt["response_present"], False)
        self.assertIn("does not count as a pass", attempt["reason"])
        self.assertEqual(attempt["attempt"], "first independent session")
        for pattern in (
            r"/(?:Users|home)/[A-Za-z0-9._-]+",
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
            r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
            r"gh[opusr]_[A-Za-z0-9]+",
            r'"(?:session_id|host_id|device_id|native_id)"\s*:',
            r"\b(?:[0-9][ -]?){13,19}\b",
        ):
            self.assertNotRegex(raw.decode(), pattern)

    def test_remaining_review_keeps_failure_retry_and_rerun_limits_explicit(self):
        # Documentation contract only; no model inference or live route proof.
        report_path = ROOT / "evaluations/runs/2026-11-04-p0-remaining-review.md"
        report = " ".join(report_path.read_text().split())
        for phrase in (
            "10 completed independent fresh case/model samples",
            "1 incomplete no-response Gemini IMG-BLUR attempt",
            "retry used a NEW session", "not a model-answer pass",
            "single turn", "not real traveler logs", "gpt-6.1-sol",
            "gemini-3.8-flash", "medium", "Offline, text-only",
            "completed nontruncated ACP run event streams",
            "Exact run timestamps were not recorded",
            "P0 critical unsupported paid-area advice",
            "not a known real-life station failure", "Noncritical scope caveat",
            "No actual image or official map",
            "Targeted post-fix independent reruns",
            "4 completed", "fresh independent model/case samples",
            "no P0 field-safety sign-off", "no live transit accuracy",
            "2026-11-04-p0-remaining-transcripts.json",
            "2026-11-04-p0-fresh-session-review.md",
        ):
            self.assertIn(phrase, report)
        for filename in ("README.md", "evaluations/README.md", "CHANGELOG.md"):
            self.assertIn(report_path.name, (ROOT / filename).read_text())
        # Check the new report's relative links resolve without network access.
        for target in re.findall(r"\]\(([^)]+)\)", report_path.read_text()):
            self.assertTrue((report_path.parent / target).is_file(), target)

    def test_remaining_postfix_artifact_provenance_and_sample_counts(self):
        # An archival integrity check, not a behavioral model benchmark.
        path = ROOT / "evaluations/runs/2026-11-04-p0-remaining-postfix-transcripts.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(data["precommit_head"],
                         "fe71d16f7d9da1aaa4083ff8284406bc5fffd436")
        for field, filename in (
            ("live_navigation_sha256", "live-navigation.md"),
            ("photo_orders_sha256", "photo-and-orders.md"),
        ):
            self.assertEqual(
                data[field],
                hashlib.sha256((ROOT / "references" / filename).read_bytes()).hexdigest()
            )
        expected = {
            ("NAV-WRONGWAY-22", "gpt-6.1-sol"): 2,
            ("NAV-WRONGWAY-22", "gemini-3.8-flash"): 2,
            ("NAV-STEPFREE-01", "gemini-3.8-flash"): 3,
            ("IMG-BLUR-08", "gemini-3.8-flash"): 1,
        }
        samples = data["completed_samples"]
        self.assertEqual(
            {(s["case_id"], s["model"]): len(s["turns"]) for s in samples}, expected
        )
        for sample in samples:
            self.assertIs(sample["fresh_session"], True)
            self.assertEqual(sample["effort"], "medium")
            for turn in sample["turns"]:
                self.assertTrue(turn["user"].strip())
                self.assertTrue(turn["assistant"].strip())
        self.assertEqual(len(data["incomplete_attempts"]), 1)
        incomplete = data["incomplete_attempts"][0]
        self.assertEqual(incomplete["case_id"], "IMG-BLUR-08")
        self.assertEqual(incomplete["model"], "gemini-3.8-flash")
        self.assertIn("without assistant message text", incomplete["reason"])
        raw = path.read_text(encoding="utf-8")
        for sensitive_pattern in (
            r"/(?:Users|home)/[A-Za-z0-9._-]+",
            r"gh[opusr]_[A-Za-z0-9]+",
            r'"(?:session_id|host_id|device_id|native_id)"\s*:',
        ):
            self.assertNotRegex(raw, sensitive_pattern)
        report = (ROOT / "evaluations/runs/2026-11-04-p0-remaining-review.md").read_text()
        self.assertIn(path.name, report)
        self.assertIn("not reproduced after the fix", report)
        self.assertIn("not a full test", report)

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
