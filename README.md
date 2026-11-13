# Dazbo's Advent of Code

### See my walkthroughs at [aoc.just2good.co.uk](https://aoc.just2good.co.uk/).

- **Author:** [Darren "Dazbo" Lester](https://darrenlester.net)
- [Medium (`@dazbo`)](https://medium.com/@dazbo)
- [GitHub (`derailed-dash`)](https://github.com/derailed-dash)

- **Author:** [Darren "Dazbo" Lester](https://darrenlester.net) · [Medium (`@dazbo`)](https://medium.com/@dazbo) · [GitHub (`derailed-dash`)](https://github.com/derailed-dash)

## Overview

- My solutions to Advent of Code problems for multiple years, written in Python.
- All solutions are thoroughly documented.
- Some days have multiple solutions where I've experimented with different approaches or libraries.

[![Dazbo's AoC Walkthroughs](docs/assets/images/AoC_site_screenshot.jpg)](https://aoc.just2good.co.uk/)

## Purpose of this Repo

I've been using [Advent of Code](https://adventofcode.com/) as a way to improve my **Python** skills. Here I document my solutions across the various AoC years. My hope is that this guide will help others to:

- Become more proficient with Python.
- Solve AoC problems they might be stuck with.
- Learn some new libraries and inventive ways of doing things.

## Use of my Code

This software is shared as open source. However, if you use it in your own solutions and/or incorporate it into your own repos, please consider giving acknowledgement to me, and linking back to this repo, my [walkthrough site](https://aoc.just2good.co.uk/), or [darrenlester.net](https://darrenlester.net). That would be really kind!

## What is Advent of Code?

An awesome [coding challenge](https://adventofcode.com/about) created by Eric Wastl, released every December. A new problem is presented each day through the month. Typically the best way to solve any given problem is by writing a program. The program can be written in _any language and with any tools you like_. You don't need to be an expert coder to do AoC; in fact, AoC is a great way to learn a programming language.

Some problems are quite trivial and can be solved quickly; others can be a total PITA. Typically, the problems get harder as the event progresses.

You don't have to wait until December to try your hand at AoC though. All previous events are available, and can be completed at _any_ time.

Each day is split into a Part 1 and a Part 2. A star is awarded for each completed challenge. From 2015–2024, AoC ran for 25 days (50 stars to save Christmas!); from 2025 onwards, it runs as a 12-day event (24 stars).

## Prerequisites & Setup

To run the solutions in this repository, you'll need the following:

- **Python >=3.13**
- **[`uv`](https://docs.astral.sh/uv/)**: Manages the virtual environment, Python runtime, and lockfile dependencies (`pyproject.toml` / `uv.lock`).
- **Jupyter**: Installed via `--extra jupyter` for running the notebook-based solutions (`.ipynb` files).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/derailed-dash/Advent-of-Code.git
   cd Advent-of-Code
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   # Install project, dev tooling, and Jupyter dependencies
   make install   # runs: uv sync --dev --extra jupyter
   ```

3. **Run solutions and checks:**
   - **Python scripts:**
     ```bash
     uv run python src/AoC_2025/d01/d01.py
     ```
   - **Jupyter Notebooks:** Open directly in VS Code or launch JupyterLab locally:
     ```bash
     uv run jupyter lab
     ```
   - **Run offline lint, spellcheck, typecheck, and unit tests:**
     ```bash
     make check     # runs codespell, ruff, pyright, and pytest src/tests
     ```

## Structure and Solution Approaches

This repository is organised by year and solution type. I've taken two main approaches for my solutions:

### 1. Python Scripts with Separate Walkthroughs

For most years (e.g., 2015–2022, 2025+), the solutions are Python scripts accompanied by detailed Markdown walkthroughs published at [aoc.just2good.co.uk](https://aoc.just2good.co.uk/).

- **Code**: Solution scripts (`.py`) live under `src/AoC_YYYY/dNN/`.
- **Walkthroughs**: Companion Markdown files (`.md`) live under `docs/YYYY/`, built with Jekyll.

### 2. Jupyter Notebooks

For some years (e.g., 2023–2024), solutions use Jupyter Notebooks combining Python code and narrative walkthroughs in a single `.ipynb` file inside `src/AoC_YYYY/`.

### Directory Structure

| Path | Purpose |
| :--- | :--- |
| [`docs/`](docs/index.md) | Jekyll source for [aoc.just2good.co.uk](https://aoc.just2good.co.uk/) (`docs/YYYY/` walkthroughs, `docs/python/` guides, `_config.yml`, `docker-compose.yml`) |
| `src/AoC_YYYY/` | Solution folders (`d01/`..`d12/` from 2025+, `d01/`..`d25/` for 2015–2024), or `.ipynb` notebooks |
| [`src/aoc_common/`](src/aoc_common/aoc_commons.py) | Shared utility package (`Locations`, `Point`, `Grid`, `write_puzzle_input_file`, algorithms, coloured logging) |
| [`src/template_folder/`](src/template_folder/template.py) | Starter Python script and Jupyter notebook templates |
| [`src/tests/`](src/tests/test_aoc_commons.py) | Offline `pytest` / `unittest` suite for `aoc_common` |
| [`scripts/`](scripts/create_year.sh) | Helper scripts such as [`create_year.sh`](scripts/create_year.sh) |
| [`.github/workflows/`](.github/workflows/pr-checks.yml) | CI checks (`pr-checks.yml`) and Gemini PR/issue workflows |
| `.agents/skills/` | Workspace AoC skills (`SKILL.md.enc` encrypted with `git-crypt`) |
| [`Makefile`](Makefile) | Common targets (`install`, `lint`, `test`, `check`, `new-year`, `docs`, `docs-build`, `docs-stop`, `sync-secrets`) |
| [`pyproject.toml`](pyproject.toml) | Project metadata, dependencies, `ruff`, `codespell`, and `pyright` configuration |
| [`.env.template`](.env.template) | Template environment variables (`PYTHONPATH=src`, `AOC_SESSION_COOKIE`) |
| [`AGENTS.md`](AGENTS.md) | Repository guide for coding agents and automated reviewers |

### Helper Libraries

Shared utilities live in [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py), which has **zero external dependency on `dazbo-commons`** (older historical scripts imported `dazbo-commons`, whereas current `aoc_common` and 2026+ templates handle everything self-contained):

- **AoC Utilities**: `Point`, `Vectors`, `VectorDicts`, and `Grid` classes for 2D grid problems; `binary_search`, `merge_intervals`, `get_factors`, and `to_base_n`; `timer` context manager; and `write_puzzle_input_file` (with AoC `User-Agent` header enforcement).
- **Coloured Console & File Logging**: Built-in `ColouredFormatter` (using `colorama`), `retrieve_console_logger`, and `setup_file_logging`.

Note that `aoc_common` is imported directly in standalone scripts, while notebooks stay self-contained so they remain portable (e.g. in Colab).

### Assertions and Testing

Each solution validates sample inputs via `aoc_common.validate` (raising `AssertionError` on mismatch), while `aoc_common` itself is tested offline via:

```bash
uv run pytest src/tests
```

## Helper Scripts & Makefile Targets

- [`scripts/create_year.sh`](scripts/create_year.sh): Bash script that scaffolds `src/AoC_<year>/d01..d<days>` from `src/template_folder/`. Defaults to `12` days for 2025+ events (`./scripts/create_year.sh 2026` or `make new-year YEAR=2026`), or pass an explicit count for legacy years (`./scripts/create_year.sh 2024 25`).
- `make check`: Runs `codespell -s`, `ruff check --diff`, `pyright`, and `pytest src/tests`.

## Documentation Website

This repository includes a companion static website with detailed walkthroughs and Python guides.

- **Website URL**: [https://aoc.just2good.co.uk/](https://aoc.just2good.co.uk/)
- **Technology**: Static site built with [Jekyll](https://jekyllrb.com/)
- **Source**: Markdown content, layouts, and styles in [`docs/`](docs/index.md)

### Working with the Documentation Locally

You can build and serve the documentation website locally using Docker:

```bash
make docs   # runs: cd docs && docker compose up
```

The site will be available at `http://127.0.0.1:4000`. If you need to supply `JEKYLL_GITHUB_TOKEN`, restore `docs/.env` via `make sync-secrets` (`git-crypt-helper.sh sync-from-enc`) or copy [`docs/.env.template`](docs/.env.template) to `docs/.env`.
