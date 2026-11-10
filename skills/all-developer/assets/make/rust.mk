# Make hooks for a Rust project (one Cargo workspace).

.PHONY: .rust  ## Make sure that Rust is installed
.rust:
	@rustup --version > /dev/null 2>&1 || (echo "Rust is not installed. Install it from https://rust-lang.org/tools/install/"; exit 1)

.PHONY: format  ## Format every crate
format: .rust
	cargo fmt --all

.PHONY: lint  ## Check the format and run clippy with warnings as errors
lint: .rust
	cargo fmt --all -- --check
	cargo clippy --workspace --all-targets -- -D warnings

.PHONY: typecheck  ## Check that every crate compiles
typecheck: .rust
	cargo check --workspace --all-targets

.PHONY: test  ## Run the tests (ARGS passes cargo test options)
test: .rust
	cargo test --workspace $(ARGS)

.PHONY: benchmark  ## Run the benchmarks against an optimized build
benchmark: .rust
	cargo bench --workspace $(ARGS)

.PHONY: clean  ## Remove build output
clean:
	cargo clean
