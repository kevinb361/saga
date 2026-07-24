"""Public documentation contract for the unified v2 operator toolbox (REQ-085)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRIMARY = {
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
}
LEGACY_SLASH = {
    "/saga-next",
    "/saga-loop",
    "/saga-roadmap",
    "/saga-verify",
    "/saga-decision",
    "/saga-context",
    "/saga-retro",
    "/saga-spec",
}


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def test_readme_presents_exactly_ten_primary_intents_plus_separate_audit() -> None:
    readme = read("README.md")
    primary = section(readme, "## Ten everyday intents", "### Independent milestone audit")
    names = set(re.findall(r"`((?:ops|saga)-[a-z0-9-]+)`", primary))

    assert names == PRIMARY
    assert "saga-audit" not in names
    audit = section(readme, "### Independent milestone audit", "## Typical project flow")
    assert "`saga-audit`" in audit
    assert "independent" in audit.lower()
    assert "executor never audits itself" in audit.lower()


def test_readme_states_review_and_document_boundaries() -> None:
    readme = read("README.md")
    assert "`ops-review` is the ordinary read-only second look" in readme
    assert "does **not** certify a Saga milestone" in readme
    assert "`ops-document` is for documentation or durable-memory intent" in readme
    assert "does **not** mean every ordinary file edit" in readme


def test_primary_docs_use_current_names_and_natural_language() -> None:
    paths = ("README.md", "skills/saga/DESCRIPTION.md", "docs/DESIGN.md", "CLAUDE.md")
    combined = "\n".join(read(path) for path in paths)
    for stale in LEGACY_SLASH:
        assert stale not in combined

    examples = section(read("README.md"), "## Ten everyday intents", "## Compatibility during v2 migration")
    quoted_examples = re.findall(r"“([^”]+)”", examples)
    assert len(quoted_examples) >= len(PRIMARY)
    assert all("--" not in example for example in quoted_examples)
    for name in PRIMARY:
        assert f"`{name}`" in examples


def test_docs_identify_canonical_package_and_temporary_aliases() -> None:
    readme = read("README.md")
    toolbox = read("docs/TOOLBOX.md")
    package = json.loads(read("package.json"))

    assert "This repository is the **canonical source**" in readme
    assert "This `saga` repository is the canonical package source" in toolbox
    assert "IMPLEMENTED and independently verified" in toolbox
    assert "One-release compatibility aliases" in readme
    assert "migration aids rather than primary workflows" in readme
    assert "Planned unified" not in package["description"]
