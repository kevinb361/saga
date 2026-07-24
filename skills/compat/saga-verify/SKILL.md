---
name: saga-verify
description: "Compatibility alias for saga-check (one release only, removed at REQ-086). The saga-verify requirement-to-evidence pass is now saga-check's evidence lane. Use when an operator or older automation explicitly invokes the legacy name."
category: "saga"
disable-model-invocation: true
argument-hint: "[milestone — defaults to the current one in REQUIREMENTS.md]"
---

# saga-verify (compatibility alias)

`saga-verify` is a **deprecated compatibility alias** kept for one release cycle
so existing invocations keep working during the v2 migration. It holds no
implementation of its own.

The former `saga-verify` behavior — classify every requirement against named
evidence as PROVEN / ASSERTED / OPEN / WAIVED and write
`.planning/TRACEABILITY.md` — is now the **evidence lane of `saga-check`**.

## What to do

1. Read and follow the canonical skill: `saga-check`
   (`../../saga/saga-check/SKILL.md` from this directory).
2. Treat this invocation as `saga-check`'s **evidence lane**: run the
   requirement-to-evidence traceability pass, not the deterministic structure
   lane and not an audit verdict.
3. Preserve the boundary unchanged: `saga-check` never issues the independent
   milestone quality verdict, which remains owned by `saga-audit`. `[x]` and
   `[/]` both count as done; unevidenced `[x]` is ASSERTED, never PROVEN.

Prefer `saga-check` directly in new work. This alias will be removed once
migration is verified and the old repository is archived (REQ-086).
