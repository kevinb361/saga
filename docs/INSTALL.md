# Installing Saga

Saga installs by linking each `saga-*` skill directory from this checkout into one or more agent homes. Edits to the checkout become live immediately; no copy or package build is involved.

## All supported agents

```bash
git clone https://github.com/kevinb361/saga.git
cd saga
./install.sh
```

No flags means Claude Code, Codex, and Hermes. The script creates missing `skills/` directories and refuses to replace an existing file or a symlink owned by another checkout.

## Select agents

```bash
./install.sh --claude
./install.sh --codex
./install.sh --hermes
./install.sh --claude --hermes
./install.sh --all
```

Default destinations:

| Agent | Destination |
| --- | --- |
| Claude Code | `~/.claude/skills/saga-*` |
| Codex | `~/.codex/skills/saga-*` |
| Hermes | `~/.hermes/skills/saga-*` |

Override an agent home for profiles, tests, or nonstandard layouts:

```bash
HERMES_HOME="$HOME/.hermes/profiles/deepworker" ./install.sh --hermes
CLAUDE_HOME=/path/to/claude-home ./install.sh --claude
```

Restart or begin a new agent session after installation so its skill index is rebuilt.

The installed `/saga-lint` skill carries a portable `scripts/run.sh` wrapper. It resolves the validator from the source checkout even when invoked through an agent-home symlink; no global `saga-lint` binary is required.

## Uninstall

```bash
./uninstall.sh
./uninstall.sh --codex
```

The uninstaller removes only symlinks that resolve to skill directories in the current Saga checkout. Foreign files and links are left untouched.

## Optional Claude Code statusline

`bin/saga-statusline.js` can be used as a Claude Code command statusline. Add this to `~/.claude/settings.json`, replacing the checkout path if necessary:

```json
{
  "statusLine": {
    "type": "command",
    "command": "node /absolute/path/to/saga/bin/saga-statusline.js"
  }
}
```

The statusline is read-only. Outside a project with Saga state, milestone output is omitted.

## Verify installation

```bash
for home in "$HOME/.claude" "$HOME/.codex" "$HOME/.hermes"; do
  printf '%s: ' "$home"
  test -L "$home/skills/saga-next" && test -x "$home/skills/saga-lint/scripts/run.sh" && echo installed || echo absent
done
```
