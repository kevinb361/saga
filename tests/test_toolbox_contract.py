import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "TOOLBOX.md"
EXPECTED_SKILLS = {
    "ops-grill-me",
    "ops-troubleshoot",
    "ops-review",
    "ops-upgrade",
    "ops-document",
    "saga-init",
    "saga-plan",
    "saga-run",
    "saga-state",
    "saga-check",
    "saga-audit",
}


def contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def natural_language_examples(text: str) -> list[str]:
    section = text.split("## Natural-language interface", maxsplit=1)[1]
    example_block = section.split("```text", maxsplit=1)[1].split("```", maxsplit=1)[0]
    return [line.strip() for line in example_block.splitlines() if line.strip()]


def test_catalog_has_exact_target_skill_names() -> None:
    catalog_names = set(re.findall(r"^\| `(ops-[^`]+|saga-[^`]+)` \|", contract_text(), re.MULTILINE))

    assert catalog_names == EXPECTED_SKILLS


def test_every_skill_has_a_plain_language_example() -> None:
    examples = natural_language_examples(contract_text())
    example_names = {line.split(":", maxsplit=1)[0] for line in examples}

    assert example_names == EXPECTED_SKILLS
    assert all("--" not in line for line in examples)


def test_contract_explains_harness_syntax_without_requiring_flags() -> None:
    text = contract_text()

    assert "Pi uses `/skill:<name>`" in text
    assert "must not require the operator to discover or memorize those flags" in text
