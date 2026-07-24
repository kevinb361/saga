# Saga v2.0.0 — Unified operator toolbox

Saga v2.0.0 consolidates the former Saga and `agent-skills` surfaces into one version-controlled package for Claude Code, Codex, Hermes, and Pi.

## Primary interface

The everyday surface is ten intent-driven skills:

- `ops-grill-me`, `ops-troubleshoot`, `ops-review`, `ops-upgrade`, `ops-document`
- `saga-init`, `saga-plan`, `saga-run`, `saga-state`, `saga-check`

`saga-audit` remains separate as the independent milestone close-out gate. `ops-review` reviews a bounded change or subsystem; it does not certify a milestone. `ops-document` is used for documentation or durable-memory intent, not every ordinary file edit.

## What changed

- One canonical Pi/Agent Skills package owns both `ops-*` and `saga-*` namespaces.
- `saga-run` defaults to one bounded slice and enters capped loop mode only on explicit natural-language intent.
- `saga-check` separates deterministic structure checks from requirement-to-evidence checking.
- Five operator workflows work without a Saga `.planning/` spine.
- The installer manages Claude Code, Codex, Hermes, and Pi from an explicit, foreign-safe manifest.
- Package and CI gates validate metadata, references, deterministic tools, risk boundaries, audit independence, and isolated install/migration/rollback lifecycles.

## Compatibility and migration

Ten self-named compatibility aliases remain for one release cycle. They are migration aids, not the primary interface. Existing installations upgrade reversibly:

```bash
AGENT_SKILLS_ROOT=/path/to/agent-skills ./install.sh --migrate
```

Migration snapshots exact pre-existing links before changing any home. See `docs/INSTALL.md` for destinations, conflict handling, verification, and selective-agent commands.

## Rollback

Keep the migration snapshot until the transition release is retired. Restore the exact pre-migration links with:

```bash
AGENT_SKILLS_ROOT=/path/to/agent-skills ./install.sh --rollback
```

Rollback preflights every selected path and aborts without mutation if a foreign entry would be overwritten.

## Verification

The release source archive excludes the repository's private root `.planning/` spine while retaining nested public example and fixture spines. An extracted archive must pass:

```bash
make ci
```

The package manifest exports exactly 11 canonical skills plus 10 one-release compatibility aliases.
