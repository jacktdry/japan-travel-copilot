# Optional portable file memory

## Consent and capability boundary

There is no built-in agent memory, automatic lookup, account sync, cloud
storage, monitoring, or storage service. Never automatically use persistent
state on invocation. Reads as well as writes require explicit user opt-in,
an explicitly supplied `state_path`, filesystem tools, and host policy
permission. If the host disables memory/storage, do not work around it using
another tool, shell, location, or service. Continue conversation-only with
optional manual export/copy. Installation does not authorize file access.

This boundary includes autonomous plan files, scratch artifacts and tool
outputs that store private travel details: do not intentionally write those
when the user or host forbids storage. A host-internal temporary planning file
is a file side effect even if it is not a portable cross-session travel-state
JSON. Do not claim an absolute guarantee that the host creates no temporary
files unless verified. A host that automatically writes planning files may be
incompatible with strict no-file privacy requirements; host policy/configuration
enforcement is required, not merely prompt compliance. If that enforcement is
unknown, disclose the limit before handling private details; do not claim
conversation-only instructions prove host-wide zero-file behavior.

The user/host chooses an existing private directory **outside the installed
Skill and any Git repository**. There are no default paths, home directory
assumptions, environment variables, auto-discovery, or automatic directory
creation. Cross-session restoration works only if the same explicitly shared
file is accessible to the current agent and access is authorized again in the
current host context; no portability promise beyond moving JSON manually.

Before persistence, show the sanitized profile and snapshot, confirm
corrections, explain exactly which file will be used, and obtain storage
consent. Changing the destination or scope requires consent covering that
change. Each mutation requires confirmation of its content/action. A host may
retain a clearly scoped opt-in during the current session, but must never
infer it from skill invocation or a correct-summary acknowledgment. Never
automatically save a confirmed conversation delta.

## Helper interface

Optional helper: `python3 scripts/run.py`, Python **3.9+**, standard library
only. Secure file operations currently require POSIX; CI is configured to run
the suite on Linux. Unsupported platforms fail closed. Other hosts may
implement the same consent/schema contract with their own permitted tools,
or use manual JSON. No network, dependencies, module environment, or managed
installation.

One UTF-8 JSON request on stdin; one JSON result on stdout; no travel data or
diagnostics on stderr. Exit 0 means success, 2 means an error. No command-line
flags. Output keys are stable; whitespace/key ordering is not an API promise.
For every action provide:

| Field | Requirement |
| --- | --- |
| skill_action | `status`, `save`, `load`, `export`, `import`, `delete`, or alias `forget` |
| state_path | Explicit absolute POSIX path ending in `.travel-state.json` |
| consent | Literal `true`, representing actual user opt-in |
| confirmed | Literal `true` for save/import/delete/forget; omit on reads |
| expected_revision | Required for mutations: `null` to create only, or current positive revision to replace/delete |
| state | [Version 0.2 state](travel-state.md), required only for save/import |

These flags are **not security authorization** and cannot prove a user agreed.
The caller/host must enforce real consent, tool permissions and policy. The
helper cannot discover a host's memory-disabled setting. Do not send `true`
unless those checks actually passed. Unknown request fields are rejected.

| Action | Success fields in addition to `ok: true`, `skill_action` |
| --- | --- |
| status | `exists`, `revision` (null when absent); read-only, validates existing state, does not return travel content |
| load / export | `state`; both read-only, export is stdout only |
| save / import | `revision`; sanitized state supplied inline, full replacement, revision assigned by destination |
| delete / forget | `deleted: true`; removes exactly the selected state file |

For a roundtrip, take the `state` member from export output and place it in an
import request. Import is never a request to read a second path. When moving
state, the user explicitly chooses the new external `state_path`; confirm
that target and the content first. Never redirect export output into the
Skill/repository or a default file. Manual copy is available when file access
is unavailable; do not claim cross-session recall until the user supplies the
block/file to a capable, permitted agent. Read-only status cannot create files.

Saved revision starts at 1; each replacement increments the destination's
revision, regardless of the submitted state's revision. Missing or mismatched
`expected_revision` never permits overwrite. Load again and reconfirm the
change after a conflict; do not blindly retry. No merge, backup, or history is
automatically created. Forgetting does not erase copies, exports, host chat
history, filesystem snapshots, or backups, and is not secure disk erasure.

## Errors and filesystem limits

Error shape: `{"ok": false, "error": {"code": "...", "message": "..."}}`.
Messages never include paths or submitted travel data. Stable codes:

- `INVALID_JSON`: malformed/duplicate/non-finite/oversize JSON or invalid UTF-8.
- `INVALID_REQUEST`: unsupported action, fields, or mutation revision argument.
- `INVALID_SCHEMA`: invalid or unsupported trip state schema.
- `SENSITIVE_DATA`: obvious sensitive content; review and remove it.
- `CONSENT_REQUIRED`, `CONFIRMATION_REQUIRED`: missing explicit flags.
- `INVALID_PATH`: missing/nonabsolute path, wrong suffix, dot/traversal components.
- `UNSAFE_PATH`: Skill/Git directory, symlink, nonregular file, hardlink,
  nonprivate existing file, foreign owner, or writable-by-others parent directory.
- `UNSUPPORTED_PLATFORM`: required descriptor/locking facilities unavailable.
- `NOT_FOUND`: selected state missing (except status reports absence).
- `REVISION_CONFLICT`: revision/identity mismatch or occupied creation target.
- `IO_ERROR`: filesystem operation failed; do not claim success.

All path components are opened without following symlinks, using directory
descriptors. Relative paths, `.`/`..`, symlink aliases (including OS temporary
directory aliases), and linked state files are rejected. Select a direct
physical absolute path rather than relying on alias resolution. No unrelated
file is overwritten: existing targets must be valid private state files and
match the expected revision. This is not proof that an arbitrary valid state
file belongs to this user: the host must bind consent to the selected path.

Writes stage a random exclusive 0600 temporary file in the same directory,
flush/fsync its content, and publish atomically. New-file publication is
exclusive; replacements use atomic rename. Temporary files are removed on
ordinary failures. Cooperating helper invocations serialize with an advisory
directory lock and check target identity before replacement/deletion. The
host must provide a private local directory controlled by the user; this is
not a sandbox against malicious concurrent writers, a privilege boundary,
encryption, or a guarantee on network filesystems. Abrupt process termination
can leave an owner-only temporary file; power-loss durability of directory
entries is not guaranteed. The helper cannot make stdout or the host's logs
private. Never put secret values in any request or shareable block.
