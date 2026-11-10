# Make hooks for a Python package with a Rust extension (PyO3 and maturin).
# Use them together with python.mk. The Rust commands have a `-rust` suffix,
# because `lint`, `format` and `test` belong to the Python code.

.PHONY: .rust  ## Make sure that Rust is installed
.rust:
	@rustup --version > /dev/null 2>&1 || (echo "Rust is not installed. Install it from https://rust-lang.org/tools/install/"; exit 1)

.PHONY: rebuild-rust  ## Compile the Rust extension after a change to the Rust code
rebuild-rust: .uv .rust
	$(uv-run) maturin develop --uv

.PHONY: rebuild  ## Compile the Rust extension, then sync the environment
rebuild: rebuild-rust
	uv sync --frozen --all-groups --all-extras

.PHONY: build-release  ## Compile the optimized extension, for benchmarks
build-release: .uv .rust
	$(uv-run) maturin develop --uv --release

.PHONY: lint-rust  ## Check the format of the Rust code and run clippy
lint-rust: .rust
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: test-rust  ## Run the pure Rust tests
test-rust: .rust
	cargo test --workspace

.PHONY: lint-all  ## Check the Python code and the Rust code
lint-all: lint lint-rust

.PHONY: format-all  ## Format the Python code and the Rust code
format-all: format
	cargo fmt --all

.PHONY: benchmark-release  ## Run the benchmarks against the optimized extension
benchmark-release: build-release
	$(uv-run) pytest benchmarks --benchmark-enable --benchmark-columns=min,median,max --benchmark-sort=name $(ARGS)
