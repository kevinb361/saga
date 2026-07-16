---
name: saga-retro
description: "Append a dated lesson or surprise to .planning/RETROSPECTIVE.md."
category: "saga"
disable-model-invocation: true
argument-hint: "[what to capture — a lesson, surprise, or what you'd do differently]"
---

# /saga-retro

Append a dated entry to `.planning/RETROSPECTIVE.md` (or the project's existing `LEARNINGS.md`) — the durable
record of what was learned, so the next milestone doesn't relearn it. Append-only; never rewrite past entries.

## Process

1. Find the project's retro file: prefer an existing `.planning/RETROSPECTIVE.md` or `LEARNINGS.md`; if neither
   exists, create `RETROSPECTIVE.md` with a `# Retrospective: <project>` heading.
2. Append a dated entry capturing at least one of: **what happened**, **what surprised you**, **what to do
   differently**. Operator terms, not generic filler — "went well" is a no-op; "icmplib beat fping on jitter under
   load, kept it" is signal.
3. If the entry implies a durable rule or a reusable term, flag it for promotion: a rule → `CLAUDE.md`; a term →
   `/saga-context`; a hard-to-reverse choice → `/saga-decision`.

## Completion criterion

DONE when a dated entry is appended (existing entries untouched) containing at least one concrete surprise or
lesson in operator terms, and any durable rule/term/decision it implies has been flagged for promotion to its
proper home. Do not append a generic "milestone complete, went well" with no specific learning.
