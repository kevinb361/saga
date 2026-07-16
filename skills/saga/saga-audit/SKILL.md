---
name: saga-audit
description: "Post-execution quality audit of a completed milestone. Frontier-model review: architecture, code quality, unintended side effects, test gaps. Runs after /saga-loop drains or /saga-verify flags ASSERTED gaps."
category: "saga"
disable-model-invocation: true
argument-hint: "[--milestone X.Y | --focus <area>]"
---

# /saga-audit

Post-execution quality audit for a completed milestone. Designed to run on a frontier model after a local model has executed slices via `/saga-loop`. This is the judgment layer — not mechanical traceability, but actual code quality, architecture soundness, and risk assessment.

## Process

1. **Read context.** Load STATE.md, ROADMAP.md, REQUIREMENTS.md, TRACEABILITY.md, and RETROSPECTIVE.md from `.planning/`. Identify the active milestone and its scope. Also check `.planning/config.json` for a `close_out_auditor` key: if absent or empty, WARN in the audit report — without it, a non-frontier close-out on this project stops dead at the frontier-verify gate (paste-handoff only, no autonomous close). Recommend copying the validated value from saga's own config. **Record the auditing model name** (e.g., from the current session's model/provider, or from `close_out_auditor` if running as a delegated auditor) — it goes into the `Auditor:` line in the audit output.

2. **Identify changed artifacts.** Find all files modified during this milestone: git diff against the milestone start commit, new files, deleted files. Parse the diff stats to get concrete counts: `git diff <milestone-start-commit> --stat` for per-file line changes, and `git diff <milestone-start-commit> --shortstat` for totals (e.g., "12 files changed, 340 insertions(+), 15 deletions(-)"). Record these numbers in the `Files reviewed:` line of the audit output. If git history is unclear, use REQUIREMENTS.md to infer touched areas. **If more than 50 changed files, STOP and report:** "Milestone too large for single audit pass. Use `--focus <pillar>` to chunk by pillar, or audit individual files. Recommend splitting into multiple audit passes."

3. **Audit pillars.** For each changed area, assess:
   - **Correctness:** Does the implementation match the requirement intent? Not just "does it pass tests" but "does it solve the right problem?"
   - **Safety:** Are there unintended side effects? Unhandled edge cases? Missing error paths? Production blast radius?
   - **Test coverage:** Are the tests sufficient or just covering the happy path? Missing negative cases? Integration gaps?
   - **Architecture fit:** Does this change strain existing abstractions? Create circular dependencies? Violate established patterns?
   - **Operability:** Can this be debugged later? Are logs/metrics adequate? Is rollback clear?

4. **Cross-reference with verify results.** Read TRACEABILITY.md. Any ASSERTED items are automatically flagged — they claimed done but had no evidence. Check whether the audit finds evidence or confirms the gap.

5. **Write findings.** Write audit results to `.planning/AUDIT.md` (create if absent). **Idempotent re-run:** if a `## Audit: <milestone>` section already exists, replace its entire block (from that heading to the next `## Audit:` or end-of-file). If no section for this milestone exists, append a new one. Never delete prior audit entries for *other* milestones. Include the auditing model name in the `Auditor:` line. See `reference.md` for the AUDIT.md template.

6. **Report.** Summarize: critical findings that block milestone closure, warnings to fix before shipping, info items for later. Explicitly state whether the milestone passes audit or needs follow-up work.

## Completion criterion

DONE when `.planning/AUDIT.md` exists with a dated audit entry covering all five pillars, every ASSERTED item from TRACEABILITY.md is addressed, and the operator has a clear pass/fail recommendation with specific follow-up items. The audit must name concrete files and lines, not vague concerns.

See `reference.md` for the AUDIT.md template, pillar definitions, and severity levels.