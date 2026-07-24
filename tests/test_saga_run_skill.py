import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "skills" / "saga" / "saga-run"


def skill_text() -> str:
    return (RUN_DIR / "SKILL.md").read_text(encoding="utf-8")


def reference_text() -> str:
    return (RUN_DIR / "reference.md").read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None
    return match.group(1)


def squished(text: str) -> str:
    """Collapse whitespace so contract phrases match regardless of line wrapping."""
    return " ".join(text.split())


# --- One bounded slice is the auto-invocable default (load-bearing) ------------


def test_saga_run_is_auto_invocable_one_slice_default() -> None:
    text = skill_text()
    metadata = frontmatter(text)
    body = squished(text)

    assert re.search(r"^name: saga-run$", metadata, re.MULTILINE)
    # Auto-invocable, exactly like saga-next: a bare/auto call must be able to fire.
    assert re.search(r"^disable-model-invocation: false$", metadata, re.MULTILINE)
    # Mutating either of these sentences (e.g. deleting "exactly one" or the
    # unbounded-loop prohibition) must fail the gate.
    assert "A bare or auto-invoked `saga-run` executes exactly one bounded slice and stops" in body
    assert "never interpret a bare invocation as permission for an unbounded loop" in body


# --- Multi-slice looping requires explicit intent, not a bare/auto call --------


def test_saga_run_loop_requires_explicit_intent() -> None:
    body = squished(skill_text())

    assert "Looping across multiple slices happens ONLY on explicit operator intent" in body
    assert "## Loop mode (explicit intent only)" in skill_text()
    # The consent is the explicit natural-language intent, never a flag or a bare call.
    assert "This intent, not a flag, is the loop consent" in body
    assert "a bare or auto-invoked `saga-run` is never loop consent" in body


# --- Iteration cap is preserved and bounded -----------------------------------


def test_saga_run_loop_keeps_default_cap_of_ten() -> None:
    body = squished(skill_text())

    assert "default cap of 10 iterations" in body
    assert "unbounded running is not offered" in body
    # State/requirements are re-read each iteration.
    assert "Each iteration re-reads `STATE.md` and `REQUIREMENTS.md` from disk" in body


# --- Risk classes and the stop-before-mutation gate ---------------------------


def test_saga_run_preserves_four_risk_classes_and_approval_stop() -> None:
    text = skill_text()
    body = squished(text)

    for risk in ("inspect-only", "repo-only", "live-mutation", "destructive"):
        assert f"`{risk}`" in text
    assert (
        "stop before mutation unless the operator explicitly approved that mutation in this invocation"
        in body
    )
    # The bounded-Ansible exception survives the merge.
    assert "Ansible approval rule:" in body
    assert "It never covers fleet-wide, destructive, ambiguous, or locally human-only execution" in body


# --- Fail-closed close-out: a failed auditor never falls back to self-cert -----


def test_saga_run_close_out_fails_closed_on_failed_auditor() -> None:
    skill = squished(skill_text())
    ref = squished(reference_text())

    assert "FAIL CLOSED" in skill
    # The load-bearing prohibition: no executor self-verify fallback.
    assert "NEVER run `saga-check` or `saga-audit` yourself as a fallback" in skill
    assert "NEVER run `saga-check` or `saga-audit` yourself as a fallback" in ref
    assert "STOP the close-out" in ref
    assert "leave the ROADMAP UNflipped" in ref


# --- Structural contract carried over from saga-next / saga-loop ---------------


def test_saga_run_keeps_three_state_markers_and_escalation_limit() -> None:
    body = squished(skill_text())

    assert "`[x]` AND `[/]` both mean done" in body
    assert "never pick a `[/]` requirement as \"next open work\"" in body
    assert "at most 2 same-slice repairs" in body
    assert "On the 2nd gate failure: STOP and escalate" in body


def test_saga_run_loop_has_stall_concurrency_and_corruption_guards() -> None:
    body = squished(skill_text())
    ref = squished(reference_text())

    for guard in ("stall", "concurrent modification", "corruption"):
        assert guard in body
    assert "Stall detection" in ref
    assert "Concurrent modification guard" in ref
    assert "Corruption guard" in ref


def test_saga_run_never_issues_the_audit_verdict() -> None:
    skill = squished(skill_text())
    ref = squished(reference_text())

    # Independence boundary: run flips mechanically only after an independent
    # frontier context certifies; the verdict stays owned by saga-audit.
    assert "The independent quality verdict stays owned by `saga-audit`" in skill
    assert "Capability alone does not make the executor independent" in ref
    assert "If the current context executed any milestone slice, frontier or not" in ref
    assert "never issues the quality verdict and never certifies its own milestone" in ref
