# Saga project guidance

Saga is a skills toolbox for AI-assisted coding, not a standalone application. The repository is the source of truth for the `saga-*` skills used by Claude Code, Codex, and Hermes.

Read `README.md` for the user-facing guide and `docs/DESIGN.md` for rationale and authoring conventions.

## Layout

```text
skills/saga/                 skill collection and per-skill references
bin/saga-project             requirement-to-Kanban DAG projector
bin/saga-statusline.js       optional Claude Code statusline
install.sh / uninstall.sh    cross-agent symlink management
tests/                       executable behavior tests
docs/                        installation and design documentation
.planning/                   Saga's own private files of record
```

## Change policy

- Keep skills inspectable: plain Markdown, small `SKILL.md`, deeper material in `reference.md`.
- Preserve `/saga-decision`'s three-part gate: hard to reverse, surprising without context, and a real trade-off.
- Preserve `/saga-next`'s safety boundary: inspect before mutation, deterministic verification after mutation, and explicit approval before risky live changes.
- Never author live-only Saga skills. Change the repository source and let symlink installation propagate it.
- Do not force `.planning/` into projects that use a different durable workflow.

## Installation behavior

`./install.sh` and `./uninstall.sh` support `--claude`, `--codex`, `--hermes`, and `--all`. No flags means all supported agents. They honor `CLAUDE_HOME`, `CODEX_HOME`, and `HERMES_HOME`.

Installers must:

- remain idempotent
- use symlinks rather than copies
- refuse to overwrite foreign entries
- remove only links that resolve back into this repository

## Verification

Run the canonical gate before committing:

```bash
make ci
```

Tests must use pytest-xdist (`pytest -n auto`). Review the diff and documentation impact before every commit.

## Cross-agent convention

`AGENTS.md` is a symlink to this file. Claude Code reads `CLAUDE.md`; Codex reads `AGENTS.md`; Hermes discovers the skill directories installed under its configured skills path.
