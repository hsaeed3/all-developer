"""
Render pictures and recordings of terminal programs from annotated Markdown code blocks.

Run it from the repository root with ``make render-assets`` (or
``python scripts/render_assets.py [NAME ...]``). A code block is rendered when the lines
directly above its opening fence are an HTML comment, which a Markdown page does not show.
The first line of the comment holds the options. The lines after it, if any, are the
actions, one on each line, run in order::

    <!-- @code-block name="pick-a-color" type="gif" height=8
    wait 1
    press down
    press enter
    -->
    ```python
    ...
    ```

The code runs as written in a real Kitty window, so an asset shows what a person sees.
Blocks in ``python`` run with the interpreter that runs this script. Blocks in ``sh`` and
``bash`` run with that shell. Every block is rendered once for each theme in ``THEMES``.

Options (all but ``name`` are optional):

- ``name="..."``: the start of the asset file names (lowercase letters, digits and
  hyphens), unique across all files.
- ``type="image"`` (a PNG, the default) or ``type="gif"``.
- ``height=ROWS``: the window height in rows (default 12). Every window is ``COLUMNS``
  columns wide, so every asset has the same width.
- ``duration=SECONDS``: how long a gif records. The default is the total of the ``wait``
  actions plus one second, and at least two seconds.

Actions (a position is a 0-based cell, the column first):

- ``wait SECONDS``
- ``press KEY [KEY ...]``: keys such as ``left``, ``space``, ``q`` or ``ctrl+s``.
- ``type TEXT``: the rest of the line, as typed text.
- ``paste TEXT``: the rest of the line, as a bracketed paste.
- ``click COLUMN ROW [left|right|middle]``
- ``drag COLUMN ROW COLUMN ROW``
- ``scroll up|down COLUMN ROW [COUNT]``

Mouse actions send xterm SGR mouse reports. A program receives them only when it has
turned on mouse reporting.

After a render, a region that shows the asset is written directly below each annotated
block. ``README.md`` gets a ``<picture>`` element, which GitHub resolves by the theme of the
reader. Every other file gets two Markdown images with ``#only-light`` and ``#only-dark``,
which Zensical and Material for MkDocs show by the color scheme. The region is replaced on
every run, and removed when the block loses its annotation.

``python scripts/render_assets.py --check`` renders nothing and starts no terminal. It
fails when an asset file is missing or a region is not current, so it can run in continuous
integration.

Requirements: Kitty 0.49 or newer, ``ffmpeg`` for gifs, and ``xvfb-run`` on Linux with no
display. The script uses only the standard library of Python 3.10 or newer. It reads the
Markdown files in ``DOCUMENTS`` and writes only those files and ``OUTPUT``. It opens no
network connection. It runs the code blocks of your own repository, so render only
Markdown that you trust.

Change the constants below ``CONFIGURATION`` to fit the repository.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent.parent

# CONFIGURATION

DOCUMENTS = ("README.md", "docs/**/*.md")
"""The Markdown files to read, as glob patterns from the repository root."""
OUTPUT = ROOT / "docs" / "assets" / "terminal"
"""Where the asset files go."""
COLUMNS = 100
"""The width of every window in columns."""
DEFAULT_HEIGHT = 12
MINIMUM_HEIGHT = 3
MAXIMUM_HEIGHT = 60
FONT_FAMILY = ""
"""The font of the windows, such as ``IBM Plex Mono``. Empty uses the default font of Kitty."""
FONT_SIZE = 12
WINDOW_PADDING = 10
"""The margin around the cells in points, so that text does not touch the edge of an asset."""
FRAMES_PER_SECOND = 12
STARTUP_TIMEOUT = 20
"""How many seconds a program has to draw its first text."""
STILL_SECONDS = 0.5
"""How long a window must stay unchanged before an image is taken of it."""
STILL_TIMEOUT = 5
"""The longest that an image waits for a still window."""
INTERPRETERS = {
    "python": (sys.executable,),
    "py": (sys.executable,),
    "sh": ("sh",),
    "bash": ("bash",),
}
"""The command that runs a code block, by the language of its fence."""


@dataclass(frozen=True)
class Theme:
    """The colors of one page theme, which its assets are drawn against."""

    name: str
    background: str
    foreground: str
    palette: tuple[str, ...]
    """The 16 ANSI colors as ``#rrggbb``, by ANSI color number."""
    dim_opacity: float
    """How much color dim text keeps, from 0 (invisible) to 1 (not dim)."""


