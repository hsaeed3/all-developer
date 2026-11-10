# Documentation

Write docstrings and documentation for the **people who use the software**,
never for the people who maintain it.

- Describe what a thing **is, does, accepts and returns**, and when a person
  uses it. Start with a summary of one line.
- **Never explain changes.** Do not write "now does X", "previously", "used
  to", "fixed", "regression", "no longer" or other history. A docstring
  describes the current behavior as if it was always that way. History belongs
  in commits and changelogs.
- Never mention internal details, refactors, bugs, workarounds or the reasons
  of maintainers. The exception is a detail that changes how the person must
  call or think about the interface.
- Document errors, units, ranges and defaults when they change how a person
  uses the interface.
- Add a short example when it helps a person start. Keep each example minimal
  and runnable. Where the project can, run the examples as tests.
- Use the documentation format of the language and of the project for
  sections, code and cross-references. Make each cross-reference a link that a
  person can follow. Use one format everywhere.
- If a thing is a direct binding of an upstream item, say so. Link to the
  exact upstream item, at the version that the project pins.
- A comment says why the code is as it is, when the code cannot say it. A
  comment does not repeat the code and does not tell history.

## The documentation site

- Keep the documentation in the repository, in `docs/`, and build it with one
  command: `make docs-build`. Serve it for a preview with `make docs-serve`.
- Build in strict mode, so that a broken link or a missing page stops the
  build. Run the build in continuous integration.
- For a Python project, [Zensical](https://github.com/zensical/zensical) builds the site from
  Markdown and one `zensical.toml` file. See [toolchains](toolchains.md).
- Generate the API reference from the source and its docstrings. Do not write
  it by hand. Put the generator in `scripts/`, and run it with a `--check`
  option in continuous integration, so that a stale reference fails.
- Never edit a generated file by hand. Say at the top of the file which
  command makes it.

## Examples are tests

- Every example in a docstring and in the documentation runs as a test. An
  example that cannot run is a defect.
- Keep one runnable program for each feature in `examples/`, with a test that
  runs it and checks what it shows.
- An example imports only from the public interface.

## Pictures of terminal programs

Do not paste a screenshot that you made by hand. A picture of a terminal
program comes from the code block beside it, rendered in a real terminal with
`make render-assets`. Then the picture cannot become stale. See
[terminal assets](terminal-assets.md).
