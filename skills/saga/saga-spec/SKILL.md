---
name: saga-spec
description: "Maintain the living behavior spec library in .planning/specs/ — delta-driven, domain-organized, updated as changes are verified. The accumulated 'what the system currently does' across milestones."
category: "saga"
disable-model-invocation: true
argument-hint: "[show | add <domain> | delta <change> | merge <milestone> | init]"
---

# /saga-spec

Maintain `.planning/specs/<domain>/spec.md` — the living behavior spec library. Unlike
REQUIREMENTS.md (per-milestone plan), SPECS is the accumulated truth: what the system
currently does, updated via deltas as changes are verified. Delta-first — record what
changed, not what exists.

## Process

### init

1. If `.planning/specs/` is absent, create it. For small projects (<=5 domains), a single
   `.planning/SPEC.md` is acceptable — use that instead. Print confirmation.

### show

1. List `.planning/specs/<domain>/spec.md` files with their last-modified dates and
   requirement counts. If a domain is named, print its spec contents.

### add

1. Create or append to the domain spec file. Use the lite spec format (see reference.md):
   short behavior-first requirements, GIVEN/WHEN/THEN scenarios, scope/non-goals. No
   implementation detail. Use operator leading words where they fit.

### delta

1. Record a behavioral change as a delta block at the bottom of the relevant spec file(s).
   Format: `## Delta: <change-id> — <YYYY-MM-DD>` with ADDED/MODIFIED/REMOVED requirement
   blocks. Check for existing unmerged deltas first — if another delta exists in the same
   file, append with a clear separator. Commit immediately to avoid conflicts.

2. **For solo workflow, skip the delta step** — just update the spec directly in the
   Requirements section. Use `delta` only when you want a visible staging step (e.g.,
   mid-milestone with multiple pending changes).

### merge

1. For each spec file with unmerged delta blocks, fold deltas into the main Requirements
   section and remove the delta metadata. Print a summary of changes. No phase directories.

## Completion criterion

DONE when the requested action is applied to the correct spec file(s), the delta format
is consistent with reference.md, and no stale delta blocks remain after a merge. Do not
invent requirements — only record what has been verified or explicitly scoped. Keep specs
lite: behavior contracts, not implementation plans.

See `reference.md` for the spec format, delta format, and worked examples.
