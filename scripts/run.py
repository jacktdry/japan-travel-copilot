#!/usr/bin/env python3
"""Optional, stdlib-only trip file helper. One JSON request in, one result out."""

import datetime
import errno
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys


LIMIT = 65536
SKILL_ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    "destinations", "dates", "travelers", "origins", "arrival", "departure",
    "accommodation", "luggage", "accessibility", "interests", "budget",
    "transport", "booking_status", "current_place", "destination", "constraints",
    "confirmed_changes", "open_question",
}
MODES = {"pre_trip", "on_trip", "translation", "disruption"}
MESSAGES = {
    "INVALID_JSON": "Provide one bounded UTF-8 JSON object without duplicate keys.",
    "INVALID_REQUEST": "Request fields or action are invalid.",
    "INVALID_SCHEMA": "Trip state does not match schema version 0.2.",
    "SENSITIVE_DATA": "Remove sensitive identifiers or credentials before sharing.",
    "CONSENT_REQUIRED": "Explicit user consent is required for file access.",
    "CONFIRMATION_REQUIRED": "Explicit mutation confirmation is required.",
    "INVALID_PATH": "Supply an absolute external path ending in .travel-state.json.",
    "UNSAFE_PATH": "Path must be outside skills and repositories without links or unsafe files.",
    "UNSUPPORTED_PLATFORM": "Secure POSIX descriptor-based file access is unavailable.",
    "NOT_FOUND": "No state file exists at the supplied path.",
    "REVISION_CONFLICT": "State changed or creation target already exists; reload before confirming.",
    "IO_ERROR": "File operation failed; success is not established.",
}
# A best-effort backstop, not a semantic secret/PII detector.
SENSITIVE = re.compile(
    r"(?i)(?:passport|護照|password|密碼|api[ _-]?key|access[ _-]?token|"
    r"token|secret|bearer|credit[ _-]?card|信用卡|booking[ _-]?(?:code|reference)|"
    r"reservation[ _-]?(?:code|number)|訂位代碼|訂房代碼)\s*[:=：]|"
    r"\b(?:sk|pk)[-_][a-zA-Z0-9]{12,}|\b(?:\d[ -]?){13,19}\b"
)


class Failure(Exception):
    def __init__(self, code):
        self.code = code


def fail(code):
    raise Failure(code)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("INVALID_JSON")
        result[key] = value
    return result


def decode(raw):
    if len(raw) > LIMIT:
        fail("INVALID_JSON")
    try:
        return json.loads(
            raw.decode("utf-8"), object_pairs_hook=unique_object,
            parse_constant=lambda _: fail("INVALID_JSON"),
        )
    except (ValueError, UnicodeError, RecursionError):
        fail("INVALID_JSON")


def text_value(value):
    if not isinstance(value, str) or len(value) > 1000:
        fail("INVALID_SCHEMA")
    if any(ord(char) < 32 for char in value):
        fail("INVALID_SCHEMA")
    if SENSITIVE.search(value):
        fail("SENSITIVE_DATA")


def validate_facts(facts, raw=False):
    if not isinstance(facts, dict) or not facts.keys() <= FIELDS:
        fail("INVALID_SCHEMA")
    for field, fact in facts.items():
        if not isinstance(fact, dict):
            fail("INVALID_SCHEMA")
        if not {"value", "source"} <= fact.keys() or not fact.keys() <= {
            "value", "source", "evidence", "checked_at",
        }:
            fail("INVALID_SCHEMA")
        source = fact["source"]
        if not isinstance(source, str) or source not in {"user", "verified", "inferred"}:
            fail("INVALID_SCHEMA")
        if raw and source != "user":
            fail("INVALID_SCHEMA")
        value = fact["value"]
        if field == "travelers":
            if value is not None and (type(value) is not int or not 1 <= value <= 100):
                fail("INVALID_SCHEMA")
        elif value is not None:
            if isinstance(value, list):
                if len(value) > 20:
                    fail("INVALID_SCHEMA")
                for item in value:
                    text_value(item)
            else:
                text_value(value)
        if source == "verified":
            if not {"evidence", "checked_at"} <= fact.keys():
                fail("INVALID_SCHEMA")
            text_value(fact["evidence"])
            if not fact["evidence"].strip():
                fail("INVALID_SCHEMA")
            text_value(fact["checked_at"])
            try:
                stamp = datetime.datetime.fromisoformat(fact["checked_at"].replace("Z", "+00:00"))
                if stamp.utcoffset() is None:
                    fail("INVALID_SCHEMA")
            except ValueError:
                fail("INVALID_SCHEMA")
        elif fact.keys() & {"evidence", "checked_at"}:
            fail("INVALID_SCHEMA")


