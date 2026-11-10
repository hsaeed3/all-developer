# Terminal Assets

A picture of a terminal program in a README or on a documentation page must
show what a person sees, and must never become stale. So the picture is not
made by hand. It is **rendered from the code block beside it**, in a real
Kitty window, with one command: `make render-assets`.

This is a [make hook](make-hooks.md). It has one script,
`scripts/render_assets.py`, and three commands.

| Command | What it does |
| --- | --- |
| `make install-terminal` | Installs Kitty, ffmpeg and, on Linux, the tools for a virtual display. |
| `make render-assets` | Renders every annotated code block. `ARGS="name other-name"` renders only those. |
| `make check-assets` | Renders nothing. Fails when an asset is missing or a Markdown region is not current. |

## Add it to a project

Follow the contract in [make hooks](make-hooks.md):

1. Offer it when the project shows a terminal program in its documentation.
   Tell the person what it needs: Kitty 0.49 or newer, `ffmpeg` for gifs, and
   `xvfb-run` on Linux with no display. Wait for a yes.
2. Read `scripts/render_assets.py` of this skill. Copy it to
   `scripts/render_assets.py` of the project, with no changes.
3. Copy the three targets from `assets/make/render-assets.mk` into the
   `Makefile` of the project.
4. If the project needs other values, change only the constants between
   `CONFIGURATION` and `END OF CONFIGURATION` in the script: the Markdown
   files to read (`DOCUMENTS`), the output directory (`OUTPUT`), the width
   (`COLUMNS`), the font, and the colors (`THEMES`).
5. Run `make render-assets`. Open the assets and look at them.
6. Add `make check-assets` to the gate, if the person wants it.

Touch nothing else. The script uses only the Python standard library, so the
project gets no new dependency.

## Annotate a code block

A code block is rendered when the lines directly above its opening fence are
an HTML comment that starts with `@code-block`. A Markdown page does not show
the comment.

````markdown
<!-- @code-block name="hello" type="image" height=5 -->
```python
print("hello")
```
````

A recording has actions, one on each line, and the comment ends with `-->` on
its own line:

````markdown
<!-- @code-block name="pick-a-color" type="gif" height=8
wait 1
press down
press enter
wait 1
-->
```python
...
```
````

Options (all but `name` are optional):

| Option | Meaning |
| --- | --- |
| `name="..."` | The start of the asset file names: lowercase letters, digits and hyphens. Each name is used once. |
| `type="image"` or `type="gif"` | A PNG picture (the default) or a recording. |
| `height=ROWS` | The window height in rows. The default is 12. Every window has the same width. |
| `duration=SECONDS` | How long a gif records. The default is the total of the waits plus one second. |

Actions (a position is a 0-based cell, the column first):

| Action | Meaning |
| --- | --- |
| `wait SECONDS` | Do nothing for that time. |
| `press KEY [KEY ...]` | Press keys such as `left`, `space`, `q` or `ctrl+s`. |
| `type TEXT` | Type the rest of the line. |
| `paste TEXT` | Paste the rest of the line. |
| `click COLUMN ROW [left\|right\|middle]` | Click a cell. |
| `drag COLUMN ROW COLUMN ROW` | Drag from one cell to another. |
| `scroll up\|down COLUMN ROW [COUNT]` | Turn the wheel at a cell. |

A program receives mouse actions only when it has turned on mouse reporting.

## What it writes

- Each block is rendered once for each theme: `<name>-dark` and
  `<name>-light`, as `.png` or `.gif`, in `docs/assets/terminal/`.
- Directly below each annotated block, the script writes a region that shows
  the asset. It replaces the region on every run, and removes it when the
  block loses its annotation. Never edit a region by hand.
- In `README.md`, the region is a `<picture>` element, and GitHub shows the
  dark file to a reader who uses its dark theme.
- In every other file, the region is two Markdown images with `#only-light`
  and `#only-dark`, which Zensical and Material for MkDocs show by the color
  scheme of the site.

## How it works

- The code block runs as written: a `python` block with the interpreter that
  runs the script, and `sh` and `bash` blocks with that shell. The working
  directory is the root of the repository.
- Each block gets a private Kitty window with its own configuration, its own
  control socket and its own temporary directory. The script never reads the
  Kitty settings of the person and never touches a window that they use.
- The window has the colors of the page that shows the asset (the GitHub
  dark and light themes by default), so that the picture blends into the
  page. Named colors stay readable in both.
- A picture is taken after the screen stops changing, so it never shows a
  frame that is half drawn.
- A recording is a set of screenshots at a fixed rate, joined into a gif
  that loops.
- On Linux with no display, the script starts itself again under
  `xvfb-run`.

## Safety

- The script **runs the code blocks of the repository**. Render only
  Markdown that you and the person trust. Read a new annotated block before
  you render it.
- It reads only the files in `DOCUMENTS`. It writes only those files and the
  directory `OUTPUT`.
- It opens no network connection, and it starts no shell for its own
  commands.
- The terminal and the code block receive only a short list of environment
  variables (`PATH`, `HOME`, the display). Keys and tokens in the
  environment do not reach them.
- A name can contain only lowercase letters, digits and hyphens, so an asset
  cannot be written outside `OUTPUT`.

## If it fails

Every error says what is wrong and what to do. The common causes:

| Message | Cause |
| --- | --- |
| Kitty is not installed | Run `make install-terminal`, or set `RENDER_ASSETS_KITTY` to the path of Kitty. |
| Kitty could not do the command screenshot | Kitty is older than 0.49. Install a newer version. |
| The code block drew nothing | The program failed or printed nothing. Run the code on its own. |
| The assets do not all have the same width | Some assets were rendered on a different display. Run `make render-assets` with no names. |
