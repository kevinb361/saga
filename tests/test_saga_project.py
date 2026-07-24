"""Tests for bin/saga-project — the saga milestone → kanban DAG projector.

Covers:
  - pure chain from unannotated file (implicit serial)
  - explicit roots via (depends: none)
  - DONE dep edges are dropped
  - fail-closed: unknown dep, cycle, self-dep, contradiction, cross-milestone OPEN
  - cross-milestone DONE dep is allowed (edge dropped)
  - no OPEN reqs for milestone → error
  - missing REQUIREMENTS.md → error
  - --execute without --repo → error (REQ-031)
  - worktree workspace set on every card spec (REQ-031)
  - >3 roots produces the serial chain of surplus roots (REQ-031)
  - parent links emitted for every edge (REQ-031)
  - dry-run output includes exactly one convergence card (REQ-032)
  - convergence card parented on all sinks, and only sinks (REQ-032)
  - convergence body carries the fail-closed auditor contract (REQ-032)
  - --execute creates ONE convergence card, last, parented on sinks (REQ-032)

Note (integration, decision 0005): on --execute, every DAG projects one
extra `hermes kanban create` for the convergence card (REQ-032), so the
REQ-031 command-count assertions are slice-cards + 1.
"""

from datetime import date as _date
import json
import os
import subprocess
import sys
import tempfile

import pytest

# Path to the saga-project script
SCRIPT = os.path.join(os.path.dirname(__file__), "..", "bin", "saga-project")
FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def run_project(requirements_file, milestone="test", execute=False, repo=None):
    """Run saga-project against a fixture file and return (returncode, stdout, stderr)."""
    cmd = [
        sys.executable,
        SCRIPT,
        "--milestone",
        milestone,
        "--requirements",
        requirements_file,
    ]
    if execute:
        cmd.append("--execute")
        if repo:
            cmd.extend(["--repo", repo])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def _load_script_module():
    """Load bin/saga-project as a Python module for unit-testing execute()."""
    with open(SCRIPT) as f:
        src = f.read()
    mod = type(sys)("saga_project")
    mod.__file__ = SCRIPT
    mod.__name__ = "saga_project"
    exec(compile(src, SCRIPT, "exec"), mod.__dict__)
    return mod


class MockRunResult:
    """Fake subprocess.run result returning a deterministic task ID from the command."""

    def __init__(self, cmd):
        self.returncode = 0
        self.stderr = ""
        for part in cmd:
            if part.startswith("REQ-"):
                req_id = part.split(":")[0]
                break
        else:
            req_id = "REQ-000"
        self.stdout = json.dumps({"id": f"t_{req_id.lower()}"})


# ── dry-run tests (original) ──────────────────────────────────────────────


def test_pure_chain():
    """A file with no depends tags projects to a pure serial chain."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 3

    assert cards[0]["req"] == "REQ-100"
    assert cards[0]["depends"] == []
    assert cards[1]["req"] == "REQ-101"
    assert cards[1]["depends"] == ["REQ-100"]
    assert cards[2]["req"] == "REQ-102"
    assert cards[2]["depends"] == ["REQ-101"]


def test_explicit_roots():
    """(depends: none) creates parallel roots; explicit deps work."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "explicit_roots.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 3

    assert cards[0]["req"] == "REQ-200"
    assert cards[0]["depends"] == []
    assert cards[1]["req"] == "REQ-201"
    assert cards[1]["depends"] == []
    assert cards[2]["req"] == "REQ-202"
    assert sorted(cards[2]["depends"]) == ["REQ-200", "REQ-201"]


def test_done_dep_dropped():
    """A dependency on a DONE req ([x] or [/]) is satisfied; edge is dropped."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "done_dep_dropped.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 2

    assert cards[0]["req"] == "REQ-301"
    assert cards[0]["depends"] == []
    assert cards[1]["req"] == "REQ-302"
    assert cards[1]["depends"] == []


def test_malformed_requirement_line_fails_closed():
    """Requirement-like rows that cannot be parsed must block projection."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-001** — valid (milestone: test) (depends: none)\n")
        f.write("- [?] **REQ-002** — malformed (milestone: test) (depends: none)\n")
        f.flush()
        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc != 0
    assert stdout == ""
    assert "malformed requirement line" in stderr


