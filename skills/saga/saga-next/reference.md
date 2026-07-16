# /saga-next Reference

## Target resolution

When the operator supplies a target:

1. Exact requirement ID wins: `REQ-104`, `SAFE-21`.
2. Exact roadmap, state, or native-project artifact text wins next.
3. Legacy phase-plan references such as `73-06` or `.planning/phases/.../73-06-PLAN.md` are accepted as source material.
4. Free text maps to the closest open requirement, active roadmap item, or native-project artifact.

When there is no target:

1. Use a valid explicit next step from `STATE.md`.
2. Prefer open requirements with negative evidence in `TRACEABILITY.md`.
3. Prefer blockers over downstream work.
4. In native-project mode, follow the project’s declared source-to-derived workflow.
5. If the real next step is risky, report it; do not substitute easier work.

## Native-project mode

If `.planning/` is absent, read `CLAUDE.md`, `AGENTS.md`, and `README.md` and derive one bounded slice from the project’s own contract.

Rules:

1. Do not create `.planning/` automatically.
2. Do not invent requirements or traceability for a scratchpad, corpus, or one-off utility.
3. Respect generated-file rules, rate limits, test conventions, and refresh commands in local guidance.
4. Offer a minimal bootstrap only when durable tracking would reduce future steering; `--bootstrap` should normally begin with `STATE.md` only.
5. Still classify risk and stop before unapproved external mutation.

## Risk examples

`inspect-only`:

- read files
- run tests
- query logs or read-only APIs
- compare manifests without fetching

`repo-only`:

- edit source, documentation, and tests
- update files of record
- add regression coverage

`live-mutation`:

- rebuild or restart a service
- deploy or sync to a live host
- reindex a live corpus
- fetch external data
- change power, network, or smart-home state

`destructive`:

- delete data, indexes, backups, or unmerged work
- perform an irreversible migration
- roll back by discarding current state
- run broad cleanup without a bounded target

## Legacy phase-plan compatibility

Old plans under `.planning/phases/` may be read as source material. Saga must not create new phase directories or require an external workflow engine.

When a target points at an old plan:

1. Extract the real requirement and done condition.
2. Keep only dependencies that encode a genuine safety or ordering constraint.
3. Execute one bounded slice.
4. Record results in current files of record, not new summary exhaust.

## Output template

```text
Next slice: <requirement / roadmap item / native artifact>
Why this is next: <evidence from state, traceability, roadmap, or local guidance>
Risk: <inspect-only | repo-only | live-mutation | destructive>
Touches: <files, hosts, services, or external artifacts>
Done when: <mechanically checkable condition>
Action: <execute now | stop for approval | blocked because ...>
```

## Stop conditions

Stop before action when:

- live or destructive mutation was not explicitly approved
- rollback is missing for production-like mutation
- evidence is stale or contradictory
- unrelated dirty changes would be overwritten
- required credentials or access are unavailable
- a generated artifact’s regeneration path is unknown

## Example: blocked requirement

Given:

- `TRACEABILITY.md` marks `REQ-104` open with failing freshness evidence.
- Several measurement requirements depend on fresh inputs.
- The fix requires a live service rebuild and index refresh.

Expected result:

```text
Next slice: REQ-104 / restore index freshness
Why this is next: stale inputs block trustworthy downstream measurements
Risk: live-mutation
Touches: indexing service, collection, freshness evidence
Done when: rollback captured, rebuild completed, two clean checks recorded, traceability updated
Action: stop for explicit approval before rebuild
```

Do not jump to downstream repo-only work merely because it is safer; the blocker remains next.

## Example: native content project

Given:

- no `.planning/` directory
- local guidance says raw inputs and generated synthesis must remain distinct
- refresh requires network access

`/saga-next --dry-run` should choose an inspect-only freshness check first and stop before network refresh unless explicitly approved. It should not invent requirements, tests, or a planning spine.

## Plan block

Use this compact structure under `STATE.md` `## Active Work` or in the card comment when scope excludes `STATE.md`:

```markdown
### <slice id/title>
- Goal: <one observable outcome>
- Touches: <expected files/systems>
- Gate: `<exact command or readback>`
- Risk: <class>; approval/rollback: <requirement or n/a>
- Status: planned
```

Edit `STATE.md` in place. Preserve all unrelated content and frontmatter.

## Escalation block

After the second gate failure:

```markdown
### ESCALATE: <slice>
- Goal: <done condition>
- Plan attempted: <steps>
- Touches: <files/systems>
- Gate: `<command>`
- Attempt 1: <exact failure>
- Attempt 2: <exact failure>
- Need: <capability or decision required>
- Do not: <scope boundaries and risky actions>
```

Do not mark the requirement complete. A Kanban-invoked slice should also report `blocked-escalate` so dispatch does not blindly retry it.

## Frontier-shaped work

Route up front when:

- the change crosses many files or layers
- working context cannot be bounded to a manageable slice
- architecture or long-horizon sequencing is the hard part

Write a `frontier:` handoff rather than spending retries on a predictably underscoped attempt.

## Card and deployment safety

- Express scope restrictions as gate conditions, not prose.
- Use isolated worktrees for repo-touching dispatched work.
- Diff-audit production-adjacent output before integration.
- Deploy only committed content from a clean worktree or explicit file list.
- Treat deployment approval as permission for the assigned worker to act immediately.
- Do not rely on an initial blocked state as a durable approval gate; encode the approval requirement in the task contract and dispatcher policy.
- Guard and invariant tests are read-only within the slice they police. A failure is gate output, not permission to weaken the guard.
- Report-only cards must end with an explicit terminal completion instruction and include findings as the deliverable.

## Loop drivers

Looping stays outside `/saga-next`:

- a Kanban card invokes one target and completes only on a green gate
- an operator or scheduled job invokes one fresh context per slice

Concurrency must respect the measured capacity of the execution backend. Start conservatively, add one replacement worker per completion, and avoid releasing synchronized retries after a timeout burst.
