"""Package-shaped export gate (REQ-084).

Everything here runs from a `.planning`-free copy of the package — the shape a Pi
install or release tarball actually ships — so the canonical `make ci` gate owns
the checks that used to live only in the separate `agent-skills/scripts`
validators. It proves, without any private local state or real agent/Pi home:

* Pi discovery over `package.json` `pi.skills` yields exactly the 21 canonical +
  compatibility identities, collision-free, with no retired raw legacy skill.
* Every exported skill's metadata is valid under the Agent Skills standard
  (name == directory, name charset, description length).
* Every local reference in a shipped skill resolves inside the export.
* The deterministic Saga tool preserves its 0/1/2 + JSON exit contract when run
  from the export (bare binary and the compat `saga-lint` wrapper).
* Risk and audit-independence invariants survive in the exported skill text.

The install/migrate/rollback/uninstall lifecycle is owned by
`tests/test_install.py` (four isolated fake homes + a `.planning`-free package
fresh install); this module adds the package/discovery, metadata, reference,
tool-contract, and invariant lanes.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

CANONICAL_NAMES = {
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
ALIAS_NAMES = {
    "saga-next",
    "saga-loop",
    "saga-verify",
    "saga-lint",
    "adversarial-review",
    "review",
    "security-review",
    "debug",
    "dependency-upgrade",
    "write-docs",
}
SURFACE_NAMES = CANONICAL_NAMES | ALIAS_NAMES

# Retired raw Saga skills kept in-tree for REQ-086; must never be a discovered
# package identity.
RETIRED_RAW = {
    "saga-context",
    "saga-decision",
    "saga-retro",
    "saga-roadmap",
    "saga-spec",
}


def load_installer():
    spec = importlib.util.spec_from_file_location(
        "saga_skill_install", ROOT / "bin" / "saga-skill-install"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def export(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A private-state-free copy of the package, as shipped."""
    dest = tmp_path_factory.mktemp("package")
    shutil.copytree(ROOT / "skills", dest / "skills")
    shutil.copytree(ROOT / "bin", dest / "bin")
    if (ROOT / "examples").is_dir():
        shutil.copytree(ROOT / "examples", dest / "examples")
    for name in ("package.json", "install.sh", "uninstall.sh"):
        shutil.copy2(ROOT / name, dest / name)
    # The private spine must not be part of the shipped package.
    assert not (dest / ".planning").exists()
    return dest


def frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"missing YAML frontmatter: {skill_md}"
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


# --- Pi discovery -----------------------------------------------------------


def test_export_carries_no_private_planning_state(export: Path) -> None:
    assert not (export / ".planning").exists()
    # Nested public spines (examples/fixtures) may ship; the private root may not.
    assert (export / "skills").is_dir()


def test_pi_discovery_yields_exactly_the_21_identities(export: Path) -> None:
    manifest = json.loads((export / "package.json").read_text(encoding="utf-8"))
    names: list[str] = []
    for rel in manifest["pi"]["skills"]:
        skill_dir = (export / rel).resolve()
        assert skill_dir.is_relative_to(export.resolve())
        assert (skill_dir / "SKILL.md").is_file()
        names.append(frontmatter(skill_dir / "SKILL.md")["name"])

    # Exactly 21, all distinct (Pi warns+drops on collision — none may occur),
    # and precisely the canonical + alias surface.
    assert len(names) == 21
    assert len(set(names)) == 21, "duplicate skill identity would be dropped by Pi"
    assert set(names) == SURFACE_NAMES


def test_pi_discovery_exposes_no_retired_raw_legacy_skill(export: Path) -> None:
    manifest = json.loads((export / "package.json").read_text(encoding="utf-8"))
    names = {
        frontmatter((export / rel).resolve() / "SKILL.md")["name"]
        for rel in manifest["pi"]["skills"]
    }
    assert names.isdisjoint(RETIRED_RAW)

    # The four forwarder names resolve into skills/compat, never the raw skill.
    for rel in manifest["pi"]["skills"]:
        skill_dir = (export / rel).resolve()
        name = frontmatter(skill_dir / "SKILL.md")["name"]
        if name in ALIAS_NAMES:
            assert (
                "compat" in skill_dir.parts
            ), f"{name} must resolve into skills/compat"

    # The raw skills still ship in-tree (kept for REQ-086) but are unlisted, so
    # convention recursion is never what surfaces them.
    for name in RETIRED_RAW | {"saga-next", "saga-loop", "saga-verify", "saga-lint"}:
        assert (export / "skills" / "saga" / name / "SKILL.md").is_file()


def test_alias_forwarders_are_hidden_from_auto_invocation(export: Path) -> None:
    for name in ALIAS_NAMES:
        fields = frontmatter(export / "skills" / "compat" / name / "SKILL.md")
        assert fields.get("disable-model-invocation") == "true", name


# --- metadata (Agent Skills standard, ported into CI) -----------------------


def _validate_metadata(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir}: missing SKILL.md"]
    fields = frontmatter(skill_md)
    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != skill_dir.name:
        errors.append(
            f"{skill_md}: name {name!r} must match directory {skill_dir.name!r}"
        )
    if not NAME_RE.fullmatch(name):
        errors.append(f"{skill_md}: invalid skill name {name!r}")
    if not description:
        errors.append(f"{skill_md}: missing description")
    if len(description) > 1024:
        errors.append(f"{skill_md}: description exceeds 1024 characters")
    return errors