def test_lowercase_requirement_id_fails_closed():
    """Projector must reject the same non-canonical ID casing as saga-lint."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **safe-21** — lowercase (milestone: test) (depends: none)\n")
        f.flush()
        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc != 0
    assert stdout == ""
    assert "malformed requirement line" in stderr


def test_missing_requirement_markup_fails_closed():
    """A checkbox row in Requirements cannot disappear due to missing bold markup."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-001** — valid (milestone: test) (depends: none)\n")
        f.write("- [ ] REQ-002 — missing bold markup (milestone: test)\n")
        f.flush()
        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc != 0
    assert stdout == ""
    assert "malformed requirement line" in stderr


def test_semantic_requirement_ids_are_projected_and_gate_convergence():
    """Documented SAFE/ACCESS-style IDs participate in the complete DAG."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-001** — feature (milestone: test) (depends: none)\n")
        f.write("- [ ] **SAFE-21** — invariant (milestone: test) (depends: REQ-001)\n")
        f.flush()
        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc == 0, stderr
    data = json.loads(stdout)
    assert [card["req"] for card in data["cards"]] == ["REQ-001", "SAFE-21"]
    assert data["convergence"]["depends"] == ["SAFE-21"]


def test_duplicate_requirement_id_fails_closed():
    """Duplicate IDs must block projection instead of collapsing DAG nodes."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-001** — first (milestone: test) (depends: none)\n")
        f.write("- [ ] **REQ-001** — duplicate (milestone: test) (depends: none)\n")
        f.flush()
        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc != 0
    assert stdout == ""
    assert "duplicate requirement ID" in stderr


def test_unknown_dep_fails():
    """Dependency on a non-existent REQ-ID → exit nonzero."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "unknown_dep.md"))
    assert rc != 0, "expected nonzero exit for unknown dep"
    assert "REQ-999" in stderr


def test_cycle_fails():
    """Cycle detection → exit nonzero."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "cycle.md"))
    assert rc != 0, "expected nonzero exit for cycle"
    assert "cycle" in stderr.lower()


def test_self_dep_fails():
    """Self-dependency → exit nonzero."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "self_dep.md"))
    assert rc != 0, "expected nonzero exit for self-dep"
    assert "self" in stderr.lower()


def test_contradiction_fails():
    """(depends: none, REQ-NNN) is a contradiction → exit nonzero."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "contradiction.md"))
    assert rc != 0, "expected nonzero exit for contradiction"
    assert "contradiction" in stderr.lower()


def test_cross_milestone_open_fails():
    """OPEN cross-milestone dependency → exit nonzero."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "cross_milestone_open.md"))
    assert rc != 0, "expected nonzero exit for cross-milestone OPEN dep"
    assert "cross-milestone" in stderr.lower()


def test_cross_milestone_done_allowed():
    """DONE cross-milestone dependency is satisfied (edge dropped, not an error)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [x] **REQ-900** — done in other milestone (milestone: other)\n")
        f.write(
            "- [ ] **REQ-901** — depends on done cross-milestone (milestone: test) (depends: REQ-900)\n"
        )
        f.flush()

        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc == 0, f"expected success for cross-milestone DONE dep, got {rc}: {stderr}"
    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 1
    assert cards[0]["req"] == "REQ-901"
    assert cards[0]["depends"] == []


def test_no_open_reqs_for_milestone():
    """When no OPEN reqs exist for the milestone → exit nonzero."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [x] **REQ-950** — done (milestone: test)\n")
        f.flush()

        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc != 0, "expected nonzero exit when no OPEN reqs for milestone"


def test_missing_requirements_file():
    """Missing REQUIREMENTS.md → exit nonzero."""
    rc, stdout, stderr = run_project("/nonexistent/path/REQUIREMENTS.md")
    assert rc != 0, "expected nonzero exit for missing file"


def test_slash_marker_is_done():
    """[/] is accepted as a compatibility marker for completed work."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [/] **REQ-970** — done with slash (milestone: test)\n")
        f.write(
            "- [ ] **REQ-971** — depends on slash-done (milestone: test) (depends: REQ-970)\n"
        )
        f.flush()

        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc == 0, f"expected success, got {rc}: {stderr}"
    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 1
    assert cards[0]["req"] == "REQ-971"
    assert cards[0]["depends"] == []


