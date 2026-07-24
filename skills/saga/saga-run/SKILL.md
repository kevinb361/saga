---
name: saga-run
description: "Execute planned Saga work safely: one bounded slice behind a deterministic gate by default, a bounded multi-slice loop only on explicit intent. Use for 'what next', 'continue', 'run this', or 'keep going'; reads .planning/ or native guidance; stops before risky live mutation."
category: "saga"
disable-model-invocation: false
argument-hint: "[what to run | keep going until X]"
---

# saga-run

Execute the next bounded work slice and either finish it behind a deterministic gate or stop at an explicit
risk checkpoint. `saga-run` is NOT a phase engine. **A bare or auto-invoked `saga-run` executes exactly one
bounded slice and stops** — one invocation = one slice. Progress lives in the files of record, not in a growing
conversation, so a fresh context can resume from disk. Looping across multiple slices happens ONLY on explicit
operator intent (see `## Loop mode`); **never interpret a bare invocation as permission for an unbounded loop.**

## One bounded slice (default)

1. **Read the local shape first.** If `.planning/` exists, read `STATE.md`, `ROADMAP.md`, `REQUIREMENTS.md`, and
   `TRACEABILITY.md` when present. If `TRACEABILITY.md` is missing or stale relative to `REQUIREMENTS.md`, run the
   `saga-check` process first or report that checking is the next slice. **Checkbox markers are 3-state:** `[ ]`
   = not done (a candidate slice); **`[x]` AND `[/]` both mean done** — never pick a `[/]` requirement as "next
   open work" (`[/]` is a supported compatibility marker, so treating it as open re-does shipped work). If
   `.planning/` is absent, DO NOT create it automatically; read `CLAUDE.md` / `AGENTS.md` / `README.md` and
   operate in native-project mode. Completion: position, open work, and blockers are visible before choosing.

2. **Resolve the target.** If the operator supplied a target, map it to a requirement ID, roadmap item, state
   note, or native artifact. If none was supplied, choose the next slice in this order: explicit `STATE.md` next
   step; OPEN requirement with negative/blocking evidence; OPEN requirement that blocks other work; active
   roadmap/native item with no evidence. Completion: exactly one slice is named with the evidence that made it
   next. An operator instruction that NARROWS scope ("touch only file X") is itself part of the gate — violating
   it makes the gate red no matter what else passed.

3. **Plan before code.** Write a 3–5 line plan into `.planning/STATE.md` `## Active Work` (or the native
   equivalent) BEFORE editing anything — it is the external memory a fresh iteration resumes from. **STATE.md is
   edited IN PLACE, never rewritten.** Read it first; append or update ONLY the `## Active Work` section; every
   other byte — YAML frontmatter, milestone fields, history, deferred items — is preserved verbatim. Replacing
   STATE.md wholesale is a scope violation that makes the gate red. If STATE.md cannot be read, put the plan in a
   card comment instead. If the slice is **frontier-shaped** (cross-cutting refactor across many files/layers,
   needs >~100K working context, or the plan itself is the hard part), do NOT attempt it: record it in STATE.md
   as `frontier: <slice>` with a ready-to-paste handoff and stop.

4. **Classify risk.** Label the slice `inspect-only`, `repo-only`, `live-mutation`, or `destructive`.
   - `inspect-only`: read/test/verify only.
   - `repo-only`: local source/docs/tests/derived-artifact edits.
   - `live-mutation`: deploy, restart, reindex, service config, network fetch/refresh, power, or production-ish change.
   - `destructive`: deletion, rollback, data loss, irreversible migration.
   - **Ansible approval rule:** a Saga invocation or assigned card that names a bounded Ansible slice is itself
     approval to run its scoped `ansible-playbook` command — do not ask again merely because Ansible changes a
     managed host. The exception requires an exact playbook, bounded host/limit, a rollback or idempotent
     recovery path, and post-run evidence. It never covers fleet-wide, destructive, ambiguous, or locally
     human-only execution. Completion: risk label, touched system, rollback/evidence need, and stop/continue are explicit.

5. **Execute or stop.** Execute inspect-only/repo-only slices directly when the context allows it, and a bounded
   Ansible slice directly under the step-4 rule without a redundant prompt. For any other live-mutation or
   destructive slice, **stop before mutation unless the operator explicitly approved that mutation in this
   invocation.** Completion: no risky mutation happens by implication.

