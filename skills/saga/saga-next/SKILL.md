---
name: saga-next
description: "Find and execute the next bounded work slice behind a deterministic verification gate. Use when asked 'what next', 'continue', 'keep going', or to pick up project work; reads .planning/ or native project guidance; stops before risky live mutation."
category: "saga"
disable-model-invocation: false
argument-hint: "[target | --dry-run | --no-execute | --bootstrap]"
---

# /saga-next

Find the next bounded work slice and either execute it safely or stop at an explicit risk checkpoint. It is
deliberately NOT a phase engine — and NOT a loop. One invocation = one slice; the loop driver lives OUTSIDE (a Hermes kanban card
dispatching this skill per tick, a cron, or the operator repeating it). Fresh context per iteration is the
point: progress lives in the files of record, not in a growing conversation.

## Process

1. **Read the local shape first.** If `.planning/` exists, read `.planning/STATE.md`, `.planning/ROADMAP.md`,
   `.planning/REQUIREMENTS.md`, and `.planning/TRACEABILITY.md` when present. If `TRACEABILITY.md` is missing or
   stale relative to `REQUIREMENTS.md`, run the `/saga-verify` process first or report that verification is the
   next slice. **Checkbox markers are 3-state:** `[ ]` = not done (a candidate slice); **`[x]` AND `[/]` both mean
   done** — never pick a `[/]` req as "next open work" (`[/]` is a supported compatibility marker, so treating
   it as open would re-do shipped work). If `.planning/` is absent, DO NOT create it automatically; read `CLAUDE.md` / `AGENTS.md` /
   `README.md` and operate in native-project mode from that project's own conventions. Completion: current
   position, open work, and known blockers are visible before choosing work.

2. **Resolve the target.** If the operator supplied a target, map it to a requirement ID, roadmap item, state
   note, native-project artifact, or legacy phase-plan file. If no target was supplied, choose the next slice in
   this order: explicit `STATE.md` next step; OPEN requirement with negative/blocking evidence; OPEN requirement
   that blocks other work; active roadmap/native-project item with no evidence. Completion: exactly one slice is
   named with the evidence that made it next.

3. **Bound the slice and route it.** If the operator's instruction NARROWS scope below this skill's
   defaults (e.g. "touch only file X", "do not update other records"), the narrowing IS part of the
   gate: violating it means the gate is red no matter what else passed. Operator restrictions always
   beat this skill's own step-7 defaults.
   Reduce the target to one inspectable unit that can be completed and
   verified without sprawling — short horizon beats clever scope (agents fail non-linearly with compositional
   depth). Do not fan out across phases, waves, or many independent plans. If the slice is **frontier-shaped**
   — a cross-cutting refactor spanning many files/layers, needs >~100K tokens of working context, or the plan
   itself is the hard part — do NOT attempt it here: record it in STATE.md as `frontier: <slice>` with a
   ready-to-paste handoff and stop. Completion: the slice has a clear done condition, a short list of expected
   file/host touches, and a local-vs-frontier route.