def test_mixed_milestones_only_active_shown():
    """Only reqs matching the --milestone slug appear in the output."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-980** — in other milestone (milestone: other)\n")
        f.write("- [ ] **REQ-981** — in test milestone (milestone: test)\n")
        f.flush()

        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc == 0, f"expected success, got {rc}: {stderr}"
    data = json.loads(stdout)
    cards = data["cards"]
    assert len(cards) == 1
    assert cards[0]["req"] == "REQ-981"


# ── REQ-031: knee-capped isolated dispatch ─────────────────────────────────


def test_execute_without_repo_fails():
    """--execute without --repo → exit nonzero."""
    rc, stdout, stderr = run_project(
        os.path.join(FIXTURES, "pure_chain.md"),
        execute=True,
    )
    assert rc != 0, "expected nonzero exit when --execute lacks --repo"
    assert "--repo" in stderr


def test_worktree_workspace_set_on_every_card():
    """Every created card gets --workspace worktree:<repo> in its create command."""
    mod = _load_script_module()
    cards = [
        {"req": "REQ-100", "title": "First", "depends": []},
        {"req": "REQ-101", "title": "Second", "depends": ["REQ-100"]},
    ]
    commands = []

    def mock_run(cmd, **kwargs):
        commands.append(cmd)
        return MockRunResult(cmd)

    mod.execute(cards, "test", "/tmp/example-repo", _run_cmd=mock_run)

    # 2 slice cards + 1 convergence card (REQ-032 / decision 0005)
    assert len(commands) == 3
    for cmd in commands:
        assert "--workspace" in cmd
        idx = cmd.index("--workspace")
        assert cmd[idx + 1] == "worktree:/tmp/example-repo"


def test_more_than_three_roots_produces_serial_chain():
    """>3 roots: roots[3:] are chained serially on their predecessor (file order)."""
    mod = _load_script_module()
    cards = [
        {"req": f"REQ-{400 + i}", "title": f"Root {i}", "depends": []} for i in range(5)
    ]
    commands = []

    def mock_run(cmd, **kwargs):
        commands.append(cmd)
        return MockRunResult(cmd)

    mod.execute(cards, "test", "/tmp/example-repo", _run_cmd=mock_run)

    # 5 slice cards + 1 convergence card (REQ-032 / decision 0005)
    assert len(commands) == 6

    # First 3 roots have no --parent
    for i in range(3):
        assert "--parent" not in commands[i], f"root {i} should have no --parent"

    # 4th root (REQ-403) depends on 3rd (REQ-402)
    assert "--parent" in commands[3], "4th root should have --parent"
    pidx = commands[3].index("--parent")
    assert commands[3][pidx + 1] == "t_req-402"

    # 5th root (REQ-404) depends on 4th (REQ-403)
    assert "--parent" in commands[4], "5th root should have --parent"
    pidx = commands[4].index("--parent")
    assert commands[4][pidx + 1] == "t_req-403"


def test_parent_links_emitted_for_every_edge():
    """Every dependency edge produces a --parent in the create command."""
    mod = _load_script_module()
    cards = [
        {"req": "REQ-200", "title": "Root A", "depends": []},
        {"req": "REQ-201", "title": "Root B", "depends": []},
        {"req": "REQ-202", "title": "Dependent", "depends": ["REQ-200", "REQ-201"]},
    ]
    commands = []

    def mock_run(cmd, **kwargs):
        commands.append(cmd)
        return MockRunResult(cmd)

    mod.execute(cards, "test", "/tmp/example-repo", _run_cmd=mock_run)

    # 3 slice cards + 1 convergence card (REQ-032 / decision 0005)
    assert len(commands) == 4

    # Find REQ-202's command
    req202_cmd = [c for c in commands if "REQ-202" in " ".join(c)][0]
    parent_count = req202_cmd.count("--parent")
    assert (
        parent_count == 2
    ), f"REQ-202 should have 2 --parent flags, got {parent_count}"
    assert "t_req-200" in req202_cmd
    assert "t_req-201" in req202_cmd


# ── Convergence card tests (REQ-032) ──────────────────────────────────


def test_convergence_exactly_one():
    """Dry-run output includes exactly one convergence card."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    assert "convergence" in data, "expected a 'convergence' key in dry-run output"
    conv = data["convergence"]
    assert conv["req"] == "__convergence__"