THEMES = (
    Theme(
        "dark",
        background="#0d1117",
        foreground="#e6edf3",
        palette=(
            "#484f58",
            "#ff7b72",
            "#3fb950",
            "#d29922",
            "#58a6ff",
            "#bc8cff",
            "#39c5cf",
            "#b1bac4",
            "#6e7681",
            "#ffa198",
            "#56d364",
            "#e3b341",
            "#79c0ff",
            "#d2a8ff",
            "#56d4dd",
            "#ffffff",
        ),
        dim_opacity=0.6,
    ),
    Theme(
        "light",
        background="#ffffff",
        foreground="#1f2328",
        palette=(
            "#24292f",
            "#cf222e",
            "#116329",
            "#4d2d00",
            "#0969da",
            "#8250df",
            "#1b7c83",
            "#6e7781",
            "#57606a",
            "#a40e26",
            "#1a7f37",
            "#633c01",
            "#218bff",
            "#a475f9",
            "#3192aa",
            "#8c959f",
        ),
        dim_opacity=0.7,
    ),
)
"""The themes of every asset: the page colors and ANSI colors of GitHub, dark and light."""

# END OF CONFIGURATION

NAME_PATTERN = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
OPTION_PATTERN = re.compile(r'\s*(\w+)=("[^"]*"|\S+)')
FENCE_PATTERN = re.compile(r"```\s*(\w+)(?:\s.*)?")
REGION_PATTERN = re.compile(
    r'\n<!-- @code-block-asset name="[^"]*" -->\n.*?<!-- /@code-block-asset -->\n',
    re.DOTALL,
)
MOUSE_BUTTONS = {"left": 0, "middle": 1, "right": 2}
SCROLL_BUTTONS = {"up": 64, "down": 65}
KITTY_ENVIRONMENT = (
    "PATH",
    "HOME",
    "USER",
    "LOGNAME",
    "LANG",
    "LC_ALL",
    "DISPLAY",
    "XAUTHORITY",
    "XDG_RUNTIME_DIR",
    "DBUS_SESSION_BUS_ADDRESS",
    "LIBGL_ALWAYS_SOFTWARE",
    "VIRTUAL_ENV",
)
"""The only environment variables that the terminal and the code block receive."""


class RenderError(Exception):
    """A problem that a person can correct, told in plain sentences."""


def label(path: pathlib.Path) -> str:
    """Return a path from the repository root, as messages name it."""
    return path.relative_to(ROOT).as_posix()


@dataclass(frozen=True)
class Action:
    """One step of input: its kind (``wait``, ``press``, ``text`` or ``mouse``) and its values."""

    kind: str
    seconds: float = 0.0
    keys: tuple[str, ...] = ()
    text: str = ""
    is_paste: bool = False
    reports: tuple[str, ...] = ()
    pause: float = 0.05


@dataclass(frozen=True)
class Block:
    """One annotated code block of a Markdown file."""

    document: pathlib.Path
    line: int
    name: str
    kind: str
    height: int
    duration: float | None
    language: str
    code: str
    actions: tuple[Action, ...]
    closing_line: int

    def where(self) -> str:
        """Return the file and the line of the block, for messages."""
        return f"{label(self.document)} line {self.line}"

    def filename(self, theme: Theme) -> str:
        """Return the name of the asset file for a theme."""
        return f"{self.name}-{theme.name}.{'gif' if self.kind == 'gif' else 'png'}"

    def recording_seconds(self) -> float:
        """Return how long a gif of the block records."""
        if self.duration is not None:
            return self.duration
        return max(sum(action.seconds for action in self.actions) + 1.0, 2.0)


