# Make hooks for a Python project that uses uv.
# Development tools: uv add --dev ruff basedpyright codespell pytest pytest-cov pytest-benchmark prek
# Set `sources` to the directories of the project.

sources = src tests scripts
uv-run = uv run --no-sync

.PHONY: .uv  ## Make sure that uv is installed
.uv:
	@uv -V > /dev/null 2>&1 || (echo "uv is not installed. Install it from https://docs.astral.sh/uv/getting-started/installation/"; exit 1)

.PHONY: install  ## Install the project, the development tools and the git hooks
install: .uv
	uv sync --frozen --all-groups --all-extras
	$(uv-run) prek install --install-hooks

.PHONY: format  ## Format the Python source files
format: .uv
	$(uv-run) ruff check --fix $(sources)
	$(uv-run) ruff format $(sources)

.PHONY: lint  ## Check the Python source files
lint: .uv
	$(uv-run) ruff check $(sources)
	$(uv-run) ruff format --check $(sources)

.PHONY: typecheck  ## Check the types
typecheck: .uv
	$(uv-run) basedpyright

.PHONY: spellcheck  ## Check the spelling
spellcheck: .uv
	$(uv-run) codespell

.PHONY: test  ## Run the tests (ARGS passes pytest options)
test: .uv
	$(uv-run) pytest tests $(ARGS)

.PHONY: test-coverage  ## Run the tests and write a coverage report
test-coverage: .uv
	$(uv-run) pytest tests --cov --cov-report=term --cov-report=html $(ARGS)

.PHONY: benchmark  ## Run the benchmarks (ARGS passes pytest options)
benchmark: .uv
	$(uv-run) pytest benchmarks --benchmark-enable --benchmark-columns=min,median,max --benchmark-sort=name $(ARGS)

.PHONY: rebuild-lockfiles  ## Lock every dependency again, at its newest version
rebuild-lockfiles: .uv
	uv lock --upgrade

.PHONY: clean  ## Remove caches and build output
clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage build dist site
	find . -name __pycache__ -not -path './.venv/*' -prune -exec rm -rf {} +
