"""The Pi package manifest must declare the exact v2 skill surface.

REQ-084: `package.json` `pi.skills` had recursively listed the namespace parents
`./skills/ops` and `./skills/saga`. Under Pi's convention recursion that (a) leaks
the retired raw legacy Saga skills still kept in-tree for REQ-086 and (b) omits
the `skills/compat/` forwarders entirely. Adding compat recursion to that old form
would then collide on the four superseded Saga identities. The fix enumerates the 21 leaf skill directories explicitly
(11 canonical + 10 one-release compatibility aliases), which is exactly the
installer's manifest, so package discovery and the symlink installer agree on one
surface with no glob ambiguity.
"""

from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "package.json"

# Retired raw Saga skills kept in-tree for REQ-086 archival. None may appear in
# the package surface: the four with a forwarder would collide on `name:`, and the
# other five are simply no longer part of the visible surface.
RAW_LEGACY_SAGA = {
    "saga-next",
    "saga-loop",
    "saga-verify",
    "saga-lint",
    "saga-context",
    "saga-decision",
    "saga-retro",
    "saga-roadmap",
    "saga-spec",
}


def load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load_installer():
    loader = SourceFileLoader(
        "saga_skill_install", str(ROOT / "bin" / "saga-skill-install")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_pi_package_has_v2_public_release_metadata() -> None:
    manifest = load_manifest()

    assert manifest["name"] == "saga-operator-toolbox"
    assert manifest["version"] == "2.0.0"
    assert manifest["private"] is False
    assert manifest["license"] == "MIT"
    assert "pi-package" in manifest["keywords"]


def test_pi_manifest_equals_the_installer_surface() -> None:
    manifest = load_manifest()
    installer = load_installer()

    # Single source of truth: the package export declares exactly the leaf
    # directories the symlink installer manages, in the same order.
    expected = ["./" + rel for rel in installer.SURFACE.values()]
    assert manifest["pi"]["skills"] == expected
    assert len(expected) == 21  # 11 canonical + 10 aliases


def test_pi_manifest_lists_leaf_skill_dirs_never_namespace_parents() -> None:
    manifest = load_manifest()
    package_root = MANIFEST.parent.resolve()

    declared = manifest["pi"]["skills"]
    # No namespace-parent entry: recursive discovery on those is the original bug.
    assert "./skills/ops" not in declared
    assert "./skills/saga" not in declared
    assert "./skills/compat" not in declared

    for rel in declared:
        skill_dir = (package_root / rel).resolve()
        assert skill_dir.is_relative_to(package_root)
        assert (skill_dir / "SKILL.md").is_file(), f"{rel} is not a leaf skill dir"


def test_pi_manifest_excludes_every_retired_raw_legacy_skill() -> None:
    manifest = load_manifest()
    declared_names = {Path(rel).name for rel in manifest["pi"]["skills"]}

    # The raw legacy Saga skills survive in-tree for REQ-086 archival...
    for name in RAW_LEGACY_SAGA:
        assert (ROOT / "skills" / "saga" / name / "SKILL.md").is_file()

    # ...but only under skills/saga; the surface never routes to them. The four
    # forwarder names appear in the surface, but they resolve into skills/compat.
    for rel in manifest["pi"]["skills"]:
        assert not rel.startswith("./skills/saga/saga-next")
        assert not rel.startswith("./skills/saga/saga-loop")
        assert not rel.startswith("./skills/saga/saga-verify")
        assert not rel.startswith("./skills/saga/saga-lint")
        assert "context" not in rel and "decision" not in rel
        assert "retro" not in rel and "roadmap" not in rel and "spec" not in rel

    # Canonical saga names that happen to share the prefix are still present.
    assert "./skills/saga/saga-init" in manifest["pi"]["skills"]
    assert "./skills/saga/saga-audit" in manifest["pi"]["skills"]
    # The forwarder names are present exactly once, sourced from compat.
    assert declared_names & RAW_LEGACY_SAGA == {
        "saga-next",
        "saga-loop",
        "saga-verify",
        "saga-lint",
    }
    for name in ("saga-next", "saga-loop", "saga-verify", "saga-lint"):
        assert f"./skills/compat/{name}" in manifest["pi"]["skills"]
