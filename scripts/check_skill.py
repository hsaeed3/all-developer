"""
Check the structure of the skill in ``skills/all-developer``.

Run it from the repository root with ``make lint-skill``. It fails when:

- the front matter of ``SKILL.md`` has no valid ``name`` or ``description``;
- ``SKILL.md`` has more than 500 lines;
- a relative link in a Markdown file of the skill leads to no file;
- a file in ``references/``, ``assets/make/`` or ``scripts/`` of the skill is not named
  in ``SKILL.md``;
- a make target in a snippet has no description;
- the versions in ``pyproject.toml`` and ``.claude-plugin/plugin.json`` differ.

The script uses only the standard library. It reads files and writes nothing.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "all-developer"
MAXIMUM_LINES = 500
MAXIMUM_DESCRIPTION = 1024
NAME_PATTERN = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
LINK_PATTERN = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
FENCE_PATTERN = re.compile(r"^(`{3,})")


def front_matter(text: str) -> dict[str, str]:
    """Return the fields of the YAML front matter, with folded values joined."""
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    fields: dict[str, str] = {}
    key = ""
    for line in text[4 : text.index("\n---\n", 4)].split("\n"):
        match = re.fullmatch(r"([a-z-]+):\s*(.*)", line)
        if match:
            key = match.group(1)
            fields[key] = "" if match.group(2) in {">", "|"} else match.group(2)
        elif key and line.startswith(" "):
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    return fields


def prose(text: str) -> str:
    """Return the text of a Markdown file with its fenced code blocks removed."""
    kept: list[str] = []
    fence = ""
    for line in text.split("\n"):
        match = FENCE_PATTERN.match(line.strip())
        if match and not fence:
            fence = match.group(1)
        elif fence and line.strip() == fence:
            fence = ""
        elif not fence:
            kept.append(line)
    return "\n".join(kept)


def check() -> list[str]:
    """Return every problem of the skill, as one sentence each."""
    problems: list[str] = []
    skill_file = SKILL / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    fields = front_matter(text)
    name = fields.get("name", "")
    if not NAME_PATTERN.fullmatch(name) or name != SKILL.name:
        problems.append(
            f'SKILL.md: the name is "{name}". Expected "{SKILL.name}", the name of its '
            "directory. Correct the front matter."
        )
    description = fields.get("description", "")
    if not 1 <= len(description) <= MAXIMUM_DESCRIPTION:
        problems.append(
            f"SKILL.md: the description has {len(description)} characters. Expected 1 to "
            f"{MAXIMUM_DESCRIPTION}. Make it shorter."
        )
    lines = text.count("\n") + 1
    if lines > MAXIMUM_LINES:
        problems.append(
            f"SKILL.md: the file has {lines} lines. Expected {MAXIMUM_LINES} or fewer. "
            "Move details into a file in references/."
        )
    for document in sorted(SKILL.rglob("*.md")):
        for link in LINK_PATTERN.findall(prose(document.read_text(encoding="utf-8"))):
            if "://" in link or link.startswith("mailto:"):
                continue
            if not (document.parent / link).exists():
                problems.append(
                    f"{document.relative_to(ROOT)}: the link to {link} leads to no file. "
                    "Correct the path or add the file."
                )
    for directory in ("references", "assets/make", "scripts"):
        for path in sorted((SKILL / directory).iterdir()):
            if path.is_file() and f"{directory}/{path.name}" not in text:
                problems.append(
                    f"SKILL.md: {directory}/{path.name} is not named in the file. Add it to "
                    "the table of guides or the table of make hooks."
                )
    for snippet in sorted((SKILL / "assets" / "make").glob("*.mk")):
        for line in snippet.read_text(encoding="utf-8").split("\n"):
            if line.startswith(".PHONY:") and "## " not in line:
                problems.append(
                    f"{snippet.relative_to(ROOT)}: the target in '{line}' has no "
                    "description. Add '## ' and what the command does."
                )
    project_version = re.search(
        r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M
    )
    plugin_version = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    ).get("version")
    if project_version is None or project_version.group(1) != plugin_version:
        problems.append(
            "The versions in pyproject.toml and .claude-plugin/plugin.json differ. Set both "
            "to the same version."
        )
    return problems


def main() -> int:
    """Print every problem and return 1 when there is one."""
    problems = check()
    for problem in problems:
        sys.stderr.write(f"{problem}\n")
    if not problems:
        sys.stdout.write("The skill is correct.\n")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
