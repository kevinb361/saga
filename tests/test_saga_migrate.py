"""Behavior tests for the dry-run-first legacy spine migrator."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parents[1]
MIGRATE = ROOT / "bin" / "saga-migrate"
LINT = ROOT / "bin" / "saga-lint"


def make_legacy_spine(root: Path) -> Path:
    planning = root / ".planning"
    planning.mkdir()
    (planning / "STATE.md").write_text(
        """---
gsd_state_version: 1.0
milestone: v0.1
milestone_name: Legacy migration
status: milestone_drained
last_updated: "2026-01-01T00:00:00Z"
last_activity: fixture
---

# state
"""
    )
    (planning / "ROADMAP.md").write_text(
        "# roadmap\n\n## Milestones\n\n🚧 **v0.1 Legacy migration** — fixture\n"
    )
    (planning / "REQUIREMENTS.md").write_text(
        """# Requirements: fixture — Milestone v0.1 Legacy migration

## Behavior

- [/] LEGACY-01: Existing behavior remains proven.
"""
    )
    (planning / "TRACEABILITY.md").write_text(
        """# traceability

| REQ-ID | Status | Evidence |
|---|---|---|
| LEGACY-01 | PROVEN | fixture |
"""
    )
    return planning


def run_migrate(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, MIGRATE, str(root), *args],
        capture_output=True,
        text=True,
    )


def test_dry_run_previews_changes_without_mutating(tmp_path):
    planning = make_legacy_spine(tmp_path)
    before = {path.name: path.read_bytes() for path in planning.iterdir()}

    result = run_migrate(tmp_path)

    assert result.returncode == 1
    assert "dry-run: 4 file(s) would change" in result.stdout
    assert "**LEGACY-01** — Existing behavior remains proven. (milestone: v0.1)" in result.stdout
    assert {path.name: path.read_bytes() for path in planning.iterdir()} == before


def test_write_normalizes_legacy_spine_until_saga_lint_is_clean(tmp_path):
    planning = make_legacy_spine(tmp_path)

    result = run_migrate(tmp_path, "--write")

    assert result.returncode == 0, result.stderr
    assert "updated: 4 file(s)" in result.stdout
    assert "saga_state_version: 1.0" in (planning / "STATE.md").read_text()
    assert "status: complete" in (planning / "STATE.md").read_text()
    assert "- 🚧 **v0.1 Legacy migration**" in (planning / "ROADMAP.md").read_text()
    assert "- [/] **LEGACY-01** — Existing behavior remains proven. (milestone: v0.1)" in (
        planning / "REQUIREMENTS.md"
    ).read_text()
    assert "| LEGACY-01 |  | PROVEN | fixture |" in (planning / "TRACEABILITY.md").read_text()

    lint = subprocess.run(
        [sys.executable, LINT, str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert lint.returncode == 0, lint.stdout + lint.stderr


def test_clean_spine_is_a_noop(tmp_path):
    make_legacy_spine(tmp_path)
    assert run_migrate(tmp_path, "--write").returncode == 0
    before = {path.name: path.read_bytes() for path in (tmp_path / ".planning").iterdir()}

    result = run_migrate(tmp_path)

    assert result.returncode == 0
    assert "clean: no deterministic migrations available" in result.stdout
    assert {path.name: path.read_bytes() for path in (tmp_path / ".planning").iterdir()} == before


def test_future_saga_state_version_is_not_silently_downgraded(tmp_path):
    planning = make_legacy_spine(tmp_path)
    state = (planning / "STATE.md").read_text().replace(
        "gsd_state_version: 1.0", "saga_state_version: 2.0"
    )
    (planning / "STATE.md").write_text(state)

    result = run_migrate(tmp_path, "--write")

    assert result.returncode == 0, result.stderr
    assert "saga_state_version: 2.0" in (planning / "STATE.md").read_text()


def test_partial_legacy_spine_migrates_files_that_are_present(tmp_path):
    planning = make_legacy_spine(tmp_path)
    (planning / "TRACEABILITY.md").unlink()

    result = run_migrate(tmp_path, "--write")

    assert result.returncode == 0, result.stderr
    assert "updated: 3 file(s)" in result.stdout
    assert "**LEGACY-01** — Existing behavior remains proven." in (
        planning / "REQUIREMENTS.md"
    ).read_text()


def test_milestone_tag_is_inserted_before_legacy_evidence_metadata(tmp_path):
    planning = make_legacy_spine(tmp_path)
    (planning / "REQUIREMENTS.md").write_text(
        """# Requirements: fixture — Milestone v0.1 Legacy migration

- [/] LEGACY-01: Existing behavior remains proven. (evidence: fixture)
"""
    )

    result = run_migrate(tmp_path, "--write")

    assert result.returncode == 0, result.stderr
    requirement = (planning / "REQUIREMENTS.md").read_text()
    assert "(milestone: v0.1) (evidence: fixture)" in requirement
    lint = subprocess.run([sys.executable, LINT, str(tmp_path)], capture_output=True, text=True)
    assert lint.returncode == 0, lint.stdout + lint.stderr


def test_legacy_state_and_trace_statuses_map_without_inventing_proof(tmp_path):
    planning = make_legacy_spine(tmp_path)
    (planning / "STATE.md").write_text(
        (planning / "STATE.md")
        .read_text()
        .replace("gsd_state_version: 1.0", "saga_state_version: 1")
        .replace("status: milestone_drained", "status: planning")
    )
    (planning / "REQUIREMENTS.md").write_text(
        """# requirements

## Requirements

- [x] **REQ-001** — done (milestone: v0.1)
- [ ] **REQ-002** — deferred (milestone: v0.1)
- [ ] **REQ-003** — superseded (milestone: v0.1)
"""
    )
    (planning / "TRACEABILITY.md").write_text(
        """| REQ-ID | Description | Status | Evidence |
|---|---|---|---|
| REQ-001 | done | DONE | fixture |
| REQ-002 | deferred | DEFERRED | fixture |
| REQ-003 | superseded | **SUPERSEDED** | fixture |
"""
    )

    result = run_migrate(tmp_path, "--write")

    assert result.returncode == 0, result.stderr
    assert "saga_state_version: 1.0" in (planning / "STATE.md").read_text()
    assert "status: idle" in (planning / "STATE.md").read_text()
    trace = (planning / "TRACEABILITY.md").read_text()
    assert "| REQ-001 | done | ASSERTED | fixture |" in trace
    assert "| REQ-002 | deferred | OPEN | fixture |" in trace
    assert "| REQ-003 | superseded | WAIVED | fixture |" in trace

    lint = subprocess.run([sys.executable, LINT, str(tmp_path)], capture_output=True, text=True)
    assert lint.returncode == 0, lint.stdout + lint.stderr
