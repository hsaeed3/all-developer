# Writing for Users

Every text that a person reads obeys these rules: labels, hints, titles, help
text, tooltips, error messages, command line output, docstrings, comments and
documentation. The rules come from Simplified Technical English
([ASD-STE100](https://www.asd-ste100.org/)). A name in code is a technical
noun and keeps its spelling.

## Words

- Use one word for one meaning, and one meaning for one word. The same
  technical noun names the same item in code, on the screen, in errors and in
  the documentation.
- Use simple, well-known words: "use", not "utilize"; "start", not "initiate";
  "show", not "display" (as a verb); "make sure", not "ensure"; "help", not
  "facilitate". Use no slang, jargon or regional words.
- Do not use a noun as a verb, or a verb as a noun: "Run the code", not "Do a
  run".
- Use a single verb when one exists: "start", not "fire up"; "remove", not
  "get rid of".
- A technical noun has three words at most. Give a long one in full once, then
  use a short form.
- Do not use Latin abbreviations. Write "for example" and "that is", not
  "e.g." and "i.e.".
- Use gender-neutral language.
- Use American English spelling ("color", "center").

## Verbs

- Use the active voice. Use the passive voice only to describe something when
  the agent is unknown.
- Use only the simple present, the simple past, the simple future and the
  imperative. Do not write "has been compiled" or "will have run". A past
  participle can be an adjective ("cached result").
- Use the "-ing" form only as part of a technical noun ("type checking").
- Describe an action with a verb, not with a noun: "Install the packages", not
  "Do the installation of the packages".

## Sentences

- Keep an instruction to 20 words and a description to 25 words.
- Give one instruction in each sentence, in the imperative.
- Do not omit words and do not use contractions ("do not", "is not"). Keep the
  articles.
- If the reader must know a condition first, give the condition, then a comma,
  then the instruction: "If the terminal has no mouse, use the arrow keys."
- Do not use semicolons. Write two sentences.
- Use a vertical list for many items or steps.
- Give one topic in each paragraph, in six sentences or fewer. Give
  information gradually.
- A note gives information, not an instruction.

## Labels, hints, options, errors and warnings

- A label names the thing or the action in as few words as possible, with no
  sentence: "Theme", "Pause".
- A help text says what the thing does and when to change it, in one or two
  short sentences.
- A hint names each key and then its action. The key that leaves comes last:
  `↑ ↓ choose · enter open · q quit`.
- An option says what happens, not how it works or where a value comes from:
  "Answer on this device", not "Local backend".
- An error says what is wrong, then what to do: "No network. The answer shows
  when the network is back."
- A message about a missing part names the command that installs it.
- A warning gives the risk and its result: "This closes the terminal. Unsaved
  text is lost."
