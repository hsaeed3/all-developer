# Tests, Benchmarks and Evals

A test proves that the code is correct. A benchmark proves that it is fast.
An eval proves that a model behaves. All Developer recommends them at the
start of new work (see [repository management](repository-management.md)),
and runs them through `make` (see [make hooks](make-hooks.md)).

## Tests

- **Pure logic has tests that need nothing.** No screen, no network, no
  device, no API key. These tests run on every commit.
- **A change of behavior comes with its test.** A bug fix starts with a test
  that fails for the bug, and ends with the same test passing.
- **Test through the public interface.** A test that reads private state
  breaks at each refactor and proves little.
- **Every example runs.** Examples in docstrings, in the documentation and
  in `examples/` are tests.
- **Anything that a person sees has a test against the real thing.** A real
  terminal, a real browser. See [direct verification](direct-verification.md).
- **Test the unhappy path.** An invalid value, an empty input, missing
  data, no network, a missing optional part. Test that each error message
  says what to do.
- **Test what the person reads.** If an error message or a label is part of
  the contract, assert on its text.
- **Never weaken a test to pass it.** Do not skip it, delete it or change
  what it expects, unless the expectation was wrong. Say so when it was.
- Keep slow suites separate, with their own command (`make test-terminal`,
  `make test-browser`), so that the fast suite stays fast.

## Benchmarks

Add a benchmark for anything on a hot path: drawing, input, a parser, a
query, a start time.

A benchmark must measure what its name says:

- **Run an optimized build.** A debug build is many times slower. Refuse to
  measure one.
- **Assert on the result.** A benchmark that does not check its output can
  measure a function that does nothing.
- **Keep setup out of the measured call.** Build the input first, then
  measure only the operation.
- **Do not measure a shortcut.** If a second identical call can return a
  stored result, do not time the same operation on the same input twice.
- **Set the rounds explicitly** when the first call is faster or slower than
  the others.
- **Measure the whole effect.** Time a change together with the frame that
  draws it, not the change alone.
- **Compare with something.** Record the results across commits (for
  example with CodSpeed in the pipeline), so that a slower change shows. To
  compare with other libraries, run the same job on the same input in each.
- **State the budget.** If the project has a budget (a frame in 8 ms), the
  benchmark checks it. Wall-clock limits are checked only where the hardware
  is known.
- Also record CPU time and memory growth where they matter, not only wall
  time.

A claim about speed in a report comes with the command and the numbers.

## Evals

Anything that uses a model has evals. An eval is to a model what a test is to
a function, but its result is a score, not pass or fail.

- **A fixed set of cases.** Each case has an input and a way to grade the
  output. Keep the cases in the repository.
- **Grade with code where you can.** An exact value, a schema, a check that
  runs the output. Use a model as a grader only for what code cannot judge,
  and give that grader a clear rubric.
- **Run each case more than once.** A model varies. Report the rate, not one
  run.
- **Always compare with a baseline.** The same cases with no change, or with
  the previous prompt. A score alone says little.
- **Run the evals when something changes:** the prompt, the model, the tools
  or the retrieved data.
- **Keep failures.** When the model fails in real use, add that case to the
  set.
- **Separate the logic from the model.** The code around a model (parsing,
  validation, routing, retries) has normal tests that use no network and no
  key, with recorded or made-up model answers.
- **Bounded answers first.** Where an answer is yes or no, one of a set, or a
  score, ask for exactly that type. It is cheaper to run and exact to grade.

For an agent skill or a prompt, the same rules apply: a set of tasks, a run
with the skill and a run without it, and a grader.
