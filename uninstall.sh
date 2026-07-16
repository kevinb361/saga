#!/usr/bin/env bash
# Remove only Saga-owned skill links from Claude Code, Codex, and/or Hermes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$ROOT/skills/saga"

usage() {
  cat <<'EOF'
Usage: ./uninstall.sh [--all | --claude | --codex | --hermes ...]

With no options, uninstalls from all supported agents. Agent homes may be
overridden with CLAUDE_HOME, CODEX_HOME, and HERMES_HOME.
EOF
}

agents=()
add_agent() {
  local candidate="$1" existing
  for existing in "${agents[@]:-}"; do
    [[ "$existing" == "$candidate" ]] && return
  done
  agents+=("$candidate")
}

if [[ $# -eq 0 ]]; then
  agents=(claude codex hermes)
else
  for arg in "$@"; do
    case "$arg" in
      --all) agents=(claude codex hermes) ;;
      --claude) add_agent claude ;;
      --codex) add_agent codex ;;
      --hermes) add_agent hermes ;;
      -h|--help) usage; exit 0 ;;
      *) echo "error: unknown option: $arg" >&2; usage >&2; exit 2 ;;
    esac
  done
fi

agent_home() {
  case "$1" in
    claude) printf '%s\n' "${CLAUDE_HOME:-$HOME/.claude}" ;;
    codex) printf '%s\n' "${CODEX_HOME:-$HOME/.codex}" ;;
    hermes) printf '%s\n' "${HERMES_HOME:-$HOME/.hermes}" ;;
  esac
}

resolve_path() {
  python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$1"
}

skills=()
for skill in "$SOURCE"/saga-*; do
  [[ -d "$skill" ]] && skills+=("$(basename "$skill")")
done

for agent in "${agents[@]}"; do
  destination="$(agent_home "$agent")/skills"
  removed=0
  for name in "${skills[@]}"; do
    link="$destination/$name"
    expected="$SOURCE/$name"
    if [[ -L "$link" ]] && [[ "$(resolve_path "$link")" == "$(resolve_path "$expected")" ]]; then
      rm "$link"
      ((removed += 1))
    fi
  done
  printf 'saga: %d skill link(s) removed for %s from %s\n' "$removed" "$agent" "$destination"
done
