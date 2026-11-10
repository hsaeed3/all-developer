"""Shared fixtures: a temporary repository that received the terminal assets make hook."""

from __future__ import annotations

import importlib.util
import pathlib
import shutil
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "all-developer"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--actual-terminal",
        action="store_true",
        help="run the tests that render assets in a real Kitty window",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--actual-terminal"):
        return
    skip = pytest.mark.skip(reason="needs --actual-terminal (make test-terminal)")
    for item in items:
        if "actual_terminal" in item.keywords:
            item.add_marker(skip)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "actual_terminal: the test starts a real Kitty window")


@pytest.fixture
def project(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a new repository with the script and the make targets copied as the skill says."""
    (tmp_path / "scripts").mkdir()
    shutil.copy(SKILL / "scripts" / "render_assets.py", tmp_path / "scripts")
    snippet = (SKILL / "assets" / "make" / "render-assets.mk").read_text(encoding="utf-8")
    (tmp_path / "Makefile").write_text(
        snippet.replace("uv run --no-sync python", "python3"), encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def render_assets(project: pathlib.Path) -> types.ModuleType:
    """Return the copied script as a module, with the temporary repository as its root."""
    specification = importlib.util.spec_from_file_location(
        "render_assets", project / "scripts" / "render_assets.py"
    )
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules["render_assets"] = module
    specification.loader.exec_module(module)
    return module
