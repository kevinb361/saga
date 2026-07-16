# /saga-roadmap — reference

## File shape
```markdown
# Roadmap: <project>

## Milestones

- 🚧 **v1.57 <Name>** — planning <date> (Phases 258–260; 10 REQs; <scope>; SAFE-21 <invariant>)
- ✅ **v1.56 <Name>** — shipped <date> (Phases 255–257; 13/13 REQs; <scope>) — `milestones/v1.56-ROADMAP.md`
- 📌 **Pipeline: <future work>** — pending follow-up: <why>
```

## Status emoji (keep the project's existing vocabulary)
- 🚧 in planning / active
- ✅ shipped (or shipped-with-deferral / closed)
- 📌 pipeline / pending follow-up

## Phase line (under the active milestone, if the project lists phases)
```
**Phase 259 — Read-Only Netwatch + Route-Ownership Inspection** (INSPECT-01..03, SAFE-21): <one-line scope>. Depends on 258.
```

## Rules
- Newest milestone at the top. Never reorder/rewrite shipped history — only flip status and append the archive link.
- REQ-ID tags (`ACCESS-01..03`, `SAFE-21`) and SAFE cross-cutting invariants are load-bearing for `/saga-verify`;
  carry them through edits unchanged.
- A cross-cutting `SAFE-NN` invariant is a milestone-wide property, not a phase — note it inline, don't make a phase for it.

## Requirement line formats (REQUIREMENTS.md)

Fresh-file default:

```
- [ ] **REQ-001** — install.sh links all 8 skills into ~/.claude/skills (milestone: v0.2)
- [x] **REQ-002** — saga skills reachable from Hermes via skills.external_dirs (milestone: v0.2) (evidence: ~/.hermes/skills/.usage.json saga-next use_count)
```

Rules: IDs are append-only and never renumbered; statements are observable
outcomes saga-verify can hunt evidence for; `[x]` always carries a trailing
`(evidence: ...)` pointer. Legacy files may use different widths/formats —
match whatever the file already does.
