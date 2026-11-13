SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help install lint fix test check sync-secrets new-year docs docs-build docs-stop clean

-include .env.template
-include .env

help: ## Show available targets and usage
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

install: ## Install Python and Jupyter dependencies with uv
	uv sync --dev --extra jupyter

lint: ## Run read-only offline checks (codespell, ruff, pyright)
	uv run codespell -s
	uv run ruff check --diff
	uv run pyright

fix: ## Auto-fix spelling, lint, and formatting on active modules
	uv run codespell -w
	uv run ruff check --fix
	uv run ruff format src/aoc_common src/tests src/template_folder

test: ## Run offline unit tests
	uv run pytest src/tests

check: lint test ## Run full offline verification gate (lint + unit tests)

sync-secrets: ## Show git-crypt parallel secrets status
	/home/dazbo/.gemini/config/skills/secrets-with-git-crypt/scripts/git-crypt-helper.sh status

new-year: ## Scaffold AoC year folders: make new-year YEAR=2026 [DAYS=12]
	@if [ -z "$(YEAR)" ]; then echo "Usage: make new-year YEAR=2026 [DAYS=12]"; exit 1; fi
	./scripts/create_year.sh "$(YEAR)" "$(if $(DAYS),$(DAYS),12)"

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
