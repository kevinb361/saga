# /saga-state — reference

## STATE.md template (create only if absent)

```markdown
---
saga_state_version: 1.0
milestone: <slug>
milestone_name: <short name>
status: <active | paused | blocked | complete | closed | idle>
stopped_at: <where work paused>
last_updated: "<ISO 8601, e.g. 2026-06-24T00:00:00.000Z>"
last_activity: <date -- one-line what just happened>
---

# Session State

## Current Position
Phase/Milestone: <id>
Status: <status>
Last activity: <date -- one line>

## Active Work
- <what is in-flight right now>

## Deferred
- <ugly-but-works item to revisit; date it>
```

## Frontmatter keys that MUST be preserved
The version marker, `milestone`, `milestone_name`, `status`, `last_updated`, and `last_activity` are read by
project state readers and RAG indexers. A `progress:` block may also exist; carry it forward verbatim unless the
operator gives new numbers. Adding keys is fine; dropping these is not.

## Notes
- `## Deferred` is the home for SOUL's "something ugly works — make nicer later" items. Always date them.
- Keep STATE.md short (a screenful). It is a pointer, not a log — narrative history belongs in RETROSPECTIVE.md.
