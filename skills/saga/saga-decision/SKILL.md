---
name: saga-decision
description: "Record a hard-to-reverse, surprising, trade-off decision as a structured 7-section file in .planning/decisions/ (gated — most choices don't qualify)."
category: "saga"
disable-model-invocation: true
argument-hint: "[short description of the decision you just made]"
---

# /saga-decision

Record a durable decision as `.planning/decisions/NNNN-slug.md` — but only the ones worth keeping. Most
choices are not. This skill's value is the **gate**, not the writing: it refuses to record decisions that
fail the bar, which is why your `decisions/` stays a signal, not a swamp.

## Process

### 1. Apply the 3-criteria gate (state each out loud)

Record **only if ALL THREE hold**:

- **Hard to reverse** — undoing it costs real effort (production network mutation, ownership flip, threshold
  retune, an accepted risk window, a schema/format choice). If it's a cheap toggle, skip.
- **Surprising without context** — a future operator reading the code/config would not guess _why_. If it's
  the obvious move, skip.
- **Result of a real trade-off** — a genuine fork existed (you rejected a viable alternative). If there was
  no real alternative, skip.

If **any** criterion fails: **write nothing.** Say which one failed and propose the lighter record instead
(an inline code comment, or a line in `.planning/STATE.md` via `/saga-state`). Stop here.

### 2. Number it

Next number = (max existing numeric prefix in `.planning/decisions/` + 1), zero-padded to 4. Count legacy
`phase-NNN-*.md` files by their NNN so the sequence never collides. Slug = short kebab summary.

### 3. Write the record

Use the **7-section schema** in `reference.md` (Title, Symptom, Blast Radius, Evidence Links, Default
Disposition, Override Path, Sign-Off). Fill Evidence Links with **concrete** paths / commit SHAs / test names
— never a placeholder. Use operator leading words where they fit (failover, blast radius, route ownership,
canary, rollback, steering cycle, CAKE ceiling).

### 4. Production guard

If the decision touches a production system: the **Override Path
and a rollback note are mandatory before the Sign-Off line** — no signed record without a stated reversal.

## Completion criterion

DONE when EITHER:

- (a) the gate failed, you named the failing criterion, and you proposed the lighter alternative — and NO file
  was written; OR
- (b) a file exists at `.planning/decisions/NNNN-slug.md` containing all 7 sections, with at least one concrete
  path or SHA in Evidence Links (no `TODO`/placeholder), and a Sign-Off line naming the operator and a date.
  Do not stop on a half-filled template.

See `reference.md` for the full template, the numbering rule, and worked gate examples.
