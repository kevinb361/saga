import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK_DIR = ROOT / "skills" / "saga" / "saga-check"
WRAPPER = CHECK_DIR / "scripts" / "run-lint.sh"
FIXTURES = ROOT / "tests" / "fixtures" / "saga_lint"


def skill_text() -> str:
    return (CHECK_DIR / "SKILL.md").read_text(encoding="utf-8")


def reference_text() -> str:
    return (CHECK_DIR / "reference.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    return match.group(1)


def run_wrapper(target: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(WRAPPER), str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_saga_check_exposes_two_separate_lanes_and_costs() -> None:
    text = skill_text()
    metadata = frontmatter(text)

    assert re.search(r"^name: saga-check$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: false$", metadata, re.MULTILINE)
    assert "## Structure lane — deterministic" in text
    assert "## Evidence lane — requirement traceability" in text
    assert "deterministic local executable, inspect-only, no model judgment" in text
    assert "model-assisted repository cross-reference" in text
    assert "rewrites `.planning/TRACEABILITY.md`" in text


def test_saga_check_stops_evidence_when_structure_is_red() -> None:
    text = skill_text()

    assert "Evidence never skips the structural prerequisite" in text
    assert "stop without rewriting traceability" in text
    assert "semantic classification against malformed records is unreliable" in text


def test_saga_check_preserves_evidence_classifications_and_markers() -> None:
    text = skill_text()
    reference = reference_text()

    assert "Treat `[x]` and `[/]` as claimed done" in text
    for status in ("PROVEN", "ASSERTED", "OPEN", "WAIVED"):
        assert f"**{status}**" in text
        assert status in reference
    assert "every requirement exactly once" in text
    assert "status in the third data column" in text


def test_saga_check_never_claims_audit_authority() -> None:
    text = skill_text()

    assert "That remains `saga-audit`" in text
    assert "never writes `AUDIT.md`" in text
    assert "never issues PASS/CONDITIONAL/FAIL" in text
    assert "never flips ROADMAP or closes a milestone" in text
    assert "capability alone does not make the executor independent" in text


def test_saga_check_wrapper_is_executable_and_valid_shell() -> None:
    assert os.access(WRAPPER, os.X_OK)
    subprocess.run(["bash", "-n", str(WRAPPER)], check=True)


def test_saga_check_wrapper_preserves_lint_exit_contract(tmp_path: Path) -> None:
    clean = run_wrapper(FIXTURES / "valid")
    findings = run_wrapper(FIXTURES / "invalid")
    missing = run_wrapper(tmp_path / "missing")

    assert clean.returncode == 0
    assert findings.returncode == 1
    assert missing.returncode == 2
