---
name: saga-lint
description: "Run Saga's read-only structural health check against the current or supplied project. Use when asked to lint, validate, inspect, or diagnose a Saga .planning spine; preserves deterministic finding codes and exit semantics."
category: "saga"
disable-model-invocation: false
argument-hint: "[PATH] [--format human|json]"
---

# /saga-lint

Run the bundled structural validator without modifying the target project. This is the mechanical health check for Saga records; evidence quality remains `/saga-verify`'s job.

## Process

1. **Resolve the installed wrapper.** Use `scripts/run.sh` beside this `SKILL.md`. If the runtime does not expose the loaded skill directory, inspect these agent-home candidates:
   - `${HERMES_HOME:-$HOME/.hermes}/skills/saga-lint/scripts/run.sh`
   - `${CLAUDE_HOME:-$HOME/.claude}/skills/saga-lint/scripts/run.sh`
   - `${CODEX_HOME:-$HOME/.codex}/skills/saga-lint/scripts/run.sh`
   Resolve every executable match. If they point to one Saga checkout, use that wrapper; if they point to different checkouts, stop and report the ambiguity instead of choosing arbitrarily. Do not copy or reimplement the validator. Completion: the wrapper resolves to the Saga checkout that supplied this skill.

2. **Choose the target.** Forward the supplied path unchanged. With no path, pass `.` so the current project is checked. Forward `--format human|json` when requested; default to human output. Completion: exactly one target and one output mode are selected.

3. **Run read-only.** Execute the wrapper and preserve its output and exit code:
   - `0` — clean
   - `1` — structural findings
   - `2` — invocation or handled parser/read failure
   Do not turn exit `1` into a tool failure or claim the command malfunctioned; findings are the expected diagnostic result. Completion: stdout, stderr, and the numeric exit are captured.

4. **Report.** For exit `0`, report the clean target. For exit `1`, summarize findings by stable code with file and line evidence; do not modify records unless the operator separately asks for fixes. For exit `2`, report the invocation/parser error directly. Completion: the user can distinguish clean, structurally unhealthy, and unable-to-run states.

## Common Pitfalls

1. **Calling `bin/saga-lint` relative to the target project.** Most projects do not contain Saga's source checkout. Use this skill's wrapper, which resolves the bundled validator through the installed symlink.
2. **Treating findings as a crash.** Exit `1` means the validator worked and found drift.
3. **Claiming evidence is proven.** This command checks structure only; use `/saga-verify` for requirement-to-evidence quality.
4. **Silently fixing records.** `/saga-lint` is inspect-only. Mutations require a separate explicit task and the project's normal gate.

## Verification Checklist

- [ ] Wrapper came from the installed `saga-lint` skill
- [ ] Target and output format were explicit
- [ ] Exit code was preserved and interpreted correctly
- [ ] Findings include stable code plus file/line evidence
- [ ] No target files were modified
