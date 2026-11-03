# Trip continuity: constraints, cascading changes, and progress

Use when a trip changes, the user asks "what is left?", or shopping and
booking choices span many turns. This is a **conversation workflow**; it does
not add fields to the v0.2 JSON schema or authorize automatic persistence.
See [travel-state.md](travel-state.md).

## Status discipline

- **Hard constraints**: user-required elevators, party/luggage needs, explicit
  exclusions, a budget ceiling or deadline. Keep them in effect until the
  traveler changes them. A faster option that violates a hard constraint
  is not a valid recommendation.
- **Confirmed**: user reports a booking, arrival, cancellation, purchase,
  served dish or completed visit; classify it as the user's report, not
  independently verified. When the traveler corrects a location or shop,
  immediately replace the conflicting prior inference.
- **Tentative / unknown**: a preferred stop is not booked or visited; a
  checked web listing is not confirmed in-store stock; "undecided" remains
  unknown. Do not promote or merge these into confirmed facts.
- **Superseded**: when the traveler says "not that store", "skip this item",
  "we changed hotels", or "we canceled this stop", remove the old target
  from the active plan. Do not resurrect exclusions without permission.

This operational status ledger lives inside the conversation by default.
Optional persistence is **separate**: only sanitized, supported `schema_version:
0.2` facts, after consent and summary confirmation; no hidden logs or
automatic writes.

## Flight or accommodation disruption cascade

When a flight, hotel or day changes, review dependencies without silently
acting or implying provider guarantees.

| Dependency | Re-evaluation |
| --- | --- |
| Flights | New route, date, terminal and baggage rules: confirmed or pending |
| Lodging | Which nights are confirmed, moved, canceled or still undecided |
| Timed passes | Which purchased entry windows no longer fit the new schedule |
| Ground travel | Step-free transfers, checked luggage, arrival-time feasibility |
| Arrival declarations | Ask whether user-entered itinerary/accommodation details need review |
| Refunds and insurance | Actual policy/document evidence needed; no promised waiver |

Use labels **confirmed / pending / affected / not applicable**. For
provider-specific policies consult a current suitable source. Show a small
action order and a simple message to staff if useful; never book, cancel,
send or buy without explicit approval and a capable tool.

## Shopping, receipts and timed venues

Keep a short active item list with **wanted, checking, purchased,
unavailable, deferred, abandoned**; do not repeatedly recommend a purchased
or abandoned item. If stock, same-day manufacture or refund policy changes the
route, check the specific store rather than inferring from web catalog text.
Price comparisons preserve size, quantity, tax-included/after-tax, discounts,
currency exchange assumptions and eligible refund conditions. Treat canceled
shopping stops as removed.

For non-reentry attractions, appointments, reservations and timed tickets,
put **confirmed entry windows** ahead of optional shows or shopping. Check
live closure and performance schedules; do not move a confirmed timed slot
based on guessed operating hours.

## Message budget while moving

For a traveler boarding a train, dragging luggage or following a photo,
prefer **Now → Verify → Next checkpoint**. Expand only on request or when
deadline alternatives need comparison. After a checkpoint update, don't
repeat old directions or restart trip onboarding. Never request a booking
code or retain raw tickets, receipts or images in trip memory.
