"""Integration tests for Saga's cross-agent installer and uninstaller."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(path.name for path in (ROOT / "skills" / "saga").glob("saga-*") if path.is_dir())


def run_script(script: str, tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_HOME": str(tmp_path / "claude"),
            "CODEX_HOME": str(tmp_path / "codex"),
            "HERMES_HOME": str(tmp_path / "hermes"),
        }
    )
    return subprocess.run(
        [str(ROOT / script), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_installed(home: Path) -> None:
    for name in SKILLS:
        link = home / "skills" / name
        assert link.is_symlink(), f"missing symlink: {link}"
        assert link.resolve() == (ROOT / "skills" / "saga" / name).resolve()


def assert_not_installed(home: Path) -> None:
    assert not any((home / "skills").glob("saga-*"))


def test_default_installs_all_supported_agents(tmp_path: Path) -> None:
    result = run_script("install.sh", tmp_path)

    assert result.returncode == 0, result.stderr
    for agent in ("claude", "codex", "hermes"):
        assert_installed(tmp_path / agent)


def test_target_flag_installs_only_selected_agent(tmp_path: Path) -> None:
    result = run_script("install.sh", tmp_path, "--hermes")

    assert result.returncode == 0, result.stderr
    assert_installed(tmp_path / "hermes")
    assert_not_installed(tmp_path / "claude")
    assert_not_installed(tmp_path / "codex")


def test_install_is_idempotent(tmp_path: Path) -> None:
    first = run_script("install.sh", tmp_path, "--claude")
    second = run_script("install.sh", tmp_path, "--claude")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert_installed(tmp_path / "claude")


def test_install_refuses_to_overwrite_foreign_entry(tmp_path: Path) -> None:
    conflict = tmp_path / "claude" / "skills" / SKILLS[0]
    conflict.parent.mkdir(parents=True)
    conflict.write_text("keep me\n")

    result = run_script("install.sh", tmp_path, "--claude")

    assert result.returncode != 0
    assert conflict.read_text() == "keep me\n"
    assert "refusing to replace" in result.stderr.lower()


def test_uninstall_removes_only_saga_owned_links(tmp_path: Path) -> None:
    installed = run_script("install.sh", tmp_path, "--codex")
    assert installed.returncode == 0, installed.stderr

    foreign_target = tmp_path / "foreign"
    foreign_target.mkdir()
    foreign = tmp_path / "codex" / "skills" / "saga-foreign"
    foreign.symlink_to(foreign_target)

    result = run_script("uninstall.sh", tmp_path, "--codex")

    assert result.returncode == 0, result.stderr
    assert_not_installed(tmp_path / "claude")
    assert_not_installed(tmp_path / "hermes")
    for name in SKILLS:
        assert not (tmp_path / "codex" / "skills" / name).exists()
        assert not (tmp_path / "codex" / "skills" / name).is_symlink()
    assert foreign.is_symlink()


def test_unknown_flag_fails(tmp_path: Path) -> None:
    result = run_script("install.sh", tmp_path, "--bogus")

    assert result.returncode != 0
    assert "unknown option" in result.stderr.lower()
