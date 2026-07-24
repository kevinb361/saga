import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = ROOT / "skills" / "ops"


def skill_text(name: str) -> str:
    return (OPS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    return match.group(1)


def test_ops_grill_me_metadata_is_explicit_only() -> None:
    text = skill_text("ops-grill-me")
    metadata = frontmatter(text)

    assert re.search(r"^name: ops-grill-me$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: true$", metadata, re.MULTILINE)
    assert "explicitly asks to be questioned or challenged" in metadata


def test_ops_grill_me_pins_bounded_inspect_first_process() -> None:
    text = skill_text("ops-grill-me")

    assert "**Inspect before asking.**" in text
    assert "Ask at most five high-value questions at a time" in text
    assert "Stop after three rounds unless the operator explicitly asks to continue" in text
    assert "## Mutation boundary" in text
    assert "read-only by default" in text
    assert ".planning/" not in text


def test_ops_grill_me_handoff_has_all_required_fields() -> None:
    text = skill_text("ops-grill-me")

    for field in ("Goal", "Constraints", "Decisions", "Unknowns", "Next action"):
        assert f"- **{field}**" in text


def test_ops_troubleshoot_metadata_is_auto_invocable() -> None:
    metadata = frontmatter(skill_text("ops-troubleshoot"))

    assert re.search(r"^name: ops-troubleshoot$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: false$", metadata, re.MULTILINE)
    for domain in ("code", "configuration", "service", "host", "network"):
        assert domain in metadata


def test_ops_troubleshoot_pins_evidence_and_hypothesis_loop() -> None:
    text = skill_text("ops-troubleshoot")

    assert "**Gather read-only evidence first.**" in text
    assert "**Build a ranked hypothesis ledger.**" in text
    assert "the result that would falsify it" in text
    assert "Keep no more than three active hypotheses" in text
    assert "**Apply the smallest coherent remediation.**" in text


def test_ops_troubleshoot_pins_risk_gate_and_fresh_verification() -> None:
    text = skill_text("ops-troubleshoot")

    for risk in ("inspect-only", "repo-only", "live-mutation", "destructive"):
        assert f"`{risk}`" in text
    assert "stop unless the operator has approved that bounded mutation" in text
    assert "Re-run the original reproduction" in text
    assert "original live-health signal" in text
    assert "no Saga dependency" in text


def test_ops_review_is_explicit_and_read_only() -> None:
    text = skill_text("ops-review")
    metadata = frontmatter(text)

    assert re.search(r"^name: ops-review$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: true$", metadata, re.MULTILINE)
    assert "Remain read-only" in text
    assert "This is not `saga-audit`" in text
    assert "no Saga dependency" in text


def test_ops_review_always_applies_correctness_and_operability() -> None:
    text = skill_text("ops-review")

    assert "Always apply and report both" in text
    assert "**Correctness:**" in text
    assert "**Operability:**" in text
    assert "Lenses applied:" in text


def test_ops_review_preserves_security_and_adversarial_evidence() -> None:
    text = skill_text("ops-review")

    assert "**Security:**" in text
    assert "protected assets, actors, attacker-controlled inputs" in text
    assert "plausible exploit path and required preconditions" in text
    assert "**Adversarial:**" in text
    assert "attempt to falsify them with concrete sequences" in text
    assert "claims that survived" in text
    for field in ("severity", "path:line", "specific remediation", "prove the remediation"):
        assert field in text


def test_ops_upgrade_covers_operator_upgrade_classes() -> None:
    text = skill_text("ops-upgrade")
    metadata = frontmatter(text)

    assert re.search(r"^name: ops-upgrade$", metadata, re.MULTILINE)
    for upgrade_class in (
        "application dependencies",
        "OS packages",
        "containers",
        "services",
        "runtimes",
        "collections",
        "toolchains",
    ):
        assert upgrade_class in metadata


def test_ops_upgrade_requires_authoritative_staging_and_rollback() -> None:
    text = skill_text("ops-upgrade")

    assert "**Research authoritative sources.**" in text
    assert "release notes, migration guides, security advisories, compatibility matrices" in text
    assert "**Establish baseline and rollback.**" in text
    assert "**Plan coherent stages.**" in text
    assert "rollback trigger" in text


def test_ops_upgrade_gates_mutation_and_proves_version_and_health() -> None:
    text = skill_text("ops-upgrade")

    for risk in ("inspect-only", "repo-only", "live-mutation", "destructive"):
        assert f"`{risk}`" in text
    assert "stop unless that bounded mutation is explicitly approved" in text
    assert "Prove the installed or resolved version" in text
    assert "A successful installer exit is not health proof" in text
    assert "no Saga dependency" in text


def test_ops_document_is_reader_first_and_portable() -> None:
    text = skill_text("ops-document")
    metadata = frontmatter(text)

    assert re.search(r"^name: ops-document$", metadata, re.MULTILINE)
    assert "Choose the destination before writing" in text
    assert "When no Saga spine exists" in text
    assert "no Saga dependency" in text
    assert "Organize around the reader's path" in text


def test_ops_document_preserves_saga_record_safeguards() -> None:
    text = skill_text("ops-document")

    assert "preserve frontmatter plus unrelated content byte-for-byte" in text
    assert "only when **all three** criteria hold" in text
    assert "single glossary/context source" in text
    assert "never rewrite or reorder existing lessons" in text
    assert "never record planned or assumed behavior as current truth" in text
    assert "do not self-certify by prose" in text


def test_ops_document_limits_mutation_and_public_data() -> None:
    text = skill_text("ops-document")

    assert "does not authorize file edits" in text
    assert "only the named or confirmed destination" in text
    assert "Do not opportunistically rewrite" in text
    assert "Keep private details, credentials, internal addresses" in text
    assert "diff limited to the requested destination" in text
