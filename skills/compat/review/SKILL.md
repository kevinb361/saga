---
name: review
description: "Compatibility alias for ops-review (one release only, removed at REQ-086). The review read-only code review is now ops-review's correctness and operability lenses. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[diff, commit, branch, pull request, or subsystem]"
---

# review (compatibility alias)

`review` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations and muscle memory keep working during the v2 migration. It
holds no implementation of its own.

The former `review` behavior — a read-only scoped diff or subsystem review over a
real merge-base, reporting concrete introduced failures with severity, precise
location, remediation, and verification gaps — is now the **correctness and
operability lenses of `ops-review`**.

## What to do

1. Read and follow the canonical skill: `ops-review`
   (`../../ops/ops-review/SKILL.md` from this directory).
2. Treat this invocation as `ops-review`'s **correctness and operability
   review**. Add the security or adversarial lens when the surface or operator
   request warrants it. Remain read-only: inspect and report, do not edit,
   remediate, deploy, or change live state.
3. This is not `saga-audit`: `ops-review` examines a bounded change or subsystem;
   the independent milestone verdict stays with `saga-audit`.

Prefer `ops-review` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
