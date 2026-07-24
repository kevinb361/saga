import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs" / "CAPABILITY-MAP.md"
GENERAL_LEGACY = {
    "adversarial-review",
    "api-design",
    "debug",
    "dependency-upgrade",
    "design-an-interface",
    "review",
    "security-review",
    "tdd",
    "verify-before-complete",
    "write-docs",
}
SAGA_LEGACY = {
    "saga-audit",
    "saga-context",
    "saga-decision",
    "saga-lint",
    "saga-loop",
    "saga-next",
    "saga-retro",
    "saga-roadmap",
    "saga-spec",
    "saga-state",
    "saga-verify",
}


def map_text() -> str:
    return MAP.read_text(encoding="utf-8")


def legacy_rows(section: str) -> set[str]:
    body = map_text().split(f"## {section}", maxsplit=1)[1].split("## ", maxsplit=1)[0]
    return set(re.findall(r"^\| `([^`]+)` \|", body, re.MULTILINE))


def test_capability_map_accounts_for_every_legacy_visible_skill() -> None:
    assert legacy_rows("General operator skills") == GENERAL_LEGACY
    assert legacy_rows("Saga lifecycle skills") == SAGA_LEGACY


def test_capability_map_accounts_for_required_internal_disciplines() -> None:
    text = map_text()

    expected_routes = {
        "`adversarial-review` | `ops-review` adversarial lens",
        "`security-review` | `ops-review` security lens",
        "`debug` | `ops-troubleshoot`",
        "`dependency-upgrade` | `ops-upgrade`",
        "`tdd` | `saga-plan` proof conditions + `saga-run` execution discipline",
        "`api-design` | `saga-plan` + `ops-review`",
        "`design-an-interface` | `saga-plan` + `ops-review`",
        "`verify-before-complete` | every mutating `ops-*` skill + `saga-run` gate",
        "`saga-decision` | `ops-document` decision route",
        "`saga-context` | `ops-document` context route",
        "`saga-retro` | `ops-document` lesson route",
        "`saga-spec` | `ops-document` behavior route",
    }
    for route in expected_routes:
        assert route in text


def test_capability_map_blocks_premature_source_loss() -> None:
    text = map_text()

    assert "uncommitted source under `agent-skills/skills/adversarial-review/`" in text
    assert "must remain untouched until migration is verified" in text
    assert "Old source files and the separate `agent-skills` repository are not deleted" in text
    assert "one-release compatibility aliases" in text
    assert "Alias targets must resolve to the canonical v2 source" in text
