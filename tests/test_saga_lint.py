"""Tests for bin/saga-lint spine discovery and finding model (REQ-051)."""

from pathlib import Path
import json
import re
import subprocess
import sys
from types import ModuleType


SCRIPT = Path(__file__).parents[1] / "bin" / "saga-lint"
SPINE_FILES = ("STATE.md", "ROADMAP.md", "REQUIREMENTS.md", "TRACEABILITY.md")
VALID_STATE = """---
saga_state_version: 1.0
milestone: v0.0-test
milestone_name: Test
status: active
last_updated: "2026-01-01T00:00:00Z"
last_activity: fixture

# state
"""


def load_lint_module():
    module = ModuleType("saga_lint")
    module.__file__ = str(SCRIPT)
    sys.modules[module.__name__] = module
    source = SCRIPT.read_text()
    exec(compile(source, str(SCRIPT), "exec"), module.__dict__)
    return module


def make_spine(root):
    planning = root / ".planning"
    planning.mkdir()
    for name in SPINE_FILES:
        (planning / name).write_text(f"# {name}\n")
    (planning / "STATE.md").write_text(VALID_STATE)
    return planning


def snapshot_tree(root):
    return {
        path.relative_to(root): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def test_inspect_spine_from_explicit_project_path_returns_structured_result(tmp_path):
    planning = make_spine(tmp_path)
    module = load_lint_module()

    result = module.inspect_spine(tmp_path)

    assert result.project_root == tmp_path.resolve()
    assert result.planning_dir == planning.resolve()
    assert result.findings == ()
    assert result.files == {
        name: (planning / name).resolve()
        for name in SPINE_FILES
    }


def test_inspect_spine_defaults_to_current_directory(tmp_path, monkeypatch):
    planning = make_spine(tmp_path)
    monkeypatch.chdir(tmp_path)
    module = load_lint_module()

    result = module.inspect_spine()

    assert result.project_root == tmp_path.resolve()
    assert result.planning_dir == planning.resolve()
    assert result.findings == ()


def test_missing_spine_returns_a_structured_finding(tmp_path):
    module = load_lint_module()

    result = module.inspect_spine(tmp_path)

    assert result.files == {}
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.code == "SPINE_NOT_FOUND"
    assert finding.severity == "error"
    assert finding.path == (tmp_path / ".planning").resolve()
    assert finding.line is None
    assert finding.message == "Saga spine directory not found"


def test_cli_default_path_does_not_mutate_the_spine(tmp_path):
    planning = make_spine(tmp_path)
    before = snapshot_tree(planning)

    result = subprocess.run(
        [sys.executable, SCRIPT],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert f"Saga spine: {planning.resolve()}" in result.stdout
    assert snapshot_tree(planning) == before


def inspect_requirements(tmp_path, lines):
    planning = make_spine(tmp_path)
    lines = [line.replace("(milestone: test)", "(milestone: v0.0-test)") for line in lines]
    (planning / "REQUIREMENTS.md").write_text(
        "# requirements\n\n## Requirements\n\n" + "\n".join(lines) + "\n"
    )
    has_valid_requirement = any(
        re.match(r"^- \[([ x/])\] \*\*(REQ-\d{3})\*\*", line) for line in lines
    )
    roadmap_marker = "🚧" if has_valid_requirement else "✅"
    (planning / "ROADMAP.md").write_text(
        f"# roadmap\n\n## Milestones\n\n- {roadmap_marker} **v0.0 Test** — fixture\n"
    )
    rows = []
    for line in lines:
        match = re.match(r"^- \[([ x/])\] \*\*(REQ-\d{3})\*\*", line)
        if match and match.group(2) not in {row[0] for row in rows}:
            status = "PROVEN" if match.group(1) in {"x", "/"} else "OPEN"
            rows.append((match.group(2), status))
    (planning / "TRACEABILITY.md").write_text(
        "# traceability\n\n| Requirement | Description | Status | Evidence |\n"
        "|---|---|---|---|\n"
        + "".join(f"| {req_id} | fixture | **{status}** | fixture |\n" for req_id, status in rows)
    )
    return load_lint_module().inspect_spine(tmp_path)


def finding_codes(result):
    return [finding.code for finding in result.findings]


def test_duplicate_requirement_id_reports_second_line(tmp_path):
    result = inspect_requirements(
        tmp_path,
        [
            "- [ ] **REQ-001** — first (milestone: test)",
            "- [x] **REQ-001** — duplicate (milestone: test)",
        ],
    )

    assert finding_codes(result) == ["REQ_DUPLICATE"]
    assert result.findings[0].line == 6


def test_malformed_requirement_id_is_reported(tmp_path):
    result = inspect_requirements(
        tmp_path,
        ["- [ ] **REQ-12** — malformed (milestone: test)"],
    )

    assert finding_codes(result) == ["REQ_ID_MALFORMED"]
    assert result.findings[0].line == 5


def test_unsupported_checkbox_marker_is_reported(tmp_path):
    result = inspect_requirements(
        tmp_path,
        ["- [?] **REQ-001** — unsupported marker (milestone: test)"],
    )

    assert finding_codes(result) == ["REQ_MARKER_UNSUPPORTED"]
    assert result.findings[0].line == 5


def test_unknown_requirement_dependency_is_reported(tmp_path):
    result = inspect_requirements(
        tmp_path,
        ["- [ ] **REQ-001** — unknown dep (milestone: test) (depends: REQ-999)"],
    )

    assert finding_codes(result) == ["REQ_DEP_UNKNOWN"]
    assert result.findings[0].line == 5


def test_requirement_dependency_cycle_is_reported(tmp_path):
    result = inspect_requirements(
        tmp_path,
        [
            "- [ ] **REQ-001** — first (milestone: test) (depends: REQ-002)",
            "- [ ] **REQ-002** — second (milestone: test) (depends: REQ-001)",
        ],
    )

    assert finding_codes(result) == ["REQ_DEP_CYCLE"]
    assert result.findings[0].line == 5


def test_contradictory_dependency_declaration_is_reported(tmp_path):
    result = inspect_requirements(
        tmp_path,
        [
            "- [ ] **REQ-001** — contradiction (milestone: test) "
            "(depends: none, REQ-002)",
            "- [ ] **REQ-002** — other (milestone: test) (depends: none)",
        ],
    )

    assert finding_codes(result) == ["REQ_DEP_CONTRADICTION"]
    assert result.findings[0].line == 5


def test_dependency_syntax_in_title_is_not_a_declaration(tmp_path):
    result = inspect_requirements(
        tmp_path,
        [
            "- [x] **REQ-001** — documents `(depends: none|REQ-…)` syntax "
            "(milestone: test)"
        ],
    )

    assert finding_codes(result) == []


def inspect_traceability(tmp_path, requirement_lines, traceability_rows):
    planning = make_spine(tmp_path)
    requirement_lines = [
        line.replace("(milestone: test)", "(milestone: v0.0-test)")
        for line in requirement_lines
    ]
    (planning / "REQUIREMENTS.md").write_text(
        "# requirements\n\n## Requirements\n\n" + "\n".join(requirement_lines) + "\n"
    )
    (planning / "TRACEABILITY.md").write_text(
        "# traceability\n\n| Requirement | Description | Status | Evidence |\n"
        "|---|---|---|---|\n"
        + "\n".join(traceability_rows)
        + "\n"
    )
    (planning / "ROADMAP.md").write_text(
        "# roadmap\n\n## Milestones\n\n- 🚧 **v0.0 Test** — fixture\n"
    )
    return load_lint_module().inspect_spine(tmp_path)


def test_missing_traceability_row_is_reported_at_requirement(tmp_path):
    result = inspect_traceability(
        tmp_path,
        ["- [ ] **REQ-001** — missing trace row (milestone: test)"],
        [],
    )

    assert finding_codes(result) == ["TRACE_REQ_MISSING"]
    assert result.findings[0].path.name == "REQUIREMENTS.md"
    assert result.findings[0].line == 5


def test_malformed_traceability_status_is_reported_at_trace_row(tmp_path):
    result = inspect_traceability(
        tmp_path,
        ["- [ ] **REQ-001** — malformed trace status (milestone: test)"],
        ["| REQ-001 | fixture | **DONE** | fixture |"],
    )

    assert finding_codes(result) == ["TRACE_STATUS_MALFORMED"]
    assert result.findings[0].path.name == "TRACEABILITY.md"
    assert result.findings[0].line == 5


def test_duplicate_traceability_row_is_reported(tmp_path):
    row = "| REQ-001 | fixture | **OPEN** | fixture |"
    result = inspect_traceability(
        tmp_path,
        ["- [ ] **REQ-001** — duplicate trace row (milestone: test)"],
        [row, row],
    )

    assert finding_codes(result) == ["TRACE_REQ_DUPLICATE"]
    assert result.findings[0].path.name == "TRACEABILITY.md"
    assert result.findings[0].line == 6


def test_unknown_traceability_requirement_is_reported(tmp_path):
    result = inspect_traceability(
        tmp_path,
        ["- [ ] **REQ-001** — known (milestone: test)"],
        [
            "| REQ-001 | fixture | **OPEN** | fixture |",
            "| REQ-999 | fixture | **OPEN** | fixture |",
        ],
    )

    assert finding_codes(result) == ["TRACE_REQ_UNKNOWN"]
    assert result.findings[0].line == 6


def test_done_requirement_classified_open_is_reported(tmp_path):
    result = inspect_traceability(
        tmp_path,
        ["- [x] **REQ-001** — done (milestone: test)"],
        ["| REQ-001 | fixture | **OPEN** | fixture |"],
    )

    assert finding_codes(result) == ["TRACE_DONE_OPEN"]
    assert result.findings[0].line == 5


def inspect_roadmap(tmp_path, requirement_lines, roadmap_lines):
    trace_rows = []
    for line in requirement_lines:
        match = re.match(r"^- \[([ x/])\] \*\*(REQ-\d{3})\*\*", line)
        assert match
        status = "PROVEN" if match.group(1) in {"x", "/"} else "OPEN"
        trace_rows.append(f"| {match.group(2)} | fixture | **{status}** | fixture |")
    inspect_traceability(tmp_path, requirement_lines, trace_rows)
    (tmp_path / ".planning" / "ROADMAP.md").write_text(
        "# roadmap\n\n## Milestones\n\n" + "\n".join(roadmap_lines) + "\n"
    )
    return load_lint_module().inspect_spine(tmp_path)


def test_shipped_milestone_with_open_requirement_is_reported(tmp_path):
    result = inspect_roadmap(
        tmp_path,
        ["- [ ] **REQ-001** — open (milestone: v1.0-test)"],
        ["- ✅ **v1.0 Test** — shipped"],
    )

    assert finding_codes(result) == ["ROADMAP_SHIPPED_OPEN"]
    assert result.findings[0].line == 5


def test_active_milestone_without_requirements_is_reported(tmp_path):
    result = inspect_roadmap(
        tmp_path,
        [],
        ["- 🚧 **v1.0 Empty** — active"],
    )

    assert finding_codes(result) == ["ROADMAP_ACTIVE_EMPTY"]
    assert result.findings[0].line == 5


def test_unresolved_requirement_milestone_tag_is_reported(tmp_path):
    result = inspect_roadmap(
        tmp_path,
        [
            "- [ ] **REQ-001** — known (milestone: v1.0-project-health)",
            "- [ ] **REQ-002** — unknown (milestone: v9.9-nope)",
        ],
        ["- 🚧 **v1.0 Project health** — active"],
    )

    assert finding_codes(result) == ["ROADMAP_MILESTONE_UNKNOWN"]
    assert result.findings[0].path.name == "REQUIREMENTS.md"
    assert result.findings[0].line == 6


def test_version_and_name_slug_resolves_roadmap_milestone(tmp_path):
    result = inspect_roadmap(
        tmp_path,
        ["- [ ] **REQ-001** — known (milestone: V1.0-Project_Health!)"],
        ["- 🚧 **v1.0 Project health** — active"],
    )

    assert finding_codes(result) == []


def test_missing_required_state_frontmatter_key_is_reported(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "STATE.md").write_text(VALID_STATE.replace("milestone_name: Test\n", ""))

    result = load_lint_module().inspect_spine(tmp_path)

    assert finding_codes(result) == ["STATE_FRONTMATTER_MISSING"]
    assert result.findings[0].path.name == "STATE.md"
    assert result.findings[0].line == 1


def test_invalid_state_frontmatter_value_is_reported(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "STATE.md").write_text(VALID_STATE.replace("status: active", "status: surprising"))

    result = load_lint_module().inspect_spine(tmp_path)

    assert finding_codes(result) == ["STATE_FRONTMATTER_INVALID"]
    assert result.findings[0].line == 5


def test_invalid_state_timestamp_is_reported(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "STATE.md").write_text(
        VALID_STATE.replace('last_updated: "2026-01-01T00:00:00Z"', "last_updated: yesterday")
    )

    result = load_lint_module().inspect_spine(tmp_path)

    assert finding_codes(result) == ["STATE_FRONTMATTER_INVALID"]
    assert result.findings[0].line == 6


def test_broken_local_markdown_link_is_reported(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "ROADMAP.md").write_text("# roadmap\n\n[missing](MISSING.md)\n")

    result = load_lint_module().inspect_spine(tmp_path)

    assert finding_codes(result) == ["LINK_LOCAL_MISSING"]
    assert result.findings[0].path.name == "ROADMAP.md"
    assert result.findings[0].line == 3


def test_external_markdown_link_is_not_followed(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "ROADMAP.md").write_text(
        "# roadmap\n\n[remote](https://example.invalid/definitely-missing)\n"
    )

    result = load_lint_module().inspect_spine(tmp_path)

    assert finding_codes(result) == []


def test_human_output_includes_stable_code_and_source_line(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "REQUIREMENTS.md").write_text(
        "# requirements\n\n## Requirements\n\n- [ ] **REQ-12** — malformed\n"
    )

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)], text=True, capture_output=True, check=False
    )

    assert result.returncode == 1
    assert "ERROR REQ_ID_MALFORMED" in result.stdout
    assert "REQUIREMENTS.md:5" in result.stdout