def fail(where: str, problem: str, expected: str, correction: str) -> RenderError:
    """Build an error: where it is, what is wrong, what was expected and what to do."""
    return RenderError(f"{where}: {problem}. Expected {expected}. {correction}")


def number(text: str, where: str, meaning: str, *, whole: bool = False) -> float:
    """Read a number that is zero or more, or fail with the place and the meaning."""
    try:
        value = int(text) if whole else float(text)
    except ValueError:
        value = -1
    if value < 0:
        kind = "a whole number" if whole else "a number"
        raise fail(
            where,
            f'{meaning} is "{text}"',
            f"{kind} that is zero or more",
            "Correct the value.",
        )
    return value


def mouse_report(button: int, column: int, row: int, *, is_release: bool = False) -> str:
    """Return the SGR mouse report for a 0-based cell (the report itself is 1-based)."""
    return f"\x1b[<{button};{column + 1};{row + 1}{'m' if is_release else 'M'}"


def parse_action(text: str, where: str) -> Action:
    """Read one action line."""
    verb, _, rest = text.strip().partition(" ")
    words = rest.split()

    def cell(index: int) -> tuple[int, int]:
        if len(words) < index + 2:
            raise fail(
                where,
                f'the action "{text.strip()}" has no position',
                "a column and a row",
                "Add the two numbers.",
            )
        return (
            int(number(words[index], where, "the column", whole=True)),
            int(number(words[index + 1], where, "the row", whole=True)),
        )

    if verb == "wait":
        return Action("wait", seconds=number(rest.strip(), where, "the wait"))
    if verb == "press" and words:
        return Action("press", keys=tuple(words))
    if verb in {"type", "paste"} and rest:
        return Action("text", text=rest, is_paste=verb == "paste")
    if verb == "click":
        column, row = cell(0)
        button = words[2] if len(words) > 2 else "left"
        if button not in MOUSE_BUTTONS:
            raise fail(
                where,
                f'the button is "{button}"',
                "left, right or middle",
                "Correct the button.",
            )
        code = MOUSE_BUTTONS[button]
        return Action(
            "mouse",
            reports=(
                mouse_report(code, column, row),
                mouse_report(code, column, row, is_release=True),
            ),
        )
    if verb == "drag":
        (start_column, start_row), (end_column, end_row) = cell(0), cell(2)
        steps = max(abs(end_column - start_column), abs(end_row - start_row), 1)
        moves = tuple(
            mouse_report(
                32,
                start_column + round((end_column - start_column) * step / steps),
                start_row + round((end_row - start_row) * step / steps),
            )
            for step in range(1, steps + 1)
        )
        return Action(
            "mouse",
            reports=(
                mouse_report(0, start_column, start_row),
                *moves,
                mouse_report(0, end_column, end_row, is_release=True),
            ),
            pause=0.03,
        )
    if verb == "scroll" and words and words[0] in SCROLL_BUTTONS:
        column, row = cell(1)
        count = int(number(words[3], where, "the count", whole=True)) if len(words) > 3 else 1
        return Action(
            "mouse",
            reports=(mouse_report(SCROLL_BUTTONS[words[0]], column, row),) * count,
        )
    raise fail(
        where,
        f'"{text.strip()}" is not an action',
        "wait, press, type, paste, click, drag or scroll, with its values",
        "Read the list of actions at the top of scripts/render_assets.py.",
    )


