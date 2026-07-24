---
name: security-review
description: "Compatibility alias for ops-review (one release only, removed at REQ-086). The security-review threat-model pass is now ops-review's security lens. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[diff, commit, branch, pull request, or subsystem]"
---

# security-review (compatibility alias)

`security-review` is a **deprecated compatibility alias** kept for one release
cycle so existing invocations and muscle memory keep working during the v2
migration. It holds no implementation of its own.

The former `security-review` behavior — an explicit threat model over assets,
actors, trust boundaries, attacker-controlled inputs, privilege, persistence and
audit, and availability, with plausible exploit preconditions, impact,
remediation, and a proof check — is now the **security lens of `ops-review`**.

## What to do

1. Read and follow the canonical skill: `ops-review`
   (`../../ops/ops-review/SKILL.md` from this directory).
2. Treat this invocation as `ops-review` with its **security lens engaged**:
   build the explicit threat model above and report exploitable findings with
   preconditions, impact, and remediation. Remain read-only.
3. This is not `saga-audit`: `ops-review` examines a bounded change or subsystem;
   the independent milestone verdict stays with `saga-audit`.

Prefer `ops-review` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
