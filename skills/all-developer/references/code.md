# Code for All

The power of All Developer is **Code for All**: software that is powerful
enough for experts, readable enough for beginners, and predictable enough for
everyone. The goal is not to make the software simple. The goal is to make its
complexity **legible**. A person never needs to read the source to use the
public interface.

Apply these rules to every name, signature, type, error and docstring that you
write or review.

## Names are full words

- Never abbreviate a name: public or private, a parameter, a variable, a
  module or a type. Write `Configuration` (not `Config`), `Context` (not
  `Ctx`), `Message` (not `Msg`), `Parameters` (not `Params`), `Directory` (not
  `Dir`), `Index` (not `Idx`), `Application` (not `App`) and
  `FunctionReference` (not `FunctionRef`).
- A short form that is conventional in a language or a community is not a
  reason to use it.
- The only accepted short forms are standard acronyms with no longer form in
  everyday use: `URL`, `HTTP`, `API`, `CLI`, `UI`, `TUI`, `GPU`, `AI`, `HTML`,
  `CSS`, `JSON`, `UUID`, `UTF8`, `IO`, `id`.
- A project can list more accepted short forms in its own instructions. Add no
  short form to a list without a decision from the maintainer.
- Use no single-letter names, in loops and comprehensions too. Write `index`,
  `item`, `row`, `column`.
- A boolean reads as a question: `is_visible`, `has_focus`, `should_wrap`.
- Follow the letter case of the language (`snake_case`, `camelCase`,
  `PascalCase`). The words stay full in each of them.
- Before you add a name, examine it for abbreviations. If it has one, write it
  again now, not later.

## Names describe the concept

- A name says what a thing **is** or **does**, not how it works.
- **A name is complete in its place.** A person reads a name together with
  the path that leads to it. The path says where the thing lives, and the
  last word says what it is: `canvas.screen.width`, `canvas.clock.pause()`,
  `context.mouse.position`.
  - Group related things under the object that owns them. Write
    `screen.width` and `screen.height`, not `screen_width` and
    `screen_height` on a larger object.
  - Do not repeat the path in the name. Write `screen.width`, not
    `screen.screen_width`.
  - A name that stands alone carries its full context. A function argument,
    a module-level value or an exported type has no path to read, so write
    `terminal_color_profile`, not `profile`.
  - Each step of the path is a real concept that a person knows (a screen, a
    clock, a mouse). Do not add a level only to group names.
- Do not use vague names (`Manager`, `Handler`, `Helper`, `Util`, `Data`,
  `Object`) when a specific concept exists.
- **ONE CONCEPT, ONE NAME.** Do not add a new term for a concept that has a
  name. Use the same vocabulary in code, types, docstrings, errors, the
  interface and the documentation. If two names seem to mean one thing, prove
  that they are different or merge them.
- If the project has a vocabulary table, use its terms. Never show an internal
  name to a person who uses the product.

## Calls are obvious at the call site

A reader predicts what a call does from its name and its arguments alone.
Prefer:

- named arguments to positional conventions;
- meaningful return types to loose containers;
- safe defaults to configuration that the code can infer;
- small pieces that combine to large pieces that a person configures;
- the common case in one line, with the advanced case still possible.

Add no ceremony to make an abstraction look pure.

## Types reduce uncertainty

Make public types precise enough for editor discovery and static analysis.
Do not make them harder to read than the behavior that they describe. Use a
named type when it carries meaning. Add no alias, trait, protocol, interface,
generic or wrapper only to make the code look sophisticated. An abstraction
that exists only for internal machinery stays internal.

## Errors teach recovery

Every error message says, in full plain sentences and with the names that the
person wrote:

1. which operation failed;
2. the value or the condition that caused it, when this helps;
3. what was expected;
4. what the person can do next.

Never show a bare internal trace, a code with no explanation, or a message
that needs the source to decode. An error shows where the problem is.

## Documentation is part of the API

A public interface that works, but that needs its source to use, is not
finished. Docstrings and comments obey [Documentation](documentation.md).

## PLUS ULTRA means discipline, not more

Go beyond the minimum in what helps the person who uses the software:
correctness, tests, types, docstrings and errors. Then stop. Add no feature,
parameter, option, alias, class or helper that the task does not need. Do not
add a class where a function says it better. Do not add a second spelling of
the same interface.

## Preserve the Symbol

The public interface is a promise: the same call behaves the same way each
time. Bindings, wrappers, dispatch, rendering and compatibility layers stay
behind it. If something internal is awkward, fix it behind the interface and
leave the interface alone. **HIDE THE WOUND, NOT THE CONTRACT.**

- A saved format is also a promise. A file that one version saves opens in
  every later version. Never rename or remove a saved field. Add a migration.
- A direct binding of an upstream library still uses full-word names. Record
  the upstream name in the docstring (see
  [Documentation](documentation.md)).
- For an incompatible change, say so in the commit title and explain the
  migration.
