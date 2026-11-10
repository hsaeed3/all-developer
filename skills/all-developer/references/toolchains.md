# Toolchains

These are the tools that All Developer recommends for each language, and how
he uses them. They are recommendations for new work. If a project already has
a tool for a job, use that tool. Each job is a `make` command (see
[make hooks](make-hooks.md)).

## Python

| Job | Tool | Notes |
| --- | --- | --- |
| Project and dependencies | [uv](https://docs.astral.sh/uv/) | One `pyproject.toml`, one `uv.lock`. |
| Format and lint | [Ruff](https://docs.astral.sh/ruff/) | `ruff format` and `ruff check`. |
| Types | [basedpyright](https://docs.basedpyright.com/) | Strict where the project can. |
| Docstrings | [Griffe](https://mkdocstrings.github.io/griffe/) | `griffe dump` finds a docstring that does not parse. |
| Spelling | [codespell](https://github.com/codespell-project/codespell) | |
| Tests | [pytest](https://docs.pytest.org/) | With `pytest-cov` for coverage. |
| Benchmarks | `pytest-benchmark`, [CodSpeed](https://codspeed.io/) in the pipeline | See [testing](testing.md). |
| Commit hooks | [prek](https://github.com/j178/prek) | Reads `.pre-commit-config.yaml`. |
| Documentation | [Zensical](https://github.com/zensical/zensical) | One `zensical.toml`. |

How to use them:

- Start a project with `uv init`. Add a dependency with `uv add <name>`, and
  a development tool with `uv add --dev <name>` or `uv add --group <group>
  <name>`. Never edit `uv.lock` by hand.
- Put development tools in dependency groups (`dev`, `docs`), so that a
  person who installs the package does not get them.
- Install with `uv sync --frozen`. Run tools with `uv run --no-sync <tool>`,
  so that a command never changes the environment as a side effect.
- Update on purpose with `uv lock --upgrade` (`make rebuild-lockfiles`), in
  its own change.
- Configure Ruff in `pyproject.toml` or `ruff.toml`. Turn on the docstring
  rules with one convention (`google`), and one quote style.
- Use a `src/` layout for a package that people install. Ship a `py.typed`
  file, so that the types reach the people who use the package.
- Optional features are extras. Import an optional package lazily, and when
  it is missing, name the command that installs it
  (`pip install "name[extra]"`).

## Rust

| Job | Tool | Notes |
| --- | --- | --- |
| Project and dependencies | Cargo | One workspace, crates in `crates/`. |
| Format | `cargo fmt` | |
| Lint | `cargo clippy` | `-D warnings`, with the `pedantic` group. |
| Types | `cargo check` | On every target that the project supports. |
| Tests | `cargo test` | |
| Benchmarks | [Criterion](https://github.com/bheisler/criterion.rs) with `cargo bench` | |

How to use them:

- Set the lints once, for the workspace, in the root `Cargo.toml`:

  ```toml
  [workspace.lints.rust]
  unsafe_code = "deny"

  [workspace.lints.clippy]
  pedantic = { level = "warn", priority = -1 }
  ```

  Each crate then has `[lints] workspace = true`.
- Put shared dependency versions in `[workspace.dependencies]`.
- Keep the core logic in crates with no platform code, so that their tests
  run anywhere. Platform code lives in thin crates around them.
- If the project supports a second target (WebAssembly, Windows), run
  `cargo clippy --target <target>` for it too.
- Commit `Cargo.lock` for an application and for a workspace that builds
  binaries or extensions.

## Python with Rust

Use [PyO3](https://pyo3.rs/) for the bindings and
[maturin](https://www.maturin.rs/) to build them.

- **Keep the engine free of Python.** The logic lives in pure Rust crates
  that do not depend on PyO3. One thin crate for each Python package holds
  only the bindings. Then the engine has fast pure Rust tests, and can also
  build for other targets.
- **Layout.** Rust crates in `crates/`, Python distributions in
  `packages/<name>/`, one Cargo workspace and one uv workspace at the root.
  Each package has a `pyproject.toml` with `build-backend = "maturin"`.
- **Stubs are the public interface.** The compiled module has a `.pyi` stub
  file with full docstrings. The package's `__init__.py` exports every public
  name again, and people never import the private compiled module.
- **A Rust change needs a rebuild.** After a change to Rust code, run
  `make rebuild-rust` (`maturin develop --uv`) before the Python tests. A
  change to Python code only does not need it.
- **Debug builds say nothing about speed.** `maturin develop` makes a debug
  build. Benchmarks run only against `maturin develop --uv --release`
  (`make build-release`).
- **Names stay full words in Python.** A direct binding of a Rust item uses
  a full-word Python name, and its docstring says which item it maps to (see
  [documentation](documentation.md)).
- **Run the examples of the stubs as tests.**

## Web

See [web interface](web-interface.md) for the choice of components. The
tools:

| Job | Tool | Notes |
| --- | --- | --- |
| Packages | [pnpm](https://pnpm.io/) | One `pnpm-lock.yaml`. |
| Development server and build | [Vite](https://vite.dev/) | Shows each change at once. |
| Language | TypeScript | `strict`, with `noUncheckedIndexedAccess`. |
| Format and lint | [Biome](https://biomejs.dev/) | One tool for both. |
| Unit tests | [Vitest](https://vitest.dev/) | |
| Browser tests | [Playwright](https://playwright.dev/) | See [direct verification](direct-verification.md). |

- Use `unknown` and real types, never `any`.
- Install from the lock file (`pnpm install --frozen-lockfile`).

## Documentation site

- Build the site with Zensical: `zensical build --clean --strict`
  (`make docs-build`) and `zensical serve` (`make docs-serve`).
- Keep its tool in a `docs` dependency group, and run it with
  `uv run --only-group docs`.
- Generate the API reference from the source. See
  [documentation](documentation.md).

## Other languages

For a language that is not in this guide, find the standard tool for each
job in the first table of [make hooks](make-hooks.md): format, lint, types,
spelling, tests and benchmarks. Read the current documentation of the tool
before you recommend its options. Then give each job the same `make` name.
