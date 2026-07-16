# /saga-decision — reference

## The 7-section template

```markdown
# <Title — the decision, stated as a fact>

## Symptom
<What forced the decision? The situation, behavior, or gap. Be concrete and specific —
name the fixture/test/observation. One or two paragraphs. End with a `References:` line
pointing at the evidence that established the situation.>

## Blast Radius
- Time window / scope: <what is affected, how long, how often>
- Recovery / reversal mechanism: <how the system returns to normal, if applicable>
- Frequency: <when this occurs — restart only? steady state? a one-time choice?>
- Not affected: <explicitly bound it — what this does NOT touch>

## Evidence Links
- <concrete path to a file, test, or evidence artifact>
- <commit SHA, `pytest` target, or live-output capture — NEVER a placeholder>

## Default Disposition
<What is being accepted/chosen and why. State the option taken. If a risk is accepted,
say it is expected and does not constitute a regression when next observed.>

## Override Path
<The escape hatch: if the operator instead chooses the other fork, exactly what they must
do (strike the sign-off, open a prework item, etc.) and what becomes of this record.
MANDATORY for production-touching decisions, with a rollback note.>

## Sign-Off
Accepted: <YES/NO — one-line restatement of what's accepted>.   Date: <YYYY-MM-DD>   Operator: <name>

> Authorized via <how — session/command/approval> on <date>. Default Disposition accepted;
> Override Path <invoked/NOT invoked>. Recorded by Claude Code on operator instruction.
```

## Numbering rule

```
next = (max numeric prefix found in .planning/decisions/*.md) + 1, zero-padded to 4 digits
```
Treat legacy files named `phase-NNN-slug.md` as their `NNN` value when computing the max, so new
`NNNN-slug.md` records never collide with history. Do not rename existing files.

## The gate — worked examples

**PASSES (record it):**
- *Accept a ~750ms post-restart steering window rather than block the milestone for a daemon fix.* Hard to
  reverse (ships to prod), surprising (a reader wouldn't know the window is intentional), real trade-off
  (fix-now vs accept-and-proceed).
- *Flip route ownership from Netwatch to the route-management surface.* Hard to reverse (live routing),
  surprising, real fork (keep interim owner vs cut over).
- *Choose `NNNN-slug.md` over `phase-NNN-slug.md` for decision filenames.* Hard-ish to reverse (sets a
  convention), surprising (why abandon the phase prefix?), real trade-off (continuity vs engine-free).

**FAILS the gate (do NOT record — propose the lighter note):**
- *Bumped a log level from INFO to DEBUG while chasing a bug.* Trivially reversible → inline comment, not a record.
- *Named a new test file `test_foo.py`.* Not surprising, no real alternative → nothing.
- *Picked the only library that does X.* No real trade-off → at most a CONTEXT.md note.

When the gate fails, say e.g.: *"Skipping a decision record — this is cheaply reversible (criterion 1 fails).
Suggest an inline comment at <file> instead."*

## Leading words to reach for
failover, RTT backend, CAKE ceiling, route ownership, Netwatch, canary, rollback, blast radius, steering
cycle, dry-run, least-privilege, quorum, measurement authority.
