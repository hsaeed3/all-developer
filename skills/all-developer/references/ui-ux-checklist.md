# UI/UX Checklist

## Accessibility and ergonomics

- Does every keyboard shortcut work, on each platform and keyboard?
- Can a person find the shortcuts: in a hint, a tooltip, a menu or the
  documentation?
- Can a person do everything from the keyboard alone? The arrow keys move a
  choice, Tab moves between controls, Enter and Space activate, and Escape
  closes or goes back.
- Does every pointer action work: click, drag, scroll, resize, context menu,
  touch and stylus?
- Do screen readers read it? Does it make sense as plain text, with no color
  and no position?
- Is it correct in the light theme and in the dark theme?
- Are the focus state and the hover state clear, the same everywhere, and
  visible without color? One view has one focus.
- Can a person turn motion off or skip it? Does the product obey the reduced
  motion setting of the system? No information shows only while something
  moves.

## Responsiveness

- Is it usable at the smallest size (a phone, a narrow pane, a short window),
  at the largest size, and at each size between?
- After a resize, is it still usable and well arranged? Nothing is cut in the
  middle of a word, drawn past an edge, or left behind.
- Do menus, tooltips, popovers and dialogs stay inside the window?
- Is it sharp on high-DPI screens, and usable when a person zooms in or out?

## Platform consistency

- Is it fully usable on every platform that the project supports: each
  operating system, each browser, each terminal?
- Does it use what the platform gives: text input, input methods, dictation,
  accessibility, file pickers and menus? Never draw a copy of a native
  control.
- Does it obey the settings of the system: font, text size, color theme,
  number of colors (`NO_COLOR` included), scroll direction, key repeat?
- If something is missing (no network, no GPU, no mouse, no audio, no TTY),
  does it still do what it can, and say what it cannot do?

## Performance

- Does each interaction give feedback in the next frame? Nothing on the input
  path waits for a network, a disk or a model.
- Does slow work run in the background and show its progress or its state?
- Do large inputs stay fast: a long text, a big table, many images? Draw only
  what is visible, and load the rest when it is necessary.
- Does a frame fit the frame budget of the project (8ms for 120 fps, if the
  project sets no budget)? Does an idle program use no CPU?
- Is the change measured, not guessed? Add or update a benchmark for anything
  on the drawing path or the input path.

## Consistency

- Does it follow the [design language](design-language.md) and use the kit?
- Are the terms, the labels and the tone the same as in the rest of the
  product?
- Do interactions behave the same everywhere: how a program stops, how a menu
  closes, how a setting saves, how an error shows?
- Can code do everything that a person can do? Whatever a key or a click
  changes is also a value that a program can set and read.

## Text and internationalization

- Are the strings short and clear, with one meaning? Do they obey
  [Writing for Users](writing.md)?
- Do they contain no internal names: modules, crates, types, protocols?
- Do wide characters, emoji, combining marks, long translations and
  right-to-left text keep the layout correct?

## User paths and edge cases

- What is the happy path? What is the unhappy path: an error, a rejected
  value, an invalid state? An action that cannot act in the current state
  does nothing, quietly.
- What happens with no network, and when the network comes back?
- What happens when data is missing, damaged, empty or late?
- Does it work with and without each optional part?
- Does it behave the same in each mode: interactive, scripted, with no screen?
- Does every error say what is wrong and what to do?

## Discoverability and learning

- Can a first-time user use it from the example and the docstring alone, or
  with no documentation?
- Can the person always leave or undo? When the person leaves, is everything
  as it was before?
- Are advanced features available but out of the way? Basic controls come
  first, and the rest comes on request (progressive disclosure).
- Is there a path from beginner to expert: the common case in one line, the
  advanced case through options?
