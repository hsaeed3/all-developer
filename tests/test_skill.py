"""Tests of the structure of the skill and of the make snippets that it ships."""

from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNIPPETS = sorted((ROOT / "skills" / "all-developer" / "assets" / "make").glob("*.mk"))


def test_the_skill_passes_its_own_check() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_skill.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("snippet", SNIPPETS, ids=lambda path: path.name)
def test_make_reads_each_snippet(snippet: pathlib.Path, tmp_path: pathlib.Path) -> None:
    base = snippet.with_name("base.mk")
    makefile = tmp_path / "Makefile"
    text = snippet.read_text(encoding="utf-8")
    if snippet != base:
        text = base.read_text(encoding="utf-8") + "\n" + text
    makefile.write_text(text, encoding="utf-8")
    result = subprocess.run(["make", "help"], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "List the commands" in result.stdout
