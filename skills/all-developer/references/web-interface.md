# Web Interface

This guide says what All Developer recommends for a new web interface, and
how he works on one. The rule from the [design language](design-language.md)
decides the choice: **every control comes from one kit**, and a change shows
on the screen at once, so that he can look at the real thing.

## The recommendation

Use **Vite, React and TypeScript, with [Astryx](https://github.com/meta/astryx)
for the components**.

- **Vite** starts in about a second and shows each saved change in the
  browser at once. There is nothing to wait for between a change and the
  look at it.
- **Astryx** is the kit: an open source design system from Meta with more
  than 150 accessible components, theme tokens, a dark mode and page
  templates. It ships pre-built CSS, so it needs no build plugin.
- **Astryx is made for agents too.** Its command line tool prints the
  documentation of each component, so that All Developer reads the real API
  and does not guess it.

Astryx is in beta and needs React 19 or newer. Tell the person this when you
recommend it.

## Start a project

```bash
pnpm create vite@latest my-app --template react-ts
```

```bash
pnpm add @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
```

```bash
pnpm add -D @astryxdesign/cli
```

Import the three stylesheets in this order, and wrap the application in the
theme:

```css
@import '@astryxdesign/core/reset.css';
@import '@astryxdesign/core/astryx.css';
@import '@astryxdesign/theme-neutral/theme.css';
```

```tsx
import {Theme} from '@astryxdesign/core/theme';
import {neutralTheme} from '@astryxdesign/theme-neutral/built';

export function Providers({children}: {children: React.ReactNode}) {
  return <Theme theme={neutralTheme}>{children}</Theme>;
}
```

Then add the make hooks from `assets/make/web.mk` (see
[make hooks](make-hooks.md)): `make serve` starts the development server.

## Read the kit before you write

Always run the scoped package name. The short name `astryx` alone, through
`npx`, is a different package.

```bash
pnpm exec astryx component --list
```

```bash
pnpm exec astryx component Button
```

```bash
pnpm exec astryx docs tokens
```

```bash
pnpm exec astryx template --list
```

- Before you use a component, read its documentation with the command. Do
  not write its props from memory.
- Before you write a new component, search the kit for one that exists.
- Start a page from a template when one fits.

## Rules for the interface

- **Use the kit for every control.** Do not write a button, a dialog or a
  menu by hand when the kit has one.
- **Change the look with the theme, not with one-off styles.** A theme is a
  set of token values. A color or a space that is not a token is a defect.
- **If a component must change, own its source on purpose.** Astryx can copy
  the source of a component into the project. Do that with the agreement of
  the person, not as a quiet workaround.
- **Light and dark come from the tokens.** Do not write a color for one
  scheme only.
- **The [UI/UX checklist](ui-ux-checklist.md) applies in full:** keyboard,
  focus, screen readers, small and large sizes, reduced motion.

## Look at it

Keep `make serve` running while you work, and look at each change in a real
browser with Playwright: both color schemes, a phone width and a desktop
width, the keyboard path, the console errors. The steps are in
[direct verification](direct-verification.md).

## When to choose something else

| Situation | Use |
| --- | --- |
| The project already has a design system or a component library. | That one. Never add a second kit. |
| The project already uses Tailwind and wants to own every component. | [shadcn/ui](https://ui.shadcn.com/), which copies component source into the project. Astryx also works beside Tailwind. |
| One static page with no state. | Plain HTML and CSS, with tokens as CSS custom properties. No build step. |
| The project needs server rendering or routing by files. | A framework such as Next.js. Astryx works in it with the same three stylesheets. |
| The project is not React. | The standard kit of that framework. The rules of this guide stay the same. |

Whatever the choice, the two tests stay: the controls come from one kit, and
a saved change shows in the browser at once.