def parse_blocks(document: pathlib.Path, text: str) -> list[Block]:
    """Find the annotated code blocks in the text of a Markdown file."""
    lines = text.split("\n")
    blocks: list[Block] = []
    for index, line in enumerate(lines):
        fence = FENCE_PATTERN.fullmatch(line.rstrip())
        if fence is None or index == 0 or not lines[index - 1].strip().endswith("-->"):
            continue
        start = index - 1
        while start >= 0 and not lines[start].startswith("<!--"):
            start -= 1
        if start < 0 or not lines[start].startswith("<!-- @code-block "):
            continue
        where = f"{label(document)} line {start + 1}"
        comment = lines[start:index]
        first = comment[0][len("<!-- @code-block ") :].rstrip()
        if len(comment) == 1:
            option_text, action_lines = first.removesuffix("-->"), []
        elif first.endswith("-->") or comment[-1].strip() != "-->":
            raise fail(
                where,
                "the comment has actions but does not end with a line that holds only -->",
                "the options on the first line, one action on each line below, then -->",
                "Move the --> to its own line.",
            )
        else:
            option_text, action_lines = first, comment[1:-1]
        options = {
            match.group(1): match.group(2).strip('"')
            for match in OPTION_PATTERN.finditer(option_text)
        }
        unknown = sorted(set(options) - {"name", "type", "height", "duration"})
        if unknown:
            raise fail(
                where,
                f'"{unknown[0]}" is not an option',
                "name, type, height or duration",
                "Remove the option or correct its name.",
            )
        name = options.get("name", "")
        if not NAME_PATTERN.fullmatch(name):
            raise fail(
                where,
                f'the name is "{name}"',
                'lowercase letters, digits and hyphens, such as name="first-screen"',
                "Correct the name.",
            )
        kind = options.get("type", "image")
        if kind not in {"image", "gif"}:
            raise fail(where, f'the type is "{kind}"', "image or gif", "Correct the type.")
        height = int(
            number(options.get("height", str(DEFAULT_HEIGHT)), where, "the height", whole=True)
        )
        if not MINIMUM_HEIGHT <= height <= MAXIMUM_HEIGHT:
            raise fail(
                where,
                f"the height is {height}",
                f"a height from {MINIMUM_HEIGHT} to {MAXIMUM_HEIGHT} rows",
                "Correct the height.",
            )
        language = fence.group(1)
        if language not in INTERPRETERS:
            raise fail(
                where,
                f'the code block is in "{language}"',
                f"one of these languages: {', '.join(sorted(INTERPRETERS))}",
                "Change the language, or add it to INTERPRETERS in scripts/render_assets.py.",
            )
        closing = next(
            (later for later in range(index + 1, len(lines)) if lines[later].rstrip() == "```"),
            None,
        )
        if closing is None:
            raise fail(where, "the code block has no end", "a closing ``` line", "Add it.")
        actions = tuple(
            parse_action(action, f"{label(document)} line {start + 2 + offset}")
            for offset, action in enumerate(action_lines)
            if action.strip()
        )
        duration = (
            number(options["duration"], where, "the duration") if "duration" in options else None
        )
        waits = sum(action.seconds for action in actions)
        if duration is not None and duration < waits:
            raise fail(
                where,
                f"the duration is {duration:g} seconds but the actions wait {waits:g} seconds",
                "a duration of at least the total wait",
                "Increase the duration or decrease the waits.",
            )
        blocks.append(
            Block(
                document,
                start + 1,
                name,
                kind,
                height,
                duration,
                language,
                "\n".join(lines[index + 1 : closing]) + "\n",
                actions,
                closing,
            )
        )
    return blocks


def read_documents() -> list[Block]:
    """Read every file in ``DOCUMENTS`` and make sure that each name is used once."""
    blocks: list[Block] = []
    for pattern in DOCUMENTS:
        for document in sorted(ROOT.glob(pattern)):
            blocks.extend(parse_blocks(document, document.read_text(encoding="utf-8")))
    seen: dict[str, Block] = {}
    for block in blocks:
        if block.name in seen:
            raise fail(
                block.where(),
                f'the name "{block.name}" is already used in {seen[block.name].where()}',
                "a name that only one block has",
                "Change one of the two names.",
            )
        seen[block.name] = block
    return blocks


