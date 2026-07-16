#!/usr/bin/env node
// saga-statusline.js — lean Claude Code statusline for Saga projects
// Contract: reads JSON on stdin with: { model: { display_name }, workspace: { current_dir }, context_window: { remaining_percentage } }
// Output: single line: MODEL │ DIR [branch] │ ctx NN%

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

// Saga segment: read the nearest .planning/STATE.md frontmatter and render the
// active milestone (e.g. "○ v0.5 public release"). Returns '' outside Saga projects
// so it stays invisible elsewhere. Fail-silent; capped ancestor walk.
function sagaSeg(startDir) {
  let d = startDir;
  for (let i = 0; i < 6; i++) {
    try {
      const p = path.join(d, ".planning", "STATE.md");
      if (fs.existsSync(p)) {
        const fm = {};
        let inFm = false;
        for (const line of fs.readFileSync(p, "utf8").split("\n", 40)) {
          if (line.trim() === "---") {
            if (inFm) break;
            inFm = true;
            continue;
          }
          if (!inFm) continue;
          const m = line.match(/^(milestone|milestone_name|status):\s*(.+)$/);
          if (m) fm[m[1]] = m[2].replace(/^["']|["']$/g, "").trim();
        }
        // No segment when there's no active milestone (e.g. between_milestones).
        if (!fm.milestone || fm.milestone.toLowerCase() === "none") return "";
        const glyph =
          fm.status === "in_progress"
            ? "○" // ○
            : fm.status === "blocked"
              ? "✗" // ✗
              : "✓"; // ✓
        const name = fm.milestone_name ? ` ${fm.milestone_name}` : "";
        return `\x1b[2m${glyph} ${fm.milestone}${name}\x1b[0m`; // dim, quiet
      }
    } catch (_) {}
    const parent = path.dirname(d);
    if (parent === d) break;
    d = parent;
  }
  return "";
}

// Dir label: a Claude Code worktree (.../<project>/.claude/worktrees/<wt>) renders
// as "project ⑂ wt", dropping the auto-generated "worktree-<wt>" branch (redundant);
// a divergent branch is still shown. Non-worktree dirs render as "basename (branch)".
function dirLabel(dir, branch) {
  const DIMMER = "\x1b[2;2m";
  const BACK = "\x1b[2m"; // back to normal-dim after the extra-dim run
  const marker = "/.claude/worktrees/";
  const idx = dir.indexOf(marker);
  if (idx !== -1) {
    const project = path.basename(dir.slice(0, idx)) || dir.slice(0, idx);
    const wt = dir.slice(idx + marker.length).split("/")[0];
    const showBranch = branch && branch !== `worktree-${wt}`;
    const b = showBranch ? ` ${DIMMER}(${branch})${BACK}` : "";
    return `${project} ${DIMMER}⑂${BACK} ${wt}${b}`;
  }
  const base = path.basename(dir);
  return `${base}${branch ? ` ${DIMMER}(${branch})${BACK}` : ""}`;
}

function run() {
  let input = "";
  const stdinTimeout = setTimeout(() => process.exit(0), 3000);
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => (input += chunk));
  process.stdin.on("end", () => {
    clearTimeout(stdinTimeout);
    try {
      const data = JSON.parse(input);
      const model = data.model?.display_name || "";
      const dir = data.workspace?.current_dir || process.cwd();
      const remaining = data.context_window?.remaining_percentage;

      // Dim model name
      const modelSeg = model ? `\x1b[2m${model}\x1b[0m` : "";

      // Dir label (worktree-aware) + git branch
      let branch = "";
      try {
        branch = execSync("git rev-parse --abbrev-ref HEAD 2>/dev/null", {
          cwd: dir,
          timeout: 2000,
          encoding: "utf8",
        }).trim();
      } catch (_) {}
      const saga = sagaSeg(dir);
      const sagaSuffix = saga ? ` \x1b[2m·\x1b[0m ${saga}` : "";
      const dirSeg = `\x1b[2m${dirLabel(dir, branch)}\x1b[0m${sagaSuffix}`;

      // Context usage (simple: 100 - remaining, no buffer normalization)
      let ctxSeg = "";
      if (remaining != null) {
        const used = Math.max(0, Math.min(100, Math.round(100 - remaining)));
        const filled = Math.floor(used / 10);
        const bar = "\u2588".repeat(filled) + "\u2591".repeat(10 - filled);
        let color = "32"; // green
        if (used >= 80)
          color = "5;31"; // blink+red
        else if (used >= 65)
          color = "31"; // red
        else if (used >= 50) color = "33"; // yellow
        ctxSeg = ` \x1b[${color}m${bar} ${used}%\x1b[0m`;
      }

      const parts = [modelSeg, dirSeg].filter(Boolean);
      let line = parts.join(" │ ");
      if (ctxSeg) line += ctxSeg;
      process.stdout.write(line + "\n");
    } catch (e) {
      // Silent fail — don't break the statusline
    }
  });
}

run();
