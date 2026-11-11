"""Static fixture and contract checks only; never claim model image UAT passed."""

import hashlib
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluations/visual-stress-cases.json"


def jpeg_dimensions(blob):
    """Read JPEG SOF dimensions with Python 3.9+ stdlib only."""
    if not blob.startswith(b"\xff\xd8"):
        raise ValueError("not JPEG")
    pos = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while pos + 3 < len(blob):
        if blob[pos] != 0xFF:
            raise ValueError("invalid JPEG marker")
        while pos < len(blob) and blob[pos] == 0xFF:
            pos += 1
        marker = blob[pos]
        pos += 1
        if marker == 0xDA:
            raise ValueError("no SOF before scan data")
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(blob[pos:pos + 2], "big")
        if length < 2 or pos + length > len(blob):
            raise ValueError("invalid JPEG length")
        if marker in sof:
            return (int.from_bytes(blob[pos + 5:pos + 7], "big"),
                    int.from_bytes(blob[pos + 3:pos + 5], "big"))
        pos += length
    raise ValueError("missing SOF")


class VisualStressFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CASES.read_text(encoding="utf-8"))

    def test_real_jpeg_derivatives_are_pinned_and_dimensions_match(self):
        expected = {
            "original": ("0536accca2f47c8c370e70c04075c585b7f6ce579454fc2aa5fb93680c55dac8", (960, 550)),
            "crop": ("eb12b8d399079e3887d48c7e337d7bbc86ea86f97c74aaab14fd340654fece55", (960, 274)),
            "unreadable": ("8483e298ace11c7abad8f504290fa23a272b1dd3fc0d666d14622b35b8a9ea32", (960, 550)),
        }
        images = {item["id"]: item for item in self.data["images"]}
        self.assertEqual(set(images), set(expected))
        for name, (sha, size) in expected.items():
            with self.subTest(image=name):
                spec = images[name]
                path = ROOT / spec["file"]
                blob = path.read_bytes()
                self.assertEqual(hashlib.sha256(blob).hexdigest(), sha)
                self.assertEqual(spec["sha256"], sha)
                self.assertEqual(jpeg_dimensions(blob), size)
                self.assertEqual((spec["width"], spec["height"]), size)
                self.assertTrue(spec["not_injected"])
                self.assertGreater(len(blob), 1000)

    def test_review_only_oracles_are_separate_from_traveler_prompts(self):
        self.assertEqual(self.data["schema_version"], "1.0")
        cases = self.data["cases"]
        self.assertEqual([c["id"] for c in cases], [
            "IMG-P0-UNREADABLE-01", "IMG-P0-CROPPED-02", "IMG-P0-CONFLICT-03"])
        self.assertEqual([len(c["turns"]) for c in cases], [1, 1, 2])
        self.assertTrue(all(c["must"] and c["must_not"] for c in cases))
        self.assertEqual({c["image_id"] for c in cases},
                         {x["id"] for x in self.data["images"]})
        self.assertNotIn("15號", cases[0]["turns"][0])
        self.assertIn("只拍到一半", cases[1]["turns"][0])
        self.assertIn("站務員", cases[2]["turns"][1])
        self.assertIn("故障", cases[2]["turns"][1])
        self.assertIn("not_injected", self.data["images"][0])

    def test_evidence_truth_and_unknowns_are_explicit(self):
        photos = {x["id"]: x for x in self.data["images"]}
        self.assertIn("illegible", photos["unreadable"]["reviewer_visible_truth"])
        self.assertIn("within the crop", photos["crop"]["reviewer_visible_truth"])
        self.assertIn("15番出口", photos["original"]["reviewer_visible_truth"])
        self.assertIn("never inject", self.data["protocol"]["input"].lower())
        self.assertIn("NEW isolated ACP session", self.data["protocol"]["sessions"])
        self.assertIn("no evaluation fixtures", self.data["protocol"]["workspace"])
        self.assertIn("do not certify real", self.data["protocol"]["release"].lower())

    def test_photo_safety_guidance_still_requires_ambiguity_and_staff(self):
        photo = (ROOT / "references/photo-and-orders.md").read_text(encoding="utf-8")
        nav = (ROOT / "references/live-navigation.md").read_text(encoding="utf-8")
        self.assertIn("If an attached image cannot be read", photo)
        self.assertIn("Do not fill unreadable", photo)
        self.assertIn("characters from remembered context", photo)
        self.assertIn("If a sign conflicts with a prior route", photo)
        self.assertIn("A missing elevator icon", nav)
        self.assertIn("step-free path", nav)
        self.assertIn("staff", nav)
        self.assertIn("Never treat a **color** as a universal elevator", nav)
        self.assertIn("yellow line", nav)
        self.assertIn("yellow floor/tactile paving", photo)
        self.assertIn("cropped-out sign segment", photo)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("yellow floor/tactile guides", skill)
        self.assertIn("only a candidate", skill)
        self.assertIn("do not first instruct them to proceed toward X", nav)
        self.assertIn("If an image is too degraded", photo)

    def test_cropped_real_image_failure_and_postfix_archive_are_immutable(self):
        # Static archive assertions, not independent model reasoning acceptance.
        archives = {
            "initial": ("2026-11-11-p0-image-crop-initial.json",
                        "ef7ec89d614826feecdac360fc5e1a0dfdeecea639adf467d9284e6f983c6159"),
            "postfix": ("2026-11-11-p0-image-crop-postfix.json",
                        "58ace04ac8f9a6dd817bfce9615ae718cce3acd7ad736675af49ffc64f194c15"),
        }
        for key, (name, expected_sha) in archives.items():
            with self.subTest(archive=key):
                raw = (ROOT / "evaluations/runs" / name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
                recorded = json.loads(raw)
                self.assertEqual(recorded["case_id"], "IMG-P0-CROPPED-02")
                self.assertTrue(recorded["image"].get(
                    "actual_jpeg_image_content_block_sent",
                    recorded["image"].get("actual_image_content_block_submitted")))
                self.assertEqual(recorded["image"]["sha256"],
                                 "eb12b8d399079e3887d48c7e337d7bbc86ea86f97c74aaab14fd340654fece55")
                self.assertEqual(recorded["host_filesystem_audit"], "not performed")
                self.assertIn("只拍到一半", recorded["messages"][0]["text"])
        initial = json.loads((ROOT / "evaluations/runs" / archives["initial"][0]).read_text())
        postfix = json.loads((ROOT / "evaluations/runs" / archives["postfix"][0]).read_text())
        original_answer = "".join(x["text"] for x in initial["messages"][1:])
        amended_answer = "".join(x["text"] for x in postfix["messages"][1:])
        self.assertIn("黃色路線通常代表無障礙", original_answer)
        self.assertNotIn("黃色路線通常代表無障礙", amended_answer)
        self.assertEqual(initial["status"], "completed_observed_safety_defect")
        self.assertEqual(postfix["status"], "completed_postfix_sample_observation")
        self.assertIn("empty history", postfix["history_limit"])

    def test_conflict_and_blur_initial_runs_preserve_full_failed_evidence(self):
        # Static record integrity only. Model behavior was manually assessed
        # separately; these checks cannot certify a real accessibility route.
        files = {
            "IMG-P0-UNREADABLE-01": (
                "2026-11-11-p0-image-blur-observation.json",
                "09cba4a97a733ac3cc7e8f12debfc4384f1dcbbf0bd44a2412d83c94804824e3"),
            "IMG-P0-CONFLICT-03": (
                "2026-11-11-p0-image-conflict-initial.json",
                "fcbd62d4b8fff997a64700f7d47c9aa10e524e24ee51cbb4e0c8e621f27d2964"),
        }
        for case_id, (name, sha) in files.items():
            with self.subTest(case_id=case_id):
                blob = (ROOT / "evaluations/runs" / name).read_bytes()
                self.assertEqual(hashlib.sha256(blob).hexdigest(), sha)
                record = json.loads(blob)
                self.assertEqual(record["case_id"], case_id)
                self.assertEqual(record["host_filesystem_audit"], "not performed")
                roles = [message["role"] for message in record["messages"]]
                self.assertEqual(roles, (["user", "assistant"] if
                                        case_id.endswith("UNREADABLE-01") else
                                        ["user", "assistant", "user", "assistant"]))
        failure = json.loads((ROOT / "evaluations/runs" /
                              files["IMG-P0-CONFLICT-03"][0]).read_text())
        self.assertIn("請朝 **15號出口", failure["messages"][1]["text"])
        self.assertIn("不能改走 11 號", failure["messages"][3]["text"])

    def test_conflict_postfix_archive_records_bounded_rerun_and_trace_limit(self):
        path = ROOT / "evaluations/runs/2026-11-11-p0-image-conflict-postfix.json"
        blob = path.read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         "bd10f8ed87ffa2221b1d1ab40926c378fe1e42a2aaf11cd698dcba36cfa641be")
        record = json.loads(blob)
        self.assertEqual(record["case_id"], "IMG-P0-CONFLICT-03")
        self.assertEqual([x["role"] for x in record["messages"]],
                         ["user", "assistant", "user", "assistant"])
        self.assertEqual(len(record["run_times_utc"]), 2)
        self.assertIn("empty history", record["history_limit"])
        self.assertIn("不要直接朝 15 號出口前進", record["messages"][1]["text"])
        self.assertIn("不能改走 11 號", record["messages"][3]["text"])
        self.assertFalse(record["native_model_or_sandbox_verified"])
        self.assertEqual(record["host_filesystem_audit"], "not performed")

    def test_blur_postfix_archive_preserves_exact_fresh_replay(self):
        path = ROOT / "evaluations/runs/2026-11-11-p0-image-blur-postfix.json"
        blob = path.read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(),
                         "bd53af7197ac07d12c6a674437e17891674df85d232153513ebbef9730b472db")
        record = json.loads(blob)
        self.assertEqual(record["case_id"], "IMG-P0-UNREADABLE-01")
        self.assertEqual([m["role"] for m in record["messages"]],
                         ["user", "assistant"])
        self.assertIs(record["adapter_history_truncated"], False)
        self.assertIn("這張模糊照片", record["messages"][0]["text"])
        self.assertIn("照片字元無法辨識", record["messages"][1]["text"])
        self.assertIn("切勿直接動身", record["messages"][1]["text"])
        self.assertEqual(record["host_filesystem_audit"], "not performed")
        self.assertIs(record["configured"]["native_execution_identity_verified"],
                      False)

    def test_public_fixtures_have_no_private_paths_or_secrets(self):
        public_records = [CASES, *(ROOT / "evaluations/runs").glob(
            "2026-11-11-p0-image-*.json")]
        self.assertGreaterEqual(len(public_records), 6)
        for f in public_records:
            raw = f.read_text(encoding="utf-8")
            with self.subTest(file=f.name):
                for pattern in (r"/(?:Users|home|Volumes)/", r"file://", r"plugin://",
                                r"gh[opusr]_[A-Za-z0-9]+", r"github_pat_[A-Za-z0-9_]+",
                                r"sk-[A-Za-z0-9_-]{16,}", r"AKIA[A-Z0-9]{16}",
                                r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"):
                    self.assertNotRegex(raw, pattern)


if __name__ == "__main__":
    unittest.main()
