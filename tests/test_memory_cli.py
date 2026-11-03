"""Real subprocess roundtrips and failure invariants using fictional state."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run.py"
SPEC = importlib.util.spec_from_file_location("trip_helper", SCRIPT)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def example():
    return {
        "schema_version": "0.2", "revision": 0, "mode": "pre_trip",
        "profile": {
            "destinations": {"value": ["Example City", "Example Harbor"], "source": "user"},
            "dates": {"value": "undecided", "source": "user"},
            "travelers": {"value": 2, "source": "user"},
        },
        "raw_snapshot": {
            "destinations": {"value": ["Example City", "Example Harbor"], "source": "user"},
        },
    }


class MemoryCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="trip-cli-test-")
        self.addCleanup(self.temporary.cleanup)
        # Tests explicitly choose a physical path, including on systems with /var aliases.
        self.directory = Path(self.temporary.name).resolve()
        self.path = self.directory / "example.travel-state.json"

    def request(self, action="save", **changes):
        request = {"skill_action": action, "state_path": str(self.path), "consent": True}
        if action in {"save", "import", "delete", "forget"}:
            request.update(confirmed=True, expected_revision=None)
        if action in {"save", "import"}:
            request["state"] = example()
        request.update(changes)
        return request

    def run_cli(self, request=None, raw=None, cwd=None, args=()):
        if raw is None:
            raw = json.dumps(request, ensure_ascii=False).encode("utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args], input=raw,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, timeout=10,
        )
        self.assertEqual(result.stderr, b"")
        output = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0 if output["ok"] else 2)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        return output

    def reject(self, request, code):
        result = self.run_cli(request)
        self.assertEqual(result, {
            "ok": False, "error": {"code": code, "message": HELPER.MESSAGES[code]},
        })
        return result

    def test_status_missing_is_read_only_and_does_not_create_directory_or_file(self):
        self.assertEqual(self.run_cli(self.request("status")), {
            "ok": True, "skill_action": "status", "exists": False, "revision": None,
        })
        self.assertEqual(list(self.directory.iterdir()), [])
        missing = self.directory / "missing" / "example.travel-state.json"
        self.reject(self.request("status", state_path=str(missing)), "IO_ERROR")
        self.assertFalse(missing.parent.exists())

    def test_save_load_across_subprocesses_and_different_working_directories(self):
        self.assertEqual(self.run_cli(self.request()), {
            "ok": True, "skill_action": "save", "revision": 1,
        })
        expected = example()
        expected["revision"] = 1
        self.assertEqual(self.run_cli(self.request("load"), cwd=self.directory)["state"], expected)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), expected)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertEqual(self.path.stat().st_nlink, 1)
        self.assertEqual(self.run_cli(self.request("status"))["revision"], 1)
        self.assertNotIn("state", self.run_cli(self.request("status")))

    def test_export_import_roundtrip_is_stdout_only_and_revisions_are_local(self):
        self.run_cli(self.request())
        self.run_cli(self.request(expected_revision=1))
        before = self.path.read_bytes()
        exported = self.run_cli(self.request("export"))["state"]
        self.assertEqual(exported["revision"], 2)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.directory.iterdir()), [self.path])
        other = self.directory / "copy.travel-state.json"
        self.assertEqual(self.run_cli(self.request("import", state=exported, state_path=str(other)))["revision"], 1)
        restored = self.run_cli(self.request("load", state_path=str(other)))["state"]
        exported["revision"] = 1
        self.assertEqual(restored, exported)
        self.assertEqual(self.path.read_bytes(), before)

    def test_no_file_access_or_writes_without_literal_opt_in(self):
        self.run_cli(self.request())
        before = self.path.read_bytes()
        for action in ("status", "save", "load", "export", "import", "delete", "forget"):
            for consent in (False, None, "true", 1):
                with self.subTest(action=action, consent=consent):
                    self.reject(self.request(action, consent=consent), "CONSENT_REQUIRED")
            request = self.request(action)
            del request["consent"]
            self.reject(request, "CONSENT_REQUIRED")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.directory.iterdir()), [self.path])
        with patch.object(HELPER, "open_parent", side_effect=AssertionError("file access")):
            with self.assertRaises(HELPER.Failure) as caught:
                HELPER.execute(self.request(consent=False))
            self.assertEqual(caught.exception.code, "CONSENT_REQUIRED")

    def test_all_mutations_require_confirmation_and_explicit_revision(self):
        for action in ("save", "import", "delete", "forget"):
            for confirmed in (False, None, "true", 1):
                self.reject(self.request(action, confirmed=confirmed), "CONFIRMATION_REQUIRED")
            for field, code in (("confirmed", "CONFIRMATION_REQUIRED"), ("expected_revision", "INVALID_REQUEST")):
                request = self.request(action)
                del request[field]
                self.reject(request, code)
            for revision in (0, -1, True, "1", 1.0, 2**53):
                self.reject(self.request(action, expected_revision=revision), "INVALID_REQUEST")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_revision_conflicts_preserve_data_and_confirmed_delta_replaces(self):
        self.run_cli(self.request())
        before = self.path.read_bytes()
        for action in ("save", "import", "delete", "forget"):
            for revision in (None, 2):
                self.reject(self.request(action, expected_revision=revision), "REVISION_CONFLICT")
        self.assertEqual(self.path.read_bytes(), before)
        changed = example()
        changed["profile"]["travelers"]["value"] = 3
        self.assertEqual(self.run_cli(self.request(state=changed, expected_revision=1))["revision"], 2)
        loaded = self.run_cli(self.request("load"))["state"]
        self.assertEqual(loaded["profile"]["travelers"]["value"], 3)
        self.assertEqual(loaded["raw_snapshot"], changed["raw_snapshot"])
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_delete_and_forget_only_selected_file(self):
        other = self.directory / "unrelated.txt"
        other.write_text("fictional unrelated file", encoding="utf-8")
        for action in ("delete", "forget"):
            self.run_cli(self.request())
            self.assertTrue(self.run_cli(self.request(action, expected_revision=1))["deleted"])
            self.assertFalse(self.path.exists())
            self.assertEqual(other.read_text(encoding="utf-8"), "fictional unrelated file")
            self.reject(self.request(action), "NOT_FOUND")

    def test_missing_reads_fail_without_creating_state(self):
        for action in ("load", "export"):
            self.reject(self.request(action), "NOT_FOUND")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_invalid_json_and_request_shapes_produce_stable_errors(self):
        for raw in (
            b"", b"{", b"{} {}", b"\xff", b'{"a":1,"a":2}',
            b'{"state":{"mode":"a","mode":"b"}}', b'{"a":NaN}',
            b'{"a":Infinity}', b" " * (HELPER.LIMIT + 1), b"[" * 1100,
        ):
            self.assertEqual(self.run_cli(raw=raw)["error"]["code"], "INVALID_JSON")
        for value in (None, [], "save", 1, {}, {"skill_action": []}):
            self.reject(value, "INVALID_REQUEST")
        self.reject(self.request("unknown"), "INVALID_REQUEST")
        self.reject(self.request(extra="not supported"), "INVALID_REQUEST")
        self.reject(self.request("export", output_path="anything"), "INVALID_REQUEST")
        self.assertEqual(self.run_cli(self.request(), args=("--path",))["error"]["code"], "INVALID_REQUEST")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_schema_rejects_invalid_types_unknown_fields_and_versions(self):
        invalid = [None, [], {}, {**example(), "schema_version": "0.1"}]
        for field in ("profile", "raw_snapshot"):
            for value in (None, [], {"passport_number": {"value": "REDACTED", "source": "user"}}):
                invalid.append({**example(), field: value})
        for value in (True, -1, 1.5, 2**53):
            invalid.append({**example(), "revision": value})
        for value in ("invalid", [], None):
            invalid.append({**example(), "mode": value})
        bad_facts = [
            {}, [], {"value": "city"}, {"source": "user"},
            {"value": {}, "source": "user"}, {"value": 2, "source": "user"},
            {"value": "city", "source": "guessed"}, {"value": "city", "source": []},
            {"value": "city", "source": "user", "token": "REDACTED"},
            {"value": ["city", 2], "source": "user"},
            {"value": "x" * 1001, "source": "user"},
            {"value": ["city"] * 21, "source": "user"},
            {"value": "line\nbreak", "source": "user"},
            {"value": "city", "source": "verified"},
            {"value": "city", "source": "user", "evidence": "source"},
        ]
        for fact in bad_facts:
            state = example()
            state["profile"]["destinations"] = fact
            invalid.append(state)
        for value in (True, 0, 101, "2", [2]):
            state = example()
            state["profile"]["travelers"]["value"] = value
            invalid.append(state)
        invalid.append({**example(), "arbitrary_metadata": {}})
        for state in invalid:
            with self.subTest(state=state):
                self.reject(self.request(state=state), "INVALID_SCHEMA")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_optional_unknowns_multicity_and_provenance_roundtrip(self):
        state = example()
        state["profile"]["travelers"]["value"] = None
        state["profile"]["luggage"] = {"value": None, "source": "user"}
        state["profile"]["interests"] = {"value": "possibly museums", "source": "inferred"}
        state["profile"]["destination"] = {
            "value": "Example Museum", "source": "verified",
            "evidence": "Fictional official board supplied for this test",
            "checked_at": "2030-01-02T12:00:00+09:00",
        }
        self.run_cli(self.request(state=state))
        state["revision"] = 1
        self.assertEqual(self.run_cli(self.request("load"))["state"], state)
        for timestamp in ("2030-01-02", "2030-01-02T12:00:00", "invalid"):
            bad = deepcopy(state)
            bad["profile"]["destination"]["checked_at"] = timestamp
            self.reject(self.request(state=bad, expected_revision=1), "INVALID_SCHEMA")
        for source in ("inferred", "verified"):
            bad = deepcopy(state)
            bad["raw_snapshot"]["destinations"]["source"] = source
            self.reject(self.request(state=bad, expected_revision=1), "INVALID_SCHEMA")

    def test_sensitive_fields_and_obvious_sensitive_values_are_rejected(self):
        for section in ("profile", "raw_snapshot"):
            for field in ("token", "api_key", "passport", "payment", "booking_code", "address"):
                state = example()
                state[section][field] = {"value": "REDACTED", "source": "user"}
                self.reject(self.request(state=state), "INVALID_SCHEMA")
            for value in (
                "passport: FAKE", "護照：假資料", "password=FAKE", "api_key: FAKE",
                "access token: FAKE", "token: FAKE", "booking reference: FAKE", "訂位代碼：假資料",
                "credit card: FAKE", "4111 1111 1111 1111",
            ):
                state = example()
                state[section]["destinations"] = {"value": value, "source": "user"}
                result = self.reject(self.request(state=state), "SENSITIVE_DATA")
                self.assertNotIn(value, json.dumps(result, ensure_ascii=False))
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_rejected_update_and_invalid_stored_content_are_not_rewritten(self):
        self.run_cli(self.request())
        before = self.path.read_bytes()
        state = example()
        state["profile"]["dates"]["value"] = "passport: FAKE"
        self.reject(self.request(state=state, expected_revision=1), "SENSITIVE_DATA")
        self.assertEqual(self.path.read_bytes(), before)
        for raw, error in ((b"x" * (HELPER.LIMIT + 1), "INVALID_JSON"),
                           (json.dumps({**state, "revision": 1}).encode(), "SENSITIVE_DATA")):
            self.path.write_bytes(raw)
            self.reject(self.request("load"), error)
            self.assertEqual(self.path.read_bytes(), raw)
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_paths_must_be_explicit_absolute_external_and_unambiguous(self):
        for path in (None, "", "example.travel-state.json", "~/example.travel-state.json",
                     str(self.directory / "other.json"), str(self.directory) + "/../example.travel-state.json",
                     str(self.directory) + "/./example.travel-state.json", str(self.directory) + "//example.travel-state.json",
                     str(self.directory) + "/.git/example.travel-state.json", "/nul\x00.travel-state.json"):
            self.reject(self.request(state_path=path), "INVALID_PATH")
        self.reject(self.request(state_path=str(ROOT / "blocked.travel-state.json")), "UNSAFE_PATH")
        for marker in (".git", "SKILL.md"):
            nested = self.directory / marker.replace(".", "")
            nested.mkdir()
            (nested / marker).write_text("fixture", encoding="utf-8")
            child = nested / "data"
            child.mkdir()
            self.reject(self.request(state_path=str(child / "blocked.travel-state.json")), "UNSAFE_PATH")
            self.assertEqual(list(child.iterdir()), [])
        self.assertFalse(self.path.exists())

    def test_symlink_target_and_parent_are_rejected_for_every_action(self):
        real = self.directory / "real"
        real.mkdir(mode=0o700)
        target = real / "real.travel-state.json"
        target.write_text("unrelated data", encoding="utf-8")
        os.chmod(target, 0o600)
        self.path.symlink_to(target)
        alias = self.directory / "alias"
        alias.symlink_to(real, target_is_directory=True)
        for action in ("status", "load", "export", "save", "import", "delete", "forget"):
            for path in (self.path, alias / "new.travel-state.json"):
                self.reject(self.request(action, state_path=str(path)), "UNSAFE_PATH")
        self.assertEqual(target.read_text(encoding="utf-8"), "unrelated data")
        self.assertEqual(list(real.iterdir()), [target])
        self.assertTrue(self.path.is_symlink())
        self.path.unlink()
        self.path.symlink_to(real / "missing.travel-state.json")
        self.reject(self.request(), "UNSAFE_PATH")

    def test_hardlinks_fifo_directories_and_nonprivate_files_are_rejected(self):
        self.run_cli(self.request())
        original = self.path.read_bytes()
        hardlink = self.directory / "hardlink.travel-state.json"
        os.link(self.path, hardlink)
        self.reject(self.request("load"), "UNSAFE_PATH")
        self.reject(self.request("delete", expected_revision=1), "UNSAFE_PATH")
        hardlink.unlink()
        os.chmod(self.path, 0o644)
        self.reject(self.request("load"), "UNSAFE_PATH")
        self.assertEqual(self.path.read_bytes(), original)
        self.path.unlink()
        self.path.mkdir()
        self.reject(self.request(), "UNSAFE_PATH")
        self.path.rmdir()
        os.mkfifo(self.path, 0o600)
        self.reject(self.request("load"), "UNSAFE_PATH")
        self.path.unlink()
        os.chmod(self.directory, 0o777)
        self.reject(self.request(), "UNSAFE_PATH")
        os.chmod(self.directory, 0o700)

    def test_existing_unrelated_malformed_or_invalid_state_is_never_clobbered(self):
        for raw, error in ((b"unrelated data", "INVALID_JSON"), (b"{}", "INVALID_SCHEMA"),
                           (json.dumps(example()).encode(), "INVALID_SCHEMA")):
            self.path.write_bytes(raw)
            os.chmod(self.path, 0o600)
            for action in ("status", "save", "import", "delete", "forget"):
                self.reject(self.request(action, expected_revision=1) if action != "status" else self.request(action), error)
                self.assertEqual(self.path.read_bytes(), raw)

    def test_failed_write_does_not_partially_replace_or_leave_temporary_files(self):
        self.run_cli(self.request())
        before = self.path.read_bytes()
        for function in ("fsync", "replace"):
            with patch.object(HELPER.os, function, side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    HELPER.execute(self.request(expected_revision=1))
            self.assertEqual(self.path.read_bytes(), before)
            self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_new_target_collision_and_identity_change_preserve_other_file(self):
        other = b"fictional unrelated data"
        real_link = HELPER.os.link

        def collide(source, destination, **kwargs):
            self.path.write_bytes(other)
            return real_link(source, destination, **kwargs)

        with patch.object(HELPER.os, "link", side_effect=collide):
            with self.assertRaises(HELPER.Failure) as caught:
                HELPER.execute(self.request())
            self.assertEqual(caught.exception.code, "REVISION_CONFLICT")
        self.assertEqual(self.path.read_bytes(), other)
        self.assertEqual(list(self.directory.iterdir()), [self.path])
        self.path.unlink()
        self.run_cli(self.request())
        real_check = HELPER.check_identity
        calls = 0

        def change_identity(fd, name, expected):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.path.write_bytes(other)
            return real_check(fd, name, expected)

        with patch.object(HELPER, "check_identity", side_effect=change_identity):
            with self.assertRaises(HELPER.Failure) as caught:
                HELPER.execute(self.request(expected_revision=1))
            self.assertEqual(caught.exception.code, "REVISION_CONFLICT")
        self.assertEqual(self.path.read_bytes(), other)
        self.assertEqual(list(self.directory.iterdir()), [self.path])

    def test_cooperating_concurrent_updates_do_not_clobber_each_other(self):
        self.run_cli(self.request())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.run_cli(self.request(expected_revision=1)), range(2)))
        self.assertEqual(sum(result["ok"] for result in results), 1)
        self.assertEqual([r["error"]["code"] for r in results if not r["ok"]], ["REVISION_CONFLICT"])
        self.assertEqual(self.run_cli(self.request("load"))["state"]["revision"], 2)

    def test_unsupported_facilities_fail_closed(self):
        with patch.object(HELPER.os, "O_NOFOLLOW", new=None):
            # Missing attributes are checked before any open, as on unsupported hosts.
            del HELPER.os.O_NOFOLLOW
            with self.assertRaises(HELPER.Failure) as caught:
                HELPER.execute(self.request())
            self.assertEqual(caught.exception.code, "UNSUPPORTED_PLATFORM")
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_documented_json_example_matches_actual_validator(self):
        text = (ROOT / "references" / "travel-state.md").read_text(encoding="utf-8")
        state = json.loads(re.search(r"```json\s*(\{.*?\})\s*```", text, re.S).group(1))
        self.run_cli(self.request(state=state))
        state["revision"] = 1
        self.assertEqual(self.run_cli(self.request("load"))["state"], state)

    def test_machine_schema_tracks_the_cli_field_and_provenance_contract(self):
        schema = json.loads((ROOT / "references" / "travel-state.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(schema["properties"]), set(example()))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]["mode"]["enum"]), HELPER.MODES)
        for group in ("profile", "raw_snapshot"):
            self.assertEqual(set(schema["properties"][group]["properties"]), HELPER.FIELDS)
            self.assertFalse(schema["properties"][group]["additionalProperties"])
        self.assertEqual(schema["$defs"]["fact"]["properties"]["source"]["enum"], ["user", "verified", "inferred"])


if __name__ == "__main__":
    unittest.main()
