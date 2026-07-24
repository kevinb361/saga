---
name: saga-init
description: "Explicitly and idempotently bootstrap the minimum useful Saga spine after inspecting a project's existing guidance and mechanical gate; never invent requirements or impose Saga automatically."
category: "saga"
disable-model-invocation: true
argument-hint: "[project goal or existing plan to preserve]"
---

# saga-init

Start Saga only because the operator explicitly asked. A project without `.planning/` is not broken, and ordinary work in a native project is never a reason to create a spine automatically.

## Process

1. **Inspect the native project first.** Read `CLAUDE.md`, `AGENTS.md`, `README.md`, and the smallest relevant existing planning or contribution files. Identify the repository root, current dirty state, existing roadmap/issues/specs, and local rules for generated or private files. Do not replace an established project workflow without the operator's stated intent.

2. **Detect the mechanical gate.** Prefer, in order: an explicit gate in existing project guidance; `make ci` when defined; the evident package/project test and lint command; then the narrowest syntax or content check available. Detection is read-only. Do not install dependencies, refresh indexes, fetch the network, start services, or run production commands merely to discover a gate. If no gate is safely detectable, record `gate: null` and say verification must be chosen during planning.

3. **Inspect before creating.** If `.planning/` already exists, read its files and run the available read-only Saga structural check. Do not reinitialize, rewrite, normalize, or downgrade it. Report missing files or drift as follow-up work. A repeated invocation against a valid spine must leave every byte unchanged.

4. **Create only the minimum useful spine.** When `.planning/` is absent, create the directory and these four plain-Markdown records:
   - `STATE.md` — valid frontmatter, current position, active work, and deferred work;
   - `ROADMAP.md` — an empty milestones section;
   - `REQUIREMENTS.md` — an empty requirements section that explains `[ ]`, `[x]`, and `[/]` markers;
   - `TRACEABILITY.md` — an empty evidence table distinguishing PROVEN, ASSERTED, OPEN, and WAIVED.

   Add `.planning/config.json` only when a mechanical gate was detected or another explicit configuration value is supplied. Do not create decision, retrospective, context, specification, audit, phase, wave, summary, or verification files speculatively.

5. **Preserve operator intent without invention.** If the operator supplied a goal, quote or faithfully normalize it in STATE as unplanned intent. Do not decompose it into requirements, assign IDs, infer milestones, mark work complete, or fabricate evidence. Direct the operator to `saga-plan` for that judgment-bearing work.

6. **Verify idempotency and structure.** Run the detected project gate only when it is safe and already available, plus the read-only Saga structural check. Snapshot hashes of every created spine file, repeat the initialization logic, and prove the second pass changes nothing. Report created files, detected gate, checks run, and the next natural-language planning action.

## Safety and completion

All bootstrap work is repository-only. Stop before creation when the repository root is ambiguous, local guidance forbids the directory, `.planning` is a non-directory or foreign-owned path, existing records would be overwritten, or the requested project is production-mounted and local policy requires a different execution host.

DONE only when the minimum records exist, no pre-existing file was overwritten, the structure check is green, and a second pass is byte-for-byte unchanged. If no files were needed, DONE means the existing spine was inspected and left untouched.
