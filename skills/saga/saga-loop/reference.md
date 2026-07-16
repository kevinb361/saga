# /saga-loop Reference

## Loop contract template (shown to operator in step 2)

```
Loop contract for <project>:
  Milestone: <from STATE.md frontmatter>
  Open requirements: <count>
  Active slices: <estimate from STATE.md + ROADMAP>
  Retro lessons loaded: 5 (last 5 from RETROSPECTIVE.md)
  Max iterations: <N or 10 default>
  Stale active work: <escalation block or incomplete item from prior session, if any>

  Stop conditions:
  - All open slices completed (gate green)
  - Escalation after 2 gate failures
  - Live-mutation/destructive slice without explicit approval
  - Frontier-shaped work detected
  - No forward progress (STATE.md unchanged after an iteration)
  - Milestone shifted mid-loop (concurrent modification)
  - STATE.md unreadable or malformed
  - Max iterations reached
  - Operator says stop

  Reply "go" to start. Reply with a target to narrow scope.
```

Wait for explicit operator confirmation. Do not proceed without it.

## Retro-as-control injection

Before each `/saga-next` invocation, read `.planning/RETROSPECTIVE.md`. Inject the last 5 entries regardless of topic — recency is the signal, not editorial judgment. Prepend to the `/saga-next` context:

```
Lessons from RETROSPECTIVE.md (inject into this slice):
- <most recent entry>
- <second most recent>
... (up to 5)
```

If RETROSPECTIVE.md doesn't exist or has fewer than 5 entries, inject whatever is there. If empty, skip silently.

Do NOT attempt to filter by relevance — that adds subjective judgment and can miss cross-cutting lessons. Last-5 is deterministic and bounded.

## Progress reporting

After each completed slice:

```
[N/M] ✓ <slice description> — <risk level>
Next: <preview of what comes next, or "draining...">
```

N = current iteration count. M = total estimated or "∞" if unknown. Risk level matches the slice classification from `/saga-next` (inspect-only, repo-only, live-mutation, destructive).

For live-mutation or destructive slices, add explicit approval prompt:

```
[N/M] ⚠ <slice description> — <live-mutation>
Touches: <systems affected>
Rollback: <brief rollback path if known>
Approve? (yes/no)
```

Do not execute until the operator confirms. This is per-slice risk disclosure, not just the upfront contract.

## Termination conditions

After each `/saga-next` returns, check ALL of these before continuing:

**Normal termination:**

- Re-read REQUIREMENTS.md — are all `[ ]` items for the current milestone now done (`[x]` **or `[/]`** — both mean done; `[/]` remains a supported compatibility marker)?
- Re-read STATE.md — is `## Active Work` empty or only deferred items remain?
- Both indicate no remaining work → terminate.

**Error termination (stop immediately, report):**

- Escalation block written to STATE.md (2 gate failures) → stop, show escalation brief
- `/saga-next` reports frontier-shaped work → stop, show handoff brief
- `/saga-next` stops at a risk checkpoint → stop, wait for operator
- `--max N` limit reached → stop with summary

**Stall detection (kanban-inspired WIP guard):**

- Compare STATE.md before and after the iteration. If `## Current Position` and `## Active Work` are byte-identical, the slice completed without reducing work. After 2 consecutive no-progress iterations, STOP and report: "Loop stalled — no forward progress detected."
- This prevents infinite spinning on slices that complete but don't close requirements (e.g., verify-only slices, documentation updates).

**Corruption guard:**

- If STATE.md is unreadable, truncated, or has malformed YAML frontmatter, STOP immediately. Do not attempt recovery. Report: "STATE.md appears corrupted, aborting loop."
- Rationale: continuing with bad state risks silent drift or double-execution of slices.

**Concurrent modification guard:**

- If STATE.md `milestone:` frontmatter key changed between iterations, STOP and re-present the loop contract. Another process may have shifted the active milestone.
- This is the kanban equivalent of detecting a board rule change mid-flight.

