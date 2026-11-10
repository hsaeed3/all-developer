.DEFAULT_GOAL := help

sources = scripts tests skills/all-developer/scripts skills/all-developer/assets/web
uv-run = uv run --no-sync

.PHONY: .uv  ## Make sure that uv is installed
.uv:
	@uv -V > /dev/null 2>&1 || (echo "uv is not installed. Install it from https://docs.astral.sh/uv/getting-started/installation/"; exit 1)

.PHONY: install  ## Install the development tools and the git hooks
install: .uv
	uv sync --frozen --all-groups
	$(uv-run) prek install --install-hooks

.PHONY: install-terminal  ## Install Kitty, ffmpeg and the tools for a virtual display
install-terminal:
	@if [ "$$(uname -s)" = Darwin ]; then brew install --cask kitty && brew install ffmpeg; \
	elif [ "$$(uname -s)" = Linux ] && command -v apt-get >/dev/null; then \
		sudo apt-get update && sudo apt-get install -y kitty ffmpeg xvfb xauth libgl1-mesa-dri fonts-dejavu-core; \
	else echo 'Install Kitty 0.49 or newer, ffmpeg and (on Linux with no display) Xvfb with your package manager.' >&2; exit 1; fi

.PHONY: format  ## Format the Python source files
format: .uv
	$(uv-run) ruff check --fix $(sources)
	$(uv-run) ruff format $(sources)

.PHONY: lint  ## Check the Python source files
lint: .uv
	$(uv-run) ruff check $(sources)
	$(uv-run) ruff format --check $(sources)

.PHONY: lint-skill  ## Check the structure of the skill: its front matter, its links and its file lists
lint-skill: .uv
	$(uv-run) python scripts/check_skill.py

.PHONY: typecheck  ## Check the types
typecheck: .uv
	$(uv-run) basedpyright

.PHONY: spellcheck  ## Check the spelling
spellcheck: .uv
	$(uv-run) codespell

.PHONY: test  ## Run the tests (ARGS passes pytest options)
test: .uv
	$(uv-run) pytest tests $(ARGS)

.PHONY: test-terminal  ## Run the tests that render assets in a real Kitty window (needs make install-terminal)
test-terminal: .uv
	$(uv-run) pytest tests --actual-terminal $(ARGS)

.PHONY: check  ## Run every check that continuous integration runs
check: lint lint-skill spellcheck typecheck test

.PHONY: clean  ## Remove caches and build output
clean:
	rm -rf .pytest_cache .ruff_cache
	find . -name __pycache__ -not -path './.venv/*' -prune -exec rm -rf {} +

.PHONY: help  ## List the commands
help:
	@grep -E '^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
