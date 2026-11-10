# All Developer

Agent skill for the symbol of engineering.

**All Developer** is a mentor for coding agents. He speaks with the warmth of
a hero who teaches a student, and he holds every change to strict rules:

- names are full words, and one concept has one name;
- every text that a person reads is in Simplified Technical English;
- docstrings describe the current behavior for the people who use the code;
- a change that a person can see is checked in the real terminal or the real
  browser, not predicted from the code;
- nothing is committed without permission, and a missing answer is never a
  reason for a workaround;
- telemetry is off, and nothing about you or your project goes to an outside
  service that the task does not need.

His power is **Code for All**: software that is powerful enough for experts,
readable enough for beginners, and predictable enough for everyone.

## Two versions

| Version | File | Use it when |
| --- | --- | --- |
| The single file | [`ALL-DEVELOPER.md`](ALL-DEVELOPER.md) | You want the rules inside the `AGENTS.md` or `CLAUDE.md` of a project. It works with every agent. |
| The skill | [`skills/all-developer/`](skills/all-developer/) | Your agent supports skills. The skill is modular, has longer guides, and can add make hooks to a project. |

## Install

### The skill, with `npx skills`

```bash
DISABLE_TELEMETRY=1 npx skills add hsaeed3/all-developer --skill all-developer
```

Add `-g` to install it for every project, and `-a claude-code` to choose the
agent. `DISABLE_TELEMETRY=1` tells the tool to send no usage data.

### The skill, as a Claude Code plugin

```bash
/plugin marketplace add hsaeed3/all-developer
```

```bash
/plugin install all-developer@all-developer
```

### The skill, as a directory

Copy `skills/all-developer/` into the skills directory of your agent. For
Claude Code, that is `~/.claude/skills/` for every project, or
`.claude/skills/` for one project.

```bash
git clone https://github.com/hsaeed3/all-developer
```

```bash
cp -r all-developer/skills/all-developer ~/.claude/skills/
```

### The single file

Copy the contents of [`ALL-DEVELOPER.md`](ALL-DEVELOPER.md) into the
`AGENTS.md` or `CLAUDE.md` of your project. If the project has its own rule
for the same subject, the rule of the project wins.

## The skill

[`SKILL.md`](skills/all-developer/SKILL.md) says who All Developer is, gives
his laws, and lists his guides. The agent reads a guide only when the work
needs it.

| Guide | Subject |
| --- | --- |
| [`code.md`](skills/all-developer/references/code.md) | Names, calls, types and errors. |
| [`documentation.md`](skills/all-developer/references/documentation.md) | Docstrings, examples and the documentation site. |
| [`writing.md`](skills/all-developer/references/writing.md) | Simplified Technical English for every text that a person reads. |
| [`design-language.md`](skills/all-developer/references/design-language.md) | Spacing, type, color, layers, motion and icons. |
| [`ui-ux-checklist.md`](skills/all-developer/references/ui-ux-checklist.md) | The questions for every change that a person can see. |
| [`direct-verification.md`](skills/all-developer/references/direct-verification.md) | How to look at the real thing, with Playwright and Kitty. |
| [`repository-management.md`](skills/all-developer/references/repository-management.md) | Layout, the Makefile, commit hooks, continuous integration and commits. |
| [`toolchains.md`](skills/all-developer/references/toolchains.md) | The tools for Python, Rust, Python with Rust, and the web. |
| [`make-hooks.md`](skills/all-developer/references/make-hooks.md) | How All Developer adds a command to a project. |
| [`testing.md`](skills/all-developer/references/testing.md) | Tests, benchmarks and evals. |
| [`web-interface.md`](skills/all-developer/references/web-interface.md) | Runnable artifacts in one HTML file, and web applications. |
| [`terminal-assets.md`](skills/all-developer/references/terminal-assets.md) | Pictures of terminal programs, rendered from code blocks. |
| [`working-rules.md`](skills/all-developer/references/working-rules.md) | Permission, focus and honest reports. |

## Make hooks

A make hook is how All Developer gives a project a new ability: one target in
the `Makefile`, and one script in `scripts/` when the job needs one. He offers
a hook, and adds it only after you say yes. The skill ships the targets in
[`assets/make/`](skills/all-developer/assets/make/): formatting, linting,
type checking, spelling, tests and benchmarks for Python, Rust and the web, a
documentation site, and terminal assets.

**Terminal assets** renders a picture or a recording of a terminal program
from the code block beside it, in a real Kitty window:

````markdown
<!-- @code-block name="hello" type="image" height=5 -->
```python
print("hello")
```
````

```bash
make render-assets
```

The picture then shows below the block, in the light or the dark theme of the
reader. The script is
[`render_assets.py`](skills/all-developer/scripts/render_assets.py). It uses
only the Python standard library.

## Artifacts

All Developer can make a **runnable artifact**: one HTML file that you open,
with no install and no build. It uses raw HTML, Pico CSS from a CDN, and htmx
when the page talks to a server. A dashboard or a small application becomes
a make command, such as `make dashboard`, with a server that uses only the
standard library. Every file from a CDN has an exact version and an
integrity hash, and a page never tracks you. The templates are in
[`assets/web/`](skills/all-developer/assets/web/). For a full application, he
recommends React, TypeScript, Vite, Tailwind CSS and shadcn/ui.

## Layout

| Path | Contents |
| --- | --- |
| `ALL-DEVELOPER.md` | The single file version. |
| `skills/all-developer/SKILL.md` | The skill: the persona, the laws and the list of guides. |
| `skills/all-developer/references/` | The guides. |
| `skills/all-developer/assets/make/` | The make targets that a hook copies into a project. |
| `skills/all-developer/assets/web/` | The templates for runnable artifacts. |
| `skills/all-developer/scripts/` | The scripts that a hook copies into a project. |
| `.claude-plugin/` | The plugin and marketplace files for Claude Code. |
| `scripts/` | The development scripts of this repository. |
| `tests/` | The tests. |

## Development

Run `make help` to list the commands.

| Command | What it does |
| --- | --- |
| `make install` | Installs the development tools and the git hooks. |
| `make format` | Formats the Python source files. |
| `make lint` | Checks the Python source files. |
| `make lint-skill` | Checks the front matter, the links and the file lists of the skill. |
| `make typecheck` | Checks the types. |
| `make spellcheck` | Checks the spelling. |
| `make test` | Runs the tests. |
| `make test-terminal` | Runs the tests that render assets in a real Kitty window. |
| `make check` | Runs every check that continuous integration runs. |

## License

MIT. See [`LICENSE`](LICENSE).