def asset_region(block: Block) -> str:
    """Return the generated region that shows the asset in the theme of the reader."""
    links = {
        theme.name: pathlib.Path(
            os.path.relpath(OUTPUT / block.filename(theme), block.document.parent)
        ).as_posix()
        for theme in THEMES
    }
    if block.document.name == "README.md":
        body = (
            "<picture>\n"
            f'  <source media="(prefers-color-scheme: dark)" srcset="{links["dark"]}">\n'
            f'  <img alt="{block.name}" src="{links["light"]}">\n'
            "</picture>\n"
        )
    else:
        body = (
            f"\n![{block.name}]({links['light']}#only-light)\n"
            f"![{block.name}]({links['dark']}#only-dark)\n\n"
        )
    return f'<!-- @code-block-asset name="{block.name}" -->\n{body}<!-- /@code-block-asset -->\n'


def updated_text(document: pathlib.Path) -> str:
    """Return the text of a file with a current region below every annotated block."""
    stripped = REGION_PATTERN.sub("", document.read_text(encoding="utf-8"))
    lines = stripped.split("\n")
    for block in reversed(parse_blocks(document, stripped)):
        lines[block.closing_line + 1 : block.closing_line + 1] = [
            "",
            *asset_region(block).rstrip("\n").split("\n"),
        ]
    return "\n".join(lines)


