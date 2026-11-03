# Contributing

Keep changes focused on a portable Agent Skill for Japan travel. Preserve
vendor neutrality, Traditional Chinese as the default, concise next-step-first
responses, conversation-only state, and explicit uncertainty around live
facts. Use fictional names and examples only; do not add private itineraries,
personal data, account details, secrets, databases, or caches.

Keep references relative and linked from `SKILL.md` or the README. The root
skill must remain below 500 lines and must not require a particular runtime,
API, or vendor contract. Never state current schedules, routes, availability,
or policy as fact without suitable current evidence.

Before submitting, run:

```sh
python3 -m unittest discover -s tests -v
```

Describe behavior changes and report checks actually run. Do not claim a host
integration or live-travel behavior that was not exercised.
