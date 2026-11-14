---
title: Project Structure
description: Clear, maintainable Python project layout and Advent of Code repository architecture, from shared libraries to documentation.
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
| `.env.template` | Template listing expected environment variables (e.g. `PYTHONPATH`, `AOC_SESSION_COOKIE`) |
| `Makefile` | Convenience commands (`install`, `check`, `test`, `lint`, `run`, `fetch`) |
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
| `AGENTS.md` | Instructions for local coding agents and automated CI reviewers |
| `pyproject.toml` & `uv.lock` | Dependency definitions and Python `>=3.13` config managed via `uv` |
| `Makefile` | Workflow automation (`make install`, `make check`, `make run`, `make fetch`, `make new-year`, `make clean-inputs`, `make docs`) |
| `.gitignore` & `.gitattributes` | Excludes `.venv/`, caches, and plaintext secrets; configures `git-crypt` filters |
| `.env` & `.env.template` | Local environment variables (`PYTHONPATH=src`, `AOC_SESSION_COOKIE`; tracked safely via `.env.enc`) |
| `.venv/` | Local Python virtual environment managed by `uv` |
| `src/AoC_YYYY/` | Puzzle solutions per year (`d01/`..`d25/` for 2015–2024; `d01/`..`d12/` from 2025 onwards), plus `input/` folders or `.ipynb` notebooks |
| `src/aoc_common/` | Shared repository package installed editably in `.venv/` |
| `src/aoc_common/aoc_commons.py` | Shared reusable helpers (`Point`, `Grid`, `to_base_n`, interval merging, `is_git_crypt_locked`) |
| `src/aoc_common/runner.py` | Rich console runner driving `run_puzzle`, `SampleInput` checks, and automatic execution timing |
| `src/aoc_common/cli.py` | Unified repository CLI (`uv run aoc run`, `list`, `fetch`, `new-year`, `clean-inputs`) |
| `src/template_folder/template.py` | [Template v3](/python/my-aoc-template3) starter script (`-p`, `-s`, `--no-samples`, `-d`, `--json`) |
| `src/template_folder/jupyter_template.ipynb` | Starter Jupyter notebook template |
| `src/tests/test_aoc_commons.py` | Offline unit tests for common algorithms and spatial primitives |
| `src/tests/test_runner_and_cli.py` | Offline unit tests for the test runner and CLI parser |
| `scripts/create_year.sh` | Standalone Bash fallback script to scaffold `src/AoC_<year>/d01..d<days>` |
| `scripts/git-crypt-helper.sh` | Automation script to synchronise parallel `.enc` secret twins (`status`, `sync-from-enc`, `sync-to-enc`) |
| `docs/` | Jekyll documentation site styled with the custom **Midnight AoC** dark-first theme |
| `docs/YYYY/` | Jekyll Markdown walkthroughs for each puzzle day |
| `docs/python/` | Reusable Python concepts, tutorials, and guides |
| `.agents/skills/` | Workspace AoC agent skills tracked securely via `git-crypt` (`.enc` twins) |

## Scaffolding New Years and Days

Advent of Code changed from a 25-day event (2015–2024) to a **12-day event from 2025 onwards**. Our scaffolding tooling defaults to 12 days automatically:

```bash
# Scaffold an entire year from Template v3 (defaults to 12 days):
uv run aoc new-year 2026               # or: make new-year 2026

# Scaffold an older legacy year with 25 days:
uv run aoc new-year 2024 --days 25

# Bash fallback if working without uv:
./scripts/create_year.sh 2026
```

Each generated day folder (e.g. `src/AoC_2026/d01/`) contains:

- `d01.py` — A standalone solution script based on [Template v3](/python/my-aoc-template3).
- `input/` — Subdirectory holding `sample_input_part_1.txt` and `sample_input_part_2.txt`. Real puzzle input (`input/input.txt`) is downloaded lazily on demand via `uv run aoc fetch` or upon running against real data, avoiding empty placeholder files in version control.