class Terminal:
    """
    One private Kitty window that runs one code block.

    The window has its own configuration, its own control socket and its own temporary
    directory. It never reads the Kitty configuration of the person and never selects a
    window that the person uses.
    """

    def __init__(self, block: Block, theme: Theme) -> None:
        """Start the window, run the code of the block in it, and set the theme colors."""
        executable = shutil.which(os.environ.get("RENDER_ASSETS_KITTY", "kitty"))
        application = pathlib.Path("/Applications/kitty.app/Contents/MacOS/kitty")
        if executable is None and application.is_file():
            executable = str(application)
        if executable is None:
            raise RenderError(
                "Cannot start a terminal because Kitty is not installed. Install Kitty 0.49 "
                "or newer, or set RENDER_ASSETS_KITTY to its path, and try again."
            )
        # The default temporary directory of macOS is too long for a Unix socket path.
        self._temporary = tempfile.TemporaryDirectory(prefix="render-assets-", dir="/tmp")
        directory = pathlib.Path(self._temporary.name)
        self._socket = directory / "control"
        self._result = directory / "result"
        self._log = directory / "kitty.log"
        source = directory / "program"
        source.write_text(block.code, encoding="utf-8")
        # The wrapper keeps the window open after the program ends, so that its last screen
        # stays. It stops the program when Kitty goes away.
        wrapper = directory / "run.py"
        wrapper.write_text(
            "import os, pathlib, subprocess, sys, time\n"
            "kitty = os.getppid()\n"
            "program = subprocess.Popen(sys.argv[2:])\n"
            "while program.poll() is None:\n"
            "    if os.getppid() != kitty:\n"
            "        program.kill()\n"
            "        sys.exit(1)\n"
            "    time.sleep(0.1)\n"
            "pathlib.Path(sys.argv[1]).write_text(str(program.returncode))\n"
            "while os.getppid() == kitty:\n"
            "    time.sleep(0.1)\n",
            encoding="utf-8",
        )
        overrides = [
            "allow_remote_control=socket-only",
            "remember_window_size=no",
            f"initial_window_width={COLUMNS}c",
            f"initial_window_height={block.height}c",
            f"window_padding_width={WINDOW_PADDING}",
            "window_margin_width=0",
            f"font_size={FONT_SIZE}",
            "shell_integration=disabled",
            "enable_audio_bell=no",
            f"dim_opacity={theme.dim_opacity}",
            *([f"font_family={FONT_FAMILY}"] if FONT_FAMILY else []),
        ]
        self._log_stream = self._log.open("wb")
        self.process = subprocess.Popen(
            [
                executable,
                "--config",
                "NONE",
                "--start-as=normal",
                "--listen-on",
                f"unix:{self._socket}",
                *[argument for override in overrides for argument in ("--override", override)],
                sys.executable,
                str(wrapper),
                str(self._result),
                *INTERPRETERS[block.language],
                str(source),
            ],
            cwd=ROOT,
            env={name: os.environ[name] for name in KITTY_ENVIRONMENT if name in os.environ},
            stdout=self._log_stream,
            stderr=subprocess.STDOUT,
        )
        try:
            # The first start on a new computer can take many seconds, because Kitty
            # builds its font caches.
            self.wait_until(self._socket.exists, timeout=30)
            self.wait_until(lambda: bool(self.command("ls")), timeout=30)
            background = int(theme.background.removeprefix("#"), 16)
            self.command(
                "set-colors",
                all=True,
                colors={
                    "background": background,
                    "foreground": int(theme.foreground.removeprefix("#"), 16),
                    "cursor": background,
                    "cursor_text_color": background,
                    **{
                        f"color{index}": int(color.removeprefix("#"), 16)
                        for index, color in enumerate(theme.palette)
                    },
                },
            )
        except BaseException:
            self.close()
            raise

    def command(self, name: str, **payload: object) -> object:
        """Send one Kitty remote control command to this window and return its data."""
        request: dict[str, object] = {"cmd": name, "version": [0, 26, 0], "payload": payload}
        if name == "screenshot":
            request["async"] = str(uuid.uuid4())
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(10)
            connection.connect(str(self._socket))
            connection.sendall(b"\x1bP@kitty-cmd" + json.dumps(request).encode() + b"\x1b\\")
            response = bytearray()
            while not response.endswith(b"\x1b\\"):
                chunk = connection.recv(65536)
                if not chunk:
                    raise RenderError(
                        f"Kitty closed its control socket during the command {name}. "
                        "Run the script again."
                    )
                response.extend(chunk)
        decoded = json.loads(response[12:-2])
        if not decoded.get("ok"):
            raise RenderError(
                f"Kitty could not do the command {name}: {decoded.get('error')}. "
                "Make sure that Kitty is version 0.49 or newer."
            )
        return decoded.get("data")

    def text(self, *, ansi: bool = False) -> str:
        """Read the screen of the window, with its styles when ``ansi`` is true."""
        return str(self.command("get-text", ansi=ansi, extent="screen"))

    def screenshot(self, path: pathlib.Path) -> None:
        """Save the pixels of the window as a PNG file."""
        self.command("screenshot", output_path=str(path.resolve()))

    def run(self, action: Action) -> None:
        """Do one action in the window."""
        if action.kind == "wait":
            time.sleep(action.seconds)
        elif action.kind == "press":
            self.command("send-key", keys=list(action.keys))
        elif action.kind == "text":
            self.command(
                "send-text",
                data="text:" + action.text,
                bracketed_paste="auto" if action.is_paste else "disable",
            )
        else:
            for report in action.reports:
                self.command("send-text", data="text:" + report)
                time.sleep(action.pause)

    def wait_until(self, condition: Callable[[], bool], *, timeout: float) -> None:
        """Wait for a condition, and fail with the log of Kitty when the time ends."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RenderError(
                    f"Kitty stopped with status {self.process.returncode}: "
                    f"{self._log.read_text(errors='replace').strip()}. Make sure that a "
                    "display is available."
                )
            try:
                if condition():
                    return
            except (FileNotFoundError, ConnectionRefusedError):
                pass
            time.sleep(0.02)
        raise RenderError(
            f"The terminal was not ready in {timeout:g} seconds. Log of Kitty: "
            f"{self._log.read_text(errors='replace').strip() or 'empty'}."
        )

    def wait_until_still(self) -> None:
        """Wait until the screen stops changing, or until ``STILL_TIMEOUT`` ends."""
        deadline = time.monotonic() + STILL_TIMEOUT
        last, unchanged_since = self.text(ansi=True), time.monotonic()
        while time.monotonic() < deadline:
            time.sleep(0.05)
            current = self.text(ansi=True)
            if current != last:
                last, unchanged_since = current, time.monotonic()
            elif time.monotonic() - unchanged_since >= STILL_SECONDS:
                return

    def exit_status(self) -> str:
        """Return the exit status of the program, or an empty string while it runs."""
        return self._result.read_text() if self._result.exists() else ""

    def close(self) -> None:
        """Close this window and remove its socket and its temporary files."""
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self._log_stream.close()
        self._temporary.cleanup()


def record(window: Terminal, block: Block, target: pathlib.Path) -> None:
    """Photograph the window at a fixed rate while the actions run, then build the gif."""
    frames: list[tuple[pathlib.Path, float]] = []
    problems: list[BaseException] = []
    stopped = threading.Event()
    with tempfile.TemporaryDirectory(prefix="render-assets-frames-") as directory:
        started = time.monotonic()

        def photograph() -> None:
            next_frame = started
            try:
                while not stopped.is_set():
                    path = pathlib.Path(directory) / f"frame-{len(frames):05d}.png"
                    taken = time.monotonic()
                    window.screenshot(path)
                    frames.append((path, taken - started))
                    next_frame += 1 / FRAMES_PER_SECOND
                    stopped.wait(max(0.0, next_frame - time.monotonic()))
            except BaseException as problem:
                problems.append(problem)

        thread = threading.Thread(target=photograph, daemon=True)
        thread.start()
        try:
            for action in block.actions:
                window.run(action)
            remaining = block.recording_seconds() - (time.monotonic() - started)
            if remaining > 0:
                time.sleep(remaining)
        finally:
            length = time.monotonic() - started
            stopped.set()
            thread.join()
        if problems or not frames:
            raise RenderError(
                f"{block.where()}: the recording of '{block.name}' failed"
                f"{f': {problems[0]}' if problems else ' with no frames'}. Run the script again."
            )
        listing = pathlib.Path(directory) / "frames.txt"
        entries = []
        for index, (path, start) in enumerate(frames):
            end = frames[index + 1][1] if index + 1 < len(frames) else length
            entries.append(f"file '{path}'\nduration {max(end - start, 0.01):.4f}")
        entries.append(f"file '{frames[-1][0]}'")
        listing.write_text("\n".join(entries) + "\n", encoding="utf-8")
        palette = pathlib.Path(directory) / "palette.png"
        base = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing)]
        try:
            subprocess.run(
                [*base, "-vf", "palettegen=stats_mode=diff", str(palette)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    *base,
                    "-i",
                    str(palette),
                    "-lavfi",
                    "paletteuse=dither=none:diff_mode=rectangle",
                    "-fps_mode",
                    "vfr",
                    "-loop",
                    "0",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            raise RenderError(
                "Cannot build a gif because ffmpeg is not installed. Install ffmpeg and try again."
            ) from None
        except subprocess.CalledProcessError as problem:
            raise RenderError(
                f"ffmpeg could not build {target.name}: {problem.stderr.strip()}. Correct "
                "the problem that it reports and try again."
            ) from problem


def render(block: Block, theme: Theme) -> pathlib.Path:
    """Run the block in a Kitty window with the colors of a theme and save its asset."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / block.filename(theme)
    window = Terminal(block, theme)
    try:
        try:
            window.wait_until(lambda: bool(window.text().strip()), timeout=STARTUP_TIMEOUT)
        except RenderError as problem:
            raise RenderError(
                f"{block.where()}: the code block '{block.name}' drew nothing in "
                f"{STARTUP_TIMEOUT} seconds (exit status: {window.exit_status() or 'none'}). "
                f"{problem} Run the code on its own and correct what it reports."
            ) from problem
        if block.kind == "image":
            window.wait_until_still()
            for action in block.actions:
                window.run(action)
            window.wait_until_still()
            window.screenshot(target)
        else:
            record(window, block, target)
    finally:
        window.close()
    return target


