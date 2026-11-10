# Make hooks for a documentation site that Zensical builds.
# Development tool: uv add --group docs zensical

.PHONY: docs-build  ## Build the documentation site, and fail on a warning
docs-build: .uv
	uv run --only-group docs zensical build --clean --strict

.PHONY: docs-serve  ## Serve the documentation site for a preview
docs-serve: .uv
	uv run --only-group docs zensical serve
