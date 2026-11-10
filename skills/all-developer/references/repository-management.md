# Repository Management

A hero prepares before the fight. This guide says what a well-kept repository
contains, and when All Developer recommends it. The tools for each language
are in [toolchains](toolchains.md). Tests, benchmarks and evals are in
[testing](testing.md).

## When to recommend

- Recommend foundations **at the start**: when you outline a plan, create a
  repository, a package or a service, or start a new area of a project.
- Put the recommendation in the plan, as its own short part. For each item,
  say what it is and what it protects. The person decides.
- **Do not interrupt work in progress.** In the middle of a task, do not add
  tooling, and do not stop to suggest it. Use what the project has.
- If a missing foundation is a real risk to the current task, say so in one
  sentence at the end of your report. Do not act on it without a decision.
- If the project already has a tool for a job, use it. Do not propose a
  second tool for the same job.
- Fit the list to the task. A script of one file needs a formatter and one
  test. A library that other people install needs all of this guide.

## Layout

- One repository has one workspace for each language: one Cargo workspace,
  one uv workspace, one pnpm workspace.
- Use the same directory names in every project:

  | Directory | Contents |
  | --- | --- |
  | `crates/` | Rust crates. |
  | `packages/` | Packages that people install. |
  | `scripts/` | Development scripts that the Makefile runs. |
  | `tests/` | Tests of the root package. |
  | `benchmarks/` | Benchmarks. |
  | `examples/` | One runnable program for each feature. |
  | `docs/` | The documentation site. |
  | `.github/workflows/` | Continuous integration. |

- The root has a `README.md`, a `LICENSE`, a `CONTRIBUTING.md`, and one
  instruction file for agents (`AGENTS.md`, with a `CLAUDE.md` that contains
  only `@AGENTS.md`).
- Commit the lock files (`uv.lock`, `Cargo.lock`, `pnpm-lock.yaml`). Install
  from them (`uv sync --frozen`), so that every computer gets the same
  versions.
- Never edit a generated file by hand. Generate it with a script in
  `scripts/`, and check in continuous integration that it is current.

## The Makefile is the one entry point

Every job has one `make` command. A person, an agent, a commit hook and
continuous integration all run the same commands. Nobody must remember the
flags of a tool.

```makefile
.DEFAULT_GOAL := help
sources = src tests scripts

.PHONY: .uv  ## Make sure that uv is installed
.uv:
	@uv -V > /dev/null 2>&1 || (echo "uv is not installed. Install it from https://docs.astral.sh/uv/getting-started/installation/"; exit 1)

.PHONY: install  ## Install the project, the development tools and the git hooks
install: .uv
	uv sync --frozen --all-groups
	uv run --no-sync prek install --install-hooks

.PHONY: format  ## Format the source files
format: .uv
	uv run --no-sync ruff check --fix $(sources)
	uv run --no-sync ruff format $(sources)

.PHONY: lint  ## Check the source files
lint: .uv
	uv run --no-sync ruff check $(sources)
	uv run --no-sync ruff format --check $(sources)

.PHONY: typecheck  ## Check the types
typecheck: .uv
	uv run --no-sync basedpyright

.PHONY: spellcheck  ## Check the spelling
spellcheck: .uv
	uv run --no-sync codespell

.PHONY: test  ## Run the tests
test: .uv
	uv run --no-sync pytest tests

.PHONY: check  ## Run every check that continuous integration runs
check: lint spellcheck typecheck test

.PHONY: help  ## List the commands
help:
	@grep -E '^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
```

The rules of this pattern:

- **`make help` is the default goal.** Each command has a `## ` description
  on its `.PHONY` line, and `help` prints them. A command with no
  description is internal, and its name starts with a period (`.uv`).
- **A missing tool gives an error that teaches.** A guard such as `.uv` says
  what is missing and where to get it.
- **The names are the same in every project:** `install`, `format`, `lint`,
  `typecheck`, `spellcheck`, `test`, `benchmark`, `check`, `clean`,
  `docs-build`, `docs-serve`. A variant adds a suffix: `lint-rust`,
  `test-coverage`, `format-all`.
- **`make check` is the gate.** It runs everything that continuous
  integration runs. If it passes on a computer, the pipeline passes.
- **`ARGS` passes options through:** `make test ARGS="-k cursor"`.
- **A workspace fans out.** The root Makefile runs the same command in each
  package (`$(MAKE) -C packages/$$package test`), and each package has the
  same command names.
- **Scripts stay in `scripts/`.** A job that needs more than a few shell
  lines is a script in `scripts/`, and the Makefile runs it. A script uses
  the standard library where it can.

## Commit hooks

Use hooks so that a bad commit stops on the computer of the author, not in
the pipeline. The hooks run the same `make` commands.

- Use [prek](https://github.com/j178/prek), a fast runner for
  `.pre-commit-config.yaml` files. `make install` installs the hooks with
  `prek install --install-hooks`.
- Fast checks run before each commit. The full static gate runs before each
  push. Tests run in continuous integration.

```yaml
default_install_hook_types: [pre-commit, pre-push]

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: no-commit-to-branch # no direct commit to the main branch
      - id: check-yaml
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.1
    hooks:
      - id: codespell

  - repo: local
    hooks:
      - id: lint
        name: Lint (make lint)
        entry: make lint
        language: system
        pass_filenames: false
      - id: check
        name: Check (lint, spelling and types)
        entry: make lint spellcheck typecheck
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```

- Pin each hook to a version (`rev`). Update the versions on purpose, in
  their own change.
- Add hooks for what the repository contains: a Markdown linter for
  documentation, a workflow linter (`zizmor`) for GitHub Actions, a TOML
  linter (`tombi`) for configuration.
- Never skip a hook (`--no-verify`) to make a commit pass. Correct the
  cause.

## Continuous integration

- The pipeline runs `make check`, on every platform and language version
  that the project supports.
- It also checks that generated files are current (`--check` options), that
  the documentation builds, and that the title of a pull request has the
  correct format.
- Pin each action to a full commit hash, with the version in a comment.
- Give each workflow the least permissions that it needs
  (`permissions: contents: read`).
- Keep slow suites (a real terminal, a real browser, benchmarks) as separate
  jobs, and upload what they saw (screens, logs) as artifacts.

## Branches, commits and pull requests

- Never commit to the main branch directly. Make a branch named
  `<type>/<short-description>` from the latest main branch.
- Commit and pull request titles use `<type>(<scope>): <summary>`. The scope
  is optional. The types are `feat`, `fix`, `docs`, `refactor`, `perf`,
  `test`, `build`, `ci`, `chore` and `release`. Write the summary in the
  imperative mood, in lowercase, with no period at the end. Add `!` for an
  incompatible change.
- Keep one pull request to one result. Squash it when you merge, so that its
  title becomes the commit message.
- A pull request says what changed and why (**Summary**), the exact commands
  that were run (**Validation**), and what a reviewer must know (**Notes**).
- A pull request with AI-generated or AI-assisted content says so, and names
  the tool and the exact model. A commit that an agent writes ends with one
  `Co-Authored-By:` trailer. Never add session links or session identifiers.
- All of this needs the permission of the person. See
  [working rules](working-rules.md).

## Versions and releases

- One place holds each version number. A script (`make set-version`) writes
  it to every other file, and `make version-check` proves that they agree.
- Generate the change history from the release notes. Do not write it by
  hand.
- A release is its own pull request, with nothing else in it.
