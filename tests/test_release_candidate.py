"""Release-candidate metadata and public-safety contract for v2.0.0 (REQ-086)."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v2_release_metadata_and_notes_are_coherent() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    notes = (ROOT / "docs" / "RELEASE-v2.0.0.md").read_text(encoding="utf-8")
    toolbox = (ROOT / "docs" / "TOOLBOX.md").read_text(encoding="utf-8")

    assert package["version"] == "2.0.0"
    assert package["private"] is False
    assert "Saga v2.0.0" in notes
    assert "ten intent-driven skills" in notes
    assert "`saga-audit` remains separate" in notes
    assert "Ten self-named compatibility aliases" in notes
    assert "./install.sh --rollback" in notes
    assert "11 canonical skills plus 10 one-release compatibility aliases" in toolbox


def test_ruff_rules_are_explicit_across_tool_versions() -> None:
    config = tomllib.loads((ROOT / "ruff.toml").read_text(encoding="utf-8"))
    assert config["target-version"] == "py311"
    assert config["line-length"] == 100
    assert config["lint"]["select"] == ["E4", "E7", "E9", "F"]


def test_clean_export_policy_excludes_private_root_only() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()

    for rule in (
        "/.planning export-ignore",
        ".gitea export-ignore",
        "docs/PUBLISHING.md export-ignore",
    ):
        assert rule in attributes
    assert ".planning export-ignore" not in attributes


def test_internal_publishing_procedure_when_present() -> None:
    publishing_path = ROOT / "docs" / "PUBLISHING.md"
    if not publishing_path.exists():
        # Public clones and release archives intentionally omit this internal
        # procedure; the export-ignore contract above remains load-bearing.
        return
    publishing = publishing_path.read_text(encoding="utf-8")
    assert "clean export" in publishing.lower()
    assert "never rewrite public history" in publishing
    assert "make -C \"$work/public\" ci" in publishing


def test_public_worktree_has_no_private_environment_literals() -> None:
    private_home = "/" + "home" + "/" + "kevin"
    private_remote = "gitea" + ":"
    private_ip = re.compile(r"\b10(?:\.\d{1,3}){3}\b")
    findings: list[str] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in {
            ".git",
            ".planning",
            ".gitea",
            ".hermes",
            ".pytest_cache",
            ".ruff_cache",
            ".worktrees",
            "__pycache__",
        }:
            continue
        if rel == Path("docs/PUBLISHING.md"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if private_home in text or private_remote in text or private_ip.search(text):
            findings.append(str(rel))

    assert not findings, "private environment literals in public product: " + ", ".join(findings)
