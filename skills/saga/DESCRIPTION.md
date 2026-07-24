---
name: saga
description: Unified operator toolbox with five general ops workflows, five everyday Saga lifecycle workflows, and an independent milestone audit. Plain version-controlled skills and project records; bounded execution, deterministic gates, and no phase exhaust.
---

# Saga operator toolbox

This repository is the canonical source for the unified toolbox.

Ten primary intents cover everyday work:

- `ops-grill-me` — clarify the real goal, constraints, decisions, and unknowns.
- `ops-troubleshoot` — diagnose code, configuration, service, host, or network failures from evidence.
- `ops-review` — read-only correctness and operability review, with named security or adversarial lenses when warranted.
- `ops-upgrade` — research, stage, roll back, and verify software or infrastructure upgrades.
- `ops-document` — write for a future reader or route durable knowledge into the correct existing Saga record.
- `saga-init` — create only the minimum useful Saga spine, explicitly and idempotently.
- `saga-plan` — turn operator intent into observable requirements, dependencies, safety constraints, and proof.
- `saga-run` — execute one bounded slice by default or a capped loop only when explicitly requested.
- `saga-state` — resume, pause, or report project position without inventing progress.
- `saga-check` — keep deterministic structure checks distinct from requirement-to-evidence checking.

`saga-audit` remains separate. It is an explicit, independent frontier-quality review after execution and checking; it never lets an executor certify its own milestone.

Important boundaries:

- `ops-review` reviews a change or subsystem; `saga-audit` certifies milestone close-out independently.
- `ops-document` is for documentation or durable-memory intent, not a wrapper around every ordinary file edit.
- Natural language supplies scope. Operators should not need workflow flags.
- General `ops-*` skills work without `.planning/`; Saga is never imposed automatically.
- Inspect before mutation, verify after mutation, stop before unapproved live or destructive work.
- Never create phase directories or generated phase exhaust.

Temporary compatibility aliases are migration aids only. New work uses the canonical names above; `docs/CAPABILITY-MAP.md` records every legacy disposition.