def validate_state(state):
    if not isinstance(state, dict) or set(state) != {
        "schema_version", "revision", "mode", "profile", "raw_snapshot",
    }:
        fail("INVALID_SCHEMA")
    if state["schema_version"] != "0.2":
        fail("INVALID_SCHEMA")
    if type(state["revision"]) is not int or not 0 <= state["revision"] < 2**53:
        fail("INVALID_SCHEMA")
    if not isinstance(state["mode"], str) or state["mode"] not in MODES:
        fail("INVALID_SCHEMA")
    validate_facts(state["profile"])
    validate_facts(state["raw_snapshot"], raw=True)
    # Includes non-ASCII/escaped expansion; bounds both imported and saved states.
    if len(encode(state)) > LIMIT:
        fail("INVALID_SCHEMA")
    return state


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def open_parent(path):
    """Walk without following links; anchor all later operations to directory FD."""
    if not isinstance(path, str) or not path.startswith("/") or "\x00" in path:
        fail("INVALID_PATH")
    parts = path.split("/")[1:]
    if any(part in {"", ".", "..", ".git"} for part in parts):
        fail("INVALID_PATH")
    if not parts[-1].endswith(".travel-state.json"):
        fail("INVALID_PATH")
    if Path(path).is_relative_to(SKILL_ROOT):
        fail("UNSAFE_PATH")
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "O_DIRECTORY")):
        fail("UNSUPPORTED_PLATFORM")
    try:
        import fcntl
    except ImportError:
        fail("UNSUPPORTED_PLATFORM")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open("/", flags)
    try:
        for part in [None] + parts[:-1]:
            if part is not None:
                child = os.open(part, flags, dir_fd=fd)
                os.close(fd)
                fd = child
            # Any Git checkout or installed Skill ancestor is prohibited.
            for marker in (".git", "SKILL.md"):
                try:
                    os.stat(marker, dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                fail("UNSAFE_PATH")
        parent = os.fstat(fd)
        if parent.st_uid != os.getuid() or parent.st_mode & 0o022:
            fail("UNSAFE_PATH")
        # Advisory serialization for cooperating CLI invocations, no lock file.
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd, parts[-1]
    except BaseException:
        os.close(fd)
        raise


def identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read_state(fd, name):
    try:
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return None, None
    if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
            or info.st_uid != os.getuid() or info.st_mode & 0o077):
        fail("UNSAFE_PATH")
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(handle, "rb") as stream:
        if identity(os.fstat(stream.fileno())) != identity(info):
            fail("REVISION_CONFLICT")
        state = validate_state(decode(stream.read(LIMIT + 1)))
        if identity(os.fstat(stream.fileno())) != identity(info):
            fail("REVISION_CONFLICT")
    check_identity(fd, name, identity(info))
    if state["revision"] == 0:
        fail("INVALID_SCHEMA")
    return state, identity(info)


def check_identity(fd, name, expected):
    try:
        actual = identity(os.stat(name, dir_fd=fd, follow_symlinks=False))
    except FileNotFoundError:
        actual = None
    if actual != expected:
        fail("REVISION_CONFLICT")


def atomic_write(fd, name, state, previous):
    temporary = ".trip-" + secrets.token_hex(16) + ".tmp"
    handle = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(handle, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(encode(state))
            stream.flush()
            os.fsync(stream.fileno())
        check_identity(fd, name, previous)
        if previous is None:
            # Exclusive publication: even a non-cooperating new file is preserved.
            try:
                os.link(temporary, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
            except FileExistsError:
                fail("REVISION_CONFLICT")
        else:
            os.replace(temporary, name, src_dir_fd=fd, dst_dir_fd=fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=fd)
        except FileNotFoundError:
            pass


def execute(request):
    if not isinstance(request, dict):
        fail("INVALID_REQUEST")
    action = request.get("skill_action")
    if not isinstance(action, str) or action not in {"status", "load", "export", "save", "import", "delete", "forget"}:
        fail("INVALID_REQUEST")
    mutation = action in {"save", "import", "delete", "forget"}
    allowed = {"skill_action", "state_path", "consent"}
    if mutation:
        allowed |= {"confirmed", "expected_revision"}
    if action in {"save", "import"}:
        allowed.add("state")
    if not request.keys() <= allowed:
        fail("INVALID_REQUEST")
    if request.get("consent") is not True:
        fail("CONSENT_REQUIRED")
    if mutation:
        if request.get("confirmed") is not True:
            fail("CONFIRMATION_REQUIRED")
        if "expected_revision" not in request:
            fail("INVALID_REQUEST")
        revision = request["expected_revision"]
        if revision is not None and (type(revision) is not int or not 1 <= revision < 2**53):
            fail("INVALID_REQUEST")
    if action in {"save", "import"}:
        validate_state(request.get("state"))
    fd, name = open_parent(request.get("state_path"))
    try:
        current, previous = read_state(fd, name)
        if action == "status":
            return {"exists": current is not None, "revision": current["revision"] if current else None}
        if mutation:
            if request["expected_revision"] != (current["revision"] if current else None):
                fail("REVISION_CONFLICT")
        if action in {"save", "import"}:
            state = dict(request["state"])
            state["revision"] = current["revision"] + 1 if current else 1
            validate_state(state)
            atomic_write(fd, name, state, previous)
            return {"revision": state["revision"]}
        if current is None:
            fail("NOT_FOUND")
        if action in {"delete", "forget"}:
            check_identity(fd, name, previous)
            os.unlink(name, dir_fd=fd)
            return {"deleted": True}
        return {"state": current}
    finally:
        os.close(fd)


def main():
    try:
        if len(sys.argv) != 1:
            fail("INVALID_REQUEST")
        request = decode(sys.stdin.buffer.read(LIMIT + 1))
        result = {"ok": True, "skill_action": request.get("skill_action") if isinstance(request, dict) else None,
                  **execute(request)}
        code = 0
    except Failure as error:
        result = {"ok": False, "error": {"code": error.code, "message": MESSAGES[error.code]}}
        code = 2
    except OSError as error:
        key = "UNSAFE_PATH" if error.errno in {errno.ELOOP, errno.ENOTDIR} else "IO_ERROR"
        result = {"ok": False, "error": {"code": key, "message": MESSAGES[key]}}
        code = 2
    except (ValueError, TypeError, RecursionError, OverflowError):
        result = {"ok": False, "error": {"code": "INVALID_REQUEST", "message": MESSAGES["INVALID_REQUEST"]}}
        code = 2
    sys.stdout.buffer.write(encode(result))
    return code


if __name__ == "__main__":
    sys.exit(main())
