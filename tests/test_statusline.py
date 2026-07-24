"""Behavior tests for Saga's canonical STATE status glyphs."""

from pathlib import Path
import re
import subprocess

import pytest


SCRIPT = Path(__file__).parents[1] / "bin" / "saga-statusline.js"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


@pytest.mark.parametrize(
    ("status", "glyph"),
    [
        ("active", "○"),
        ("blocked", "✗"),
        ("paused", "–"),
        ("idle", "–"),
        ("complete", "✓"),
        ("closed", "✓"),
    ],
)
def test_statusline_maps_canonical_state_statuses(tmp_path, status, glyph):
    planning = tmp_path / ".planning"
    planning.mkdir()
    (planning / "STATE.md").write_text(
        "---\n"
        "saga_state_version: 1.0\n"
        "milestone: v1.0-test\n"
        "milestone_name: Test\n"
        f"status: {status}\n"
        'last_updated: "2026-01-01T00:00:00Z"\n'
        "last_activity: fixture\n"
        "---\n"
    )
    payload = (
        '{"model":{"display_name":"test"},'
        f'"workspace":{{"current_dir":"{tmp_path}"}}}}'
    )

    result = subprocess.run(
        ["node", str(SCRIPT)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = ANSI_RE.sub("", result.stdout)
    assert f"{glyph} v1.0-test Test" in output
