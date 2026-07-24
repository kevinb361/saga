import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAGA_ROOT = ROOT / "skills" / "saga"


def skill_text(name: str) -> str:
    return (SAGA_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    return match.group(1)


def test_saga_init_is_explicit_and_respects_native_projects() -> None:
    text = skill_text("saga-init")
    metadata = frontmatter(text)

    assert re.search(r"^name: saga-init$", metadata, re.MULTILINE)
    assert re.search(r"^disable-model-invocation: true$", metadata, re.MULTILINE)
    assert "project without `.planning/` is not broken" in text
    assert "never a reason to create a spine automatically" in text
    assert "Inspect the native project first" in text


def test_saga_init_detects_gate_without_live_side_effects() -> None:
    text = skill_text("saga-init")

    assert "**Detect the mechanical gate.**" in text
    assert "`make ci` when defined" in text
    assert "Detection is read-only" in text
    assert "Do not install dependencies, refresh indexes, fetch the network" in text
    assert "`gate: null`" in text


def test_saga_init_is_minimal_idempotent_and_non_inventive() -> None:
    text = skill_text("saga-init")

    for record in ("STATE.md", "ROADMAP.md", "REQUIREMENTS.md", "TRACEABILITY.md"):
        assert f"`{record}`" in text
    assert "Do not reinitialize, rewrite, normalize, or downgrade" in text
    assert "second pass changes nothing" in text
    assert "Do not decompose it into requirements" in text
    assert (
        "Do not create decision, retrospective, context, specification, audit, phase"
        in text
    )


def test_saga_plan_is_intent_driven_and_does_not_bootstrap() -> None:
    text = skill_text("saga-plan")
    metadata = frontmatter(text)

    assert re.search(r"^name: saga-plan$", metadata, re.MULTILINE)
    assert "Plan the work the operator means, not a CRUD transaction" in text
    assert "suggest explicit `saga-init`; do not bootstrap implicitly" in text
    assert "Do not implement the planned work" in text


def test_saga_plan_pins_observable_requirements_dependencies_and_proof() -> None:
    text = skill_text("saga-plan")

    assert "**Choose observable milestones.**" in text
    assert "append-only stable REQ IDs" in text
    assert "**Name proof before execution.**" in text
    assert "new requirements remain `[ ]` and OPEN" in text
    assert "**Model only real dependencies.**" in text
    assert "Reject unknown IDs, self-dependencies, and cycles" in text
    assert "Safety prose without a gate is not a safety invariant" in text


def test_saga_plan_keeps_a_flat_non_exhaustive_spine() -> None:
    text = skill_text("saga-plan")

    for record in ("ROADMAP.md", "REQUIREMENTS.md", "TRACEABILITY.md", "STATE.md"):
        assert f"`{record}`" in text
    assert "Do not create `.planning/phases/`" in text
    assert "generated planning exhaust" in text
    assert "Never mark done without located evidence" in text


def test_saga_state_remains_in_unified_pi_package() -> None:
    manifest = (ROOT / "package.json").read_text(encoding="utf-8")
    text = skill_text("saga-state")

    # REQ-084 replaced the recursive namespace parent with explicit leaf paths;
    # saga-state stays declared in the unified package under its own leaf.
    assert '"./skills/saga/saga-state"' in manifest
    assert re.search(r"^name: saga-state$", frontmatter(text), re.MULTILINE)
    assert re.search(
        r"^disable-model-invocation: false$", frontmatter(text), re.MULTILINE
    )


def test_saga_state_preserves_resume_pause_and_note_contracts() -> None:
    text = skill_text("saga-state")

    assert "### resume" in text
    assert "### note / pause" in text
    assert "READ `.planning/STATE.md` first" in text
    assert "before doing anything else" in text
    assert "Do not invent progress numbers" in text


def test_saga_state_edits_in_place_and_preserves_rag_frontmatter() -> None:
    text = skill_text("saga-state")
    reference = (SAGA_ROOT / "saga-state" / "reference.md").read_text(encoding="utf-8")

    assert "**Edit an existing STATE.md in place.**" in text
    assert "Never rebuild an existing file from the template" in text
    assert "Preserve every other frontmatter key" in text
    for key in (
        "saga_state_version",
        "milestone",
        "milestone_name",
        "status",
        "last_updated",
        "last_activity",
    ):
        assert key in reference
    assert "RAG indexers" in reference
