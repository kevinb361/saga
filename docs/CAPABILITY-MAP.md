# v2 capability preservation map

Status: implementation map for the v2.0 unified operator toolbox. It accounts for the two current source trees before compatibility migration. A row marked **absorbed** removes a visible skill name, not the underlying workflow or safety rule.

## General operator skills

| Legacy source skill | v2 owner | Disposition | Material capability preserved |
| --- | --- | --- | --- |
| `adversarial-review` | `ops-review` adversarial lens | absorbed | Extract claimed invariants; construct concrete hostile event sequences; trace persistence, retries, interruption, mixed versions, recovery, and rollback; report falsified, surviving, and untested claims. The uncommitted source under `agent-skills/skills/adversarial-review/` was read during REQ-073 and is represented by `ops-review` source/tests; it must remain untouched until migration is verified. |
| `api-design` | `saga-plan` + `ops-review` | internal discipline | Plan and review HTTP resource shape, versioning, authentication/authorization, errors, pagination, idempotency, caching, compatibility, and evolvability when an HTTP surface is in scope. It is no longer operator-facing methodology vocabulary. |
| `debug` | `ops-troubleshoot` | renamed and broadened | Evidence-driven symptom definition, ranked falsifiable hypotheses, one discriminator at a time, smallest coherent remediation, and fresh original-symptom verification across code, configuration, service, host, and network failures. |
| `dependency-upgrade` | `ops-upgrade` | renamed and broadened | Authoritative release-note review, coupled risk batches, lock/pin discipline, compatibility checks, rollback, and resolved-version proof; expanded to OS packages, containers, services, runtimes, collections, and toolchains. |
| `design-an-interface` | `saga-plan` + `ops-review` | internal discipline | Explore materially different boundaries when interface shape is the hard part, compare real trade-offs, and review callers/compatibility rather than exposing a design-method command. |
| `review` | `ops-review` correctness + operability lenses | absorbed | Read-only scoped diff/subsystem review, real merge-base/context inspection, concrete introduced failures, severity, precise location, remediation, and verification gaps. |
| `security-review` | `ops-review` security lens | absorbed | Explicit assets, actors, trust boundaries, attacker-controlled inputs, privilege, persistence/audit, availability, plausible exploit preconditions, impact, remediation, and proof check. |
| `tdd` | `saga-plan` proof conditions + `saga-run` execution discipline | internal discipline | Observable behavior drives focused tests; stable contracts still use red/green evidence where useful. TDD is an implementation technique selected by the worker, not an operator-facing intent or mandatory ritual for unsuitable work. |
| `verify-before-complete` | every mutating `ops-*` skill + `saga-run` gate | universal invariant | No completion claim without fresh task-relevant evidence; original symptom, resolved version, health, reader checks, or deterministic project gate as appropriate. Red gates cannot be narrated away. |
| `write-docs` | `ops-document` | renamed and broadened | Reader model, sourced claims, current/proposed separation, common path, prerequisites, examples, failure/rollback, public safety, link/command checks, and ownership; adds safe routing into Saga records. |

## Saga lifecycle skills

| Legacy source skill | v2 owner | Disposition | Material capability preserved |
| --- | --- | --- | --- |
| `saga-audit` | `saga-audit` | retained and hardened | Separately visible five-pillar frontier judgment, fresh-context executor independence, idempotent milestone audit, and strict check→audit→mechanical-flip ordering. |
| `saga-context` | `ops-document` context route | absorbed | `.planning/CONTEXT.md` remains the single project glossary and durable non-obvious context source; definitions are linked rather than duplicated. |
| `saga-decision` | `ops-document` decision route | absorbed | The hard-to-reverse **and** surprising **and** real-trade-off gate remains mandatory; failed gate writes no decision file; qualifying records retain concrete evidence and reversal requirements. |
| `saga-lint` | `saga-check` structure lane | absorbed with compatibility alias | Bundled deterministic read-only validator, stable finding codes, file/line evidence, and exit semantics 0 clean / 1 findings / 2 unable to run. |
| `saga-loop` | `saga-run` explicit loop mode | absorbed with compatibility alias | Explicit operator loop consent, contract confirmation, last-five retrospective injection, cap 10, per-iteration rereads, risk/stall/corruption/concurrency stops, and independent fail-closed close-out. |
| `saga-next` | `saga-run` default mode | absorbed with compatibility alias | Auto-invocable exactly-one-slice default, target ordering, plan-before-code, four risk classes, bounded Ansible exception, deterministic gate, two same-slice repairs, escalation, and in-place STATE safety. |
| `saga-retro` | `ops-document` lesson route | absorbed | Dated append-only lessons in `.planning/RETROSPECTIVE.md`; no rewriting/reordering history and no generated per-phase summaries. |
| `saga-roadmap` | `saga-plan` | replaced | Flat ROADMAP/REQUIREMENTS records, stable append-only IDs, observable claims, real dependencies, proof conditions, safety invariants, evidence-required completion, and no phase directories. |
| `saga-spec` | `ops-document` behavior route | absorbed | Living verified behavior remains distinct from milestone plans; direct solo updates, optional staged deltas, domain ownership, GIVEN/WHEN/THEN where useful, and no assumed behavior recorded as truth. |
| `saga-state` | `saga-state` | retained and hardened | Auto resume, note/pause, read-before-action, in-place section edits, frontmatter/RAG key preservation, no invented progress, and concise current/deferred state. |
| `saga-verify` | `saga-check` evidence lane | absorbed with compatibility alias | Every requirement classified exactly once as PROVEN, ASSERTED, OPEN, or WAIVED; `[x]` and `[/]` compatibility; concrete evidence rather than restatement; explicit action list; no audit verdict. |

## Migration rules

1. The v2 source is additive until REQ-083 proves new names, one-release compatibility aliases, foreign-path refusal, and rollback across every supported harness.
2. Old source files and the separate `agent-skills` repository are not deleted by this map. REQ-086 owns archival after migration, release verification, and independent audit.
3. Compatibility aliases preserve invocation continuity; they do not keep duplicate implementations. Alias targets must resolve to the canonical v2 source.
4. Internal disciplines remain load-bearing through target skill text and tests even though they disappear from the visible catalog.
5. If a future diff removes a legacy row or its named preserved mechanics, capability preservation is unproven and the migration must stop.
