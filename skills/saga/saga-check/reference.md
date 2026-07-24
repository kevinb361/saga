# saga-check reference

## Evidence classification

| Requirement marker | Concrete evidence | Explicit signed waiver | Status |
| --- | --- | --- | --- |
| `[x]` or `[/]` | located | irrelevant | PROVEN |
| `[x]` or `[/]` | absent | absent | ASSERTED |
| `[ ]` | any | absent | OPEN |
| `[ ]` or partial gap | absent or incomplete | located | WAIVED |

Promising code does not turn an OPEN marker into PROVEN. A model may report marker drift, but only the normal planning/execution workflow updates REQUIREMENTS. A waiver must name the accepted gap, rationale, scope, owner/sign-off, and recovery or revisit condition; a casual deferral note is not a waiver.

Concrete evidence includes a named test with a reproducible result, commit SHA tied to the claim, bounded live capture, published artifact inspection, deterministic static check, or signed decision proving a negative invariant. “Implemented”, a copied requirement sentence, and model confidence are not evidence.

## Traceability schema

```markdown
| Requirement | Description | Status | Evidence |
| --- | --- | --- | --- |
| REQ-001 | Observable behavior | **PROVEN** | `tests/test_behavior.py::test_case` (fresh 3/3) |
| REQ-002 | Claimed behavior | **ASSERTED** | checkbox done; no concrete artifact located |
| REQ-003 | Planned behavior | **OPEN** | not yet claimed done |
| SAFE-01 | Accepted bounded gap | **WAIVED** | `decisions/0004-accept-gap.md` |
```

Status is the third data column and must be one of PROVEN, ASSERTED, OPEN, or WAIVED. Include every requirement exactly once. Preserve existing high-value evidence details rather than replacing them with a weaker summary.

## Result template

```text
Structural check:
  Target: <path>
  Exit: 0 clean | 1 findings | 2 unable to run
  Findings: <stable code + path:line, or none>
  Cost/write boundary: deterministic, inspect-only

Evidence check: <run | skipped because structure red | not requested>
  PROVEN: N
  ASSERTED: N — <IDs>
  OPEN: N — <IDs>
  WAIVED: N — <IDs>
  Freshly reproduced: <checks>
  Located only: <artifacts not rerun>
  Unavailable: <gaps>
  Cost/write boundary: model-assisted; TRACEABILITY.md <rewritten | untouched>

Audit verdict: NOT RUN — owned by independent saga-audit
```

## Stop conditions

Stop without evidence rewrite when structural parsing fails, requirement IDs are duplicated/ambiguous, the target project is unclear, evidence requires unapproved live mutation, or another process changes REQUIREMENTS during the sweep. Report the exact blocker and leave the prior traceability artifact intact rather than publishing a partial table as current truth.
