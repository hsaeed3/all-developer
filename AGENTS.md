# Repository Rules for `all-developer`

This repository holds the All Developer agent skill. The rules of All
Developer apply to work on this repository too: read
[`ALL-DEVELOPER.md`](ALL-DEVELOPER.md) and obey it.

## Layout

- `ALL-DEVELOPER.md`: the single file version, which a person copies into an
  `AGENTS.md` or a `CLAUDE.md`. It stands alone, and it does not mention the
  skill.
- `skills/all-developer/SKILL.md`: who All Developer is, his laws, the list
  of guides and the list of make hooks. Keep it short. Details go into a
  guide.
- `skills/all-developer/references/`: one guide for each subject.
- `skills/all-developer/assets/make/`: the make targets that a hook copies
  into a project.
- `skills/all-developer/scripts/`: the scripts that a hook copies into a
  project. A script uses only the standard library, opens no network
  connection, and says in its docstring what it reads, writes and runs.
- `scripts/`: the development scripts of this repository.
- `tests/`: the tests.

## Commands

Run `make help` to list the commands. Run `make format` and then `make check`
before you ask to commit. Run `make test-terminal` after a change to
`skills/all-developer/scripts/render_assets.py`.

## Rules

- A rule that is in both versions says the same thing in both. When you
  change a rule in a guide, change it in `ALL-DEVELOPER.md` too, and the
  reverse.
- Every file in `references/`, `assets/make/` and `scripts/` of the skill is
  named in `SKILL.md`. `make lint-skill` checks this.
- Every text in this repository obeys the writing rules in
  `skills/all-developer/references/writing.md`.
- A command or a tool option in a guide is one that you ran or read in the
  documentation of the tool. Do not write one from memory.
- Commit only with the permission of the maintainer. A commit that an agent
  writes ends with one `Co-Authored-By:` trailer, with no session link.
