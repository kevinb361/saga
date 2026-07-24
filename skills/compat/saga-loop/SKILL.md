---
name: saga-loop
description: "Compatibility alias for saga-run (one release only, removed at REQ-086). The saga-loop explicit multi-slice driver is now saga-run's loop mode. Use when an operator or older automation explicitly invokes the legacy name."
category: "saga"
disable-model-invocation: true
argument-hint: "[--dry-run | --max N | --milestone X.Y]"
---

# saga-loop (compatibility alias)

`saga-loop` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations keep working during the v2 migration. It holds no
implementation of its own.

The former `saga-loop` behavior — drive bounded slices in a capped loop until the
milestone drains or an escalation occurs, then run the independent fail-closed
close-out — is now the **explicit loop mode of `saga-run`**.

## What to do

1. Read and follow the canonical skill: `saga-run`
   (`../../saga/saga-run/SKILL.md` from this directory).
2. Treat this invocation as an explicit request to run `saga-run` in **loop
   mode**: one consent up front, default cap 10, per-iteration STATE and
   REQUIREMENTS re-reads, risk/stall/corruption/concurrency stops, and the
   independent frontier close-out that never self-verifies.
3. Do not weaken the `saga-audit` boundary: the milestone quality verdict and the
   ROADMAP flip remain owned by the independent auditor, exactly as before.

Prefer `saga-run` (with explicit "keep going" intent) in new work. This alias
will be removed once migration is verified and the old repository is archived
(REQ-086).
