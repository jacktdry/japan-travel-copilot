# Travel state and delta updates

Keep only the working context needed for the current conversation. This schema
is an example contract for reasoning, not a requirement to store or serialize
anything. Do not create a database, cache, or profile. Expire a detail when it
stops helping or the user corrects it.

## Suggested fields

| Field | Meaning |
| --- | --- |
| mode | `pre_trip`, `on_trip`, `translation`, or `disruption` |
| current_place | User-stated or verified location, with source and time if relevant |
| destination | Intended next place or requested outcome |
| constraints | Relevant time, mobility, language, budget, or luggage constraint |
| confirmed_changes | User-confirmed cancellation, delay, booking change, or decision |
| open_question | One critical missing detail, if any |

Use explicit provenance in your reasoning: **user said**, **source verified**,
or **inference**. Do not promote an inference to a fact. Ask only when the
missing value can change the next step.

## Fictional example JSON

```json
{
  "mode": "on_trip",
  "current_place": {"value": "Example Central Station", "source": "user"},
  "destination": {"value": "Example Museum", "source": "user"},
  "constraints": [{"value": "step-free route preferred", "source": "user"}],
  "confirmed_changes": [],
  "open_question": "Which station entrance is the traveler near?"
}
```

All place names above are fictional. Do not retain sensitive identifiers,
payment details, full booking references, or exact addresses in working state.
