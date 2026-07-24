#!/usr/bin/env bash
# Install, migrate, or roll back Saga's v2 skill surface for Claude Code, Codex,
# Hermes, and/or Pi. This is a thin wrapper over bin/saga-skill-install.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

usage() {
  cat <<'EOF'
Usage: ./install.sh [--migrate | --rollback] [--all | --claude | --codex | --hermes | --pi ...]

With no mode flag, installs (additive, idempotent) the v2 skill surface: eleven
canonical skills plus ten one-release compatibility aliases. With no agent flag,
targets all supported agents.

  --migrate    upgrade from a legacy surface, snapshotting the exact pre-migration
               links so the change is reversible, then pruning superseded names.
  --rollback   restore every managed link to its exact pre-migration state.

Agent homes may be overridden with CLAUDE_HOME, CODEX_HOME, HERMES_HOME, and
PI_HOME. AGENT_SKILLS_ROOT identifies the old general-skill checkout during
migration. The migration snapshot path is SAGA_MIGRATION_STATE.
EOF
}

mode="install"
args=()
for arg in "$@"; do
  case "$arg" in
    --migrate) mode="migrate" ;;
    --rollback) mode="rollback" ;;
    -h|--help) usage; exit 0 ;;
    *) args+=("$arg") ;;
  esac
done

exec python3 "$ROOT/bin/saga-skill-install" "$mode" ${args[@]+"${args[@]}"}
