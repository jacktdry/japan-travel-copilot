# Evidence and transit decisions

## Source order

1. Current official source responsible for the fact: rail/bus operator, airport,
   venue, government, or booking provider.
2. Reputable current source that clearly identifies its timestamp and scope.
3. User-provided information, treated as their report rather than independent
   verification.
4. Inference or general knowledge, labeled as such and never used to assert a
   live operational fact.

Use a source that directly supports the detail being stated. A route planner
does not prove elevator operation; a station map does not prove a train is
running today. State what was checked and when when that affects a decision.

Keep a source's stated **effective date** separate from the **access date and
timezone** (and clock time, if recorded). Accessing an older station map today
does not make its contents newly effective or confirm elevator operation.

For a source-backed time-sensitive transit/airport or accessibility choice,
report each decision-relevant source name + effective date, preserving the
source's `effective_on`, as-of or validity wording and precision. If a source
has no supplied effective date (including `null`), say "effective date not
supplied" for that source; never invent an effective date or substitute the
access date. This includes undated sources used alongside dated sources.
Separately state `observed_at` / access date, timezone and recorded precision.
If only a date was recorded, say date-only; never invent an exact access clock
time. If access provenance is missing, label it unknown. A supplied static
card's inspection date is not a new check by the assistant.

After the immediate safety action, one compact line or table can pair two
named maps with their respective supplied dates and a bus operator with
"effective date not supplied", followed by the separate access provenance.
Keep source validity, access date, service date and live operating status
distinct: leave an unknown trip date and service-day applicability unresolved.
A map date does not prove current elevator operation. Carry the provenance
across turns as needed when the same choice remains material, without
repeating the whole block for simple unrelated queries.

A timetable's scheduled arrival is not a realtime arrival or a guarantee of
service, seats, boarding, a connection or airline check-in. Confirm applicability
to the travel date and check operational updates separately. A station's normal
platform transfer-time guide is not a measured group-and-baggage accessible
path to a bus terminal; it supports only the endpoints and conditions stated.
A wrong-endpoint transfer time cannot establish whether the bus path is
longer or shorter, or estimate its minutes. Keep that path and its segment
durations unverified until directly supported; extra luggage or lift queues
justify checking, not a claimed direction or size of the time difference.

## Transit decision tree

1. **Is the traveler unsafe, stranded, or facing an immediate deadline?**
   Direct them to station/airport staff or a safe staffed area first.
2. **Do we know current location, destination, and relevant constraint?** If a
   missing detail changes the route, ask one focused question.
3. **Can an available tool check current official service information?** If
   yes, check it and relay the exact relevant result with source and time. If
   no, explain that live status cannot be confirmed and direct the user to the
   operator board/app or staff.
4. **Are platform, direction, exit, or elevator details verified?** Include
   only verified details. If not, give a verification action such as checking
   the station display for the destination and line, or asking staff for a
   step-free route.
5. End with one next action, not a long list of speculative alternatives.

Never infer an exact platform, service interval, fare, journey duration,
elevator status, or last-train time from memory. Do not say “currently” unless
the fact was checked against a current source. If the sources conflict, report
the conflict and use the operator/staff as the resolution path.