6. **Verify at the gate — the gate decides, not you.** Resolve the gate command: `.planning/config.json` `gate`
   key → `make ci` if a Makefile defines it → the repo's evident test/lint runner → for non-code slices, the
   narrowest mechanical check that proves the slice. Run it. The slice CANNOT be recorded done while the gate is
   red — gate output is ground truth; self-assessment is not evidence.
   - **On gate failure: retry with the error, at most 2 same-slice repairs.** Re-attempt the SAME slice feeding
     the exact failing output back in. Do not widen scope or start a different slice.
   - **On the 2nd gate failure: STOP and escalate.** Write a ready-to-paste escalation block to STATE.md
     `## Active Work` (slice, plan, attempts, exact failing output — see `reference.md`). If invoked from a
     kanban card, report `blocked-escalate`. Never mark the slice done; never silently move on.

7. **Update files of record.** With a saga spine, update `.planning/STATE.md` (in-place, per step 3) and
   `.planning/TRACEABILITY.md` when requirement evidence changed. If observable behavior changed, update the
   living spec. Never author or edit agent skill files as part of a slice — Saga skills live only in their source
   repo and install via `install.sh`; a lesson worth keeping goes to `RETROSPECTIVE.md` or docs, never a new
   skill dropped in `~/.hermes/skills` or `~/.claude/skills`. Completion: durable state matches verified reality;
   no phase-plan exhaust is created.

## Loop mode (explicit intent only)

A bare invocation runs one slice and stops. Run multiple slices back-to-back ONLY when the operator explicitly
asks to — natural language such as "keep going until something needs me", "drain this milestone", or a narrowed
"keep going on v2.0". This intent, not a flag, is the loop consent; a bare or auto-invoked `saga-run` is never
loop consent.

When loop intent is present:

- **Bounded by default.** Run at most a **default cap of 10 iterations**; a larger milestone belongs on kanban
  cards (true isolation), not this inline loop. The operator may narrow the cap; unbounded running is not offered.
- **Re-read between iterations.** Each iteration re-reads `STATE.md` and `REQUIREMENTS.md` from disk and injects
  the last 5 `RETROSPECTIVE.md` entries before running the one-slice process above. Disclose each slice's risk as
  `[N/M] <slice> — <risk>` before executing it.
- **Stop conditions (stop and report, no close-out):** escalation after the 2nd gate failure; a non-Ansible
  live-mutation/destructive slice without explicit approval; a broad/destructive/ambiguous/human-only Ansible
  slice; frontier-shaped work; no remaining slices; the iteration cap reached; **stall** (STATE.md byte-identical
  across 2 iterations); **concurrent modification** (`milestone:` frontmatter changed mid-loop); or **corruption**
  (STATE.md unreadable or malformed frontmatter).
- **Close-out (automatic on a clean drain only).** If — and only if — the loop drained the active milestone with
  zero escalations and zero risk-stops, run the independent close-out: an independent frontier context (from
  `.planning/config.json` `close_out_auditor`) runs `saga-check` then `saga-audit` as ONE synchronous foreground
  call with a generous timeout. **FAIL CLOSED:** if it exits non-zero or does not freshly write BOTH
  `TRACEABILITY.md` AND `AUDIT.md`, STOP and report — **NEVER run `saga-check` or `saga-audit` yourself as a
  fallback** (a non-frontier executor self-certifying is the integrity hole this stage exists to close). `saga-run`
  never issues the milestone verdict and never grades its own work; it only reads the certified artifacts and, if
  every ACTIVE-milestone requirement is PROVEN, flips the ROADMAP marker 🚧→✅ (read-then-replace, re-read to
  confirm) and reconciles STATE. The independent quality verdict stays owned by `saga-audit`.

## Completion criterion

For a single slice: DONE when it was (a) completed with the gate green and the record updated, (b) blocked at a
clear risk checkpoint with the exact approval needed, or (c) escalated after 2 gate failures with the handoff
block on disk. For loop mode: DONE when the loop drained all active slices AND the independent frontier close-out
certified them (then the mechanical flip ran), or it stopped at a gate requiring the operator with NO close-out
run (milestone not done). Never loop within a bare invocation; never create `.planning/phases/`, wave plans, or
SUMMARY/VERIFICATION exhaust; never record done on a red gate; never rewrite STATE.md wholesale.

See `reference.md` for target resolution, native-project mode, risk examples, the loop contract, termination
guards, and the close-out sequence, model policy, and boundary with `saga-check` and `saga-audit`.