3b. **Plan before code.** Write a 3–5 line plan for the slice into `.planning/STATE.md` `## Active Work`
(or the native-project equivalent) BEFORE editing anything — it is the external memory a fresh-context
iteration resumes from, and the reviewable intent if the slice escalates.
**STATE.md is edited IN PLACE, never rewritten.** Read the existing file first; append or update ONLY
the `## Active Work` section (create that one section if absent). Every other byte is preserved
verbatim — especially the YAML frontmatter, version markers, milestone fields, and the history/deferred
sections consumed by project indexing. Replacing STATE.md with a fresh minimal
file is a scope violation that makes the gate red regardless of what else passed (2026-07-12
incident: a worker clobbered a project's full STATE.md with its own scratch state). If STATE.md
cannot be read, do NOT create one — put the plan in a card comment instead.
Completion: the plan is on disk AND the rest of STATE.md is unchanged.

4. **Classify risk.** Label the slice `inspect-only`, `repo-only`, `live-mutation`, or `destructive`.
   - `inspect-only`: read/test/verify only.
   - `repo-only`: local source/docs/tests/derived-artifact edits.
   - `live-mutation`: deploy, restart, reindex, service config, network fetch/refresh, power, or production-ish change.
   - `destructive`: deletion, rollback, data loss, irreversible migration.
   - **Ansible approval rule:** a Saga invocation or assigned card that names a bounded Ansible slice is itself
     approval to run its scoped `ansible-playbook` command. Do not ask again merely because Ansible changes a
     managed host. This exception requires an exact playbook, bounded host/limit, rollback or idempotent recovery
     path, and post-run evidence. It never covers all-host/fleet-wide, destructive, ambiguous, or locally marked
     human-only execution.
     Completion: risk label, touched system, rollback/evidence requirement, and stop/continue recommendation are explicit.

5. **Execute or stop.** Execute inspect-only/repo-only slices directly when the current tool/user context allows
   it. Execute a bounded Ansible slice directly under the step-4 approval rule without a redundant permission
   prompt. For other live-mutation/destructive slices, stop before mutation unless the operator explicitly
   approved that mutation in this invocation. Completion: no risky mutation happens by implication.

6. **Verify at the gate — the gate decides, not you.** Resolve the project's gate command in this order:
   `.planning/config.json` `gate` key → `make ci` if a Makefile defines it → the repo's evident test/lint
   runner → for non-code slices, the narrowest mechanical check that proves the slice (live readback, link
   check, render). Run it. The slice CANNOT be recorded done while the gate is red — gate output is ground
   truth; self-assessment is not evidence.
   - **On gate failure: retry with the error, max 2 retries.** Re-attempt the SAME slice feeding the exact
     failing output back into the fix. Do not widen scope, do not start a different slice.
   - **On the 2nd gate failure: STOP and escalate.** Write an escalation block to STATE.md `## Active Work`
     (slice, plan, what was attempted, the exact failing output — formatted as a ready-to-paste brief for an escalation-capable agent
     handoff; see reference.md). If invoked from a kanban card, report the card as blocked-escalate. Never
     mark the slice done, never silently move on.
     Completion: gate green with the command + output named, or an escalation block on disk.

7. **Update files of record.** When a saga spine exists, update `.planning/STATE.md` with the new position
   (in-place edit of the relevant sections only — same non-clobber rule as step 3b) and
   `.planning/TRACEABILITY.md` when requirement evidence changed. If the slice changed observable behavior,
   update the living spec via `/saga-spec` (inline update preferred; explicit delta only when staging multiple
   pending changes). In native-project mode, update the project's own durable artifact only when the local
   guidance says it is derived/maintained by hand. Use `/saga-roadmap`, `/saga-decision`, `/saga-retro`, or
   `/saga-spec` only when their gates actually apply. Completion: durable state matches verified reality; no
   phase-plan exhaust is created.

## Completion criterion

DONE when one next slice has either (a) been completed with the gate green and the record updated, (b) been
blocked at a clear risk checkpoint with the exact approval needed, or (c) escalated after two gate failures
with the handoff block on disk. Never loop within one invocation; never create `.planning/phases/` directories,
wave plans, or SUMMARY/VERIFICATION exhaust; never force `.planning/` into a native project unless the operator
explicitly asks for `--bootstrap`; never record done on a red gate; never rewrite `.planning/STATE.md`
wholesale (in-place section edits only — step 3b); never author or edit agent skill files as
part of a slice — saga skills live only in their source repo and install via `install.sh`, so a lesson worth
keeping goes to `RETROSPECTIVE.md` or docs, never a new skill dropped in `~/.hermes/skills` or `~/.claude/skills`.

See `reference.md` for target resolution, native-project mode, risk examples, and compatibility behavior for
projects that still contain legacy phase plans.
