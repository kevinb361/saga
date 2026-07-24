---
name: ops-document
description: "Create or revise reader-facing technical documentation, or route durable project knowledge to the correct Saga record without weakening its decision, glossary, lesson, specification, state, or public-safety rules."
disable-model-invocation: false
argument-hint: "[document, audience, or information to preserve]"
---

# ops-document

Preserve useful information for the right future reader. Documentation is not a transcript of the current session, and a Saga spine is not a dumping ground for every fact discovered during work.

## Choose the destination before writing

Inspect project guidance and existing documentation first. State the intended audience, purpose, destination, and why that file owns the information. If the operator named a file, honor it unless doing so would duplicate or contradict an authoritative source; surface that conflict instead of silently writing elsewhere.

When no Saga spine exists, write normal reader-facing documentation. This skill has no Saga dependency.

When `.planning/` exists, route durable project memory deliberately:

| Information | Destination and gate |
| --- | --- |
| Setup, operation, recovery, architecture, reference, proposal, README, or user guide | The existing reader-facing document that owns the topic, or a clearly named new document when none exists. |
| Current position, pause/resume handoff, blocker, or next action | `.planning/STATE.md`; edit the relevant section in place and preserve frontmatter plus unrelated content byte-for-byte. |
| Hard-to-reverse and surprising choice with a real trade-off | `.planning/decisions/NNNN-slug.md` only when **all three** criteria hold. If any fails, write no decision file; use a lighter state note or code comment only when requested. |
| Project-specific term or durable context fact | `.planning/CONTEXT.md`, which is the single glossary/context source; link to it rather than cloning definitions into multiple records. |
| Lesson learned from completed work or an incident | Append a dated entry to `.planning/RETROSPECTIVE.md`; never rewrite or reorder existing lessons. |
| Verified current system behavior | The existing domain spec or `.planning/SPEC.md`; update the living behavior directly for solo work, use a delta only for intentional staged work, and never record planned or assumed behavior as current truth. |
| Milestone, requirement, dependency, or proof condition | Route to `saga-plan`; do not disguise planning as documentation. |
| Requirement evidence or milestone quality verdict | Route to `saga-check` or independent `saga-audit`; do not self-certify by prose. |

## Draft for the reader

1. Gather facts from source, configuration, existing records, and live behavior where relevant. Distinguish current, historical, proposed, and unknown claims.
2. Lead with purpose and scope. Organize around the reader's path, not the author's discovery order.
3. Include prerequisites, exact examples, expected results, failure modes, verification, rollback, ownership, and update triggers where they matter.
4. Prefer links to authoritative sources over duplicated volatile values. Define terms before use and make dangerous or irreversible actions obvious.
5. Keep private details, credentials, internal addresses, personal identifiers, and environment-specific secrets out of public documentation. Use safe placeholders without fabricating a working value.

## Mutation boundary

A request to explain, summarize, inspect, or recommend does not authorize file edits. A request to write or update documentation authorizes only the named or confirmed destination and the smallest necessary supporting link/index edit. Do not opportunistically rewrite nearby docs, planning records, code, or configuration. If destination or publication boundary is ambiguous, show the proposed placement and wait.

## Reader check

Before finishing, reread without relying on conversation context:

- Can the intended reader find and complete the common path?
- Are current behavior and future proposals unmistakably separate?
- Are commands, paths, links, examples, and ownership accurate?
- Are failure, verification, and rollback instructions sufficient for the risk?
- Did the change preserve append-only, single-source, in-place, and independent-proof rules?
- Is the diff limited to the requested destination and necessary navigation?

Run the narrowest mechanical checks available for links, commands, formatting, examples, and the project gate. Report what was verified and what remains unverified.