def test_exported_surface_metadata_is_valid(export: Path) -> None:
    manifest = json.loads((export / "package.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    for rel in manifest["pi"]["skills"]:
        errors.extend(_validate_metadata((export / rel).resolve()))
    assert not errors, "\n".join(errors)


def test_every_shipped_skill_has_valid_metadata(export: Path) -> None:
    # The whole skills/ tree ships in the archive (raw legacy included); every
    # SKILL.md must satisfy the standard so nothing warns or fails to load.
    errors: list[str] = []
    for skill_md in sorted((export / "skills").rglob("SKILL.md")):
        errors.extend(_validate_metadata(skill_md.parent))
    assert not errors, "\n".join(errors)


# --- local references -------------------------------------------------------


REF_PATTERNS = (
    re.compile(r"(?<![\w./-])reference\.md"),
    re.compile(r"(?<![\w./-])scripts/[A-Za-z0-9._/-]+"),
    re.compile(r"(?<![\w./-])references/[A-Za-z0-9._/-]+"),
    re.compile(r"(?<![.\w/-])(?:\.\./)+[A-Za-z0-9._/-]+"),
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _local_references(markdown: Path) -> set[str]:
    text = markdown.read_text(encoding="utf-8")
    refs: set[str] = set()
    for pattern in REF_PATTERNS:
        for match in pattern.findall(text):
            ref = match.strip().rstrip("`.,);:")
            if ref:
                refs.add(ref)
    for match in MARKDOWN_LINK_RE.findall(text):
        ref = match.strip().split(maxsplit=1)[0].strip("<>")
        ref = ref.split("#", 1)[0]
        if ref and not ref.startswith(("/", "//")) and ":" not in ref:
            refs.add(ref)
    return refs


def test_every_shipped_skill_reference_resolves(export: Path) -> None:
    unresolved: list[str] = []
    for markdown in sorted((export / "skills").rglob("*.md")):
        for ref in _local_references(markdown):
            target = (markdown.parent / ref).resolve()
            if not target.exists():
                unresolved.append(f"{markdown}: dangling reference {ref}")
    assert not unresolved, "\n".join(unresolved)


def test_compat_forwarders_point_at_a_real_canonical_skill(export: Path) -> None:
    # Every forwarder body must route to a canonical SKILL.md that exists in the
    # export — the alias holds no implementation of its own.
    for name in ALIAS_NAMES:
        skill_md = export / "skills" / "compat" / name / "SKILL.md"
        targets = [
            r
            for r in _local_references(skill_md)
            if r.endswith("SKILL.md") and r.startswith("../")
        ]
        assert targets, f"{name}: forwarder names no canonical target"
        for ref in targets:
            resolved = (skill_md.parent / ref).resolve()
            assert resolved.is_file()
            assert (
                resolved.parent.name in CANONICAL_NAMES
            ), f"{name} -> {ref} is not canonical"


# --- deterministic tool exit contract, run from the export ------------------


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def test_exported_saga_lint_preserves_exit_contract(
    export: Path, tmp_path: Path
) -> None:
    binary = export / "bin" / "saga-lint"
    assert os.access(binary, os.X_OK)
    clean_target = export / "examples" / "minimal"

    clean = _run([str(binary), str(clean_target)])
    assert clean.returncode == 0, clean.stderr

    findings = _run(
        [str(binary), str(ROOT / "tests" / "fixtures" / "saga_lint" / "invalid")]
    )
    assert findings.returncode == 1, findings.stderr

    missing = _run([str(binary), str(tmp_path / "no-spine")])
    assert missing.returncode == 2
    assert "SPINE_NOT_FOUND" in missing.stdout

    as_json = _run([str(binary), str(clean_target), "--format", "json"])
    assert as_json.returncode == 0, as_json.stderr
    assert json.loads(as_json.stdout)["schema_version"] == "1.0"


def test_exported_compat_saga_lint_wrapper_resolves_within_the_package(
    export: Path, tmp_path: Path
) -> None:
    wrapper = export / "skills" / "compat" / "saga-lint" / "scripts" / "run.sh"
    assert os.access(wrapper, os.X_OK)

    clean = _run([str(wrapper), str(export / "examples" / "minimal")])
    assert clean.returncode == 0, clean.stderr

    missing = _run([str(wrapper), str(tmp_path / "no-spine")])
    assert missing.returncode == 2
    assert "SPINE_NOT_FOUND" in missing.stdout


# --- risk and audit-independence invariants ---------------------------------


def _skill_text(export: Path, namespace: str, name: str) -> str:
    return (export / "skills" / namespace / name / "SKILL.md").read_text(
        encoding="utf-8"
    )


def test_risk_invariants_survive_in_exported_skills(export: Path) -> None:
    review = _skill_text(export, "ops", "ops-review").lower()
    assert "read-only" in review
    assert "do not edit files" in review

    troubleshoot = _skill_text(export, "ops", "ops-troubleshoot").lower()
    assert "read-only evidence" in troubleshoot

    upgrade = _skill_text(export, "ops", "ops-upgrade").lower()
    assert "health verification" in upgrade

    run = _skill_text(export, "saga", "saga-run")
    assert "exactly one" in run.lower()
    assert "FAIL CLOSED" in run


def test_audit_independence_invariants_survive_in_exported_skills(export: Path) -> None:
    audit = _skill_text(export, "saga", "saga-audit")
    lowered = audit.lower()
    assert "never flips roadmap" in lowered
    assert "did not execute any reviewed slice" in lowered
    assert "fail closed" in lowered