## Arguments

- `--dry-run`: Show the loop contract and slice queue without executing anything. Useful for previewing what the loop would do before committing.
- `--max N`: Cap the loop at N iterations regardless of remaining work. Default is 10. Prevents runaway sessions on large milestones. Use `--max 0` for unlimited (not recommended).
- `--milestone X.Y`: Only process slices belonging to the specified milestone. During the loop, enforce: if `/saga-next` selects a slice whose requirement belongs to a different milestone, reject it and continue to the next candidate. This prevents scope bleed across milestones.

## Git dirty state

The loop does NOT commit between slices. Each `/saga-next` invocation may edit source files, planning artifacts, and tests — all uncommitted. After N iterations, you have one accumulated dirty tree.

In the post-loop summary, always report:

```
Git status: <N> modified files, <M> new files (uncommitted)
```

The operator should run the project's finalization workflow (`make ci` or project-finalizer agent) and commit after the loop finishes. This preserves per-slice reversibility through git — the operator can cherry-pick or revert individual slices if needed.

## Close-out sequence (step 4, automatic on a clean drain)

Run this ONLY when the loop terminated normally — the milestone drained with zero escalations, zero risk-stops, no stall/corruption abort, `--max` not hit. On any error termination the milestone is NOT done: skip close-out, report the stop reason. The point is that a clean drain leaves the operator nothing to run but the commit.

```
1. /saga-verify                     → writes .planning/TRACEABILITY.md (full-tree sweep)
2. read the classification — SCOPED TO THE ACTIVE MILESTONE:
     of the REQs tagged (milestone: <active>), are they ALL PROVEN?
     (ignore OPEN/ASSERTED reqs tagged to OTHER milestones — they never block this flip)
       YES → flip ROADMAP marker 🚧→✅ for this milestone (mechanical)
             /saga-state reconcile: Current Position, last_activity,
             and the active-milestone pointer (→ next milestone or none)
       NO  → STOP close-out. Report this milestone's ASSERTED/OPEN REQ-IDs.
             Verify caught a gap; the milestone is not shippable. No flip.
             (A cross-milestone open req like REQ-011/v0.5 is NOT such a gap.)
3. /saga-audit --milestone <current> → writes .planning/AUDIT.md (frontier judgment)
4. report the verdict (template below)
```

Only steps that write a skill/report's OWN file or make a mechanical marker flip are automated. Anything requiring judgment (an ASSERTED gap, an audit FAIL, an escalation) stops and surfaces — never auto-resolved. This preserves saga's operator-gated spirit for the judgment cases while removing the mechanical toil.

### Model policy — verify + audit must be frontier, not the executor

Verify and audit are the _independent-check_ stage. The model that executed the slices MUST NOT be the one that verifies and audits them — that is the executor grading its own work, the exact failure the multi-model split (deep executes, frontier audits) exists to prevent.

