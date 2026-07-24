"""Integration tests for Saga's v2 cross-harness skill installer.

The installer manages an explicit surface (never a glob): eleven canonical skills
plus ten one-release compatibility aliases (four legacy Saga names and six legacy
general names from the separate agent-skills repository). Tests run against
isolated fake homes and an isolated migration snapshot, seed BOTH legacy source
repositories, and assert the surface by loaded SKILL.md metadata identity rather
than symlink names alone.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

CANONICAL = {
    "ops-grill-me": "skills/ops/ops-grill-me",
    "ops-troubleshoot": "skills/ops/ops-troubleshoot",
    "ops-review": "skills/ops/ops-review",
    "ops-upgrade": "skills/ops/ops-upgrade",
    "ops-document": "skills/ops/ops-document",
    "saga-init": "skills/saga/saga-init",
    "saga-plan": "skills/saga/saga-plan",
    "saga-run": "skills/saga/saga-run",
    "saga-state": "skills/saga/saga-state",
    "saga-check": "skills/saga/saga-check",
    "saga-audit": "skills/saga/saga-audit",
}
ALIASES = {
    "saga-next": "skills/compat/saga-next",
    "saga-loop": "skills/compat/saga-loop",
    "saga-verify": "skills/compat/saga-verify",
    "saga-lint": "skills/compat/saga-lint",
    "adversarial-review": "skills/compat/adversarial-review",
    "review": "skills/compat/review",
    "security-review": "skills/compat/security-review",
    "debug": "skills/compat/debug",
    "dependency-upgrade": "skills/compat/dependency-upgrade",
    "write-docs": "skills/compat/write-docs",
}
SURFACE = {**CANONICAL, **ALIASES}

# A legacy Saga surface, matching what the old glob installer produced.
SAGA_LEGACY = [
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
]
# The separate agent-skills legacy general surface. Six route to a forwarder in
# the v2 surface; the remaining four are internal disciplines with no single
# canonical route -- pruned on migration, restored on rollback.
GENERAL_LEGACY = [
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
]
GENERAL_FORWARDED = {"adversarial-review", "review", "security-review", "debug", "dependency-upgrade", "write-docs"}
GENERAL_PRUNED = set(GENERAL_LEGACY) - GENERAL_FORWARDED
SAGA_PRUNED = {"saga-context", "saga-decision", "saga-retro", "saga-roadmap", "saga-spec"}
LEGACY_PRUNED = SAGA_PRUNED | GENERAL_PRUNED
HOME_DIRS = {"claude": "claude", "codex": "codex", "hermes": "hermes", "pi": "agents"}


def run(script: str, tmp_path: Path, *args: str, root: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_HOME": str(tmp_path / "claude"),
            "CODEX_HOME": str(tmp_path / "codex"),
            "HERMES_HOME": str(tmp_path / "hermes"),
            "PI_HOME": str(tmp_path / "agents"),
            "AGENT_SKILLS_ROOT": str(tmp_path / "agent-skills"),
            "SAGA_MIGRATION_STATE": str(tmp_path / "state" / "snapshot.json"),
        }
    )
    return subprocess.run(
        [str(root / script), *args],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def frontmatter_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise AssertionError(f"no name frontmatter in {skill_dir}")


def make_agent_skills(tmp_path: Path) -> Path:
    """Build a fake agent-skills checkout the installer detects structurally."""
    root = tmp_path / "agent-skills" / "skills"
    for name in GENERAL_LEGACY:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: legacy {name}\n---\n\n# {name}\n",
            encoding="utf-8",
        )
    return root


def assert_v2_surface(home: Path) -> None:
    installed = {p.name for p in (home / "skills").iterdir() if p.name in SURFACE}
    assert installed == set(SURFACE), f"surface mismatch in {home}"
    # Legacy names dropped from the visible surface must be gone.
    for name in LEGACY_PRUNED:
        assert not (home / "skills" / name).exists()
        assert not (home / "skills" / name).is_symlink()
    for name, rel in SURFACE.items():
        link = home / "skills" / name
        assert link.is_symlink(), f"missing symlink: {link}"
        assert link.resolve() == (ROOT / rel).resolve()
        # Metadata identity: the loaded skill's own name matches both the link
        # name the harness sees and its own directory -- no mismatched or
        # duplicated frontmatter identity. This is what keeps every legacy name
        # with a forwarder callable via matching frontmatter after migration.
        assert frontmatter_name(link) == name


def assert_no_surface(home: Path) -> None:
    skills = home / "skills"
    if not skills.exists():
        return
    assert not any(p.name in SURFACE for p in skills.iterdir())


def seed_legacy(home: Path, agent_skills: Path) -> dict[str, str]:
    """Seed BOTH legacy repositories into one fake home; return raw targets."""
    skills = home / "skills"
    skills.mkdir(parents=True)
    targets: dict[str, str] = {}
    for name in SAGA_LEGACY:
        (skills / name).symlink_to(ROOT / "skills" / "saga" / name)
        targets[name] = os.readlink(skills / name)
    for name in GENERAL_LEGACY:
        (skills / name).symlink_to(agent_skills / name)
        targets[name] = os.readlink(skills / name)
    return targets


# --- fresh install ---------------------------------------------------------


def test_fresh_install_all_homes_metadata_identity(tmp_path: Path) -> None:
    result = run("install.sh", tmp_path)
    assert result.returncode == 0, result.stderr
    for home in HOME_DIRS.values():
        assert_v2_surface(tmp_path / home)


def test_install_is_idempotent(tmp_path: Path) -> None:
    first = run("install.sh", tmp_path, "--claude")
    second = run("install.sh", tmp_path, "--claude")
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert_v2_surface(tmp_path / "claude")


def test_target_flag_installs_only_selected_agent(tmp_path: Path) -> None:
    result = run("install.sh", tmp_path, "--hermes")
    assert result.returncode == 0, result.stderr
    assert_v2_surface(tmp_path / "hermes")
    for home in ("claude", "codex", "agents"):
        assert_no_surface(tmp_path / home)


def test_pi_flag_installs_agent_skills_location(tmp_path: Path) -> None:
    result = run("install.sh", tmp_path, "--pi")
    assert result.returncode == 0, result.stderr
    assert_v2_surface(tmp_path / "agents")
    for home in ("claude", "codex", "hermes"):
        assert_no_surface(tmp_path / home)


def test_installed_saga_lint_alias_preserves_exit_contract(tmp_path: Path) -> None:
    installed = run("install.sh", tmp_path, "--hermes")
    assert installed.returncode == 0, installed.stderr
    wrapper = tmp_path / "hermes" / "skills" / "saga-lint" / "scripts" / "run.sh"
    assert wrapper.resolve() == (ROOT / "skills" / "compat" / "saga-lint" / "scripts" / "run.sh")

    clean = subprocess.run(
        [str(wrapper), str(ROOT / "examples" / "minimal")],
        text=True, capture_output=True, check=False,
    )
    assert clean.returncode == 0, clean.stderr

    findings = subprocess.run(
        [str(wrapper), str(ROOT / "tests" / "fixtures" / "saga_lint" / "invalid")],
        text=True, capture_output=True, check=False,
    )
    assert findings.returncode == 1, findings.stderr

    missing = subprocess.run(
        [str(wrapper), str(tmp_path / "no-saga-spine")],
        text=True, capture_output=True, check=False,
    )
    assert missing.returncode == 2, missing.stderr
    assert "SPINE_NOT_FOUND" in missing.stdout

    as_json = subprocess.run(
        [str(wrapper), str(ROOT / "examples" / "minimal"), "--format", "json"],
        text=True, capture_output=True, check=False,
    )
    assert as_json.returncode == 0, as_json.stderr
    assert json.loads(as_json.stdout)["schema_version"] == "1.0"


# --- conflict / foreign refusal (preflight) --------------------------------


def test_install_refuses_foreign_entry_and_mutates_nothing(tmp_path: Path) -> None:
    conflict = tmp_path / "claude" / "skills" / "saga-run"
    conflict.parent.mkdir(parents=True)
    conflict.write_text("keep me\n")

    result = run("install.sh", tmp_path)  # all agents

    assert result.returncode != 0
    assert conflict.read_text() == "keep me\n"
    assert "refusing to replace" in result.stderr.lower()
    # Preflight aborts before any mutation, so no other home was touched either.
    for home in ("codex", "hermes", "agents"):
        assert_no_surface(tmp_path / home)


def test_install_refuses_to_silently_repoint_legacy_saga_link(tmp_path: Path) -> None:
    agent_skills = make_agent_skills(tmp_path)
    seed_legacy(tmp_path / "claude", agent_skills)
    result = run("install.sh", tmp_path, "--claude")
    assert result.returncode != 0
    assert "migrate" in result.stderr.lower()
    # The legacy link is untouched.
    link = tmp_path / "claude" / "skills" / "saga-next"
    assert link.resolve() == (ROOT / "skills" / "saga" / "saga-next").resolve()


def test_install_refuses_to_silently_replace_legacy_general_link(tmp_path: Path) -> None:
    agent_skills = make_agent_skills(tmp_path)
    seed_legacy(tmp_path / "claude", agent_skills)
    result = run("install.sh", tmp_path, "--claude")
    assert result.returncode != 0
    assert "migrate" in result.stderr.lower()
    # An agent-skills legacy general link is detected, not clobbered.
    link = tmp_path / "claude" / "skills" / "review"
    assert os.readlink(link) == str(agent_skills / "review")


def test_arbitrary_foreign_symlink_at_legacy_name_is_still_foreign(tmp_path: Path) -> None:
    # Even a different checkout with matching path shape and frontmatter is not
    # owned unless it is the explicitly declared AGENT_SKILLS_ROOT.
    elsewhere = tmp_path / "elsewhere" / "skills" / "review"
    elsewhere.mkdir(parents=True)
    (elsewhere / "SKILL.md").write_text(
        "---\nname: review\ndescription: foreign review\n---\n",
        encoding="utf-8",
    )
    home = tmp_path / "claude" / "skills"
    home.mkdir(parents=True)
    (home / "review").symlink_to(elsewhere)
    result = run("install.sh", tmp_path, "--claude")
    assert result.returncode != 0
    assert "refusing to replace foreign entry" in result.stderr.lower()
    assert os.readlink(home / "review") == str(elsewhere)


def test_migrate_foreign_conflict_aborts_all_homes_before_snapshot(tmp_path: Path) -> None:
    agent_skills = make_agent_skills(tmp_path)
    untouched = seed_legacy(tmp_path / "codex", agent_skills)
    conflict = tmp_path / "claude" / "skills" / "saga-run"
    conflict.parent.mkdir(parents=True)
    conflict.write_text("keep me\n", encoding="utf-8")

    result = run("install.sh", tmp_path, "--migrate")

    assert result.returncode != 0
    assert "refusing to replace foreign entry" in result.stderr.lower()
    assert conflict.read_text(encoding="utf-8") == "keep me\n"
    assert not (tmp_path / "state" / "snapshot.json").exists()
    for name, raw in untouched.items():
        assert os.readlink(tmp_path / "codex" / "skills" / name) == raw
    for home in ("hermes", "agents"):
        assert_no_surface(tmp_path / home)


def test_unknown_flag_fails(tmp_path: Path) -> None:
    result = run("install.sh", tmp_path, "--bogus")
    assert result.returncode == 2
    assert "unknown option" in result.stderr.lower()


# --- migrate / rollback ----------------------------------------------------


def test_migrate_from_both_legacy_repos_then_exact_rollback(tmp_path: Path) -> None:
    agent_skills = make_agent_skills(tmp_path)
    pre = {home: seed_legacy(tmp_path / home, agent_skills) for home in HOME_DIRS.values()}

    migrated = run("install.sh", tmp_path, "--migrate")
    assert migrated.returncode == 0, migrated.stderr
    snapshot = tmp_path / "state" / "snapshot.json"
    assert snapshot.is_file()
    for home in HOME_DIRS.values():
        skills = tmp_path / home / "skills"
        assert_v2_surface(tmp_path / home)
        # Saga aliases now resolve to the forwarder source, not the old raw skill.
        assert (skills / "saga-next").resolve() == (ROOT / "skills" / "compat" / "saga-next").resolve()
        # Every legacy general name with a forwarder stays callable, and its
        # loaded frontmatter identity equals the link name (no mismatch).
        for name in GENERAL_FORWARDED:
            link = skills / name
            assert link.is_symlink()
            assert link.resolve() == (ROOT / "skills" / "compat" / name).resolve()
            assert frontmatter_name(link) == name
        # Non-routable legacy disciplines are pruned.
        for name in GENERAL_PRUNED:
            assert not (skills / name).exists()

    # Idempotent migrate keeps the original snapshot.
    again = run("install.sh", tmp_path, "--migrate", "--claude")
    assert again.returncode == 0, again.stderr

    rolled = run("install.sh", tmp_path, "--rollback")
    assert rolled.returncode == 0, rolled.stderr
    for home, targets in pre.items():
        skills = tmp_path / home / "skills"
        # Exact pre-migration links restored for BOTH legacy repositories...
        for name, raw in targets.items():
            link = skills / name
            assert link.is_symlink(), f"rollback dropped {link}"
            assert os.readlink(link) == raw, f"{name} restored to {os.readlink(link)}, want {raw}"
        # ...and v2-only names (absent before migration) are gone again.
        for name in CANONICAL:
            if name not in targets:
                assert not (skills / name).is_symlink()


def test_rollback_aborts_atomically_on_foreign_conflict(tmp_path: Path) -> None:
    agent_skills = make_agent_skills(tmp_path)
    pre = {home: seed_legacy(tmp_path / home, agent_skills) for home in HOME_DIRS.values()}
    assert run("install.sh", tmp_path, "--migrate").returncode == 0

    # Something external replaces one managed link with a foreign entry.
    victim = tmp_path / "claude" / "skills" / "saga-run"
    victim.unlink()
    victim.write_text("foreign now\n")

    # Snapshot of every other managed link across all homes, to prove zero writes.
    before = {}
    for home in HOME_DIRS.values():
        for link in (tmp_path / home / "skills").iterdir():
            if link.is_symlink():
                before[str(link)] = os.readlink(link)

    result = run("install.sh", tmp_path, "--rollback")
    assert result.returncode != 0
    assert "refusing to roll back over foreign entry" in result.stderr.lower()
    # Zero mutation: the foreign entry survives and every other link is unchanged.
    assert victim.read_text() == "foreign now\n"
    after = {}
    for home in HOME_DIRS.values():
        for link in (tmp_path / home / "skills").iterdir():
            if link.is_symlink():
                after[str(link)] = os.readlink(link)
    assert after == before
    # The still-migrated homes were never partially rolled back.
    for home in HOME_DIRS.values():
        assert (tmp_path / home / "skills" / "saga-next").resolve() == (
            ROOT / "skills" / "compat" / "saga-next"
        ).resolve()
    assert pre  # seeded state exists; rollback simply refused to touch it


def test_uninstall_removes_only_owned_surface_links(tmp_path: Path) -> None:
    installed = run("install.sh", tmp_path, "--codex")
    assert installed.returncode == 0, installed.stderr

    foreign_target = tmp_path / "foreign"
    foreign_target.mkdir()
    foreign = tmp_path / "codex" / "skills" / "saga-foreign"
    foreign.symlink_to(foreign_target)

    result = run("uninstall.sh", tmp_path, "--codex")
    assert result.returncode == 0, result.stderr
    for name in SURFACE:
        assert not (tmp_path / "codex" / "skills" / name).is_symlink()
    assert foreign.is_symlink()


# --- package-shaped operation without private state ------------------------


def test_installs_from_package_without_private_planning_state(tmp_path: Path) -> None:
    package = tmp_path / "package"
    (package / "bin").mkdir(parents=True)
    shutil.copytree(ROOT / "skills", package / "skills")
    shutil.copy2(ROOT / "bin" / "saga-skill-install", package / "bin" / "saga-skill-install")
    shutil.copy2(ROOT / "install.sh", package / "install.sh")
    os.chmod(package / "bin" / "saga-skill-install", 0o755)
    os.chmod(package / "install.sh", 0o755)
    assert not (package / ".planning").exists()

    homes = tmp_path / "homes"
    result = run("install.sh", homes, "--claude", root=package)
    assert result.returncode == 0, result.stderr
    # Surface links resolve into the package copy, not the source repo.
    for name in SURFACE:
        link = homes / "claude" / "skills" / name
        assert link.is_symlink()
        assert link.resolve() == (package / SURFACE[name]).resolve()
