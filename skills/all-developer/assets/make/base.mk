# Base make hooks: the default goal, the gate and the list of commands.
# Paste this at the top of the Makefile of the project.

.DEFAULT_GOAL := help

# Tools that obey this variable send no usage data.
export DO_NOT_TRACK := 1

.PHONY: check  ## Run every check that continuous integration runs
check: lint spellcheck typecheck test

.PHONY: help  ## List the commands
help:
	@grep -E '^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
