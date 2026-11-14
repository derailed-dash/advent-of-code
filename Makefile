SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help install lint fix test check sync-secrets list run fetch new-year docs docs-build docs-stop clean

CLI_TARGETS := list run fetch new-year
PRIMARY_GOAL := $(firstword $(MAKECMDGOALS))
ifneq ($(filter $(PRIMARY_GOAL),$(CLI_TARGETS)),)
CLI_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
ifneq ($(CLI_ARGS),)
CLI_GOAL_WORDS := $(sort $(CLI_ARGS))
.PHONY: $(CLI_GOAL_WORDS)
$(foreach arg,$(CLI_GOAL_WORDS),$(eval $(arg):;@:))
endif
endif

-include .env.template
-include .env

GIT_CRYPT_HELPER ?= $(shell command -v git-crypt-helper.sh 2>/dev/null || echo "$(HOME)/.gemini/config/skills/secrets-with-git-crypt/scripts/git-crypt-helper.sh")

help: ## Show available targets and usage
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

install: ## Install Python, Jupyter, and legacy AoC dependencies with uv
	uv sync --dev --extra jupyter --extra legacy

lint: ## Run read-only offline checks (codespell, ruff, pyright)
	uv run codespell -s
	uv run ruff check
	uv run pyright

fix: ## Auto-fix spelling, lint, and formatting on active modules
	uv run codespell -w
	uv run ruff check --fix
	uv run ruff format src/aoc_common src/tests src/template_folder

test: ## Run offline unit tests
	uv run pytest src/tests

check: lint test ## Run full offline verification gate (lint + unit tests)

sync-secrets: ## Show git-crypt parallel secrets status
	@if [ -x "$(GIT_CRYPT_HELPER)" ]; then \
		"$(GIT_CRYPT_HELPER)" status; \
	else \
		git-crypt status -e; \
	fi

list: ## List AoC years/progress or one year: make list [2025 | YEAR=2025]
	uv run aoc list $(if $(CLI_ARGS),$(CLI_ARGS),$(YEAR))

run: ## Run a puzzle: make run <1|01|d01|20251|202501|2025d01|2025 1> [ARGS="-s -d"]
	@if [ -n "$(CLI_ARGS)" ]; then \
		uv run aoc run $(CLI_ARGS) $(ARGS); \
	elif [ -n "$(TARGET)" ]; then \
		uv run aoc run "$(TARGET)" $(ARGS); \
	elif [ -n "$(YEAR)" ] && [ -n "$(DAY)" ]; then \
		uv run aoc run "$(YEAR)" "$(DAY)" $(ARGS); \
	elif [ -n "$(DAY)" ]; then \
		uv run aoc run "$(DAY)" $(ARGS); \
	else \
		echo 'Usage: make run <1|01|d01|20251|202501|2025d01|TARGET=2018d07|YEAR=2026 DAY=1> [ARGS="-s -d"]'; exit 1; \
	fi

fetch: ## Fetch puzzle description, samples, and input.txt: make fetch <1|d01|202501|2025d01|2025 1> [ARGS="--write-sample"]
	@if [ -n "$(CLI_ARGS)" ]; then \
		uv run aoc fetch $(CLI_ARGS) $(ARGS); \
	elif [ -n "$(TARGET)" ]; then \
		uv run aoc fetch "$(TARGET)" $(ARGS); \
	elif [ -n "$(YEAR)" ] && [ -n "$(DAY)" ]; then \
		uv run aoc fetch "$(YEAR)" "$(DAY)" $(ARGS); \
	elif [ -n "$(DAY)" ]; then \
		uv run aoc fetch "$(DAY)" $(ARGS); \
	else \
		echo 'Usage: make fetch <1|01|d01|20251|202501|2025d01|TARGET=2018d07|YEAR=2026 DAY=1> [ARGS="--write-sample --desc-only"]'; exit 1; \
	fi

new-year: ## Scaffold AoC year folders: make new-year <2026 | YEAR=2026> [DAYS=12]
	@year="$(or $(firstword $(CLI_ARGS)),$(YEAR))"; \
	if [ -z "$$year" ]; then echo "Usage: make new-year <2026 | YEAR=2026> [DAYS=12]"; exit 1; fi; \
	uv run aoc new-year "$$year" --days "$(if $(DAYS),$(DAYS),12)" $(ARGS)

docs: ## Serve the Jekyll documentation site locally via Docker
	cd docs && docker compose up

docs-build: ## Build or rebuild the local Jekyll Docker image
	cd docs && docker compose build

docs-stop: ## Stop and remove the local Jekyll documentation container
	cd docs && docker compose down

clean: ## Remove local Python and Jekyll build caches
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf docs/_site docs/.jekyll-cache docs/.sass-cache docs/.jekyll-metadata
	find src -type d -name "__pycache__" -prune -exec rm -rf {} +
