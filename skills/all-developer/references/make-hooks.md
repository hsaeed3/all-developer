# Make Hooks

A **make hook** is a command that All Developer adds to a project: one target
in the `Makefile`, and one script in `scripts/` when the job needs more than a
few shell lines. It is the only way that All Developer gives a project a new
ability. After it exists, the person, an agent, a commit hook and continuous
integration all run the same command.

## The contract

0. **Plain `make` shows the help.** The default goal of every `Makefile`
   that you make or change is `help`. It lists each command with its
   description. Plain `make` never builds, installs, deletes or starts
   anything. If a `Makefile` has a different default goal, tell the person
   and offer to change it. Do not change it without a yes.
1. **Offer, do not add.** Offer a make hook when you plan new work (see
   [repository management](repository-management.md)), or when the person
   asks for one. Say what the command does and what it needs. Add it only
   after the person says yes.
2. **Touch only the `Makefile` and `scripts/`.** A make hook does not add
   source code, does not move files, and does not change other settings.
3. **A tool that the hook needs is its own question.** If a hook needs a
   development dependency (for example `ruff`) or a setting in a
   configuration file, name it and ask. Add it with the package manager of
   the project (`uv add --dev ruff`), never by hand in the lock file.
4. **Use the snippets as they are.** The snippets are in `assets/make/` of
   this skill. Copy the targets that the project needs into its `Makefile`.
   Change only the values that the snippet tells you to change (for example
   `sources`). Keep the names of the commands.
5. **Do not replace what exists.** If the `Makefile` already has a target
   with that name, keep it. Show the difference and let the person decide.
6. **A script is copied, not written again.** Copy a script from `scripts/`
   of this skill into `scripts/` of the project, with no changes outside its
   `CONFIGURATION` part. Read the script before you copy it, and tell the
   person what it reads, writes and runs.
7. **Prove it.** Run the new command. Run `make help` and make sure that the
   command shows with its description. Report the output.
8. **Use it from then on.** After a make hook exists, always do that job
   through `make`. Do not call the tool directly with other options.

## The catalog

Choose the snippets for the languages of the project. Each one follows the
Makefile pattern in [repository management](repository-management.md).

| Snippet | Commands | For |
| --- | --- | --- |
| `assets/make/base.mk` | `help` (the default goal), `check`, and `DO_NOT_TRACK=1` for every command | Every project. |
| `assets/make/python.mk` | `install`, `format`, `lint`, `typecheck`, `spellcheck`, `test`, `test-coverage`, `benchmark`, `rebuild-lockfiles`, `clean` | Python with uv. |
| `assets/make/rust.mk` | `format`, `lint`, `typecheck`, `test`, `benchmark`, `clean` | Rust with Cargo. |
| `assets/make/python-rust.mk` | `rebuild-rust`, `rebuild`, `build-release`, `lint-rust`, `test-rust`, `lint-all`, `format-all`, `benchmark-release` | A Python package with a Rust extension. Use it with `python.mk`. |
| `assets/make/web.mk` | `install`, `serve`, `format`, `lint`, `typecheck`, `test`, `test-browser`, `build`, `clean` | A web interface with pnpm and Vite. |
| `assets/make/docs.mk` | `docs-build`, `docs-serve` | A documentation site with Zensical. |
| `assets/make/app.mk` | `dashboard` | A runnable dashboard or application. See [web interface](web-interface.md). |
| `assets/make/render-assets.mk` | `install-terminal`, `render-assets`, `check-assets` | Pictures of terminal programs. See [terminal assets](terminal-assets.md). |

## Telemetry is off

`base.mk` exports `DO_NOT_TRACK=1`, so every command that `make` runs tells
its tools to send no usage data. Some tools do not read that variable and
have their own setting. When you add a hook for such a tool, turn off its
usage data in the `Makefile` too, and tell the person. See
[working rules](working-rules.md).

## What each kind of command does

| Command | Job | Python | Rust | Web |
| --- | --- | --- | --- | --- |
| `format` | Change the files to the one format. | `ruff check --fix`, `ruff format` | `cargo fmt` | `biome check --write` |
| `lint` | Check the format and the code, and change nothing. | `ruff check`, `ruff format --check` | `cargo fmt --check`, `cargo clippy -D warnings` | `biome check` |
| `typecheck` | Check the types. | `basedpyright` | `cargo check` | `tsc --noEmit` |
| `spellcheck` | Check the spelling. | `codespell` | `codespell` | `codespell` |
| `test` | Run the tests. | `pytest` | `cargo test` | `vitest run` |
| `benchmark` | Measure speed on an optimized build. | `pytest --benchmark-enable` | `cargo bench` | The project's own |
| `check` | The gate: everything above that continuous integration runs. | | | |

## Project with more than one language

- Keep one `Makefile` at the root. Its commands cover every language:
  `lint-all` runs `lint` and `lint-rust`.
- The main language owns the plain names (`lint`, `test`). Each other
  language adds a suffix (`lint-rust`, `test-rust`).
- In a workspace with packages, each package has its own `Makefile` with the
  same command names, and the root runs them in turn.

## A new make hook

If the person asks for a command that the catalog does not have:

- give it a name that says its job, in the style of the others
  (`docs-build`, `test-terminal`, `set-version`);
- add a `## ` description, so that `make help` lists it;
- put real logic in a script in `scripts/`, with a docstring at the top that
  says what it does, what it reads and what it writes;
- make the script fail with an error that teaches recovery (see
  [code](code.md));
- prefer the standard library, so that the script adds no dependency.
