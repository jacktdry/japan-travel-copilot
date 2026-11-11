# ACP configuration projection discrepancy

Observed upstream on **2026-11-06**, date-only; exact diagnostic clock times
and timezone were not supplied. This note records the upstream diagnostic
account, not a new worker probe or native process inspection. The related
[source-date rerun archive](2026-11-06-source-backed-date-contract-transcripts.json)
records the same configuration/projection disagreement; the
[sample review](2026-11-06-source-backed-date-contract-review.md) keeps its
behavioral result separate from effective runtime identity.

| Observation in a NEW diagnostic session | Returned / observed result |
| --- | --- |
| session/update selected settings | gemini-3.8-flash, plan, sandbox=true |
| session/open | The same chosen values |
| inspect.runtime_state, repeatedly | gemini-4-argon, default, sandbox=false |
| Benign “連線正常” prompt | Completed successfully; inspect still projected the initial settings afterward |

The upstream report says this was a benign connection probe, not another
traveler case. No raw diagnostic trace is attached here, so its exact event
timings and response body are not reconstructed. The successful prompt does
not establish which native model ran or that sandbox enforcement was active.

Repeated initial values despite update/open acknowledgment and completed work
suggest a **stale process-local projection**. That is an inference, not a
confirmed root cause or proof that the chosen settings reached the native
runtime. **Native model identity and sandbox effectiveness are not independently
verified.** No native process inspection or host filesystem audit was performed;
absence of a reported write is not host no-file proof. The earlier blocked
submission's cause also remains unknown. Nothing is claimed fixed.

Recommended next step: investigate and fix the tool projection in a separate
AgentDock project, then confirm effective native settings through supported
runtime tracing and test sandbox enforcement independently under an authorized
host audit. Preserve the distinction between requested settings, adapter
acknowledgments, projected state and verified native behavior. No AgentDock
settings, code or repositories were changed by this repository worker, and
no further model prompts were sent.
