# Changelog

## 0.3.0 (proposed)

- Added [actual-image P1 tests and a sandbox privacy probe](evaluations/runs/2026-11-05-p1-multimodal-privacy-review.md): two wholly synthetic Japanese menu/receipt JPEGs, four fresh independent ACP image-input samples (two models) and one separate three-turn Gemini sandbox no-file observation. Both models grounded the explicit peanut warning and canceled 400-JPY receipt line. No write-type tool event observed in the sandbox probe, but **no host-wide filesystem audit**; strict zero-file and field safety remain unverified.

- Added the [P1 offline review](evaluations/runs/2026-11-05-p1-offline-review.md): 24 independent completed synthetic samples, 46 traveler turns, 2 excluded/qualified initial attempts and a host temporary plan-file observation. Tightened refund/timed-ticket grounding, receipt math, allergy translation, order-state separation and host storage boundaries; targeted contracts and static archive checks added. Six targeted fresh post-fix Gemini case samples showed narrow repairs in five cases and a residual missing-order error; a seventh independent three-turn sample after a concrete rule edit no longer made that error. Historical failures and host plan-file behavior remain; no broad all-pass or strict zero-file claim.

- Added the [remaining P0 review](evaluations/runs/2026-11-04-p0-remaining-review.md): 10 completed fresh synthetic samples plus 1 incomplete no-response attempt. Hardened wrong-direction gate/return-route verification, missing-elevator-sign uncertainty and absent-image attribution; subsequent targeted new-session reruns did not reproduce the gate/missing-icon defects, but a Gemini no-response attempt remains; no P0 sign-off.
- Grounded transfer gate/ticket instructions in operator, lines and station evidence; added static checkpoint contracts and a 10-sample fresh-session synthetic review with provenance limits; the narrow checkpoint gate rerun was observed fixed for both providers.
- Prohibited fictitious airport departure windows; tightened fresh-session evaluation protocol and logged limited offline ACP findings with no P0 sign-off.
- Strengthened evidence-grounded live navigation, date/time interpretation,
  direction and checkpoint corrections, full-route step-free requirements,
  and airport deadline/baggage safety margins.
- Added traveler-decision continuity for cancellations, shopping state,
  hard exclusions, timed entry and verified versus tentative status.
- Added multimodal/photo correction, Japanese order changes and
  requested/served/billed receipt reconciliation guidance.
- Added 22 fictional evaluation scenarios (single- and multi-turn) with a
  cross-provider manual scoring rubric. Static tests are not model UAT.


## 0.2.0 (unreleased)

- Added bilingual, copy-ready installation instructions: Agent-guided install, interactive skills CLI, and manual ZIP fallback.
- Added an Agent installation/verification checklist, scope and consent safeguards, and a first-use activation example.


- Added progressive first-trip intake, reuse of supplied context, immediate
  translation/urgent help, summary confirmation and later delta updates.
- Removed host/vendor-specific installation assumptions; tool and storage
  capabilities remain conditional on host support and policy.
- Added optional explicit file memory, provenance and sanitized raw snapshot,
  manual resume JSON fallback, and a versioned state schema.
- Added a dependency-free stdin/stdout Python CLI for status/save/load/export/
  import/delete/forget, confirmation gates, revision checks, private atomic
  writes and defensive path handling. No automatic persistence or cloud sync.
- Expanded synthetic stdlib tests and bilingual documentation; four modes and
  dynamic-travel safety boundaries remain in place.

## 0.1.0

- Initial portable Japan Travel Copilot Agent Skill.
- Added four operating modes, evidence and transit guidance, translation
  patterns, privacy boundaries, and synthetic scenarios.
- Added bilingual installation and contribution documentation with stdlib
  validation.
