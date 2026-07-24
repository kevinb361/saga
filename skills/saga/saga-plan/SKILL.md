---
name: saga-plan
description: "Turn operator intent into observable flat milestones, stable requirements, real dependencies, safety invariants, and proof conditions without phase directories or planning exhaust."
category: "saga"
disable-model-invocation: true
argument-hint: "[goal, change, or milestone to plan]"
---

# saga-plan

Plan the work the operator means, not a CRUD transaction against a roadmap. Keep the result small enough to steer execution and strong enough that another agent can tell when it is done.

## Process

1. **Read the project shape.** Inspect project guidance and the existing `STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md`, and `TRACEABILITY.md`. Read relevant specifications, decisions, and current implementation evidence. If no Saga spine exists, stop and suggest explicit `saga-init`; do not bootstrap implicitly.

2. **Frame the intent.** Restate the desired outcome, affected operators/users/systems, current baseline, must-not-break conditions, non-goals, unknowns, and why the work belongs now. Ask only questions whose answers materially change scope, safety, sequencing, or proof. Do not turn guesses into requirements.

3. **Choose observable milestones.** Split only where each milestone delivers a coherent, independently verifiable outcome or creates a necessary safety foundation. Prefer the fewest milestones that expose real delivery boundaries. Do not create phases, waves, sprint buckets, or one milestone per file/component.

4. **Write requirements as claims.** Allocate the next append-only stable REQ IDs; never renumber or reuse an ID. Each requirement states one externally observable outcome, carries its milestone tag, and is small enough to prove with named evidence. Avoid activity verbs such as “investigate,” “improve,” or “implement” unless the resulting behavior is explicit.

5. **Name proof before execution.** For every requirement, identify the expected evidence class: deterministic test, static check, rendered artifact, fresh install lifecycle, live readback, failure injection, published artifact, or independent review. Planning names a proof condition, not fabricated evidence; new requirements remain `[ ]` and OPEN.

6. **Model only real dependencies.** Add `(depends: ...)` only when a requirement cannot be safely completed or proven before another. Keep independent work independent. Reject unknown IDs, self-dependencies, and cycles; do not use dependencies merely to express preferred order.

7. **Make safety load-bearing.** Convert must-not-break conditions into explicit requirements or milestone-wide invariants with a mechanical or live proof. Identify mutation class, approval boundary, rollback/recovery, compatibility window, migration order, and independent judgment where applicable. Safety prose without a gate is not a safety invariant.

8. **Update flat files in place.** Add or edit the active milestone in `ROADMAP.md`, append requirements in `REQUIREMENTS.md`, add matching OPEN rows in `TRACEABILITY.md`, and reconcile current position/next action in `STATE.md`. Preserve shipped history, existing line conventions, frontmatter, unrelated content, and `[x]`/`[/]` compatibility. Never mark done without located evidence.

9. **Validate the plan.** Run the read-only Saga structural check and inspect the requirement graph for cycles, unknown dependencies, contradictory done/open state, duplicate IDs, untagged requirements, and milestones with no proof path. Echo the changed milestone and requirement lines plus unresolved questions.

## Boundaries

Do not implement the planned work while this skill is active. Do not create `.planning/phases/`, per-phase plans, wave files, summaries, verification reports, or generated planning exhaust. Do not archive or rewrite shipped history. Large cross-cutting work may need a frontier-capable planning context, but its durable output is still the same small flat spine.

DONE when the operator's goal maps to observable milestone outcomes; every new REQ has a stable ID, milestone, proof condition, and only real dependencies; safety invariants are explicit; TRACEABILITY starts honestly OPEN; STATE names the next bounded slice; and the structural gate is green.
