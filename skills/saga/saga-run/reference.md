# saga-run Reference

`saga-run` is the v2 execution skill. Its single-slice process is the former `saga-next`; its explicit loop mode
is the former `saga-loop`. This reference consolidates both without reintroducing a phase engine.

## Target resolution

When the operator supplies a target:

1. Exact requirement ID wins: `REQ-104`, `SAFE-21`.
2. Exact roadmap, state, or native-project artifact text wins next.
3. Legacy phase-plan references (`73-06`, `.planning/phases/.../73-06-PLAN.md`) are accepted as source material only.
4. Free text maps to the closest open requirement, active roadmap item, or native artifact.

With no target: use a valid explicit `STATE.md` next step; else prefer OPEN requirements with negative evidence
in `TRACEABILITY.md`; prefer blockers over downstream work; in native mode follow the project's declared
source-to-derived workflow. If the real next step is risky, report it — do not substitute easier work.

## Native-project mode

If `.planning/` is absent, read `CLAUDE.md`, `AGENTS.md`, and `README.md` and derive one bounded slice from the
project's own contract. Do not create `.planning/` automatically. Do not invent requirements or traceability for
a scratchpad, corpus, or one-off utility. Respect generated-file rules, rate limits, and refresh commands. Still
classify risk and stop before unapproved external mutation.

## Risk examples

- `inspect-only`: read files; run tests; query logs or read-only APIs; compare manifests without fetching.
- `repo-only`: edit source/docs/tests; update files of record; add regression coverage.
- `live-mutation`: rebuild or restart a service; deploy or sync to a live host; reindex a live corpus; fetch
  external data; change power, network, or smart-home state.
- `destructive`: delete data/indexes/backups/unmerged work; irreversible migration; roll back by discarding
  current state; broad cleanup without a bounded target.

### Ansible approval

Do not add a second permission round-trip for a bounded Ansible slice. Starting `saga-run` with that slice,
entering a loop that reaches it, or assigning a card that names it counts as approval to run the exact scoped
`ansible-playbook` command. Keep the `live-mutation` label and disclose the target, rollback/recovery path, and
post-run readback. Stop only when the playbook is fleet-wide/unbounded, destructive, ambiguous, lacks recovery,
or project guidance marks it human-only. Static checks (`ansible-lint`, `yamllint`, `--syntax-check`) are
inspect-only; do not assume `--check` is side-effect-free unless local guidance or tests establish that.

## Plan block

Use under `STATE.md` `## Active Work` (or the card comment when scope excludes STATE.md):

```markdown
### <slice id/title>
- Goal: <one observable outcome>
- Touches: <expected files/systems>
- Gate: `<exact command or readback>`
- Risk: <class>; approval/rollback: <requirement or n/a>
- Status: planned
```

Edit STATE.md in place. Preserve all unrelated content and frontmatter.

## Escalation block

After the second gate failure:

```markdown
### ESCALATE: <slice>
- Goal: <done condition>
- Plan attempted: <steps>
- Touches: <files/systems>
- Gate: `<command>`
- Attempt 1: <exact failure>
- Attempt 2: <exact failure>
- Need: <capability or decision required>
- Do not: <scope boundaries and risky actions>
```

Do not mark the requirement complete. A kanban-invoked slice should also report `blocked-escalate` so dispatch
does not blindly retry it.

## Frontier-shaped work

Route up front when the change crosses many files/layers, working context cannot be bounded to a manageable
slice, or architecture/long-horizon sequencing is the hard part. Write a `frontier:` handoff into STATE.md rather
than spending retries on a predictably underscoped attempt.

## Loop contract template (shown before any loop-mode execution)

Loop mode requires explicit operator intent. Before running slices back-to-back, show the contract and wait for
confirmation:

