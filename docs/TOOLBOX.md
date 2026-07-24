# Unified operator toolbox contract

Status: **IMPLEMENTED and independently verified for v2.0**. The canonical skills, package export, four-harness migration, compatibility aliases, and rollback are live; public release/archive remains gated by REQ-086.

## Purpose

The toolbox is for a Linux operator who uses agents to inspect systems, troubleshoot failures, make bounded changes, and maintain projects without having to choose software-development methodology or remember workflow flags.

The visible surface stays small:

- `ops-*` expresses a general operator intent and works without a Saga spine.
- `saga-*` manages durable project planning, execution, state, proof, and independent close-out.
- Skill names identify the version-controlled package family rather than a local one-off skill.
- Natural language supplies scope. CLI flags may exist behind the skill but are not the user interface.

## Package source

This `saga` repository is the canonical package source because it retains Saga's meaningful history, executable tools, tests, release machinery, and all implemented `ops-*` and canonical `saga-*` skills. Its root `package.json` identifies the public `saga-operator-toolbox` v2.0.0 package and explicitly exports the exact 21-leaf transition surface: 11 canonical skills plus 10 one-release compatibility aliases.

The separate `agent-skills` repository was an input source. Its material capabilities and uncommitted adversarial-review work are accounted for in `CAPABILITY-MAP.md`; the live four-harness migration now resolves into this checkout. Archival remains a separately gated release action, never an implied deletion.

## Operator skills

| Skill | Operator intent | Activation | Boundary |
| --- | --- | --- | --- |
| `ops-grill-me` | Ask hard questions until the real goal, constraints, decisions, and unknowns are clear. | Explicit only; ordinary work should not turn into an unsolicited interview. | Inspect known context first, ask bounded high-value rounds, summarize the handoff, and do not mutate files unless requested. |
| `ops-troubleshoot` | Find out why code, configuration, a service, host, or network path is failing and resolve the root cause. | Use for unclear, difficult, or recurring failures. | Inspect live evidence before mutation, rank falsifiable hypotheses, test one discriminator at a time, and verify the original symptom after remediation. |
| `ops-review` | Give a proposed change or bounded subsystem a careful second look. | Use when the operator asks for review; remain read-only. | Always review correctness and operability. Add named security and adversarial lenses when trust boundaries, hostile conditions, state, recovery, migration, or production risk warrant them. |
| `ops-upgrade` | Upgrade a package, runtime, container, application, service, collection, toolchain, or operating-system component safely. | Use when the operator asks to upgrade or assess an upgrade. | Read authoritative release notes, stage coupled changes, establish rollback, classify live/destructive risk, stop before unapproved mutation, and verify version plus health afterward. |
| `ops-document` | Preserve information for the right future reader. | Use when documentation or durable project memory is the requested deliverable. | Write reader-facing docs normally; when a Saga spine exists and the intent is durable project memory, preserve the existing decision gate, glossary ownership, append-only lesson history, behavior-spec truth, and STATE safety rules. |

## Saga lifecycle skills

| Skill | Operator intent | Activation | Boundary |
| --- | --- | --- | --- |
| `saga-init` | Start using Saga in this project. | Explicit only. | Inspect existing guidance, create only the minimum useful spine, detect a mechanical gate where possible, remain idempotent, and never invent requirements or impose Saga automatically. |
| `saga-plan` | Turn an operator goal into milestones, observable requirements, real dependencies, safety invariants, and proof conditions. | Explicit planning intent. | Replace the visible roadmap CRUD vocabulary without creating phase directories, plan exhaust, speculative requirements, or implementation work. |
| `saga-run` | Execute planned work safely. | Auto-invocable for one next bounded slice; multiple slices require explicit natural-language intent. | Preserve deterministic gates, risk disclosure, bounded retries, escalation, state re-reads, and stop conditions. Never interpret a bare invocation as permission for an unbounded loop. |
| `saga-state` | Tell me where the project stands, or record where work paused. | Auto-invocable for status, resume, pause, and handoff intent. | Preserve frontmatter and unrelated content, edit in place, keep state concise, and never invent progress. |
| `saga-check` | Determine whether Saga's records are structurally sound and requirements are backed by named evidence. | Use for validation, completion checks, and traceability questions. | Keep deterministic lint and requirement-evidence results distinct. It may update traceability but never issues the independent quality verdict owned by `saga-audit`. |
| `saga-audit` | Independently judge whether a completed milestone is correct, safe, operable, and ready to close. | Explicit close-out only; run from a capable context independent of the executor. | Remain separately visible, fail closed when the auditor does not complete, and finish before any ROADMAP completion flip. A local executor never certifies its own milestone. |

## Natural-language interface

The common path must be obvious without flags. Invocation syntax is harness-specific: Pi uses `/skill:<name>`, while other supported harnesses may expose the skill name directly as a slash command or select it from ordinary language.

```text
ops-grill-me: help me work out what this alerting change should do
ops-troubleshoot: the service is healthy but requests time out
ops-review: review this migration and really try to break it
ops-upgrade: upgrade this container safely
ops-document: write the recovery runbook

saga-init
saga-plan: add health monitoring to this service
saga-run
saga-run: keep going until something needs me
saga-state: where are we?
saga-check: is this milestone actually proven?
saga-audit: audit the completed v2.0 milestone
```

Underlying tools may use flags for deterministic execution. Skill descriptions and examples must not require the operator to discover or memorize those flags.

## Non-negotiable invariants

1. Inspect before mutating and verify after mutating.
2. Read-only, repository-only, live-mutation, and destructive work remain distinguishable.
3. Live or destructive mutation requires explicit scope, observable evidence, and a rollback or recovery path.
4. `saga-run` defaults to one bounded slice; looping is explicit and bounded.
5. `saga-audit` remains independent from execution and from the cheaper `saga-check` path.
6. Check and audit complete before a milestone is marked complete.
7. Consolidating visible skills must not silently discard existing review disciplines or Saga record safeguards.
8. Migration preserves compatibility and rollback until the new package is independently verified.
9. Documentation distinguishes planned, implemented, installed, and live-verified behavior.
10. The installed skill surface remains inspectable as version-controlled source.
