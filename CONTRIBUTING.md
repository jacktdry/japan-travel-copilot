# Contributing

Keep changes focused on a portable Agent Skill for Japan travel. Preserve
vendor neutrality, Traditional Chinese as the default, concise next-step-first
responses, conversation-only defaults, and explicit uncertainty around live
facts. Use fictional names and examples only; do not add private itineraries,
personal data, account details, secrets, databases, or caches.

Preserve progressive intake and its urgent/translation bypasses. Do not make
optional questions mandatory or repeat answers from supplied context. File
memory is opt-in only, outside the Skill and any Git repository; never bypass
host policies or imply built-in memory or cloud sync. Confirm profiles before
persistence. CLI consent flags cannot authenticate or authorize the caller.
Follow [onboarding](references/onboarding.md), [state schema](references/travel-state.md)
and [memory contract](references/memory.md). Use the same schema for manual copy.

Keep references relative and linked from `SKILL.md` or the README. The root
skill must remain below 500 lines and must not require a particular runtime,
API, or vendor contract. Never state current schedules, routes, availability,
or policy as fact without suitable current evidence.

Before submitting, run:

```sh
python3 -m unittest discover -s tests -v
```

Python 3.9+ and stdlib are sufficient; the optional secure helper currently
requires POSIX descriptor operations and advisory locks. Test happy and error
paths with synthetic files in private, physical temporary directories outside
the checkout. Cover cross-process restoration, mutation confirmation, schema,
privacy, path/link rejection, revision conflicts and atomic-write failures.
Never add real travel state to Git; `.gitignore` is a backstop, not permission
to write data here. Do not install dependencies or run live network tests.

Describe behavior changes and report checks actually run. Static instruction
checks do not prove a host follows onboarding correctly. Do not claim host
integration, live-travel behavior, CI, or publication that was not exercised.
