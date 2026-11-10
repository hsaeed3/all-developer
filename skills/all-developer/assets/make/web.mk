# Make hooks for a web project (pnpm, Vite, TypeScript, Biome, Vitest, Playwright).

.PHONY: .pnpm  ## Make sure that pnpm is installed
.pnpm:
	@pnpm --version > /dev/null 2>&1 || (echo "pnpm is not installed. Install it from https://pnpm.io/installation"; exit 1)

.PHONY: install  ## Install the dependencies from the lock file
install: .pnpm
	pnpm install --frozen-lockfile

.PHONY: serve  ## Start the development server, which shows each change at once
serve: .pnpm
	pnpm exec vite

.PHONY: format  ## Format the source files
format: .pnpm
	pnpm exec biome check --write .

.PHONY: lint  ## Check the source files
lint: .pnpm
	pnpm exec biome check .

.PHONY: typecheck  ## Check the types
typecheck: .pnpm
	pnpm exec tsc --noEmit

.PHONY: test  ## Run the unit tests (ARGS passes vitest options)
test: .pnpm
	pnpm exec vitest run $(ARGS)

.PHONY: test-browser  ## Run the tests in a real browser (ARGS passes playwright options)
test-browser: .pnpm
	pnpm exec playwright test $(ARGS)

.PHONY: build  ## Build the production bundle
build: .pnpm
	pnpm exec vite build

.PHONY: clean  ## Remove build output
clean:
	rm -rf dist playwright-report test-results
