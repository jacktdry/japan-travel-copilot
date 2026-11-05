"""Static integrity/provenance checks; never model inference or LLM grading."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "evaluations/runs/2026-11-05-source-backed-acp-initial-transcripts.json"
SNAPSHOTS = {
    "fixture_sha256": "c60a13df6e43e7f140632c380f9259d9b683927f41cb99124db01cd5a2ba9a27",
    "skill_sha256": "8c9bc01120c269e7ca20dfe389b18a255349d7d998a100ac842d9b0a882e0b54",
    "evidence_reference_sha256": "a559cb62b5dffe19041e28b92ae248b5295a72d0725b2c8413173975fa0c44f5",
    "navigation_reference_sha256": "55a4b4751f0fdc2e2036e105460b8f74a9fdf2d376ea64d58a1ef01c3fe7dabb",
}


def _parse_utc_timestamp(value):
    """Parse recorded UTC-Z timestamps with 1–6 fractional digits on Python 3.9+."""
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")


class SourceBackedArchiveTests(unittest.TestCase):
    def setUp(self):
        self.raw = ARCHIVE.read_text(encoding="utf-8")
        self.archive = json.loads(self.raw)
        self.fixture = json.loads((ROOT / "evaluations/source-backed-airport.json").read_text())

    def test_fixed_archive_answers_and_original_snapshots_are_preserved(self):
        # Whole-file pin protects original answers, commentary, wrapper and metadata.
        self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                         "7e619b66d01c7c80ef76fdaa78a7cf859c0179ae044eb32acf4a2b3c25ff5b93")
        for key, expected in SNAPSHOTS.items():
            self.assertEqual(self.archive[key], expected)
        for key, filename in (("fixture_sha256", "evaluations/source-backed-airport.json"),
                              ("skill_sha256", "SKILL.md")):
            self.assertEqual(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(),
                             SNAPSHOTS[key])
        # Historical reference hashes describe pre-fix input, not the repaired files.
        self.assertEqual(self.archive["head_before_run"],
                         "86a90d432d7a2e4ea6bfba6cf9fdc4f858d3b80e")
        self.assertEqual(self.archive["case_id"], self.fixture["id"])

    def test_two_independent_provider_dialogues_preserve_exact_injected_input(self):
        runs = self.archive["runs"]
        self.assertEqual([(r["model"], r["adapter"], r["mode"], r["effort"])
                          for r in runs], [
            ("gpt-6.1-sol", "Codex ACP", "read-only", "medium"),
            ("gemini-3.8-flash", "Antigravity ACP", "plan", "medium"),
        ])
        for run, roles in zip(runs, [
                ["user", "assistant", "assistant", "user", "assistant"],
                ["user", "assistant", "user", "assistant"]]):
            with self.subTest(adapter=run["adapter"]):
                self.assertTrue(run["fresh_session"])
                messages = run["messages"]
                self.assertEqual([m["role"] for m in messages], roles)
                self.assertTrue(all(set(m) == {"role", "text"} and m["text"].strip()
                                    for m in messages))
                users = [m["text"] for m in messages if m["role"] == "user"]
                prefix, payload = users[0].split("STATIC EVIDENCE CARD:\n", 1)
                self.assertIn("No web access or live transit tools", prefix)
                self.assertIn("NEW isolated fictional conversation", prefix)
                card, turn = payload.split("\n\nTRAVELER, turn 1:\n", 1)
                self.assertEqual(json.loads(card), {
                    "provenance": self.fixture["provenance"],
                    "evidence_card": self.fixture["evidence_card"],
                })
                self.assertEqual(turn, self.fixture["turns"][0])
                self.assertEqual(users[1], self.fixture["turns"][1])
                self.assertEqual(len(run["run_start_end_utc"]), 2)
                for start, end in run["run_start_end_utc"]:
                    self.assertLess(_parse_utc_timestamp(start),
                                _parse_utc_timestamp(end))
                self.assertEqual(run["start_utc"], run["run_start_end_utc"][0][0])
                self.assertEqual(run["end_utc"], run["run_start_end_utc"][-1][1])

    def test_complete_adapter_replay_is_distinct_from_truncated_event_ring(self):
        codex, gemini = self.archive["runs"]
        for run in (codex, gemini):
            self.assertEqual(run["source"], "ACP session/load complete adapter-owned history")
            self.assertIs(run["adapter_history_truncated"], False)
            self.assertEqual(run["host_filesystem_audit"], "not performed")
        self.assertIs(codex["run1_event_ring_truncated"], True)
        self.assertIs(gemini["run1_event_ring_truncated"], False)
        self.assertIn("先讀取指定的三份指南", codex["messages"][1]["text"])
        self.assertEqual(codex["sandbox"], "unrecorded")
        self.assertIs(gemini["sandbox"], True)
        for phrase in ("session/update", "gemini-3.8-flash", "sandbox=true",
                       "stale gemini-4-argon", "sandbox=false", "uncertain"):
            self.assertIn(phrase, gemini["model_settings_provenance"])

    def test_public_archive_has_no_common_secret_path_or_host_identifiers(self):
        # Sanitation checks for known identifier/credential formats, not a host audit.
        for pattern in (r"/(?:Users|home)/", r"file://", r"plugin://",
                        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                        r"gh[opusr]_[A-Za-z0-9]+", r"github_pat_[A-Za-z0-9_]+",
                        r"sk-[A-Za-z0-9_-]{16,}", r"AKIA[A-Z0-9]{16}",
                        r"-----BEGIN .*PRIVATE KEY-----",
                        r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b",
                        r'"(?:session_id|sessionId|host_id|hostId|thread_id|threadId|transcript_url|api_key|access_token)"'):
            self.assertNotRegex(self.raw, pattern)


    def test_partial_postfix_archive_keeps_blocked_provider_unassessed(self):
        # This validates an archived observation, NOT whether any model is safe.
        path = ROOT / "evaluations/runs/2026-11-05-source-backed-postfix-transcripts.json"
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "faae1b2fea53ad61c19b3af418f7a83f6bf7a279838d4e2d681548ca52001186")
        data = json.loads(raw)
        self.assertEqual(data["status"], "partial_postfix_observation")
        self.assertEqual(data["case_id"], self.fixture["id"])
        self.assertEqual(data["fixture_sha256"], SNAPSHOTS["fixture_sha256"])
        self.assertEqual(data["original_pre_fix_archive_sha256"],
                         hashlib.sha256(ARCHIVE.read_bytes()).hexdigest())
        self.assertEqual(data["revised_navigation_sha256"],
                         "8bdb456376e268190fba2e9e67fbdf2c285bb672283d44cf3fa2c262e18c5b57")
        self.assertEqual(data["revised_evidence_sha256"],
                         "44b013948ceba8577502b70c05e1d99a823c4f475819ffd55e189d7c6336cb64")
        self.assertEqual(len(data["samples"]), 2)
        codex, gemini = data["samples"]
        self.assertEqual((codex["adapter"], codex["status"], codex["mode"]),
                         ("Codex ACP", "completed", "read-only"))
        self.assertIs(codex["fresh_independent_session"], True)
        self.assertIs(codex["history_truncated"], False)
        self.assertEqual([m["role"] for m in codex["messages"]],
                         ["user", "assistant", "assistant", "user", "assistant"])
        self.assertEqual(codex["messages"][0]["text"],
                         self.archive["runs"][0]["messages"][0]["text"])
        self.assertEqual(codex["messages"][-2]["text"],
                         self.archive["runs"][0]["messages"][-2]["text"])
        self.assertEqual(len(codex["run_time_utc"]), 2)
        for start, end in codex["run_time_utc"]:
            self.assertLess(_parse_utc_timestamp(start),
                            _parse_utc_timestamp(end))
        self.assertEqual(codex["host_filesystem_audit"], "not performed")
        self.assertEqual(gemini["adapter"], "Antigravity ACP")
        self.assertEqual(gemini["status"], "blocked_before_run")
        self.assertEqual(gemini["model_response_count"], 0)
        self.assertEqual(gemini["run_time_utc"], [])
        self.assertNotIn("messages", gemini)
        self.assertIn("neither a model failure nor a pass", gemini["reason"])
        for pattern in (r"/(?:Users|home)/", r"file://",
                        r"gh[opusr]_[A-Za-z0-9]+",
                        r'"(?:session_id|host_id|run_id|access_token)"'):
            self.assertNotRegex(raw.decode("utf-8"), pattern)
        report = ROOT / "evaluations/runs/2026-11-05-source-backed-postfix-review.md"
        self.assertIn(path.name, report.read_text(encoding="utf-8"))
        for fname in ("README.md", "CHANGELOG.md", "evaluations/README.md"):
            self.assertIn(report.name, (ROOT / fname).read_text(encoding="utf-8"))

    def test_gemini_recheck_preserves_exact_inputs_complete_runs_and_limits(self):
        # Static archive/report contract only; never LLM behavior acceptance.
        path = ROOT / "evaluations/runs/2026-11-05-source-backed-gemini-recheck-transcripts.json"
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "270168dc16845c9aeac3dee25c53d3ed72d0fd393c1553ea385952a3ef94cc5a")
        data = json.loads(raw)
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(data["case_id"], self.fixture["id"])
        self.assertEqual(data["status"], "completed_single_provider_postfix_rerun")
        self.assertEqual(data["baseline_head"],
                         "ad3718173bc20cb903798b16f1ed624ce5035920")
        messages = data["messages"]
        self.assertEqual([m["role"] for m in messages],
                         ["user", "assistant", "user", "assistant"])
        self.assertTrue(all(set(m) == {"role", "text"} and m["text"].strip()
                            for m in messages))
        # Exact wrapper/card/turn parity with both historical provider inputs.
        users = [m["text"] for m in messages if m["role"] == "user"]
        for baseline in self.archive["runs"]:
            self.assertEqual(users, [m["text"] for m in baseline["messages"]
                                     if m["role"] == "user"])
        self.assertIs(data["adapter_history_truncated"], False)
        self.assertEqual(data["provenance"]["source"],
                         "ACP adapter-owned session/load complete replay")
        self.assertEqual(data["provenance"]["host_filesystem_audit"], "not performed")
        self.assertEqual(len(data["runs"]), 2)
        previous_end = None
        for turn, run in enumerate(data["runs"], 1):
            self.assertEqual(run["turn"], turn)
            self.assertEqual(run["status"], "completed")
            self.assertIs(run["run_event_ring_truncated"], False)
            start = _parse_utc_timestamp(run["started_at_utc"])
            end = _parse_utc_timestamp(run["ended_at_utc"])
            self.assertEqual(start.date().isoformat(), data["date_local"])
            self.assertLess(start, end)
            if previous_end is not None:
                self.assertLess(previous_end, start)
            previous_end = end
        config = data["model_configuration"]
        self.assertEqual((config["adapter"], config["configured_model"],
                          config["mode"], config["effort"]),
                         ("Antigravity ACP", "gemini-3.8-flash", "plan", "medium"))
        self.assertIs(config["sandbox_configured"], True)
        self.assertIs(config["configuration_update_observed"], True)
        self.assertEqual(config["post_run_runtime_state_projection"],
                         {"model": "gemini-4-argon", "mode": "default", "sandbox": False})
        self.assertIn("cannot be independently proven", config["configuration_discrepancy"])
        self.assertEqual(data["prior_blocker"]["prior_submission"], "blocked_before_run")
        self.assertEqual(data["prior_blocker"]["this_submission"], "accepted_and_completed")
        self.assertEqual(data["prior_blocker"]["root_cause"], "not established")
        report = path.with_name("2026-11-05-source-backed-gemini-recheck-review.md")
        review = report.read_text(encoding="utf-8")
        for phrase in (path.name, hashlib.sha256(raw).hexdigest(), "5/6",
                       "Partially unmet", "2026-08-01", "2026-03-14",
                       "P0 NO-GO", "not a complete rubric pass", "not conclusively repaired"):
            self.assertIn(phrase, review)
        for text in (raw.decode("utf-8"), review):
            for pattern in (r"/(?:Users|home|Volumes)/", r"/(?:private/)?var/folders/",
                            r"/(?:private/)?tmp/", r"file://", r"plugin://", r"\b[A-Za-z]:\\",
                            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                            r"gh[opusr]_[A-Za-z0-9]+", r"github_pat_[A-Za-z0-9_]+",
                            r"sk-[A-Za-z0-9_-]{16,}", r"AKIA[A-Z0-9]{16}",
                            r"-----BEGIN .*PRIVATE KEY-----",
                            r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b",
                            r'"(?:session_?[Ii]d|native_?[Ii]d|run_id|host_id|device_id|thread_id|transcript_url|api_key|access_token)"\s*:'):
                self.assertNotRegex(text, pattern)
        # Reporting limits protect against promoting this archive to acceptance.
        for fname in ("README.md", "CHANGELOG.md", "evaluations/README.md",
                      "evaluations/runs/2026-11-05-source-backed-postfix-review.md"):
            self.assertIn(report.name, (ROOT / fname).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
