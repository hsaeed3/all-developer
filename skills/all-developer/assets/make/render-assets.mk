# Make hooks for pictures and recordings of terminal programs.
# They run scripts/render_assets.py, which uses only the Python standard library.
# For a project with no uv, replace `uv run --no-sync python` with `python3`.

.PHONY: install-terminal  ## Install Kitty, ffmpeg and the tools for a virtual display
install-terminal:
	@if [ "$$(uname -s)" = Darwin ]; then brew install --cask kitty && brew install ffmpeg; \
	elif [ "$$(uname -s)" = Linux ] && command -v apt-get >/dev/null; then \
		sudo apt-get update && sudo apt-get install -y kitty ffmpeg xvfb xauth libgl1-mesa-dri fonts-dejavu-core; \
	else echo 'Install Kitty 0.49 or newer, ffmpeg and (on Linux with no display) Xvfb with your package manager.' >&2; exit 1; fi

.PHONY: render-assets  ## Render the annotated code blocks (@code-block) of the Markdown files in a real Kitty window (ARGS names blocks)
render-assets:
	uv run --no-sync python scripts/render_assets.py $(ARGS)

.PHONY: check-assets  ## Fail when a rendered asset is missing or a Markdown region is not current
check-assets:
	uv run --no-sync python scripts/render_assets.py --check
