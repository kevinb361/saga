"""End-to-end saga-lint checks for the public example and durable fixtures."""

import ast
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "bin" / "saga-lint"
EXAMPLE = ROOT / "examples" / "minimal"
VALID_FIXTURE = ROOT / "tests" / "fixtures" / "saga_lint" / "valid"
INVALID_FIXTURE = ROOT / "tests" / "fixtures" / "saga_lint" / "invalid"
FINDING_CASES = ROOT / "tests" / "fixtures" / "saga_lint" / "finding_cases.json"


def production_finding_contract():
    tree = ast.parse(SCRIPT.read_text())
    registry = None
    constructed = set()
    direct_constructors = set()
    helper_constructors = set()

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "FINDING_CODES"
                for target in node.targets
            )
            and isinstance(node.value, ast.Call)
        ):
            registry = set(ast.literal_eval(node.value.args[0]))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_finding"
            and node.args
            and isinstance(node.args[0], ast.Constant)
        ):
            constructed.add(node.args[0].value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Finding"
        ):
            direct_constructors.add(node.lineno)
        if isinstance(node, ast.FunctionDef) and node.name == "_finding":
            helper_constructors.update(
                child.lineno
                for child in ast.walk(node)
                if isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "Finding"
            )

    assert registry is not None, "production FINDING_CODES registry is missing"
    return registry, constructed, direct_constructors, helper_constructors


def run_lint(path, output_format="human"):
    return subprocess.run(
        [str(SCRIPT), "--format", output_format, str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_minimal_example_is_clean_and_demonstrates_record_states():
    result = run_lint(EXAMPLE)
    requirements = (EXAMPLE / ".planning" / "REQUIREMENTS.md").read_text()
    traceability = (EXAMPLE / ".planning" / "TRACEABILITY.md").read_text()

    assert result.returncode == 0, result.stdout + result.stderr
    assert "- [x] **REQ-001**" in requirements
    assert "- [x] **REQ-002**" in requirements
    assert "- [ ] **REQ-003**" in requirements
    assert "**PROVEN**" in traceability
    assert "**OPEN**" in traceability
    assert (EXAMPLE / ".planning" / "decisions" / "0001-output-format.md").is_file()


def test_positive_fixture_is_clean():
    result = run_lint(VALID_FIXTURE, "json")

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["findings"] == []


def test_negative_fixture_has_expected_stable_findings():
    result = run_lint(INVALID_FIXTURE, "json")

    assert result.returncode == 1, result.stdout + result.stderr
    codes = [finding["code"] for finding in json.loads(result.stdout)["findings"]]
    assert codes == ["REQ_DUPLICATE", "LINK_LOCAL_MISSING"]


def test_durable_cases_pin_every_stable_finding_code(tmp_path):
    cases = json.loads(FINDING_CASES.read_text())
    registry, constructed, direct_constructors, helper_constructors = (
        production_finding_contract()
    )
    covered = set()

    for case in cases:
        project = tmp_path / case["name"]
        project.mkdir()
        if case.get("files") is not None:
            planning = project / ".planning"
            planning.mkdir()
            for name, content in case["files"].items():
                (planning / name).write_text(content)

        result = run_lint(project, "json")
        assert result.returncode == case.get("expected_exit", 1), (
            case["name"] + result.stdout + result.stderr
        )
        actual = [finding["code"] for finding in json.loads(result.stdout)["findings"]]
        assert actual == case["expected_codes"], case["name"]
        covered.update(actual)

    assert constructed == registry
    assert covered == registry
    assert direct_constructors == helper_constructors
    assert len(direct_constructors) == 1


def test_readme_documents_lint_formats_exits_and_example():
    readme = (ROOT / "README.md").read_text()

    assert "bin/saga-lint" in readme
    assert "--format json" in readme
    assert "Exit codes: `0` clean, `1` findings, `2` invocation or parser failure." in readme
    assert "missing Saga spine" in readme
    assert "examples/minimal" in readme


def test_lint_spine_make_target_skips_export_without_private_planning(tmp_path):
    result = subprocess.run(
        ["make", "-f", str(ROOT / "Makefile"), "lint-spine"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_close_out_auditor_log_is_gitignored():
    assert ".planning/.close-out-auditor.log" in (ROOT / ".gitignore").read_text().splitlines()
    if not (ROOT / ".git").exists():
        return

    result = subprocess.run(
        ["git", "check-ignore", ".planning/.close-out-auditor.log"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == ".planning/.close-out-auditor.log"
