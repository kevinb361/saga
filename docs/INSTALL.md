# Installing Saga

Saga installs by linking its v2 skill surface from this checkout into one or more
agent homes. Edits to the checkout become live immediately; no copy or package
build is involved.

The installed surface is an **explicit manifest, never a glob**: eleven canonical
skills plus ten one-release compatibility aliases — the four legacy Saga names and
the six legacy general names (from the separate `agent-skills` repository) that
each route to a single canonical v2 skill or lens.

| Canonical `ops-*`  | Canonical `saga-*` | Compatibility alias → canonical                        |
| ------------------ | ------------------ | ------------------------------------------------------ |
| `ops-grill-me`     | `saga-init`        | `saga-next` → `saga-run`                               |
| `ops-troubleshoot` | `saga-plan`        | `saga-loop` → `saga-run`                               |
| `ops-review`       | `saga-run`         | `saga-verify` → `saga-check`                           |
| `ops-upgrade`      | `saga-state`       | `saga-lint` → `saga-check`                             |
| `ops-document`     | `saga-check`       | `adversarial-review` → `ops-review` (adversarial lens) |
|                    | `saga-audit`       | `review` → `ops-review`                                |
|                    |                    | `security-review` → `ops-review` (security lens)       |
|                    |                    | `debug` → `ops-troubleshoot`                           |
|                    |                    | `dependency-upgrade` → `ops-upgrade`                   |
|                    |                    | `write-docs` → `ops-document`                          |

Each compatibility alias is a self-named forwarder skill under `skills/compat/`.
Its `SKILL.md` `name:` matches its own directory, so no directory carries foreign
frontmatter and no second directory duplicates a canonical identity — the alias
stays callable under the legacy name without a mismatched skill identity. The
aliases exist for one release cycle and are removed when the old repository is
archived.

The four remaining legacy general names — `api-design`, `design-an-interface`,
`tdd`, and `verify-before-complete` — have no single canonical route (they are
internal disciplines or universal invariants absorbed across `saga-plan`,
`saga-run`, and every mutating `ops-*` skill), so they carry no forwarder. A
migration prunes them and a rollback restores them, but they are not callable as
standalone commands in the v2 surface.

## All supported agents

```bash
git clone https://github.com/kevinb361/saga.git
cd saga
./install.sh
```

No flags means Claude Code, Codex, Hermes, and Pi. Install is additive and
idempotent: it creates any missing surface links and leaves correct ones alone.
It refuses to replace an existing file or a symlink owned by another checkout, and
refuses to silently repoint a legacy link (run `--migrate` for that — see below).

## Select agents

```bash
./install.sh --claude
./install.sh --codex
./install.sh --hermes
./install.sh --pi
./install.sh --claude --hermes
./install.sh --all
```

Default destinations:

| Agent       | Destination                                                         |
| ----------- | ------------------------------------------------------------------- |
| Claude Code | `~/.claude/skills/`                                                 |
| Codex       | `~/.codex/skills/`                                                  |
| Hermes      | `~/.hermes/skills/`                                                 |
| Pi          | `~/.agents/skills/` (the shared Agent Skills location Pi discovers) |

Override an agent home for profiles, tests, or nonstandard layouts:

```bash
HERMES_HOME="$HOME/.hermes/profiles/deepworker" ./install.sh --hermes
CLAUDE_HOME=/path/to/claude-home ./install.sh --claude
PI_HOME=/path/to/agent-skills-home ./install.sh --pi
```

Migration recognizes legacy general-skill links only when they resolve inside the
declared old checkout, preventing an unrelated checkout with matching skill names
from being treated as owned. The default is `~/projects/agent-skills`; override it
when the old checkout lives elsewhere:

```bash
AGENT_SKILLS_ROOT=/path/to/agent-skills ./install.sh --migrate
```

Restart or begin a new agent session after installation so its skill index is
rebuilt.