def test_convergence_parented_on_sinks_only():
    """Convergence card depends on all sink cards and only sink cards."""
    # pure_chain: REQ-100 -> REQ-101 -> REQ-102; only REQ-102 is a sink
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    conv = data["convergence"]
    assert conv["depends"] == ["REQ-102"]


def test_convergence_multiple_sinks():
    """When there are multiple sinks (parallel roots with no common child),
    convergence is parented on all of them."""
    # explicit_roots: REQ-200 (root), REQ-201 (root), REQ-202 (depends on 200,201)
    # Only REQ-202 is a sink
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "explicit_roots.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    conv = data["convergence"]
    assert conv["depends"] == ["REQ-202"]


def test_convergence_two_independent_sinks():
    """Two independent roots with no shared child produce two sinks."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-400** — first root (milestone: test) (depends: none)\n")
        f.write("- [ ] **REQ-401** — second root (milestone: test) (depends: none)\n")
        f.flush()

        rc, stdout, stderr = run_project(f.name)
        os.unlink(f.name)

    assert rc == 0, f"expected success, got {rc}: {stderr}"
    data = json.loads(stdout)
    conv = data["convergence"]
    # Both are sinks — nothing depends on either
    assert sorted(conv["depends"]) == ["REQ-400", "REQ-401"]


def test_convergence_body_contains_auditor_contract():
    """Convergence card body contains the fail-closed auditor contract."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    body = data["convergence"]["body"]

    # Must contain the fail-closed contract
    assert "FAIL CLOSED" in body, "body must contain FAIL CLOSED directive"
    assert "TRACEABILITY.md" in body, "body must mention TRACEABILITY.md"
    assert "AUDIT.md" in body, "body must mention AUDIT.md"
    assert "close_out_auditor" in body, "body must reference close_out_auditor"
    assert "NEVER" in body, "body must contain the NEVER self-verify directive"
    assert "saga-verify" in body, "body must mention /saga-verify"
    assert "saga-audit" in body, "body must mention /saga-audit"


def test_convergence_body_mentions_single_flighted():
    """Convergence card body states it is the only close-out path."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    body = data["convergence"]["body"]

    assert "ONLY close-out path" in body, "body must state single-flighted close-out"


def test_convergence_body_includes_milestone():
    """Convergence card body includes the milestone slug."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# test\n\n## Requirements\n\n")
        f.write("- [ ] **REQ-450** — first (milestone: v1.0-concurrent-execution)\n")
        f.flush()

        rc, stdout, stderr = run_project(
            f.name,
            milestone="v1.0-concurrent-execution",
        )
        os.unlink(f.name)

    assert rc == 0, f"expected success, got {rc}: {stderr}"
    data = json.loads(stdout)
    body = data["convergence"]["body"]

    assert "v1.0-concurrent-execution" in body, "body must include the milestone slug"


def test_execute_creates_one_convergence_card_last_parented_on_sinks():
    """--execute creates exactly ONE convergence card, created last, with a
    --parent per sink task id, worktree workspace, and the auditor body."""
    mod = _load_script_module()
    cards = [
        {"req": "REQ-200", "title": "Root A", "depends": []},
        {"req": "REQ-201", "title": "Root B", "depends": []},
        {"req": "REQ-202", "title": "Dependent", "depends": ["REQ-200", "REQ-201"]},
    ]
    commands = []

    def mock_run(cmd, **kwargs):
        commands.append(cmd)
        return MockRunResult(cmd)

    mod.execute(cards, "test", "/tmp/example-repo", _run_cmd=mock_run)

    conv_cmds = [c for c in commands if "convergence close-out for test" in c]
    assert len(conv_cmds) == 1, "exactly one convergence card must be created"
    conv_cmd = conv_cmds[0]
    assert conv_cmd is commands[-1], "convergence card must be created last"

    # Parented on the sole sink (REQ-202) — and only sinks
    assert conv_cmd.count("--parent") == 1
    pidx = conv_cmd.index("--parent")
    assert conv_cmd[pidx + 1] == "t_req-202"

    # Worktree workspace like every other card (REQ-031)
    widx = conv_cmd.index("--workspace")
    assert conv_cmd[widx + 1] == "worktree:/tmp/example-repo"

    # Fail-closed auditor contract travels in the card body
    bidx = conv_cmd.index("--body")
    body = conv_cmd[bidx + 1]
    assert "FAIL CLOSED" in body
    assert "close_out_auditor" in body


