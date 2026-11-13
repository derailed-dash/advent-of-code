---
title: Project Structure
---

## Why?

It is a good idea for any Python project to have a clear folder structure. This makes it easier for you to maintain, and helps others understand your project quickly.

## A Good General Project Structure

Here is a modern layout that works well for Python projects:

| Path | Purpose |
| :--- | :--- |
| `.` | Repository root (the project name) |
| `README.md` | Top-level documentation describing purpose, setup, and usage |
| `LICENSE` | Open-source licence terms |
| `pyproject.toml` | Project metadata, dependencies, and tool configuration (`ruff`, `pyright`, `codespell`) |
| `uv.lock` | Locked dependency graph for reproducible environments |
| `.gitignore` | Tells Git which files and directories (such as `.venv/` and `.env`) must stay untracked |
| `.env.template` | Template listing expected environment variables (e.g. `PYTHONPATH`) |
| `Makefile` | Convenience commands (`install`, `check`, `test`, `lint`) |
| `src/` | Application and library source code |
| `src/tests/` (or `tests/`) | Unit tests (`pytest`) |
| `docs/` | Project documentation and guides |
| `scripts/` | Automation and scaffolding scripts |

## My Advent of Code Project Structure

Here is how my AoC repository is structured:

| Path | Purpose |
| :--- | :--- |
| `Advent-of-Code/` | Repository root |
| `README.md` | Repository overview, quickstart, and walkthrough links |
| `AGENTS.md` | Instructions for coding agents and automated reviewers |
| `pyproject.toml` & `uv.lock` | Dependency definitions and Python `>=3.13` config managed via `uv` |
| `Makefile` | Common workflows (`make install`, `make check`, `make new-year YEAR=2026`, `make docs`) |
| `.gitignore` & `.gitattributes` | Excludes `.venv/` / caches / plaintext secrets and configures `git-crypt` filters |
| `.env` & `.env.template` | Local environment variables (`PYTHONPATH=src`, `AOC_SESSION_COOKIE`; tracked safely via `.env.enc`) |
| `.venv/` | Local Python virtual environment managed by `uv` |
| `src/AoC_YYYY/` | Puzzle solutions per year (`d01/`..`d25/` for 2015–2024; `d01/`..`d12/` from 2025 onwards), plus `input/` folders or `.ipynb` notebooks |
| `src/aoc_common/aoc_commons.py` | Shared reusable helpers (`Point`, `Grid`, `Locations`, logging, `write_puzzle_input_file`) |
| `src/template_folder/` | Starter Python script (`template.py`) and Jupyter notebook templates |
| `src/tests/test_aoc_commons.py` | Offline unit test suite (`uv run pytest src/tests`) |
| `docs/YYYY/` | Jekyll Markdown walkthroughs for each day |
| `docs/python/` | Reusable Python concepts and guides |
| `scripts/create_year.sh` | Bash script that scaffolds `src/AoC_<year>/d01..d<days>` from `src/template_folder/` (defaults to 12 days) |
| `.agents/skills/` | Workspace AoC skills tracked via `git-crypt` (`.enc` twins) |
