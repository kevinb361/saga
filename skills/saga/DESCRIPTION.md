---
name: saga
description: saga — lean files-of-record for AI-assisted coding. Durable records (decisions, state, roadmap, requirements, traceability, retro, specs) plus one bounded-slice executor (saga-next). Plain markdown + git in each project's .planning/; no phase engine, no exhaust.
---

# saga

Files-of-record toolbox: capture the few artifacts worth keeping and execute
work in bounded, verifiable slices.

When to reach for which skill:

- **saga-next** — "what should I do next?" / continue work. Picks one bounded
  slice, executes it behind a deterministic gate, records the outcome. The
  only execution skill; auto-invocable.
- **saga-state** — "where were we?" / resume, pause, note. The living
  position file. Auto-invocable.
- **saga-roadmap** — milestones + requirements CRUD (add/done/edit,
  add-req/edit-req/done-req). Slash-only.
- **saga-verify** — re-derive requirement→evidence traceability from the
  repo; unevidenced checkboxes get reported ASSERTED, never passed. Slash-only.
- **saga-decision** — gated decision records (hard-to-reverse AND surprising
  AND real trade-off, else write nothing). Slash-only.
- **saga-retro** / **saga-context** / **saga-spec** — lessons, glossary,
  living behavior specs. Slash-only.
- **saga-loop** — run slices until a milestone drains. Auto-closes on clean
  drain (verify → audit → ROADMAP flip). Slash-only.
- **saga-audit** — frontier-model quality review after execution. Produces
  `.planning/AUDIT.md`. Slash-only.

House rules: never create phase directories; never force a .planning/ spine
into a repo that lacks one; inspect before mutating; verification reads the
repo, not the doc's self-report.