- **Loop ran on a frontier model** (e.g. operator drives `/saga-loop` in a frontier CLI, or a frontier orchestrator drives deep workers via kanban and re-reads the files of record fresh): run verify + audit inline — they are already frontier and independent of the deep workers.
- **Loop ran ON a non-frontier / deep worker model** (the common Hermes case — `/saga-loop` on the deep/27B lane): do NOT self-verify or self-audit. Delegate the check to the frontier auditor in `.planning/config.json` `close_out_auditor`, then act on its artifacts:

  1. Resolve `close_out_auditor` from `.planning/config.json`. If empty/absent, fall back to a paste handoff (milestone, drained slice list, "run `/saga-verify` then `/saga-audit --milestone <X.Y>` on a frontier model") and STOP — do NOT flip.
  2. Invoke it as ONE synchronous foreground call with a GENEROUS timeout and captured output. A full frontier verify+audit on a large project (100+ reqs) takes several minutes — the ~180s default terminal timeout is the trap that makes a working auditor look "hung." Give it room, run it once, and WAIT for it to exit:

     ```
     timeout 1200 <close_out_auditor> "<brief>" > .planning/.close-out-auditor.log 2>&1; echo "auditor exit=$?"
     ```

     Do NOT background it (`&`), do NOT poll with `sleep`, do NOT re-launch it. One blocking call. The brief:

     "In this repo, run the milestone close-out for <X.Y> as an INDEPENDENT frontier check of work a deep model just executed: run /saga-verify, then /saga-audit --milestone <X.Y>. Write .planning/TRACEABILITY.md and .planning/AUDIT.md. Print a one-line verdict: REQ counts (PROVEN/ASSERTED/OPEN) and audit PASS|CONDITIONAL|FAIL."

     (`claude -p` has the saga-\* skills natively; `codex exec` needs the process spelled into the brief. Validated form: `claude -p --allowedTools Read,Grep,Glob,Bash,Write,Edit --permission-mode acceptEdits` — variadic `--allowedTools` must NOT be last (it swallows the brief); use `acceptEdits` + a scoped allowlist, not `--dangerously-skip-permissions` which a safety classifier may block.)

  2b. **FAIL CLOSED.** After it exits, confirm the auditor actually completed: exit code 0 AND **both** `.planning/TRACEABILITY.md` AND `.planning/AUDIT.md` were freshly written by this run. If the exit is non-zero, it timed out, or either artifact is missing/stale → the auditor did NOT complete: **STOP the close-out, report `"frontier auditor did not complete"` with the exit code + tail of `.close-out-auditor.log`, and leave the ROADMAP UNflipped.** **NEVER run `/saga-verify` or `/saga-audit` yourself as a fallback** — a non-frontier model self-verifying is the exact integrity hole this stage exists to close. A failed auditor fails CLOSED (stop + surface), never OPEN (self-serve). Retry once at most with a longer timeout; then hand off to the operator.

  3. When it completes, READ the artifacts it wrote — do not trust stdout alone. From `.planning/TRACEABILITY.md`, SCOPED to the active milestone: are the REQs tagged `(milestone: <active>)` ALL PROVEN? (A full-tree sweep also lists other milestones' reqs — ignore their OPEN/ASSERTED status; they do not block this flip.)
     - YES → the frontier verify certified it: flip the ROADMAP marker and run the `/saga-state` reconcile. **Flip robustly:** first READ the active milestone's current ROADMAP line, then replace its leading `🚧` with `✅` (and update its status text) using the line's ACTUAL current text — do NOT patch against a pre-composed/assumed string. A stale exact-match patch silently fails and leaves the milestone done-but-unflipped (the exact drift this close-out exists to prevent). After editing, RE-READ the line and confirm it now shows `✅`; if not, the flip did not land — retry or report, do not proceed as if flipped. These mechanical edits may run on the deep loop, but ONLY now, gated on the frontier result — never on the deep model's own say-so.
     - NO → STOP. Report THIS milestone's ASSERTED/OPEN REQ-IDs frontier found. No flip. (Cross-milestone open reqs are not a gap.)
  4. Report the combined verdict (template below) including the auditor's `AUDIT.md` PASS/CONDITIONAL/FAIL.

  Agent→agent (deep→frontier CLI), so still hands-off for the operator: frontier owns the judgment, the deep loop only applies mechanical edits once frontier has certified them.

## Verdict template (clean close-out)

```
Milestone <X.Y> closed:
  Verify:  <N> REQ PROVEN / 0 ASSERTED / 0 OPEN  (TRACEABILITY.md)
  ROADMAP: 🚧 → ✅
  STATE:   reconciled → active milestone now <next or "none">
  Audit:   <PASS | PASS-CONDITIONAL | FAIL>  (AUDIT.md)  — <one-line finding>
  Git:     <N> modified, <M> new (uncommitted)

  Left for you: finalize + commit (project-finalizer, then git commit).
  Nothing else.
```

## Post-loop summary template (error stop — no close-out)

```
Loop stopped for <project> — <stop reason>:
  Slices executed: <count>
  Slices completed: <count>
  Escalations: <count> (list them)
  Gate failures: <count>
  Git status: <N> modified files, <M> new files (uncommitted)

  Milestone NOT closed (reason above). Current state:
  - Open requirements remaining: <count>
  - Active work: <from STATE.md>
  - Deferred: <from STATE.md>
```

## Context budget

- **Context budget:** This loop runs inline — progress lines, retro injections, and state re-reads accumulate in the session context. Disk re-reads add correctness but do NOT evict context — the model retains all accumulated tokens. On shorter-context models (<32K), expect pressure after ~8-10 iterations. On longer contexts (128K+), the loop can drain a typical milestone before hitting limits. Long milestones (>10 slices) belong on kanban cards (true isolation), not this loop.

If the session approaches context capacity, the operator should break the run: stop the loop, start a fresh session, resume with `/saga-loop`. This is the same pattern as kanban boards where a worker session ends and a new one picks up the next card.

Consider using `--max` to bound runs explicitly rather than relying on implicit context limits.

## Anti-patterns

- **Never auto-approve live-mutation slices.** Even in a loop, risky work stops for human review. Per-slice approval is mandatory.
- **Never skip the operator confirmation in step 2.** This is a session loop that may touch many files and services. Explicit consent is required.
- **Never create `.planning/` if absent.** Report the missing spine and suggest `--bootstrap` via `/saga-next`.
- **Never claim "fresh context" per iteration.** This is an inline loop — context accumulates. Each `/saga-next` reads from disk, which is the reliability mechanism. Be honest about what the loop does.

## Relationship to other tools

- `/saga-next`: defines the slice execution process (gating, retry, escalation, file-of-record updates). This skill runs that process inline, repeatedly, as the loop driver.
- `/saga-state`: reads current position. This skill uses it for pre-flight and progress tracking.
- `/saga-retro`: appends to RETROSPECTIVE.md. This skill reads it for control signals.
- `/saga-verify` + `/saga-audit`: the close-out chain, now run automatically by step 4 on a clean drain (verify → conditional ROADMAP/STATE reconcile → audit → verdict). The operator no longer runs these by hand; they only fire on a normal termination, never after an error stop.
- Hermes kanban: alternative loop driver for multi-agent/dispatched work where isolation and tracking matter. Kanban provides true session isolation per card (each worker is a fresh Hermes session). This skill is the single-operator, single-session option — simpler, no DB, no dispatcher daemon, but with the tradeoff of inline context accumulation.
- External phase runners: unsupported. This skill provides bounded looping without phase exhaust or wave orchestration.

## Design rationale

**Why inline instead of subagent dispatch?**
Subagent dispatch (delegate_task) would give true isolation — each slice in its own conversation. But it adds overhead: spawning, serialization, result aggregation. For solo ops where the operator initiated the session and sees every iteration, inline is lower friction. The reliability comes from file-based state, not session isolation.

**Why not cron?**
Cron fires on a timer regardless of whether work exists — wasted tokens, noise, no operator consent. This skill runs in the current session, starts with explicit consent, and stops when there's nothing left to do. No background processes, no polling.

**Why not kanban cards?**
Kanban adds a SQLite DB, dispatcher daemon, card lifecycle — overkill for solo ops where markdown files are the source of truth. This skill keeps everything file-based and inspectable. Kanban stays available for frontier slices that need multi-agent isolation or when you want the dispatcher to run autonomously across sessions.

**What from kanban made it in?**

- Stall detection (kanban reclaim: if a card doesn't move, something is wrong)
- WIP limit of 1 (one slice at a time, like a single-lane board)
- Per-card risk disclosure (shown before each slice, not just upfront)
- Contract presentation (like a board overview before starting work)
