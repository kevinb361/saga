---
name: saga-next
description: "Compatibility alias for saga-run (one release only, removed at REQ-086). The saga-next single-slice workflow is now saga-run's default mode. Use when an operator or older automation explicitly invokes the legacy name."
category: "saga"
disable-model-invocation: true
argument-hint: "[target | --dry-run | --no-execute | --bootstrap]"
---

# saga-next (compatibility alias)

`saga-next` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations and muscle memory keep working during the v2 migration. It
holds no implementation of its own.

The former `saga-next` behavior — find and execute the next bounded work slice
behind a deterministic verification gate — is now the **default mode of
`saga-run`**. A bare `saga-run` invocation runs exactly one bounded slice, which
is precisely what `saga-next` did.

## What to do

1. Read and follow the canonical skill: `saga-run`
   (`../../saga/saga-run/SKILL.md` from this directory).
2. Treat this invocation as `saga-run` in its **single-slice default mode**. Do
   not start a multi-slice loop unless the operator explicitly asked to keep
   going — that is `saga-run`'s explicit loop mode, formerly `saga-loop`.
3. Preserve every `saga-run` guarantee unchanged: deterministic gate, four risk
   classes with stop-before-mutation, ≤2 same-slice repairs then escalation,
   in-place STATE safety, and `[x]`/`[/]` done semantics.

Prefer `saga-run` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
