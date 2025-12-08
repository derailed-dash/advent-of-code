SHELL := /bin/bash
.PHONY: install test lint docs

# Install dependencies using uv package manager ; uv pip install -e .
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.6.12/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync --dev --extra jupyter

# Run unit tests
test:
	uv run pytest src/tests

# Run code quality checks (codespell, ruff, mypy)
lint:
	@echo "Running code quality checks..."
	uv sync --dev
	uv run codespell -s
	uv run ruff check . --diff
	uv run mypy .

# Run documentation server
docs:
	cd docs && docker compose up
