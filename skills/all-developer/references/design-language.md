# Design Language

The interface stays quiet so that the content leads. Every visual choice has a
meaning, and a meaning always looks the same. Use this section and the
[checklist](ui-ux-checklist.md) for every change that a person can see, hear or
read: a graphical interface, a terminal program, command line output, a
documentation site.

- **Restraint.** Use one accent color and neutral text. Nothing is decoration
  without a job. If the removal of an element loses no information, remove it.
- **One kit.** Every control comes from one shared set of components and
  tokens. Add to that set. Do not style one control on its own.
- **Spacing comes from one scale.** Use the spacing tokens of the project (the
  cell in a terminal, a 4px scale on a page). Never use a one-off value.
- **Type uses few sizes.** Build hierarchy from weight and color, not from
  many sizes. Prose uses the text font. Anything that a person types or reads
  as code uses the mono font.
- **Color is semantic.** A color says what something is: default, muted,
  accent, disabled, success, warning, error or information. It keeps that
  meaning everywhere. Every color is a token with a value for the light theme
  and for the dark theme. Color never carries a meaning alone: put a word or a
  symbol with it.
- **Layers show closeness.** A higher layer is closer to the person and covers
  what is below it. Only floating surfaces (menus, dialogs, popovers) have a
  shadow or a border of their own.
- **Motion confirms a change, never delays one.** The state changes at once,
  and the animation only moves the picture to the new state. The next input
  acts on the new state. Feedback takes about 50ms. A transition takes 150ms
  to 300ms and eases out. Nothing moves forever, unless the motion is the
  content or shows work in progress.
- **Icons and symbols come from one set.** Draw icons on one grid, with one
  stroke weight, in the current text color. Start from the icon set that the
  project already uses. Put text with an icon, unless its meaning is
  universal. In a terminal, make sure that a symbol is one cell wide.
- **The content belongs to the person.** These rules apply to the controls of
  the product. They do not apply to what the person makes with it.
