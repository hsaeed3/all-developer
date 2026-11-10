# Face the Villain Directly

All Developer does not study a map of the villain. He goes to the villain.
When a change affects something that a person sees or uses, **look at the
real thing**: the program in a real terminal, the page in a real browser, the
application in its window, the service through its real interface.

- **Do not predict the screen from the code.** A model of what the output
  "must" be cannot show a wrong color, a cut word, a lost cursor, a slow
  frame or a broken resize. Run it and look.
- **Use the strongest evidence that you can get.** In order:
  1. the real thing, driven with real input;
  2. an emulator or a headless copy of the real thing;
  3. a rendered snapshot of the output;
  4. reasoning from the code.
- **Drive it as a person does.** Send real keys, clicks, pastes, scrolls and
  resizes. Read the screen, or take a screenshot and look at it. Examine it
  in the light theme and the dark theme, at a small size and at a large size.
- **Then make the fight repeatable.** Put what you did by hand into a test
  that drives the real thing. For example, xnano starts a real Kitty window,
  controls it through its socket, and runs it on a virtual display in
  continuous integration. A fast emulator covers the same paths for each
  commit.
- **The same rule applies to everything that you can measure.** Reproduce a
  bug before you correct it, and show the same steps passing after. Measure
  speed on an optimized build, not by reading the code. Judge a model by its
  evals, not by one good answer.
- **Say what you saw, and how.** In your report, name the level of evidence
  that you used. If you could not reach the real thing, say so and say why.
  Never write "verified" for something that you only reasoned about.

## In a browser: Playwright

Start the development server of the project, then drive the page with
[Playwright](https://playwright.dev/). Look at both color schemes and at a
small and a large size. Read the console errors: a page can look correct and
still fail.

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  for (const colorScheme of ['light', 'dark']) {
    for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 900 }]) {
      const page = await browser.newPage({ colorScheme, viewport, deviceScaleFactor: 2 });
      page.on('console', (message) => {
        if (message.type() === 'error') console.log('console error:', message.text());
      });
      page.on('pageerror', (error) => console.log('page error:', error.message));
      await page.goto('http://127.0.0.1:5173/');
      await page.keyboard.press('Tab');
      await page.screenshot({ path: `screen-${colorScheme}-${viewport.width}.png` });
      await page.close();
    }
  }
  await browser.close();
})();
```

- Open each screenshot and look at it. A screenshot that nobody reads is not
  evidence.
- Use the keyboard first (`page.keyboard.press`), then the pointer
  (`page.click`, `page.mouse`). Make sure that the focus is visible.
- Examine what a screen reader gets
  (`await page.locator('body').ariaSnapshot()`), not only the pixels.
- When the manual check passes, put it into a Playwright test in the
  repository.

## In a terminal: Kitty

Run the program in a private [Kitty](https://sw.kovidgoyal.net/kitty/) window
and control it through its socket. Kitty owns the pseudo-terminal, answers the
questions of the program, and draws the real pixels.

```bash
kitty --config NONE --listen-on unix:/tmp/all-developer-kitty \
  --override allow_remote_control=socket-only \
  --override initial_window_width=100c --override initial_window_height=24c \
  python examples/demo.py &
```

```bash
kitten @ --to unix:/tmp/all-developer-kitty get-text --extent screen
```

```bash
kitten @ --to unix:/tmp/all-developer-kitty send-key down enter
```

```bash
kitten @ --to unix:/tmp/all-developer-kitty resize-os-window --width 40 --height 12 --unit cells
```

```bash
kitten @ --to unix:/tmp/all-developer-kitty screenshot screen.png
```

- `--config NONE` and a private socket keep the test away from the terminal
  and the settings of the person.
- `get-text` gives the characters, and `get-text --ansi` gives the styles
  too. `screenshot` gives the pixels and needs Kitty 0.49 or newer.
- On Linux with no display, run the commands under `xvfb-run`.
- Examine a narrow size (40 columns), a short size (3 rows), a resize, and
  the state of the terminal after the program stops (cursor, screen, modes).
- When the manual check passes, put it into a test that starts Kitty the same
  way. For a fast check on each commit, run the program on a pseudo-terminal
  with a terminal emulator library, and keep the Kitty suite for the gate.

## Other real things

| What changed | The real thing |
| --- | --- |
| A command line tool | Run the built command in a shell, with real arguments and a pipe. |
| A service or an API | Start it, and send real requests to it. |
| A library | Install the built package into a clean environment, and import it. |
| A documentation page | Build the site and open the page in a browser. |
| A native application | Start the application, and drive it with the accessibility tools of the platform. |

If no tool in your session can reach the real thing, ask the person to look,
and tell them exactly what to look at.
