---
name: write-docs
description: "Compatibility alias for ops-document (one release only, removed at REQ-086). The write-docs reader-oriented documentation workflow is now ops-document. Use when an operator or older automation explicitly invokes the legacy name."
category: "ops"
disable-model-invocation: true
argument-hint: "[document, audience, or information to preserve]"
---

# write-docs (compatibility alias)

`write-docs` is a **deprecated compatibility alias** kept for one release cycle so
existing invocations and muscle memory keep working during the v2 migration. It
holds no implementation of its own.

The former `write-docs` behavior — reader model, sourced claims, current versus
proposed separation, common path, prerequisites, examples, failure and rollback,
public safety, and link and command checks — is now `ops-document`, which also
routes durable project knowledge safely into Saga records.

## What to do

1. Read and follow the canonical skill: `ops-document`
   (`../../ops/ops-document/SKILL.md` from this directory).
2. Treat this invocation as `ops-document`: choose the destination before
   writing, keep the reader in mind, and preserve public safety. When the target
   is a Saga record rather than a reader-facing document, honor that record's
   decision, glossary, lesson, specification, and state rules.

Prefer `ops-document` directly in new work. This alias will be removed once the
migration is verified and the old repository is archived (REQ-086).
