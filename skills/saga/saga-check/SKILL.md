---
name: saga-check
description: "Check Saga structural health and requirement-to-evidence traceability as two clearly separated lanes; use for validation or proof questions, never for the independent milestone quality verdict."
category: "saga"
disable-model-invocation: false
argument-hint: "[project or milestone, optionally structure only or evidence only]"
---

# saga-check

Answer two different questions without pretending they have the same cost or authority:

1. **Structure:** can deterministic tooling parse and reconcile the Saga spine?
2. **Evidence:** are claimed requirements backed by concrete, locatable proof?

Neither answer is the independent milestone quality verdict. That remains `saga-audit`.

## Choose and disclose the lane

Interpret natural-language scope rather than requiring flags:

- “check the structure”, “lint this spine”, or “is Saga healthy?” with an explicit structural qualifier runs **Structure only**.
- “is this requirement proven?”, “check the milestone”, “verify the evidence”, or a bare `saga-check` runs **Structure then Evidence**.
- Evidence never skips the structural prerequisite. If deterministic structure is red, stop without rewriting traceability because semantic classification against malformed records is unreliable.

Before running, state the distinction:

- **Structure lane:** deterministic local executable, inspect-only, no model judgment, no target-file writes; cost is one bounded parser run.
- **Evidence lane:** model-assisted repository cross-reference, may run bounded existing checks, and rewrites `.planning/TRACEABILITY.md`; cost scales with requirements and evidence searched. It does not fetch, deploy, restart, or mutate live systems without separate explicit approval.

## Structure lane — deterministic

1. Resolve `scripts/run-lint.sh` beside this skill. If the loaded skill directory is unavailable, inspect the `saga-check/scripts/run-lint.sh` candidates under `${HERMES_HOME:-$HOME/.hermes}/skills`, `${CLAUDE_HOME:-$HOME/.claude}/skills`, and `${CODEX_HOME:-$HOME/.codex}/skills`. If matches resolve to different Saga checkouts, stop on ambiguity.
2. Forward the supplied project path unchanged, or `.` when omitted. Human output is the default; JSON remains available as an underlying diagnostic detail, not required user vocabulary.
3. Preserve output and exit semantics exactly:
   - `0` — structurally clean;
   - `1` — deterministic structural findings;
   - `2` — invocation, parser, or handled read failure.
4. Report under `## Structural check`: target, exit, stable finding codes, and file/line locations. Exit `1` means the tool worked and found drift, not that it crashed. Never silently fix records in this lane.

## Evidence lane — requirement traceability

1. Read `REQUIREMENTS.md` and enumerate every requirement exactly once. Treat `[x]` and `[/]` as claimed done; `[ ]` is not done. Include milestone tags, dependencies, and cross-cutting safety invariants.
2. Search source, tests, git history, planning records, published artifacts, and existing live captures for concrete proof tied to each claim. A requirement restatement, model confidence, or checked box is not evidence. Re-run safe bounded checks when practical; distinguish located evidence from freshly reproduced evidence.
3. Classify each requirement:
   - **PROVEN** — claimed done and concrete evidence is located;
   - **ASSERTED** — claimed done but no concrete evidence is locatable;
   - **OPEN** — `[ ]`, regardless of promising implementation;
   - **WAIVED** — an explicit operator-signed decision accepts the named gap.
4. Rewrite `.planning/TRACEABILITY.md` in the existing table/schema with every requirement exactly once, status in the third data column, and a concrete pointer or explicit gap note. Preserve useful provenance and boundaries; do not manufacture test runs or silently mark REQUIREMENTS done.
5. Report under `## Evidence check`: PROVEN/ASSERTED/OPEN/WAIVED counts, every ASSERTED and OPEN ID, checks freshly run, evidence only located, and evidence not available.

## Authority boundary

`saga-check` reports structural truth and claim-to-proof status. It does **not** judge architecture, operational readiness, security posture, maintainability, or whether accepted evidence is sufficient for real-world release risk. It never writes `AUDIT.md`, never issues PASS/CONDITIONAL/FAIL, and never flips ROADMAP or closes a milestone.

During close-out, the context that executed any milestone slice must not certify that work. `saga-run` arranges an independent frontier context to run `saga-check` followed by the separately visible `saga-audit`; capability alone does not make the executor independent.

## Completion criterion

DONE when the requested lanes are named separately; the structural exit is preserved; evidence mode (when requested) gives every requirement exactly one valid classification and writes complete traceability; gaps are explicit; no live mutation occurred by implication; and no audit verdict or milestone flip was issued.

See `reference.md` for the evidence schema, classification boundaries, and result template.
