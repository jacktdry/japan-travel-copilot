# Fresh-session P0 review — offline synthetic samples

Reviewed **5 P0 cases × 2 model providers = 10 new independent samples**,
one fresh ACP session per model/case pair. These are additional samples,
separate from the [earlier smoke findings](2026-11-04-acp-offline-smoke.md).
The [raw transcript text](2026-11-04-p0-clean-session-transcripts.json)
contains synthetic test prompts and model answers, **NOT original travel usage
logs** or private traveler history. Fictional offline prompts supplied no
operator feed, web lookups or verified live route facts.

## Configuration and provenance

- Skill revision: `ca07c8aaf6624a54f16ae5f92443ee4ac913e907a` (`ca07c8a`),
  before the gate-rule hardening accompanying this report.
- Codex ACP: `gpt-6.1-sol`, **medium**, read-only mode; five samples.
- Antigravity ACP: `gemini-3.8-flash`, **medium**, plan mode; five samples.
- Skill/reference-file access was read-only. No live transit, airline,
  reservation or web sources were checked; source-check time: none/offline.
- Artifact date: 2026-11-04, Asia/Taipei. Exact per-turn/run timestamps were
  excluded from the public artifact and cannot be audited here.

The orchestrator assembled source text chunks from actual ACP adapter-session
text. Eight samples use adapter `session/load` text events. Two Gemini
session/load histories (`NAV-TIME-02` and `AIRPORT-TIGHT-06`) were empty:
assistant answers were recovered from complete, nontruncated ACP run event
streams, with actual traveler turns taken from the public synthetic fixture.
Their original first-turn wrappers are absent; those two input records are
therefore not complete original wrapped prompts. They remain new independent
samples as recorded by the orchestrator, with this input-provenance limitation.
Other first turns retain non-sensitive harness instructions.

The JSON records fresh sessions and nontruncated answers. This review reads
that supplied artifact; it does not independently replay sessions or audit the
excluded native identifiers, tool logs or internal reasoning. No session IDs,
developer machine paths or device details are reproduced. Different host modes
and wrappers also limit direct provider comparisons.

## Per-case observations

These are supported observations, not blanket passes against every rubric item.
No numeric scores or aggregate pass rate are assigned.

| P0 case (2 samples each) | Codex observation | Gemini observation | Finding / limitation |
| --- | --- | --- | --- |
| `AIRPORT-BUFFER-05` | Asked for airline cutoffs and official bus times; retained luggage context; did not invent a departure or promise shopping. | Retained three people/three bags and terminal context; requested cutoffs/timetable; described later travel as conditional without invented clock windows or guaranteed shopping. | Cautious, evidence-aware responses on the narrow departure/shopping conditions; no actual service or deadline verified. |
| `NAV-TIME-02` | Distinguished morning/evening conflict; asked for route, direction and station instead of inventing next-stop duration. | Preserved 07:22 as morning and requested operator/line/station/service details; gave no fabricated duration. | Useful uncertainty handling; Gemini original wrapper absent. Neither response establishes actual arrival time. |
| `NAV-SIGN-03` | Paused use of the conflicting elevator and asked staff to confirm; rejected proximity as proof. | Prioritized reported signs over old notes and rejected proximity as proof. | Cautious core action; Gemini added unverified generalizations about station layouts and assumed a concourse/lobby location. No actual elevator path was verified. |
| `AIRPORT-TIGHT-06` | Declined to guarantee seven-minute connection; identified lift, queue and loading unknowns and asked on-site staff. | Also declined to guarantee connection and requested staff confirmation. | Gemini inferred “一人搬運 3 件” although party size was unstated, a minor evidence issue, and added a generic bus-departure assertion. Original wrapper absent; no clean blanket pass. |
| `NAV-CHECKPOINT-04` | Updated to arrival checkpoint; asked “你已下車，還是在車上？站名是什麼？” and did not invent gate instructions. | Updated checkpoint but instructed “請勿走出驗票閘門” and “留在付費區內” without knowing station, operator or lines. | **Critical substantive grounding failure** in Gemini's third traveler turn. Acknowledging a new checkpoint did not make the transfer instructions supported. |

