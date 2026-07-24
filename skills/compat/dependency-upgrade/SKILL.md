---
name: dependency-upgrade
description: "Compatibility alias for ops-upgrade (one release only, removed at REQ-086). The dependency-upgrade batched upgrade workflow is now ops-upgrade. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[component, system, or desired version]"
---

# dependency-upgrade (compatibility alias)

`dependency-upgrade` is a **deprecated compatibility alias** kept for one release
cycle so existing invocations and muscle memory keep working during the v2
migration. It holds no implementation of its own.

The former `dependency-upgrade` behavior — authoritative release-note review,
coupled risk batches, lock and pin discipline, compatibility checks, rollback,
and resolved-version proof — is now `ops-upgrade`, broadened to OS packages,
containers, services, runtimes, collections, and toolchains.

## What to do

1. Read and follow the canonical skill: `ops-upgrade`
   (`../../ops/ops-upgrade/SKILL.md` from this directory).
2. Treat this invocation as `ops-upgrade`: preserve the native management path,
   keep unrelated cleanup out, gate on risk, and verify both the selected version
   and useful health.

Prefer `ops-upgrade` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
