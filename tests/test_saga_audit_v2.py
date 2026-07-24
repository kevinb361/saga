import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "skills" / "saga" / "saga-audit"
RUN_DIR = ROOT / "skills" / "saga" / "saga-run"


def audit_skill() -> str:
    return (AUDIT_DIR / "SKILL.md").read_text(encoding="utf-8")


def audit_reference() -> str:
    return (AUDIT_DIR / "reference.md").read_text(encoding="utf-8")


def run_reference() -> str:
    return (RUN_DIR / "reference.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    return match.group(1)


def squished(text: str) -> str:
    return " ".join(text.split())


def test_saga_audit_remains_separate_explicit_frontier_judgment() -> None:
    text = audit_skill()
    metadata = frontmatter(text)

    assert re.search(r"^name: saga-audit$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: true$", metadata, re.MULTILINE)
    assert "fresh frontier-capable context" in text
    assert "This is the judgment layer — not `saga-check` traceability" in text
    for pillar in ("Correctness", "Safety", "Test coverage", "Architecture fit", "Operability"):
        assert f"**{pillar}:**" in text


def test_saga_audit_refuses_same_executor_and_never_flips() -> None:
    text = audit_skill()

    assert "Model capability alone does not create independence" in text
    assert "If the current context executed any reviewed slice" in text
    assert "stop without writing `AUDIT.md`" in text
    assert "fail closed rather than self-certify" in text
    assert "`saga-audit` never flips ROADMAP" in text
    assert "leaves the milestone open" in text


def test_close_out_order_is_check_then_audit_then_flip() -> None:
    reference = run_reference()
    check_position = reference.index("independent frontier context runs saga-check")
    audit_position = reference.index("independent frontier context runs saga-audit")
    flip_position = reference.index("flip the ROADMAP marker", audit_position)

    assert check_position < audit_position < flip_position
    assert "`saga-audit` itself never flips completion state" in audit_reference()


def test_failed_or_incomplete_auditor_leaves_roadmap_unflipped() -> None:
    reference = squished(run_reference())

    assert "exit code 0 AND that BOTH `TRACEABILITY.md` AND `AUDIT.md` were" in reference
    assert "STOP the close-out" in reference
    assert "leave the ROADMAP UNflipped" in reference
    assert "NEVER run `saga-check` or `saga-audit` yourself as a fallback" in reference
