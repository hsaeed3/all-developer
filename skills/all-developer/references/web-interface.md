# Web Interface

This guide says how All Developer makes a web interface. Two tests decide
every choice:

- **it runs at once:** a person opens it and sees it, and a saved change
  shows in the browser immediately;
- **every control comes from one kit** (see the
  [design language](design-language.md)).

There are two levels. Start at the first one. Go to the second one only when
the work needs it.

| Level | What it is | Use it for |
| --- | --- | --- |
| 1. An artifact | One HTML file, or a page with a small server that `make` starts. htmx when it talks to the server. No build step. | A page, a report, a tool, a prototype, a dashboard, a small application. |
| 2. An application | React, TypeScript, Vite, Tailwind CSS and shadcn/ui. | Much state in the browser, routing, many components, a team that builds on it. |

## Level 1: an artifact

An artifact is a file that a person can run. All Developer writes it into the
project (or where the person asks), and the person opens it. It needs no
install and no build.

### The parts

- **Raw HTML first.** Use the elements of the platform: `<form>`, `<dialog>`,
  `<details>`, `<table>`, `<button>`. They have keyboard and screen reader
  behavior that you do not need to write.
- **One stylesheet from a safe CDN.** [Pico CSS](https://picocss.com/) styles
  the raw elements, follows the light or dark setting of the person, and
  changes its look through CSS custom properties. It is the kit.
- **A small script, in the file,** when the page needs behavior that stays in
  the browser.
- **[htmx](https://htmx.org/) when the page talks to a server.** The server
  answers with a piece of HTML, and an attribute says where it goes. There is
  no client state to keep, and no build.

### Start from a template

Copy a template from `assets/web/` of this skill, then change its content.

| Template | What it is |
| --- | --- |
| `assets/web/artifact.html` | One file that opens from the disk. HTML, Pico CSS and a small script. |
| `assets/web/app/index.html` | A page that sends its form to a server with htmx. |
| `assets/web/app/serve.py` | A server for that page, with the Python standard library only. It listens only on this computer. |

### A dashboard or an application as a make command

When the page shows data of the project or changes something, make it a
[make hook](make-hooks.md). The person then starts it with one command, and
it stays in the repository as a tool of the project.

1. Offer it, and say what it adds: one directory in `scripts/` and one
   target. Wait for a yes, unless the person asked for exactly this.
2. Copy `assets/web/app/` to `scripts/<name>/`, for example
   `scripts/dashboard/`. It holds `index.html` and `serve.py`.
3. Copy the target from `assets/make/app.mk` into the `Makefile`, and give
   it the name of the application.
4. Write the page and its answers. The server reads the data of the project
   (a file of results, a log, a database) and answers with pieces of HTML.
5. Run it, and look at it in a real browser.

```bash
make dashboard
```

Then open `http://127.0.0.1:8000`. `PORT=9000 make dashboard` uses a
different port.

- The server uses only the standard library, so the hook adds no
  dependency. For a project in a different language, write the same small
  server with the standard library of that language.
- The server reads the data on each request. A refresh shows the current
  state, with no build.
- Show an empty state and an error state: what the page says when the data
  file is missing, and what the person can do.
- Touch only the `Makefile` and `scripts/`.

### Safe CDN rules

A file from a CDN runs with the full rights of the page. So every external
file obeys all of these rules:

- **Only these hosts:** `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` and
  `unpkg.com`. They serve published packages and do not change a published
  version.
- **An exact version** in the address: `htmx.org@2.0.11`, never
  `htmx.org@2`, `@latest` or no version.
- **An integrity hash** (`integrity="sha384-..."`) and
  `crossorigin="anonymous"`. The browser then refuses a file that is not
  byte for byte the one that you examined.
- **Compute the hash from the published package.** Do not copy a hash from a
  page that you cannot verify, and never write one from memory:

  ```bash
  npm pack htmx.org@2.0.11
  ```

  ```bash
  tar -xzf htmx.org-2.0.11.tgz
  ```

  ```bash
  openssl dgst -sha384 -binary package/dist/htmx.min.js | openssl base64 -A
  ```

- **As few files as possible.** One stylesheet, and one script only when the
  page needs it. No fonts from a third host, and no script that loads other
  scripts.
- **No tracking.** A page has no analytics, no usage data and no request to
  a host that the person did not agree to.
- **A new version is a decision.** Change the version and its hash together,
  on purpose, and look at the page again.

The tags that the templates use are already verified. Copy them as they
are. Compute a hash only when you add a file or change a version.

```html
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/@picocss/pico@2.1.1/css/pico.min.css"
  integrity="sha384-L1dWfspMTHU/ApYnFiMz2QID/PlP1xCW9visvBdbEkOLkSSWsP6ZJWhPw6apiXxU"
  crossorigin="anonymous"
>
```

```html
<script
  src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.11/dist/htmx.min.js"
  integrity="sha384-2OatzQy1H+Zd/IIrjr1TcuDGqLXeHhbooAyJY1KdQMKnr4LZ22k31GBLdYKHmVjg"
  crossorigin="anonymous"
></script>
```

If the artifact must work with no network, put the stylesheet and the script
into the file itself.

### Rules for an artifact

- **Change the look with tokens.** Set the Pico variables (`--pico-*`) and
  your own custom properties on `:root`. A color or a space on one element is
  a defect.
- **Light and dark both work.** Do not set a color for one scheme only.
- **Escape every value from a person** before it goes into HTML, on the
  server and in the browser (`textContent`, not `innerHTML`).
- **A server for an artifact listens on `127.0.0.1` only,** unless the person
  asks for more.
- **The page works at phone width** with no horizontal scroll.
- **State that must stay lives on the server or in a file,** not only in the
  page.
- The [UI/UX checklist](ui-ux-checklist.md) applies in full.

## Level 2: an application

When the work needs an application, use this stack:

| Part | Tool |
| --- | --- |
| Packages | [pnpm](https://pnpm.io/) |
| Development server and build | [Vite](https://vite.dev/) |
| Interface | [React](https://react.dev/) with TypeScript |
| Styles | [Tailwind CSS](https://tailwindcss.com/) |
| Components | [shadcn/ui](https://ui.shadcn.com/), on Radix UI |

- Vite shows each saved change in the browser at once.
- shadcn/ui is the kit. Its components are copied into the project, so the
  project owns their source, and their look comes from theme tokens.
- Start the project with the current instructions of Vite and of shadcn/ui.
  Read them first: the commands change between versions.
- Use `strict` TypeScript with `noUncheckedIndexedAccess`. Use `unknown` and
  real types, never `any`.
- Add the make hooks from `assets/make/web.mk` (see
  [make hooks](make-hooks.md)): `make serve` starts the development server.
- If the project already has a framework, a design system or a component
  library, use that one. Never add a second kit.

## When to go from level 1 to level 2

Stay at level 1 until one of these is true:

- the page keeps much state in the browser that many parts share;
- the interface has many screens with routing in the browser;
- the same components repeat so often that copies of HTML become a risk;
- the person asks for an application.

Say why when you recommend level 2. Do not start at level 2 because it is
familiar.

## Look at it

Open the artifact, or keep `make serve` running, and look at each change in a
real browser with Playwright: both color schemes, a phone width and a desktop
width, the keyboard path, the console errors. A wrong integrity hash shows
there as a console error and a page with no styles. The steps are in
[direct verification](direct-verification.md).
