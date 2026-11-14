# Dazbo's Advent of Code

### See my walkthroughs at [aoc.just2good.co.uk](https://aoc.just2good.co.uk/).

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
- **Legacy (`2015`–`2024`) Dependencies**: Historical solutions that still import `dazbo-commons` / `colorama` are supported via `--extra legacy` (included in `make install`).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/derailed-dash/Advent-of-Code.git
   cd Advent-of-Code
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   # Install project, dev tooling, Jupyter, and legacy (2015-2024) dependencies
   make install   # runs: uv sync --dev --extra jupyter --extra legacy
   ```

3. **Run solutions and checks:**
   - **Repository CLI (`aoc`):** Run via `uv run aoc ...` (or `make list` / `make run` / `make new-year`):
     ```bash
     uv run aoc list                     # Overview of all years, day counts, and Standalone/Jupyter format
     uv run aoc list 2025                # Inspect day scripts and sample/real input readiness for one year
     uv run aoc run 2026 1 -s            # Template v3 run (samples only)
     uv run aoc run 2025 1               # Runs legacy standalone scripts too
     uv run aoc new-year 2026 --dry-run  # Preview scaffolding d01..d12 from Template v3
     ```
   - **Python scripts directly:**
     ```bash
     uv run python src/AoC_2026/d01/d01.py --sample-only
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

## Using the `aoc` CLI

[`pyproject.toml`](pyproject.toml) exposes `[project.scripts] aoc = "aoc_common.cli:main"`, implemented in [`src/aoc_common/cli.py`](src/aoc_common/cli.py). Invoke it from the repository root with `uv run aoc <subcommand> ...` (add `--no-sync` after `uv run` for instant startup once `.venv` is synced via `make install`).

### Subcommands & Parameters

| Command | Parameters & Flags | Purpose |
| :--- | :--- | :--- |
| Global | `--root PATH` | Override auto-detected repository root (useful in scripts or tests) |
| `aoc list` | `[YEAR]` `--json` | List every `AoC_YYYY` year with `Completed/Total` progress (`e.g. 25/25, 12/25, 12/12`) and solution format (`Standalone (.py)`, `Jupyter (.ipynb)`, or `Both`), or inspect `dNN` solved status, scripts, and boolean input/sample readiness for one `YEAR` (terminal output adds clickable OSC 8 hyperlinks on `Year` and `Day` columns pointing to the AoC event and problem pages; never reads input file contents) |
| `aoc run` | `<TARGET> [DAY]` (`1`, `01`, `d01`, `20251`, `202501`, or `2025 1`) `-p/--part {1,2,all}` `-s/--sample-only` `--no-samples` `-d/--debug` `--json` `--script FILENAME` | Execute a puzzle script; runs Template v3 scripts in-process via [`run_puzzle`](src/aoc_common/runner.py) and legacy scripts via subprocess (when only a day is passed, picks `AOC_YEAR`, else current year if `src/AoC_<year>` exists, else latest existing `AoC_YYYY`; auto-resolves single scripts in historical `dNN_<slug>` folders or prompts with `--script` when multiple variants exist) |
| `aoc new-year` | `<YEAR>` `--days N` (1–25, default `12`) `--dry-run` `--force` `--json` | Scaffold `src/AoC_<YEAR>/d01..d<days>` from Template v3 without overwriting existing scripts (unless `--force`) and without creating empty `input.txt` files |

Individual Template v3 day scripts (such as [`src/template_folder/template.py`](src/template_folder/template.py)) also accept the same `-p/--part`, `-s/--sample-only`, `--no-samples`, `-d/--debug`, and `--json` flags directly via `uv run python ...` (`-s` and `--no-samples` are mutually exclusive; `--json` emits clean JSON on `stdout` and routes Rich logs to `stderr`).

### `Makefile` Integration

[`Makefile`](Makefile) wraps the primary CLI workflows while leaving standalone shell tooling available:

| Make Target | Underlying Command | Example |
| :--- | :--- | :--- |
| `make list` | `uv run aoc list ...` | `make list`, `make list 2025`, or `make list YEAR=2025` |
| `make run` | `uv run aoc run ...` | `make run 1`, `make run 01`, `make run 20251`, `make run 202501`, or `make run YEAR=2026 DAY=1 ARGS="-s -d"` *(pass runner flags via `ARGS="..."` because `make` intercepts bare `-s`/`-d`)* |
| `make new-year` | `uv run aoc new-year ...` | `make new-year 2026` or `make new-year YEAR=2026 DAYS=25` |
| [`scripts/create_year.sh`](scripts/create_year.sh) | Standalone Bash fallback (`sed` scaffold) | `./scripts/create_year.sh 2026` |

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
| [`src/aoc_common/`](src/aoc_common/aoc_commons.py) | Shared utility package (`aoc_commons.py`, `runner.py`, `cli.py`: `Locations`, `get_aoc_locations`, `run_puzzle`, `Point`, `Point3D`, `Grid`, algorithms, Rich logging) |
| [`src/template_folder/`](src/template_folder/template.py) | Starter Python script and Jupyter notebook templates (Template v3) |
| [`src/tests/`](src/tests/test_aoc_commons.py) | Offline `pytest` / `unittest` suite for `aoc_common`, `runner`, and `aoc` CLI |
| [`scripts/`](scripts/create_year.sh) | Helper scripts such as [`create_year.sh`](scripts/create_year.sh) |
| [`.github/workflows/`](.github/workflows/pr-checks.yml) | CI checks (`pr-checks.yml`) and Gemini PR/issue workflows |
| `.agents/skills/` | Workspace AoC skills (`SKILL.md.enc` encrypted with `git-crypt`) |
| [`Makefile`](Makefile) | Common targets (`install`, `lint`, `test`, `check`, `list`, `run`, `new-year`, `docs`, `docs-build`, `docs-stop`, `sync-secrets`) |
| [`pyproject.toml`](pyproject.toml) | Project metadata, dependencies, `ruff`, `codespell`, and `pyright` configuration |
| [`.env.template`](.env.template) | Template environment variables (`PYTHONPATH=src`, `AOC_SESSION_COOKIE`) |
| [`AGENTS.md`](AGENTS.md) | Repository guide for coding agents and automated reviewers |
| [`TODO.md`](TODO.md) | Project roadmap and improvement backlog |

