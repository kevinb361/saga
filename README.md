# Saga Operator Toolbox

A small, version-controlled skill toolbox for Linux operators who use AI agents to inspect systems, troubleshoot failures, make bounded changes, and keep projects understandable.

This repository is the **canonical source** for the unified `ops-*` and `saga-*` package used by Claude Code, Codex, Hermes, and Pi. Skills are plain Markdown, project memory is plain git-tracked Markdown, and deterministic tools remain ordinary executables. There is no phase engine, hidden database, or generated work-log exhaust.

## Ten everyday intents

Tell the agent what you want in ordinary language. These are the primary workflows:

| Intent | Skill | Example |
| --- | --- | --- |
| Clarify a vague goal by asking hard questions | `ops-grill-me` | “Help me work out what this alerting change should do.” |
| Diagnose a code, configuration, service, host, or network failure | `ops-troubleshoot` | “The service is healthy but requests still time out.” |
| Review a proposed change or bounded subsystem | `ops-review` | “Review this migration and really try to break it.” |
| Upgrade software or infrastructure safely | `ops-upgrade` | “Upgrade this container and verify it stays healthy.” |
| Write documentation or preserve durable project knowledge | `ops-document` | “Write the recovery runbook for this service.” |
| Start a minimal Saga spine in a project | `saga-init` | “Start using Saga here.” |
| Turn a goal into milestones, requirements, dependencies, and proof | `saga-plan` | “Plan health monitoring for this service.” |
| Execute planned work behind deterministic gates | `saga-run` | “Keep going until something needs me.” |
| Resume, pause, or report project position | `saga-state` | “Where were we?” |
| Check structure and requirement evidence | `saga-check` | “Is this milestone actually proven?” |

### Independent milestone audit

`ops-review` is the ordinary read-only second look: it always checks correctness and operability and can add named security or adversarial lenses. It does **not** certify a Saga milestone.

`saga-audit` is the separate close-out gate. A capable context independent of the executor judges the completed milestone across correctness, safety, test coverage, architecture, and operability. It runs after `saga-check` and before any milestone completion flip. The executor never audits itself.

`ops-document` is for documentation or durable-memory intent. It does **not** mean every ordinary file edit should be routed through a documentation workflow. When a Saga spine exists, it chooses the appropriate existing record and preserves its rules; otherwise it writes the requested reader-facing document normally.

## Typical project flow

1. “Start using Saga here.”
2. “Plan health monitoring for this service.”
3. “Run the next slice.”
4. “Keep going until something needs me.”
5. “Check whether this milestone is proven.”
6. Run an independent `saga-audit` before closing the milestone.

`saga-run` defaults to exactly one bounded slice. A multi-slice loop requires explicit natural-language intent and remains capped, state-aware, and fail-closed. All mutating workflows distinguish repository-only, live, and destructive work; risky mutation stops for explicit scope and a rollback or recovery path.

Projects without `.planning/` remain supported. General `ops-*` skills use the project’s native guidance, and `saga-run` follows `CLAUDE.md`, `AGENTS.md`, or `README.md` rather than imposing Saga automatically.

## Compatibility during v2 migration

One-release compatibility aliases keep common old invocations working, but they are migration aids rather than primary workflows. New work should use the names above. See [the capability map](docs/CAPABILITY-MAP.md) for every old-to-new disposition and [the installation guide](docs/INSTALL.md) for migration and rollback details.

## Install

Clone this canonical repository and install the version-controlled skill surface:

```bash
git clone https://github.com/kevinb361/saga.git
cd saga
./install.sh
```

The default installs into Claude Code, Codex, Hermes, and Pi. Installation is symlink-based and idempotent, and it refuses foreign files or links. Existing legacy installations use the reversible migration documented in [docs/INSTALL.md](docs/INSTALL.md).

Remove only links owned by this checkout with:

```bash
./uninstall.sh
```

Pi also recognizes the root `package.json`, whose explicit leaf manifest exports the same 11 canonical skills and 10 temporary aliases as the installer. See the [v2.0.0 release notes](docs/RELEASE-v2.0.0.md) for migration and rollback highlights.

## Deterministic tools

- `bin/saga-lint` — read-only structural health check with stable human/JSON findings and exit codes.
- `bin/saga-migrate` — dry-run-first normalization of deterministic legacy record syntax.
- `bin/saga-project` — projection of open requirements into a dependency-aware Hermes Kanban DAG.
- `bin/saga-skill-install` — explicit-manifest install, migration, rollback, and uninstall driver.
- `bin/saga-statusline.js` — optional Claude Code statusline.

Check a Saga spine:

```bash
bin/saga-lint
bin/saga-lint examples/minimal
bin/saga-lint --format json examples/minimal
```

The validator checks requirement IDs and dependencies, traceability coverage, roadmap consistency, required STATE frontmatter, and local Markdown links. It is read-only and does not make the evidence or independent-audit judgment owned by `saga-check` and `saga-audit`. Exit codes: `0` clean, `1` findings, `2` invocation or parser failure. A missing Saga spine is an invocation failure and retains the structured `SPINE_NOT_FOUND` finding.

Preview and apply deterministic legacy-spine normalization:

```bash
bin/saga-migrate /path/to/project
bin/saga-migrate /path/to/project --write
bin/saga-lint /path/to/project
```

## Development

Requirements: Python 3.11+, Node.js for statusline syntax validation, pytest with xdist, and Ruff.

```bash
python -m pip install pytest pytest-xdist ruff
make ci
```

The canonical gate validates shell and Node syntax, Python code under the explicit project `ruff.toml` rule set, all skill metadata and references, exact package discovery, isolated installation lifecycles, deterministic tool behavior, risk and audit-independence invariants, and the Saga spine itself.

See [docs/TOOLBOX.md](docs/TOOLBOX.md) for the complete interface contract, [docs/DESIGN.md](docs/DESIGN.md) for rationale, and [docs/INSTALL.md](docs/INSTALL.md) for installation and rollback.

## License

MIT — see [LICENSE](LICENSE).
