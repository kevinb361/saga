# /saga-spec — reference

## Directory layout

```
.planning/specs/
├── auth/spec.md
├── routing/spec.md
├── health/spec.md
└── <domain>/spec.md
```

One file per domain. Organize by capability or bounded context — whatever groups related
behavior. Common patterns:

- **By feature area:** `auth/`, `notifications/`, `search/`
- **By component:** `api/`, `frontend/`, `workers/`
- **By bounded context:** `ordering/`, `fulfillment/`, `inventory/`

Do not create a domain file for every feature. Group related behavior; a domain should
have at least 2-3 requirements before it earns its own file.

## Lite spec format (default)

```markdown
# <domain> Specification

## Purpose
One line: what this domain does in operator terms.

## Scope
- In scope: <what this domain covers>
- Not in scope: <what is explicitly excluded>

## Requirements

### REQ: <short-name>
The system SHALL <observable behavior>.

#### Scenario: <scenario-name>
- GIVEN <precondition>
- WHEN <trigger>
- THEN <observable outcome>
- AND <secondary outcome, if applicable>

### REQ: <short-name>
The system SHOULD <recommended behavior with exceptions>.

#### Scenario: <scenario-name>
- GIVEN <precondition>
- WHEN <trigger>
- THEN <observable outcome>
```

**Rules:**
- **SHALL/MUST** — absolute requirement. Use for user-facing behavior and external contracts.
- **SHOULD** — recommended, exceptions exist. Use for defaults that can be overridden.
- **MAY** — optional. Use for capabilities that exist but aren't guaranteed.
- Scenarios are testable: you could write an automated test for each one.
- No internal class/function names, no library choices, no implementation steps.
- If the implementation changes but the observable behavior doesn't, the spec stays the same.

## Delta format

Deltas go at the bottom of the affected spec file, before merge:

```markdown
## Delta: <change-id> — YYYY-MM-DD

Source: `/saga-next` slice or operator directive. Status: pending merge.

### ADDED to <domain>

### REQ: <new-requirement-name>
The system SHALL <new behavior>.

#### Scenario: <scenario-name>
- GIVEN <precondition>
- WHEN <trigger>
- THEN <observable outcome>

### MODIFIED in <domain>

OLD:
### REQ: <old-name>
The system SHALL <old behavior>.

NEW:
### REQ: <new-name>
The system SHALL <updated behavior>.

#### Scenario: <scenario-name>
- GIVEN <precondition>
- WHEN <trigger>
- THEN <observable outcome>

### REMOVED from <domain>

~~### REQ: <deprecated-name>~~
_Rationale: <one-line reason for removal>_
```

**Rules:**
- Each delta block has a unique change-id (e.g., `slice-2026-07-03-add-websocket`).
- ADDED requirements are written normally (no strikethrough).
- MODIFIED: strikethrough the old requirement, write the new one below it.
- REMOVED: strikethrough the requirement, add a one-line rationale.
- Deltas stay visible until `merge` folds them into the main Requirements section.

## Merge rules

When `merge` is invoked for a milestone:

1. **ADDED** — fold into the main Requirements section at a logical position (group related
   requirements together, don't just append at the bottom).
2. **MODIFIED** — replace the old requirement in place. Remove the strikethrough block and
   the "MODIFIED" header.
3. **REMOVED** — remove the requirement entirely from the main section. Do NOT preserve
   strikethrough in the merged spec — the RETROSPECTIVE.md (via `/saga-retro`) is where
   you record why something was removed, if it's worth remembering.
4. Remove the `## Delta: <change-id>` header and the "Source/Status" metadata lines.
5. If a spec file becomes empty after a merge (all requirements removed), keep the file
   with just the Purpose and Scope headers — do not delete it.

## Worked example

**Before — `routing/spec.md` (current state):**

```markdown
# Routing Specification

## Purpose
WAN route management and failover for dual-link setups.

## Requirements

### REQ: primary-failover
The system SHALL failover all user routes to the backup link when the primary link
loses connectivity for more than 10 seconds.

#### Scenario: primary-link-down
- GIVEN both links are active and healthy
- WHEN the primary link fails BFD detection
- THEN all user routes are moved to the backup link
- AND the failover event is logged with a timestamp
```

**After `/saga-next` slice adds route pinning — delta appended (solo mode: just update inline):**

_Skipping the delta staging step — updating the spec directly:_

```markdown
# Routing Specification

## Purpose
WAN route management and failover for dual-link setups.

## Requirements

### REQ: primary-failover
The system SHALL failover all user routes to the backup link when the primary link
loses connectivity for more than 10 seconds.

#### Scenario: primary-link-down
- GIVEN both links are active and healthy
- WHEN the primary link fails BFD detection
- THEN all user routes are moved to the backup link
- AND the failover event is logged with a timestamp

### REQ: route-pinning
The system SHALL allow operators to pin specific routes to a link, preventing automatic
failover for those routes.

#### Scenario: pinned-route-during-failover
- GIVEN a route is pinned to the primary link
- WHEN the primary link fails BFD detection
- THEN the pinned route remains on the primary link
- AND non-pinned routes failover to backup normally
```

## Integration with other saga skills

- **saga-next (step 7)** — after a slice is verified, if it changed observable behavior,
  invoke `/saga-spec delta` to record the change. If verification was for an entire
  milestone, invoke `/saga-spec merge`.
- **saga-verify** — after TRACEABILITY.md shows all requirements PROVEN for a milestone,
  the next step is `/saga-spec merge` to bake verified behavior into the living spec.
- **saga-decision** — a decision record that changes system behavior should also produce
  a spec delta. The decision is the "why"; the spec is the "what."
- **saga-retro** — if a requirement is removed, the retro should capture the lesson. The
  spec removes the requirement; the retro explains why it was removed.
- **saga-context** — terms that appear in specs but need definition (domain jargon,
  operator concepts) should be defined in CONTEXT.md. Specs link to CONTEXT.md, not
  re-explain.

## What NOT to put in a spec

- Internal implementation details (class names, function signatures, framework choices)
- Step-by-step implementation instructions (those belong in a plan or tasks.md)
- Temporary workarounds or known bugs (those belong in STATE.md Deferred)
- Requirements that haven't been scoped or verified yet (those belong in REQUIREMENTS.md)
- Architecture diagrams or performance targets without observable criteria

## Lite vs full spec

**Lite (default)** — short requirements, 1-2 scenarios each, clear scope. Use for:
- Single-component changes
- Bug fixes
- Small features with obvious acceptance criteria

**Full** — comprehensive scenarios, edge cases, cross-domain interactions. Use for:
- Cross-component or cross-repo changes
- API/contract changes
- Security or privacy-sensitive behavior
- Changes where ambiguity is likely to cause expensive rework

Most changes stay lite. Err on the light side — a spec that exists and is maintained beats
a spec that was thorough once and is now stale.

## Leading words to reach for

observable behavior, failover, blast radius, canary, rollback, steady state, idempotent,
quorum, measurement authority, least-privilege, given-when-then, scope, non-goal.
