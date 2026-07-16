# Saga

A lean files-of-record toolbox for AI-assisted coding.

Saga gives Claude Code, Codex, and Hermes a small set of skills for keeping durable project context in plain, git-tracked Markdown: decisions, state, roadmap, requirements, traceability, retrospectives, and behavior specs. It also includes a bounded executor for choosing and verifying one next work slice.

No phase engine. No hidden database. No generated exhaust trail. The repository stays inspectable and repairable.

## Skills

| When you need to… | Use | Durable output |
| --- | --- | --- |
| execute the next bounded, verifiable slice | `/saga-next` | `STATE.md` and relevant evidence |
| resume, pause, or record current position | `/saga-state` | `.planning/STATE.md` |
| maintain milestones and requirements | `/saga-roadmap` | `ROADMAP.md`, `REQUIREMENTS.md` |
| prove requirements against named evidence | `/saga-verify` | `.planning/TRACEABILITY.md` |
| record a consequential trade-off | `/saga-decision` | `.planning/decisions/NNNN-slug.md` |
| preserve project vocabulary and rationale | `/saga-context` | `.planning/CONTEXT.md` |
| capture a durable lesson | `/saga-retro` | `.planning/RETROSPECTIVE.md` |
| preserve observable behavior | `/saga-spec` | `.planning/specs/<domain>/spec.md` |
| run a bounded sequence of slices | `/saga-loop` | updated records plus close-out evidence |
| run an independent quality review | `/saga-audit` | `.planning/AUDIT.md` |

## How it works

A typical project arc:

1. Add a milestone or requirement with `/saga-roadmap`.
2. Use `/saga-next` to select and execute one bounded slice.
3. Record only hard-to-reverse, surprising, real trade-offs with `/saga-decision`.
4. Run `/saga-verify` before closing a milestone.
5. Reconcile state with `/saga-state`; capture durable lessons with `/saga-retro`.

`/saga-next` reads the project before acting, classifies risk, executes safe repo-only work, and stops before unapproved live or destructive mutation. Completion is decided by a deterministic gate—tests, lint, live readback, or another concrete check—not by model confidence.

Projects without `.planning/` are supported. Saga reads `CLAUDE.md`, `AGENTS.md`, and `README.md` and uses the project’s native workflow instead of forcing new ceremony.

## Install

Clone the repository, then run:

```bash
./install.sh
```

With no flags, Saga links all skills into the default Claude Code, Codex, and Hermes skill directories. Select one or more agents when needed:

```bash
./install.sh --claude
./install.sh --codex --hermes
./install.sh --all
```

Agent homes can be overridden with `CLAUDE_HOME`, `CODEX_HOME`, and `HERMES_HOME`. Installation is symlink-based and idempotent; existing foreign files or symlinks are never overwritten.

Remove only Saga-owned links with matching flags:

```bash
./uninstall.sh
./uninstall.sh --hermes
```

See [docs/INSTALL.md](docs/INSTALL.md) for agent-specific details and the optional Claude Code statusline.

## Tools

- `bin/saga-lint` — read-only structural health check for a Saga spine.
- `bin/saga-project` — projects open requirements into a dependency-aware Hermes Kanban DAG. Dry-run JSON is the default; `--execute` creates worktree-isolated cards and one convergence card.
- `bin/saga-statusline.js` — optional Claude Code statusline showing model, project/worktree, context use, and the nearest Saga milestone.

## Project health

Run the human-readable check from a project root or point it at another project or its `.planning` directory:

```bash
bin/saga-lint
bin/saga-lint examples/minimal
bin/saga-lint --format json examples/minimal
```

`saga-lint` checks requirement IDs, markers and dependencies; structural traceability coverage; roadmap/milestone consistency; required STATE frontmatter; and local Markdown links in the canonical spine. It is read-only and does not judge evidence quality or replace `/saga-verify`.

JSON output uses deterministic schema version `1.0` and retains stable finding codes, paths, and line numbers. Exit codes: `0` clean, `1` findings, `2` invocation or parser failure. A missing Saga spine is an invocation failure: it retains the structured `SPINE_NOT_FOUND` finding and exits `2`.

The [minimal worked project](examples/minimal) demonstrates proven, open, and decision-backed records. Dedicated positive and negative fixtures are exercised by the test suite, so the canonical `make ci` gate checks both the example and known failure behavior.

## Development

Requirements: Python 3.11+, Node.js for statusline syntax validation, and the development tools used by CI.

```bash
python -m pip install pytest pytest-xdist ruff
make ci
```

The canonical gate runs shell syntax checks, Python lint, Node syntax validation, and the test suite in parallel.

## Design

Saga’s design favors:

- plain files over opaque state
- bounded slices over long agent runs
- deterministic verification over self-assessment
- progressive disclosure in skill docs
- explicit risk checkpoints before live mutation
- small, durable records over generated work logs

See [docs/DESIGN.md](docs/DESIGN.md) for the rationale and authoring rules.

## License

MIT — see [LICENSE](LICENSE).
