---
name: saga-roadmap
description: "Maintain the flat .planning/ROADMAP.md milestone list and REQUIREMENTS.md — show / add / done / edit milestones, add-req / edit-req / done-req requirements. No phase directories."
category: "saga"
disable-model-invocation: true
argument-hint: "[show | add <milestone/phase> | done <id> | edit <id> | add-req <text> | edit-req <REQ-ID> | done-req <REQ-ID>]"
---

# /saga-roadmap

Maintain `.planning/ROADMAP.md` — the living, flat milestone list — and `.planning/REQUIREMENTS.md` — the
enumerable REQ-ID list that saga-verify traces. CRUD only; no phase directories, no PLAN/SUMMARY files. These
are the most cross-referenced spine files, so preserve their existing line formats exactly.

## Process

### show

1. Print the current `## Milestones` list (status emoji + name + date + scope). No edit.

### add

1. Insert a new milestone or phase line at the top of `## Milestones` (newest first), matching the existing
   format: `- 🚧 **<vX.Y Name>** — planning <date> (Phases N–M; <K> REQs; <one-line scope>; <SAFE-NN invariant if any>)`.
   For a phase under the active milestone, match the project's phase-line convention
   (`**Phase NNN — Title** (REQ-01..03, SAFE-NN): <scope>`).

### done

1. Flip the milestone's leading status `- 🚧 → - ✅`, change `planning` to `shipped <date>`, and record the
   `X/Y REQs` count. If the project archives shipped milestones, add the trailing
   `— \`milestones/vX.Y-ROADMAP.md\`` link; do not move history.

### edit

1. Modify the named line in place, preserving emoji-status + REQ-ID tags + any archived-milestone link.

### add-req

1. If `.planning/REQUIREMENTS.md` does not exist, create it with a single `## Requirements` section — this is
   the ONLY spine file saga may create in a repo that lacks it, and only on an explicit `add-req`.
2. Assign the next REQ-ID (`max existing numeric suffix + 1`, zero-padded to the project's existing width;
   `REQ-001` in a fresh file). Match the project's existing requirement line format if one exists; otherwise:
   `- [ ] **REQ-NNN** — <one-line testable statement> (milestone: <vX.Y or —>)`.
3. A requirement must be phrased so saga-verify can hunt evidence for it: state an observable outcome, not an
   activity ("install links 8 skills", not "improve install").

### edit-req

1. Modify the named REQ line in place. Never renumber existing REQ-IDs — TRACEABILITY.md and decisions link to
   them.

### done-req

1. Flip `- [ ]` to `- [x]` ONLY when the operator states the evidence (test, SHA, capture, TRACEABILITY row) —
   record it as a trailing `(evidence: <pointer>)`. A done-req without evidence is refused: an unevidenced
   `[x]` is exactly what saga-verify exists to catch; do not create one.

## Completion criterion

DONE when ROADMAP.md still parses as a flat `## Milestones` list (newest first), every line keeps its status
emoji and (where the project uses them) REQ-ID tags, REQUIREMENTS.md (if touched) keeps stable REQ-IDs with no
renumbering and no evidence-free `[x]`, the requested mutation is applied with a date, and **no
`.planning/phases/NNN/` directory was created**. Echo the changed line(s) back to the operator.

See `reference.md` for the line formats.