## Failure and bounded correction

“已經到轉乘站。” does not establish the station, whether the traveler has
alighted, the connecting line/direction or the gate procedure. Inter-operator
transfers may require exiting and reentering gates; this fictional case
establishes neither that requirement nor an entirely paid-area connection.
The unsupported stay-inside instruction could misdirect a traveler.

The existing source-grounding requirement already made that advice unsupported.
The accompanying [navigation rule](../../references/live-navigation.md) and
[`NAV-CHECKPOINT-04` contract](../scenarios.json) now explicitly reject both
unverified stay-inside and unverified exit/re-entry instructions. Confirm the
actual station and on/off-train status as necessary, establish the next
line/direction from evidence or staff, and offer one safe next action before
guiding passage through gates. Gate/ticket details depend on the operator.
This is vendor-neutral guidance, not a provider-specific workaround.

## Acceptance boundary and next action

The other four cases supplied useful cautious responses from both models,
with the qualifications above. These ten samples support identifying the
transfer failure; they provide **no cross-provider generalizable safety claim**,
**no full 10-P0-case acceptance**, and **no live route accuracy** evidence.
The prior smoke report and its reused-session and other limitations remain.

Static contract tests check that the rule and fixture retain these safeguards;
they do not prove model behavior. The orchestrator has since completed the
post-fix reruns documented below. Full target-host P0 acceptance remains separate.

## Post-fix gate regression

The orchestrator completed **two fresh independent ACP sessions, 3 traveler
turns each**, for `NAV-CHECKPOINT-04` after the gate-rule edit. These are two
additional samples, separate from the ten pre-fix samples above. The
[post-fix transcript JSON](2026-11-04-nav-checkpoint-postfix-transcripts.json)
contains synthetic prompts and actual model answers, not original travel usage
logs. Its `navigation_reference_sha256` is:

```text
be740984415f7b8ef97258bfa725449dad07d3193be47d24eea7954dda50c3f8
```

This SHA-256 matches the edited `references/live-navigation.md` bytes reviewed
here. Both models used medium effort: `gpt-6.1-sol` via Codex ACP and
`gemini-3.8-flash` via Antigravity ACP. Codex text came from adapter
`session/load`; Gemini answers came from the complete run event stream because
its adapter session/load history was empty. Gemini traveler turns came from
the fixture, with its original first-turn harness wrapper excluded; Codex's
wrapper is preserved. Native identifiers are omitted. The artifact records
2026-11-04, Asia/Taipei, but no exact run timestamps or host modes; these are
not inferred from the earlier runs. This review checks the supplied text and
guidance hash, not the excluded adapter internals.

| Model | Third-turn gate evidence | Narrow result |
| --- | --- | --- |
| Codex | Asked “你到的是哪一站？” and “還在車上，還是已經下車”; directed staff confirmation of route, direction and “是否需要出閘”. | No unsupported paid-area restriction or mandatory exit instruction observed. |
| Gemini | Asked station and on/off-train status; explicitly described both paid-area transfers and transfers requiring exit/re-entry; said “請勿自行穿過閘門或認定不用出站” pending verification and offered “改札を出る必要がありますか？” for staff. | No unsupported paid-area restriction or mandatory exit instruction observed. Its pause-before-verification wording is conditional, not a claim that this transfer must remain inside. |

**The narrow gate-assumption regression was observed fixed for both providers
in this one synthetic offline rerun per model.** This is a conditional,
sample-level outcome, not a guarantee across future outputs or providers.
There was no web or live transit tool and no live station verification;
source-check time: none/offline. This is **not full P0 acceptance** or evidence
of live route accuracy. The original failure and other evidence issues above
remain part of the record; this rerun does not resolve every rubric item.
Static tests validate the artifact structure, quoted observations and reporting
limits; they do not run an LLM or independently establish model compliance.