The installed `saga-lint` alias carries a portable `scripts/run.sh` wrapper. It
resolves the bundled validator from the source checkout even when invoked through
an agent-home symlink, preserving the exit contract (`0` clean / `1` findings /
`2` unable to run) plus schema 1.0 JSON; no global `saga-lint` binary is required.

## Migrate from a legacy install

Machines that installed an earlier Saga (the flat `saga-*` surface) and/or the
separate `agent-skills` general surface upgrade with a reversible migration:

```bash
./install.sh --migrate           # all agents
./install.sh --migrate --hermes  # one agent
```

Migration first records the **exact pre-migration links** (per agent home) to a
snapshot, then writes the v2 surface, repoints the compatibility aliases to their
forwarder sources, and prunes the legacy names that are no longer part of the
visible surface. Pruned names are the legacy Saga records (`saga-context`,
`saga-decision`, `saga-retro`, `saga-roadmap`, `saga-spec`) and the four
non-routable legacy general disciplines (`api-design`, `design-an-interface`,
`tdd`, `verify-before-complete`).

Legacy general links are managed only when they resolve to the exact expected name
under `AGENT_SKILLS_ROOT` and carry matching frontmatter; those links are
snapshotted like any other managed name and are **not** treated as foreign. The six with a canonical route are repointed to their forwarders; the
four without are pruned. An arbitrary foreign file or symlink at a managed path is
still refused. All homes are preflighted for foreign conflicts before any change,
so a conflict aborts the whole run without mutating anything.

The snapshot path is `SAGA_MIGRATION_STATE`, defaulting to
`${XDG_STATE_HOME:-$HOME/.local/state}/saga/skill-migration.json`. It is never
written inside the repository.

### Roll back

```bash
./install.sh --rollback          # all agents
./install.sh --rollback --codex  # one agent
```

Rollback restores every managed link to its exact pre-migration state from the
snapshot: legacy links (from either legacy repository) return to their original
raw targets, and links that did not exist before the migration are removed.
Rollback is atomic — it preflights every selected snapshot path first, and if any
current entry has become foreign (something replaced our link since the
migration) it aborts the whole rollback with zero mutation rather than clobbering
that entry or restoring a partial surface around it.

## Uninstall

```bash
./uninstall.sh
./uninstall.sh --codex
```

The uninstaller removes only symlinks that resolve to the v2 skill sources in the
current checkout. Foreign files and links, and unrelated legacy links, are left
untouched. To reverse a migration to the exact pre-migration links, use
`./install.sh --rollback` instead.

## Pi package

`package.json` declares the exact v2 surface under the `pi` key — the 21 leaf
skill directories (11 canonical plus 10 compatibility aliases), never the
namespace parents `./skills/ops`/`./skills/saga` — with the `pi-package` keyword,
so the checkout is also a valid local Pi package. Enumerating leaves keeps Pi's
recursive convention discovery from surfacing the retired raw `skills/saga/*`
skills (kept in-tree for archival) or colliding their `name:` identities with the
`skills/compat/` forwarders. The manifest is exactly the installer's managed
surface. The installer itself uses the shared `~/.agents/skills/` symlink location
that Pi discovers, and needs no `pi install`.

## Optional Claude Code statusline

`bin/saga-statusline.js` can be used as a Claude Code command statusline. Add this
to `~/.claude/settings.json`, replacing the checkout path if necessary:

```json
{
  "statusLine": {
    "type": "command",
    "command": "node /absolute/path/to/saga/bin/saga-statusline.js"
  }
}
```

The statusline is read-only. Outside a project with Saga state, milestone output
is omitted.

## Verify installation

```bash
for home in "$HOME/.claude" "$HOME/.codex" "$HOME/.hermes" "$HOME/.agents"; do
  printf '%s: ' "$home"
  test -L "$home/skills/saga-run" && test -x "$home/skills/saga-lint/scripts/run.sh" && echo installed || echo absent
done
```
