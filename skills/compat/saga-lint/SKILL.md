---
name: saga-lint
description: "Compatibility alias for saga-check (one release only, removed at REQ-086). The saga-lint deterministic validator is now saga-check's structure lane and stays runnable here via scripts/run.sh. Use when an operator or older automation explicitly invokes the legacy name."
category: "saga"
disable-model-invocation: true
argument-hint: "[PATH] [--format human|json]"
---

# saga-lint (compatibility alias)

`saga-lint` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations keep working during the v2 migration. It holds no
implementation of its own; the deterministic validator is the same bundled
`bin/saga-lint`, now surfaced as the **structure lane of `saga-check`**.

## Run the deterministic check

The validator remains directly runnable under this legacy name, preserving the
exact contract (exit `0` clean / `1` findings / `2` unable to run, plus schema
1.0 JSON):

```bash
./scripts/run.sh [PATH] [--format human|json]
```

`scripts/run.sh` resolves the bundled `bin/saga-lint` from the source checkout
even when invoked through an agent-home symlink; no global binary is required.

## Prefer saga-check

For the full check surface — the deterministic structure lane above **plus** the
model-assisted requirement-to-evidence lane — read and follow the canonical
skill `saga-check` (`../../saga/saga-check/SKILL.md` from this directory). This
alias will be removed once migration is verified and the old repository is
archived (REQ-086).
