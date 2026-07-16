# /saga-audit Reference

## AUDIT.md template (idempotent: replace existing milestone section, never overwrite other milestones)

```markdown
# Audit Log: <project>

---

## Audit: <milestone> — <date>

Auditor: <model/agent used, e.g. Claude Sonnet via Hermes>
Scope: <milestone description from STATE.md>
Files reviewed: <N> files changed, <N> insertions(+), <N> deletions(-) (from git diff --shortstat)

### Correctness
- [critical] <finding>: <file>:<line> — <specific issue and recommended fix>
- [warning] <finding>: <file>:<line> — <issue>

### Safety
- [critical] <finding>: <file>:<line> — <unhandled edge case / blast radius>
- [warning] <finding>: <file>:<line> — <issue>

### Test Coverage
- [critical] <finding>: <missing test for X scenario>
- [warning] <finding>: <existing test Y only covers happy path>

### Architecture Fit
- [warning] <finding>: <new abstraction conflicts with existing Z pattern>
- [info] <finding>: <minor style deviation, not blocking>

### Operability
- [warning] <finding>: <no log line at X for debugging Y>
- [info] <finding>: <rollback steps documented in decision record>

### ASSERTED Items from TRACEABILITY.md
- INSPECT-03: [confirmed gap / evidence found during audit]

### Verdict
[PASS / PASS-CONDITIONAL / FAIL]
- Critical findings: <count> (must fix before milestone close)
- Warnings: <count> (fix before shipping)
- Info: <count> (track for later)
```

## Idempotent re-run

For the same milestone, replace the existing `## Audit: <milestone>` section entirely (from that heading to the next `## Audit:` or end-of-file). This way a re-run produces one clean audit per milestone, not duplicate sections. Audit entries for *other* milestones are never deleted or modified.

## Five pillars (what each checks)

**Correctness:** Does the code do what the requirement says? Not just "tests pass" but "this solves the stated problem." Look for: misimplemented logic, off-by-one errors, wrong defaults, incomplete feature parity with the spec.

**Safety:** What breaks if this runs in production? Look for: missing error handling, race conditions, resource leaks, unbounded memory/growth, privilege escalation paths, data corruption scenarios. The question is "what goes wrong when the unusual happens?"

**Test Coverage:** Are tests actually testing the right things? Look for: only happy-path coverage, missing negative cases, tests that assert implementation details instead of behavior, integration gaps where unit tests pass but the composed system doesn't.

**Architecture Fit:** Does this change work with the existing structure? Look for: circular dependencies introduced, abstractions that fight each other, duplicated logic across files, new coupling between previously independent modules.

**Operability:** Can future-you debug this? Look for: missing log lines at decision points, no metrics on failure rates, unclear rollback path, configuration buried in code instead of externalized, error messages that don't tell you what went wrong.

## Severity levels

- **critical:** Blocks milestone closure. Must fix before the milestone is considered done. Examples: data loss path, security hole, incorrect core behavior.
- **warning:** Should fix before shipping. Won't immediately break things but creates technical debt or hidden risk. Examples: missing error handler on a rare path, test gap on an edge case.
- **info:** Note for future improvement. Not blocking, not urgent. Examples: style inconsistency, could add a convenience helper, minor documentation gap.

## Relationship to /saga-verify

`saga-verify` is mechanical: does requirement X have evidence Y? It produces TRACEABILITY.md with PROVEN/ASSERTED/OPEN/WAIVED classifications.

`saga-audit` is judgment: is the implementation actually good? It reads TRACEABILITY.md as input (especially ASSERTED items) but goes further — reviewing code quality, architecture, and operational readiness that traceability can't capture.

Run order: `/saga-verify` first (mechanical check), then `/saga-audit` (quality judgment). The audit should always reference the verify results.

## When to run

- After `/saga-loop` drains a milestone (all slices completed or escalated)
- Before marking a milestone as `shipped` in STATE.md
- When merging work from multiple agents (deep execution + codex escalations)
- Periodically for long-running projects (even without a fresh milestone)

## Arguments

- `--milestone X.Y`: Audit a specific milestone instead of the current one in STATE.md. Useful for retroactive audits.
- `--focus <area>`: Narrow the audit to one pillar (e.g., `--focus safety`) for targeted reviews. By default all five pillars are assessed.