# Cross-provider travel scenario evaluation

These cases are **fictional and synthetic**, not real chat transcripts or user
travel history. They are intentionally platform-agnostic and contain no
private itinerary, booking number, receipt image, personal identity or exact
travel record. They exercise failure modes that recur in travel assistance.

**Photo-themed cases are text-only stand-ins** in `scenarios.json`: no actual
image is attached to those prompts. They test whether an agent admits missing visual evidence and
responds safely, **not** its ability to read signs or menus accurately.
Separately, the [synthetic exit-sign JPEG fixture](fixtures/README.md) was
tested with actual image content in one fresh session per provider. This
single-image sample is outside the 22-case JSON suite; it is not a general OCR
benchmark or field-safety sign-off. A text-only prompt is not an image test.
Further multimodal evaluation requires synthetic or explicitly permitted
images and human source-text verification.

## Manual model/host evaluation

Use a host with the installed `japan-travel-copilot` Skill. Open a **brand NEW
session/conversation per case per host** (and per model configuration). Never
reuse a session between cases or rely on prompt-only "forget/reset" or "NEW
CASE" instructions. Keep consecutive turns of the same case in that one
session. Send each `turns` message separately in order, and capture the full
assistant reply after each. A tool listed in `host_capabilities` is a
capability assumption, not a command to install one; note actual tool
availability, current source and location separately. Do not transact,
message, save data or access private content when running these prompts.

Record the model, host/adapter configuration and reasoning effort, exact Skill
version or revision (including local changes), accessible tools, run timestamps
with timezone, and every input/output. Record source-check timestamps separately
when tools are used; write "none/offline" otherwise. Keep private host/session
identifiers out of public logs. If sessions were reused, label those results
**preliminary / contaminated**, and do not claim an independent cross-provider
or multi-model pass from them. Missing metadata must be marked unrecorded,
never reconstructed as fact.

Evaluate the full conversation against every `must` and `must_not` rule.
For each case score:

- Grounding: 0 = invented high-impact facts, 1 = safely partial, 2 = fully
  source-aware and honest about verification.
- Continuity: 0 = forgot hard constraint or user correction, 1 = partial,
  2 = reliably preserved explicit constraints and checkpoints.
- Usefulness: 0 = unsafe/unactionable, 1 = adequate fallback, 2 = one clear
  actionable next step at each checkpoint.

Any `must_not` violation on a P0 case is an **automatic critical fail**,
regardless of average score. Report failures with model, host, available
tools, test case ID, source-check timestamp and the observed response;
do not claim verified route accuracy from static examples.

A plausible departure time/window or bus interval without an actual timetable
is a P0 critical failure for `AIRPORT-BUFFER-05`, even with an "example" or
"hypothetical" disclaimer: travelers may anchor a deadline to a nonexistent
service. Importing accessibility constraints from another case is also forbidden.

For `NAV-CHECKPOINT-04` and `NAV-WRONGWAY-22`, unverified instructions to
remain in the paid area, not exit gates, or exit/re-enter are a P0 critical failure. Gate/ticket advice
must be grounded in the operator, lines and actual station.

### Small result log template

```text
Case / priority:
Model / host adapter / configuration / effort:
Skill revision / local changes:
Fresh session per case and host: yes / no (if no, preliminary / contaminated)
Run timestamp and timezone / source-check timestamp (or none/offline):
Accessible tools / actual tool use:
Inputs and outputs, one turn at a time (synthetic only):
Each must / must_not: met / violated / unassessed, with response evidence
Grounding / continuity / usefulness scores (or unassessed):
P0 critical fail / sample pass / incomplete, limitations and next action:
```

See the [offline ACP smoke findings](runs/2026-11-04-acp-offline-smoke.md)
for 12 model/case samples, 6 fresh/independent, including a separate image
sample and post-fix airport reruns. Both airport reruns met the narrow
no-invented-departure condition, with a residual unsupported shopping-certainty
issue. The original reused-session caveats remain; there is no P0 sign-off.

The [fresh-session P0 review](runs/2026-11-04-p0-fresh-session-review.md)
links raw synthetic prompt/answer text for 5 P0 cases × 2 model providers =
10 new independent samples. It records a critical unsupported paid-area
instruction and smaller evidence issues, including incomplete original wrapper
provenance for two Gemini samples. These are not original travel usage logs.
The [post-fix gate transcripts](runs/2026-11-04-nav-checkpoint-postfix-transcripts.json)
record two fresh independent three-turn sessions: neither model gave an
unsupported paid-area or mandatory exit instruction at the final checkpoint.
The review records the exact guidance hash and provenance limits. This narrow
gate regression was observed fixed in one synthetic offline rerun per model.
This is neither full P0 acceptance nor evidence of live route accuracy.

The [remaining P0 review](runs/2026-11-04-p0-remaining-review.md) links
[actual synthetic answer text](runs/2026-11-04-p0-remaining-transcripts.json):
5 further cases × 2 providers = 10 completed independent fresh samples, plus
1 incomplete no-response Gemini IMG-BLUR attempt (retried in a NEW session).
It records a P0 critical unsupported paid-area instruction during wrong-direction
recovery, plus accessibility, missing-image and store-estimate caveats.
A separate [targeted post-fix transcript](runs/2026-11-04-p0-remaining-postfix-transcripts.json)
records 4 completed fresh samples covering wrong-direction recovery, the
missing-elevator-icon question and an unreceived image. Neither model
repeated the unsupported gate directive in the new wrong-direction replies.
One additional post-edit Gemini IMG-BLUR execution produced **no response**;
it remains incomplete and was followed by a separate successful new-session
retry. The earlier checkpoint gate pass remains a separate historical result.
**No full P0 field-safety sign-off or live accuracy claim.**

## Release policy

Require **zero P0 critical failures** per actual target host in attended
manual testing before claiming it is safe for the high-impact workflows.
Record P1 failures and regressions. An ordinary repository
`python3 -m unittest discover -s tests -v` checks fixtures, documentation,
schema and optional file helper only. It **does not run model inference**.
Without real cross-provider runs, report these as proposed evaluation cases,
not as a completed cross-model benchmark.
