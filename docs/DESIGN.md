# Saga design and rationale

## Problem

AI-assisted projects need durable context, but most generated work logs are rarely consulted after the task that created them. The valuable core is small:

- current position
- roadmap and requirements
- named evidence
- consequential decisions
- shared vocabulary
- durable lessons
- behavior that future changes must preserve

Saga keeps that core as plain Markdown and avoids building a workflow engine around it.

## Design principles

### Files are the interface

Project state must remain readable with ordinary tools and repairable without Saga. Git provides history, review, branching, and rollback. Saga does not duplicate those mechanisms.

### One bounded slice

`/saga-next` chooses and executes one inspectable unit of work. Long-running orchestration belongs outside the agent context so each slice can start fresh. `/saga-loop` is a deliberately bounded convenience, not an unbounded phase runner.

### Verification is mechanical

A model’s confidence is not evidence. Each completed slice names a deterministic gate such as a test command, linter, rendered output check, or live readback. Two failed repair attempts stop and produce an escalation brief.

### Risk is explicit

Every slice is classified as inspect-only, repo-only, live mutation, or destructive. Safe local work proceeds; risky mutation requires explicit approval, a rollback path, and observable evidence.

### Records must earn their keep

Decision records use a strict three-part gate. A decision is recorded only when it is:

1. hard to reverse
2. surprising without context
3. the result of a genuine trade-off

Everything else belongs in code, an inline comment, or ordinary project documentation.

### Progressive disclosure

A skill’s `SKILL.md` contains the predictable process and completion criterion. Longer templates, examples, and edge cases live in `reference.md`. This keeps standing context small without hiding operational detail.

### Native projects stay native

Saga can work from `CLAUDE.md`, `AGENTS.md`, and `README.md` when `.planning/` is absent. It does not impose a planning directory on small utilities, content repositories, or projects with an existing files-of-record convention.

## Files of record

| Record | Purpose |
| --- | --- |
| `STATE.md` | current position, blockers, active work, deferred work |
| `ROADMAP.md` | ordered milestones and status |
| `REQUIREMENTS.md` | checkable claims and dependencies |
| `TRACEABILITY.md` | requirement-to-evidence classification |
| `decisions/*.md` | gated consequential trade-offs |
| `CONTEXT.md` | project vocabulary and non-obvious rationale |
| `RETROSPECTIVE.md` | durable lessons and surprises |
| `specs/*/spec.md` | living GIVEN/WHEN/THEN behavior |
| `AUDIT.md` | independent close-out review |

## Invocation policy

`/saga-next` and `/saga-state` may be selected when the operator asks what is next or where work stopped. Skills that create durable records are normally explicit invocations. Mechanical close-out may update traceability and milestone state only when the evidence gate is fully green; judgment calls still stop for the operator.

## Multi-model operation

Roles are capability-based, not tool-pinned:

- planning: a model with enough context for cross-cutting reasoning
- execution: a bounded worker behind deterministic checks
- audit: a fresh context that did not perform the implementation

A non-frontier executor must not certify its own milestone close-out. It hands verification and audit to an independent capable context and trusts files written on disk, not prose returned on stdout.

## Authoring rules

- Use leading words and imperative process steps.
- Give every skill a checkable completion criterion.
- Keep a single source of truth for each rule.
- Delete instructions that do not change behavior.
- Prefer specific stop conditions over broad warnings.
- Keep compatibility behavior generic and isolated.
- Update tests and public docs when behavior changes.
