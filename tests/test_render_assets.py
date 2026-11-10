"""Tests of the terminal assets make hook: its parser, its regions and a real render."""

from __future__ import annotations

import pathlib
import subprocess
import types

import pytest

IMAGE_BLOCK = """# Title

<!-- @code-block name="hello" type="image" height=5 -->
```python
print("hello")
```

Text after the block.
"""

GIF_BLOCK = """<!-- @code-block name="typing" type="gif" height=5
wait 0.5
type hello
press enter
click 3 1 right
drag 0 0 2 0
scroll down 1 1 2
-->
```bash
printf 'name: '; read answer; echo "hi $answer"; sleep 5
```
"""


def write(project: pathlib.Path, name: str, text: str) -> pathlib.Path:
    path = project / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_reads_the_options_of_a_block(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    write(project, "README.md", IMAGE_BLOCK)
    (block,) = render_assets.read_documents()
    assert (block.name, block.kind, block.height, block.language) == (
        "hello",
        "image",
        5,
        "python",
    )
    assert block.code == 'print("hello")\n'
    assert block.where() == "README.md line 3"


def test_reads_the_actions_of_a_block(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    write(project, "README.md", GIF_BLOCK)
    (block,) = render_assets.read_documents()
    kinds = [action.kind for action in block.actions]
    assert kinds == ["wait", "text", "press", "mouse", "mouse", "mouse"]
    assert block.actions[1].text == "hello"
    assert block.actions[2].keys == ("enter",)
    assert block.actions[3].reports == ("\x1b[<2;4;2M", "\x1b[<2;4;2m")
    assert block.actions[4].reports == (
        "\x1b[<0;1;1M",
        "\x1b[<32;2;1M",
        "\x1b[<32;3;1M",
        "\x1b[<0;3;1m",
    )
    assert block.actions[5].reports == ("\x1b[<65;2;2M",) * 2
    assert block.recording_seconds() == 2.0


def test_ignores_a_block_with_no_annotation(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    write(project, "README.md", "# Title\n\n```python\nprint(1)\n```\n")
    assert render_assets.read_documents() == []


@pytest.mark.parametrize(
    ("comment", "expected"),
    [
        ('<!-- @code-block name="Bad Name" -->', 'the name is "Bad Name"'),
        ('<!-- @code-block name="a" type="video" -->', 'the type is "video"'),
        ('<!-- @code-block name="a" height=99 -->', "the height is 99"),
        ('<!-- @code-block name="a" width=3 -->', '"width" is not an option'),
        ('<!-- @code-block name="a"\njump 3\n-->', '"jump 3" is not an action'),
        ('<!-- @code-block name="a"\nclick 3\n-->', "has no position"),
        ('<!-- @code-block name="a" duration=1\nwait 3\n-->', "the actions wait 3 seconds"),
    ],
)
def test_an_error_names_the_place_the_problem_and_the_correction(
    project: pathlib.Path, render_assets: types.ModuleType, comment: str, expected: str
) -> None:
    write(project, "README.md", f"{comment}\n```python\nprint(1)\n```\n")
    with pytest.raises(render_assets.RenderError) as raised:
        render_assets.read_documents()
    message = str(raised.value)
    assert message.startswith("README.md line ")
    assert expected in message
    assert "Expected" in message


def test_rejects_a_language_with_no_interpreter(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    write(project, "README.md", '<!-- @code-block name="a" -->\n```ruby\nputs 1\n```\n')
    with pytest.raises(render_assets.RenderError, match='the code block is in "ruby"'):
        render_assets.read_documents()


def test_rejects_a_name_that_two_files_use(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    write(project, "README.md", IMAGE_BLOCK)
    write(project, "docs/page.md", IMAGE_BLOCK)
    with pytest.raises(render_assets.RenderError, match=r"already used in README\.md line 3"):
        render_assets.read_documents()


def test_writes_a_picture_region_below_a_readme_block(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    readme = write(project, "README.md", IMAGE_BLOCK)
    updated = render_assets.updated_text(readme)
    assert (
        '```\n\n<!-- @code-block-asset name="hello" -->\n<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" '
        'srcset="docs/assets/terminal/hello-dark.png">\n'
        '  <img alt="hello" src="docs/assets/terminal/hello-light.png">\n'
        "</picture>\n<!-- /@code-block-asset -->\n\nText after the block.\n"
    ) in updated


def test_writes_two_images_below_a_block_of_a_page(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    page = write(project, "docs/guide/page.md", IMAGE_BLOCK)
    updated = render_assets.updated_text(page)
    assert "![hello](../assets/terminal/hello-light.png#only-light)" in updated
    assert "![hello](../assets/terminal/hello-dark.png#only-dark)" in updated


def test_a_second_update_changes_nothing(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    readme = write(project, "README.md", IMAGE_BLOCK + "\n" + GIF_BLOCK)
    first = render_assets.updated_text(readme)
    readme.write_text(first, encoding="utf-8")
    assert render_assets.updated_text(readme) == first


def test_removes_the_region_when_the_annotation_goes(
    project: pathlib.Path, render_assets: types.ModuleType
) -> None:
    readme = write(project, "README.md", IMAGE_BLOCK)
    readme.write_text(render_assets.updated_text(readme), encoding="utf-8")
    text = readme.read_text(encoding="utf-8").replace(
        '<!-- @code-block name="hello" type="image" height=5 -->\n', ""
    )
    readme.write_text(text, encoding="utf-8")
    assert "@code-block-asset" not in render_assets.updated_text(readme)


def test_check_reports_a_missing_asset_and_a_stale_region(project: pathlib.Path) -> None:
    write(project, "README.md", IMAGE_BLOCK)
    result = subprocess.run(
        ["make", "check-assets"], cwd=project, capture_output=True, text=True, check=False
    )
    assert result.returncode != 0
    assert "docs/assets/terminal/hello-dark.png is missing" in result.stderr
    assert "README.md: an asset region is not current." in result.stderr
    assert "Run make render-assets to update them." in result.stderr


@pytest.mark.actual_terminal
def test_renders_an_image_and_a_gif_in_a_real_terminal(project: pathlib.Path) -> None:
    write(project, "README.md", IMAGE_BLOCK + "\n" + GIF_BLOCK)
    result = subprocess.run(
        ["make", "render-assets"], cwd=project, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assets = project / "docs" / "assets" / "terminal"
    for name in ("hello-dark.png", "hello-light.png"):
        assert (assets / name).read_bytes().startswith(b"\x89PNG")
    for name in ("typing-dark.gif", "typing-light.gif"):
        assert (assets / name).read_bytes().startswith(b"GIF8")
    assert "@code-block-asset" in (project / "README.md").read_text(encoding="utf-8")
    checked = subprocess.run(
        ["make", "check-assets"], cwd=project, capture_output=True, text=True, check=False
    )
    assert checked.returncode == 0, checked.stderr