### Helper Libraries

Shared utilities live in [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py) and have **zero dependency on `dazbo-commons`**. Because [`pyproject.toml`](pyproject.toml) includes a `[build-system]` packaging `src/aoc_common` editably into `.venv`, both standalone Python scripts and local Jupyter notebooks import `import aoc_common.aoc_commons as ac` directly without setting `PYTHONPATH=src` (and cloud notebooks such as Google Colab install `aoc_common` straight from GitHub):

- **Logging & Output**: `setup_logging` (configured with `RichHandler`, `force=True`, and `stderr=True` support for `--json` mode), `setup_file_logging`, and `top_and_tail`.
- **Paths & Input Retrieval**: `Locations`, `get_aoc_locations` (safe in both scripts via `__file__` and Jupyter/Colab notebooks without `__file__`), `get_locations`, and `write_puzzle_input_file` (with AoC `User-Agent` header enforcement).
- **Runner, Testing & Timing**: `run_puzzle` (`Rich` + `argparse` Template v3 CLI orchestration), `check_samples` (raises `AssertionError` cleanly without `sys.exit`), `validate`, `format_duration`, and the `timer` context manager.
- **2D/3D Geometry & Algorithms**: `Point`, `Point3D`, `Vectors`, `VectorDicts`, and `Grid` classes, sparse point-cloud helpers (`bounding_box`, `render_points`), plus `binary_search`, `lower_bound`, `upper_bound`, `merge_intervals`, `get_factors`, and `to_base_n`.

#### History: From `dazbo-commons` (`dc`) to `aoc_common` (`ac`)

1. **2021–2022 (`dazbo-commons` on PyPI)**: Published [`dazbo-commons-py`](https://github.com/derailed-dash/dazbo-commons-py) as a general-purpose PyPI utility package providing `colorama`-based `ColouredFormatter` / `retrieve_console_logger`, `Locations` / `get_locations`, `top_and_tail`, and `.env` loading (`get_envs_from_file`).
2. **May–Sep 2023 (`type_defs.py` → `aoc_commons.py`)**: Extracted AoC-specific helpers (`Point`, `Vectors`, `Grid`, `binary_search`, `merge_intervals`, `to_base_n`) into an in-repo `type_defs` module, renamed it to `aoc_commons.py`, and briefly trialled PyPI packaging before keeping it inside this repository.
3. **May 2024–Oct 2025 (Dual `dc` + `ac` era)**: Scripts and the 2024 notebook imported both `dazbo_commons as dc` (for general logging, `Locations`, and `top_and_tail`) and `aoc_common.aoc_commons as ac` (for AoC geometry and puzzle retrieval).
4. **Dec 2025–2026 (Consolidated `ac` + `Rich`)**: Replaced `colorama` logging with `Rich` (`RichHandler`), consolidated `Locations`, `load_dotenv()`, and `top_and_tail` back into `aoc_common`, enabled editable packaging in `pyproject.toml` so scripts and notebooks share a single import path, and moved `dazbo-commons` and `colorama` into `[project.optional-dependencies] legacy` solely so untouched `2015`–`2024` solutions remain runnable.

### Assertions and Testing

Each solution validates sample inputs via `aoc_common.validate` (raising `AssertionError` on mismatch), while `aoc_common` itself is tested offline via:

```bash
uv run pytest src/tests
```

## Helper Scripts & Makefile Targets

- [`uv run aoc new-year <year>`](src/aoc_common/cli.py), `make new-year YEAR=<year>`, and standalone [`scripts/create_year.sh`](scripts/create_year.sh): Scaffold `src/AoC_<year>/d01..d<days>` from [`src/template_folder/template.py`](src/template_folder/template.py) (default `12` days for 2025+; pass `--days 25` / `DAYS=25` for legacy counts).
- `make list [YEAR=<year>]` & `make run YEAR=<year> DAY=<day> [ARGS="..."]`: Convenience [`Makefile`](Makefile) wrappers around `uv run aoc list` and `uv run aoc run`.
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

The site will be available at `http://127.0.0.1:4000`. If you need to supply `JEKYLL_GITHUB_TOKEN`, restore `docs/.env` via `git-crypt-helper.sh sync-from-enc` (check sync status with `make sync-secrets`) or copy [`docs/.env.template`](docs/.env.template) to `docs/.env`.
