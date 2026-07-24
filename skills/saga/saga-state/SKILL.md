---
name: saga-state
description: "Read or update .planning/STATE.md — current position, active work, deferred items. Use when asked 'where were we', 'resume', 'status of this project', or when pausing work. Preserves RAG frontmatter."
category: "saga"
disable-model-invocation: false
argument-hint: "[note <text> | pause | resume]"
---

# /saga-state

Maintain `.planning/STATE.md` — the project's living "where things stand" file: current position, active work,
and deferred items. One file, no phase engine. Project indexers read its YAML frontmatter, so preserving
that frontmatter is non-negotiable.

## Process

### resume

1. **READ `.planning/STATE.md` first.** Summarize current position (phase/milestone + status), active work, and
   the deferred list back to the operator **before doing anything else**. That summary IS the resume.

### note / pause

1. **Edit an existing STATE.md in place.** Read the complete file first and change only the relevant frontmatter values and named sections. Never rebuild an existing file from the template, truncate unrelated sections, or reorder history; the template in `reference.md` is only for a genuinely absent file.
2. Update `## Current Position` (phase, plan, status, a dated `Last activity:` line).
3. Append anything in-flight to `## Active Work`; append any "ugly-but-works, fix-later" item to `## Deferred`.
4. Update the YAML frontmatter: set `last_updated` to today's ISO timestamp and refresh `last_activity`.
   **Preserve every other frontmatter key** (version marker, `milestone`, `milestone_name`, `status`,
   `progress`) — only change what actually changed; never drop a key. If STATE.md is absent, create it from the
   template in `reference.md`.

## Completion criterion

DONE when — for `resume`, you have read STATE.md and restated the current position + deferred items before any
other action; for `note`/`pause`, STATE.md has a dated current-position line, `last_updated` is today, every
pre-existing frontmatter key is still present, and any deferred item the operator mentioned is in `## Deferred`.
Do not invent progress numbers — carry forward what's there unless told otherwise.

See `reference.md` for the STATE.md template and the frontmatter keys to preserve.