```text
Loop contract for <project>:
  Milestone: <from STATE.md frontmatter>
  Open requirements: <count>
  Active slices: <estimate from STATE.md + ROADMAP>
  Retro lessons loaded: 5 (last 5 from RETROSPECTIVE.md)
  Max iterations: <N or 10 default>
  Stale active work: <escalation block or incomplete item from a prior session, if any>

  Stop conditions:
  - All open slices completed (gate green)
  - Escalation after 2 gate failures
  - Non-Ansible live-mutation/destructive slice without explicit approval
  - Ansible slice that is broad, destructive, ambiguous, or locally human-only
  - Frontier-shaped work detected
  - No forward progress (STATE.md unchanged after an iteration)
  - Milestone shifted mid-loop (concurrent modification)
  - STATE.md unreadable or malformed
  - Max iterations reached (default cap 10)
  - Operator says stop

  Reply "go" to start. Reply with a target to narrow scope.
```

## Retro-as-control injection

Before each slice, read `.planning/RETROSPECTIVE.md` and inject the last 5 entries regardless of topic — recency
is the signal, not editorial judgment. If fewer than 5 exist, inject whatever is there; if empty, skip silently.
Do not filter by relevance: last-5 is deterministic and bounded.

## Termination guards

After each slice returns, check ALL of these before continuing:

**Normal termination:** re-read REQUIREMENTS.md — are all `[ ]` items for the current milestone now done (`[x]`
**or `[/]`** — both mean done)? Re-read STATE.md — is `## Active Work` empty or only deferred? Both → terminate.

**Error termination (stop, report, no close-out):** an escalation block was written (2 gate failures); the slice
reported frontier-shaped work; the slice stopped at a risk checkpoint; the iteration cap was reached.

**Stall detection:** if `## Current Position` and `## Active Work` are byte-identical across an iteration, the
slice completed without reducing work. After 2 consecutive no-progress iterations, STOP: "Loop stalled — no
forward progress detected." This prevents infinite spinning on verify-only or doc-only slices.

**Corruption guard:** if STATE.md is unreadable, truncated, or has malformed YAML frontmatter, STOP immediately.
Do not attempt recovery: "STATE.md appears corrupted, aborting loop." Continuing risks silent drift or
double-execution.

**Concurrent modification guard:** if the STATE.md `milestone:` frontmatter changed between iterations, STOP and
re-present the loop contract — another process may have shifted the active milestone.

## Iteration cap and git dirty state

`--max N` (or a plain-language cap) bounds the loop; default is 10. The loop does NOT commit between slices, so
after N iterations you have one accumulated dirty tree. Always report `Git status: <N> modified, <M> new
(uncommitted)` in the summary. The operator runs the finalization workflow and commits after the loop — that
preserves per-slice reversibility through git.

## Close-out sequence (loop mode, automatic on a clean drain)

Run ONLY when the loop terminated normally — the milestone drained, zero escalations, zero risk-stops, no
stall/corruption abort, cap not hit. On any error termination the milestone is NOT done: skip close-out, report
the stop reason.

```text
1. independent frontier context runs saga-check  → writes .planning/TRACEABILITY.md (full-tree sweep)
2. independent frontier context runs saga-audit   → writes .planning/AUDIT.md (independent verdict)
3. saga-run reads the certified artifacts — SCOPED TO THE ACTIVE MILESTONE:
     of the REQs tagged (milestone: <active>), are they ALL PROVEN?
     (ignore OPEN/ASSERTED reqs tagged to OTHER milestones — they never block this flip)
       YES → flip the ROADMAP marker 🚧→✅ for this milestone (read-then-replace, re-read to confirm)
             saga-state reconcile: Current Position, last_activity, active-milestone pointer
       NO  → STOP close-out. Report this milestone's ASSERTED/OPEN REQ-IDs. No flip.
4. report the verdict, including AUDIT.md PASS | PASS-CONDITIONAL | FAIL
```

Only steps that write a skill/report's OWN file or make a mechanical marker flip are automated. Anything requiring
judgment (an ASSERTED gap, an audit FAIL, an escalation) stops and surfaces.

