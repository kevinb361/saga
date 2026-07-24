---
name: adversarial-review
description: "Compatibility alias for ops-review (one release only, removed at REQ-086). The adversarial-review falsification pass is now ops-review's adversarial lens. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[diff, commit, branch, pull request, or subsystem]"
---

# adversarial-review (compatibility alias)

`adversarial-review` is a **deprecated compatibility alias** kept for one release
cycle so existing invocations and muscle memory keep working during the v2
migration. It holds no implementation of its own.

The former `adversarial-review` behavior — attempt to falsify a change's
behavioral and operational claims with concrete counterexamples, hostile
conditions, and failure sequences (persistence, retries, interruption, mixed
versions, recovery, rollback) — is now the **adversarial lens of `ops-review`**.

## What to do

1. Read and follow the canonical skill: `ops-review`
   (`../../ops/ops-review/SKILL.md` from this directory).
2. Treat this invocation as `ops-review` with its **adversarial lens engaged**:
   extract claimed invariants, construct hostile event sequences, and report
   falsified, surviving, and untested claims. Remain read-only.
3. This is not `saga-audit`: `ops-review` examines a bounded change or subsystem;
   the independent milestone verdict stays with `saga-audit`.

Prefer `ops-review` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