def test_json_output_is_versioned_and_deterministic_when_clean(tmp_path):
    make_spine(tmp_path)

    first = subprocess.run(
        [str(SCRIPT), "--format", "json", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    second = subprocess.run(
        [str(SCRIPT), "--format", "json", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(first.stdout)
    assert first.returncode == 0
    assert first.stdout == second.stdout
    assert payload["schema_version"] == "1.0"
    assert payload["clean"] is True
    assert payload["findings"] == []


def test_json_findings_preserve_code_line_and_exit_one(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "ROADMAP.md").write_text("# roadmap\n\n[missing](MISSING.md)\n")

    result = subprocess.run(
        [str(SCRIPT), "--format", "json", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["clean"] is False
    assert payload["findings"][0]["code"] == "LINK_LOCAL_MISSING"
    assert payload["findings"][0]["line"] == 3


def test_invalid_output_format_exits_two(tmp_path):
    make_spine(tmp_path)

    result = subprocess.run(
        [str(SCRIPT), "--format", "yaml", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2


def test_invalid_utf8_exercises_handled_parser_failure_exit_two(tmp_path):
    planning = make_spine(tmp_path)
    (planning / "REQUIREMENTS.md").write_bytes(b"\xff")

    result = subprocess.run(
        [str(SCRIPT), str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "saga-lint:" in result.stderr
    assert "codec can't decode" in result.stderr


def test_oserror_exercises_handled_parser_failure_exit_two(monkeypatch, capsys):
    module = load_lint_module()

    def fail_inspection(_path):
        raise OSError("fixture read denied")

    monkeypatch.setattr(module, "inspect_spine", fail_inspection)

    assert module.main(["."]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "saga-lint: fixture read denied\n"