def image_width(path: pathlib.Path) -> int:
    """Return the width in pixels of a PNG or a gif, from its header."""
    header = path.read_bytes()[:26]
    if header.startswith(b"\x89PNG"):
        return int.from_bytes(header[16:20], "big")
    return int.from_bytes(header[6:8], "little")


def check(blocks: list[Block]) -> list[str]:
    """Return what is not current: missing asset files and Markdown regions to update."""
    problems = [
        f"{block.where()}: the asset {label(OUTPUT / block.filename(theme))} is missing."
        for block in blocks
        for theme in THEMES
        if not (OUTPUT / block.filename(theme)).exists()
    ]
    for pattern in DOCUMENTS:
        for document in sorted(ROOT.glob(pattern)):
            if updated_text(document) != document.read_text(encoding="utf-8"):
                problems.append(f"{label(document)}: an asset region is not current.")
    return problems


def main() -> int:
    """Render the named blocks, or all blocks with no names, and write their regions."""
    parser = argparse.ArgumentParser(
        description="Render terminal pictures and recordings from annotated Markdown code blocks."
    )
    parser.add_argument("names", nargs="*", metavar="NAME", help="render only these blocks")
    parser.add_argument(
        "--check",
        action="store_true",
        help="render nothing, and fail when an asset or a region is not current",
    )
    arguments = parser.parse_args()
    try:
        blocks = read_documents()
        if arguments.check:
            problems = check(blocks)
            for problem in problems:
                sys.stderr.write(f"{problem}\n")
            if problems:
                sys.stderr.write("Run make render-assets to update them.\n")
            return 1 if problems else 0
        if sys.platform == "linux" and not os.environ.get("DISPLAY"):
            display_runner = shutil.which("xvfb-run")
            if display_runner is None:
                raise RenderError(
                    "Cannot render with no display. Install xvfb, or set DISPLAY to an X "
                    "display, and try again."
                )
            os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
            return subprocess.run(
                [
                    display_runner,
                    "--auto-servernum",
                    "--server-args=-screen 0 1920x1080x24",
                    sys.executable,
                    *sys.argv,
                ],
                check=False,
            ).returncode
        names = [block.name for block in blocks]
        unknown = [name for name in arguments.names if name not in names]
        if unknown:
            raise RenderError(
                f"No annotated code block has the name '{unknown[0]}'. The names are: "
                f"{', '.join(names) or 'none, because no block has an annotation'}."
            )
        for block in blocks:
            if arguments.names and block.name not in arguments.names:
                continue
            for theme in THEMES:
                sys.stdout.write(f"{block.name}: {label(render(block, theme))}\n")
        widths = {
            path.name: image_width(path)
            for block in blocks
            for path in (OUTPUT / block.filename(theme) for theme in THEMES)
            if path.exists()
        }
        if len(set(widths.values())) > 1:
            listing = ", ".join(f"{name} is {width}" for name, width in sorted(widths.items()))
            raise RenderError(
                f"The assets do not all have the same width in pixels ({listing}). Render "
                "all of them again on one display: run the script with no names."
            )
        for pattern in DOCUMENTS:
            for document in sorted(ROOT.glob(pattern)):
                text = updated_text(document)
                if text != document.read_text(encoding="utf-8"):
                    document.write_text(text, encoding="utf-8")
                    sys.stdout.write(f"updated {label(document)}\n")
    except RenderError as problem:
        sys.stderr.write(f"{problem}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