# ---- REQ-036: checkbox-flip instructions in convergence body ---------------


def test_convergence_body_contains_checkbox_flip_instruction():
    """Convergence body instructs workers to flip REQ checkboxes with read-then-replace."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    body = data["convergence"]["body"]

    # Must contain checkbox-flip instruction
    assert "[ ]" in body, "body must reference the open checkbox marker"
    assert "[x]" in body, "body must reference the done checkbox marker"
    assert "read-then-replace" in body, "body must specify read-then-replace approach"
    assert "exact-match patch" in body, "body must warn against pre-composed exact-match patches"
    assert "REQ-023" in body, "body must reference REQ-023 pattern"


def test_convergence_body_claim_before_verify_and_roadmap():
    """Card evidence becomes a claim before independent verification and close-out."""
    rc, stdout, stderr = run_project(os.path.join(FIXTURES, "pure_chain.md"))
    assert rc == 0, f"expected success, got {rc}: {stderr}"

    data = json.loads(stdout)
    body = data["convergence"]["body"]

    verify_pos = body.index("saga-verify")
    flip_pos = body.index("[ ]")
    roadmap_pos = body.index("ROADMAP")

    assert flip_pos < verify_pos, "claim marker must be recorded before /saga-verify"
    assert verify_pos < roadmap_pos, "verification must gate the ROADMAP flip"


def test_convergence_body_with_task_ids_includes_card_refs():
    """When task_ids are provided, the body lists per-REQ card-ref evidence."""
    mod = _load_script_module()
    task_ids = {"REQ-100": "t_req-100", "REQ-101": "t_req-101", "__convergence__": "t_conv"}
    body = mod.build_convergence_body("v1.2", task_ids)

    # Each REQ gets a per-line instruction with its card id
    assert "REQ-100" in body
    assert "(card: t_req-100)" in body
    assert "REQ-101" in body
    assert "(card: t_req-101)" in body
    # Convergence card itself is excluded from flip list
    assert "t_conv" not in body
    assert "__convergence__" not in body


def test_convergence_body_with_task_ids_includes_read_then_replace():
    """Per-REQ flip instructions carry the read-then-replace directive."""
    mod = _load_script_module()
    task_ids = {"REQ-200": "t_req-200"}
    body = mod.build_convergence_body("test", task_ids)

    assert "read-then-replace" in body
    assert "exact-match patch" in body


def test_execute_convergence_body_has_task_ids():
    """--execute passes task_ids to build_convergence_body so card refs appear."""
    mod = _load_script_module()
    cards = [
        {"req": "REQ-300", "title": "Slice A", "depends": []},
        {"req": "REQ-301", "title": "Slice B", "depends": ["REQ-300"]},
    ]

    commands = []

    def mock_run(cmd, **kwargs):
        commands.append(cmd)
        return MockRunResult(cmd)

    mod.execute(cards, "v1.2", "/tmp/example-repo", _run_cmd=mock_run)

    conv_cmds = [c for c in commands if "convergence close-out for v1.2" in c]
    assert len(conv_cmds) == 1
    conv_cmd = conv_cmds[0]

    bidx = conv_cmd.index("--body")
    body = conv_cmd[bidx + 1]

    # Should contain per-REQ card-ref evidence from task_ids
    assert "(card: t_req-300)" in body, "body must include card ref for REQ-300"
    assert "(card: t_req-301)" in body, "body must include card ref for REQ-301"
    assert "read-then-replace" in body
    assert "[ ]" in body
    assert "[x]" in body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ---- (not-before:) time gates ----------------------------------------------
_sp = _load_script_module()


def _mk_reqs(tmp_path, body):
    f = tmp_path / "REQUIREMENTS.md"
    f.write_text(body)
    return f


NB_FIXTURE = """# reqs
- [ ] **REQ-101** — base slice (milestone: m1) (depends: none)
- [ ] **REQ-102** — gated slice (milestone: m1) (depends: none) (not-before: 2099-01-01)
- [ ] **REQ-103** — rides on gated (milestone: m1) (depends: REQ-102)
- [ ] **REQ-104** — rides on base (milestone: m1) (depends: REQ-101)
"""


def test_not_before_defers_and_cascades(tmp_path):
    reqs = _sp.parse_requirements(_mk_reqs(tmp_path, NB_FIXTURE))
    cards = _sp.validate_and_resolve(reqs, "m1")
    eligible, deferred = _sp.apply_not_before(cards, reqs, today=_date(2026, 7, 11))
    assert [c["req"] for c in eligible] == ["REQ-101", "REQ-104"]
    assert [d["req"] for d in deferred] == ["REQ-102", "REQ-103"]
    assert deferred[0]["reason"] == "time-gated"
    assert "REQ-102" in deferred[1]["reason"]


def test_not_before_past_date_is_eligible(tmp_path):
    body = NB_FIXTURE.replace("2099-01-01", "2020-01-01")
    reqs = _sp.parse_requirements(_mk_reqs(tmp_path, body))
    cards = _sp.validate_and_resolve(reqs, "m1")
    eligible, deferred = _sp.apply_not_before(cards, reqs, today=_date(2026, 7, 11))
    assert len(eligible) == 4 and deferred == []


def test_not_before_invalid_date_fails_closed(tmp_path):
    body = NB_FIXTURE.replace("2099-01-01", "next-month")
    reqs = _sp.parse_requirements(_mk_reqs(tmp_path, body))
    cards = _sp.validate_and_resolve(reqs, "m1")
    import pytest as _pt
    with _pt.raises(SystemExit):
        _sp.apply_not_before(cards, reqs, today=_date(2026, 7, 11))


def test_execute_fails_cleanly_on_invalid_hermes_json(capsys):
    mod = _load_script_module()

    def fake_run(_cmd, **_kw):
        result = MockRunResult([])
        result.stdout = "not-json"
        return result

    with pytest.raises(SystemExit):
        mod.execute(
            [{"req": "REQ-201", "title": "a", "depends": []}],
            "m9",
            "/tmp/repo",
            _run_cmd=fake_run,
        )

    assert "invalid JSON for REQ-201" in capsys.readouterr().err


def test_execute_fails_cleanly_when_hermes_omits_task_id(capsys):
    mod = _load_script_module()

    def fake_run(_cmd, **_kw):
        result = MockRunResult([])
        result.stdout = json.dumps({"status": "created"})
        return result

    with pytest.raises(SystemExit):
        mod.execute(
            [{"req": "REQ-201", "title": "a", "depends": []}],
            "m9",
            "/tmp/repo",
            _run_cmd=fake_run,
        )

    error = capsys.readouterr().err
    assert "no task ID for REQ-201" in error
    assert "idempotency-key saga:/tmp/repo:m9:REQ-201" in error


def test_execute_sets_assignee_and_idempotency(tmp_path):
    mod = _load_script_module()
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return MockRunResult(cmd)

    cards = [
        {"req": "REQ-201", "title": "a", "depends": []},
        {"req": "REQ-202", "title": "b", "depends": ["REQ-201"]},
    ]
    mod.execute(cards, "m9", "/tmp/repo", _run_cmd=fake_run, assignee="fast-worker")
    assert len(calls) == 3  # 2 slices + convergence
    for cmd in calls:
        ai = cmd.index("--assignee")
        assert cmd[ai + 1] == "fast-worker"
        ki = cmd.index("--idempotency-key")
        assert cmd[ki + 1].startswith("saga:/tmp/repo:m9:")
    assert calls[-1][calls[-1].index("--idempotency-key") + 1].endswith("__convergence__")
