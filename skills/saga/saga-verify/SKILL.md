---
name: saga-verify
description: "Check every requirement in REQUIREMENTS.md against named evidence → .planning/TRACEABILITY.md; flags asserted-but-unproven gaps."
category: "saga"
disable-model-invocation: true
argument-hint: "[milestone — defaults to the current one in REQUIREMENTS.md]"
---

# /saga-verify

Check every requirement against **named evidence** and write `.planning/TRACEABILITY.md`. It answers "which
requirements are actually _proven_, not just _asserted_?" — the safety net before a milestone close,
especially on production projects.

## Process

1. **Enumerate.** Read `.planning/REQUIREMENTS.md`. List every `REQ-ID` (e.g. `ACCESS-01`, `INSPECT-02`,
   `SAFE-21`) with its checkbox state and one-line description. Include cross-cutting `SAFE-NN` invariants.
   **Marker convention (3-state, not 2):** `[ ]` = not done; **both `[x]` AND `[/]` = "claimed done"** and are
   treated identically. `[/]` is a supported compatibility marker — do NOT read it as OPEN, or shipped
   requirements may be misclassified.
2. **Find evidence** for each REQ-ID. Search the repo and `.planning/` for concrete proof: a test name/path, a
   commit SHA, a live-output capture, a `*-VERIFICATION.md`, or a `decisions/*.md` record. Grep the REQ-ID itself
   across the tree. Evidence must be a concrete artifact, not a restatement of the requirement.
3. **Classify** each REQ-ID:
   - **PROVEN** — a "claimed done" marker (`[x]` or `[/]`) AND a concrete evidence artifact located.
   - **ASSERTED** — a "claimed done" marker (`[x]` or `[/]`) but no locatable evidence. _This is the dangerous class — surface it loudly._
   - **OPEN** — checkbox `[ ]`, not yet done.
   - **WAIVED** — an open/partial gap with a `decisions/*.md` waiver accepting it (link the waiver).
4. **Write** `.planning/TRACEABILITY.md` using the executable Saga linter schema below:

   ```markdown
   | Requirement | Description | Status | Evidence |
   |-------------|-------------|--------|----------|
   | REQ-001 | Short behavior description | **PROVEN** | concrete artifact |
   | REQ-002 | Short behavior description | **OPEN** | — |
   ```

   Status must be the third data column and one of `PROVEN`, `ASSERTED`, `OPEN`, or `WAIVED` (bold markup is accepted). Include every requirement exactly once.
5. **Report** the gaps: list every ASSERTED and OPEN REQ-ID explicitly. Do not bury them under a summary count.
6. If all requirements are PROVEN or WAIVED for the active milestone, flag `/saga-spec merge` as the next
   step to bake verified behavior into the living spec library.

## Completion criterion

DONE when `.planning/TRACEABILITY.md` contains a row for **every** REQ-ID present in REQUIREMENTS.md, each row
classified PROVEN/ASSERTED/OPEN/WAIVED with either a concrete evidence pointer or an explicit gap note, and the
ASSERTED + OPEN sets are restated to the operator as the action list. A checkbox marked `[x]` with no locatable
evidence MUST be reported as ASSERTED, never silently passed.

See `reference.md` for the TRACEABILITY.md table and where to look for evidence.