### Model policy and boundary with saga-check / saga-audit

Check and audit are the *independent-check* stage: the model that executed the slices MUST NOT be the one that
checks and audits them — that is the executor grading its own work, the exact failure the multi-model split
exists to prevent.

Capability alone does not make the executor independent. If the current context executed any milestone slice,
frontier or not, it MUST NOT check or audit that work. A frontier orchestrator may run `saga-check` +
`saga-audit` inline only when separate worker contexts executed every slice and the orchestrator is reading the
files of record fresh. Otherwise delegate to the frontier auditor in `.planning/config.json`
`close_out_auditor`:

  1. Resolve `close_out_auditor`. If empty/absent, emit a paste handoff (milestone, drained slice list, "run
     `saga-check` then `saga-audit` on a frontier model") and STOP — do NOT flip.
  2. Invoke it as ONE synchronous foreground call with a generous timeout and captured output. A full check+audit
     on a large project takes minutes; the ~180s default terminal timeout is the trap that makes a working
     auditor look "hung":

     ```text
     timeout 1200 <close_out_auditor> "<brief>" > .planning/.close-out-auditor.log 2>&1; echo "auditor exit=$?"
     ```

     Do NOT background it (`&`), poll with `sleep`, or re-launch it. One blocking call. The brief instructs the
     frontier context to run `saga-check` then `saga-audit --milestone <X.Y>`, write both artifacts, and print a
     one-line verdict.

  3. **FAIL CLOSED.** After it exits, confirm exit code 0 AND that BOTH `TRACEABILITY.md` AND `AUDIT.md` were
     freshly written by this run. If the exit is non-zero, it timed out, or either artifact is missing/stale, the
     auditor did NOT complete: **STOP the close-out, report "frontier auditor did not complete" with the exit
     code + tail of `.close-out-auditor.log`, and leave the ROADMAP UNflipped. NEVER run `saga-check` or
     `saga-audit` yourself as a fallback** — a non-frontier model self-verifying is the exact integrity hole this
     stage exists to close. A failed auditor fails CLOSED (stop + surface), never OPEN (self-serve). Retry once at
     most with a longer timeout, then hand off to the operator.
  4. When it completes, READ the artifacts — do not trust stdout alone. If every ACTIVE-milestone REQ is PROVEN,
     flip robustly (read the current line, replace its actual 🚧 with ✅, re-read to confirm) and reconcile STATE.
     These mechanical edits may run on the deep loop, but ONLY now, gated on the frontier result. If any
     ACTIVE-milestone REQ is ASSERTED/OPEN, STOP and report the gap.

`saga-run` owns loop control and the mechanical flip; the independent verdict is owned by `saga-audit` and the
structural + evidence check by `saga-check`. `saga-run` never issues the quality verdict and never certifies its
own milestone — that separation is what keeps `saga-audit` a real independent gate.

## Card and deployment safety

- Express scope restrictions as gate conditions, not prose.
- Use isolated worktrees for repo-touching dispatched work.
- Deploy only committed content from a clean worktree or explicit file list.
- Treat deployment approval as permission for the assigned worker to act immediately.
- Guard and invariant tests are read-only within the slice they police — a failure is gate output, not permission
  to weaken the guard.
- Report-only cards end with an explicit terminal completion instruction and include findings as the deliverable.

## Loop drivers and relationship to other tools

A bare `saga-run` is one fresh-context slice; the loop mode is the inline single-operator driver. For wide,
multi-agent, or cross-session work, a Hermes kanban card invokes one target per tick (true session isolation) —
that stays the right tool for long milestones (>10 slices). External phase runners are unsupported: `saga-run`
provides bounded looping without phase exhaust or wave orchestration. Concurrency must respect the measured
capacity of the execution backend: start conservatively, add one replacement worker per completion, and avoid
releasing synchronized retries after a timeout burst.
