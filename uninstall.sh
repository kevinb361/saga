#!/usr/bin/env bash
# Remove only Saga-owned v2 skill links from Claude Code, Codex, Hermes, and/or
# Pi. This is a thin wrapper over bin/saga-skill-install.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

usage() {
  cat <<'EOF'
Usage: ./uninstall.sh [--all | --claude | --codex | --hermes | --pi ...]

Removes only the v2 skill links this checkout owns. Foreign files and links are
left untouched. With no agent flag, targets all supported agents. Agent homes may
be overridden with CLAUDE_HOME, CODEX_HOME, HERMES_HOME, and PI_HOME.

To reverse a migration to the exact pre-migration links, use ./install.sh --rollback.
EOF
}

args=()
for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
    *) args+=("$arg") ;;
  esac
done

exec python3 "$ROOT/bin/saga-skill-install" uninstall ${args[@]+"${args[@]}"}
