---
name: debug
description: "Compatibility alias for ops-troubleshoot (one release only, removed at REQ-086). The debug evidence-driven hypothesis loop is now ops-troubleshoot. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[symptom, system, or failing check]"
---

# debug (compatibility alias)

`debug` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations and muscle memory keep working during the v2 migration. It
holds no implementation of its own.

The former `debug` behavior — evidence-driven symptom definition, ranked
falsifiable hypotheses, one discriminator at a time, the smallest coherent
remediation, and fresh original-symptom verification — is now
`ops-troubleshoot`, broadened across code, configuration, service, host, and
network failures.

## What to do

1. Read and follow the canonical skill: `ops-troubleshoot`
   (`../../ops/ops-troubleshoot/SKILL.md` from this directory).
2. Treat this invocation as `ops-troubleshoot`: start from observable reality,
   change as little as possible, and prove the original symptom recovered rather
   than a nearby test.

Prefer `ops-troubleshoot` directly in new work. This alias will be removed once
the migration is verified and the old repository is archived (REQ-086).
