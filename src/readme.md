# Welcome to the source for my Advent of Code Solutions

If you'd like to peruse this code along with my solution walkthroughs, take a look at [aoc.just2good.co.uk](https://aoc.just2good.co.uk/). See the root [`README.md`](../README.md) for full repository setup, the Daily AoC Workflow, and `git-crypt` maintainer details.

## Contents

- `AoC_YYYY/` — Per-year puzzle solutions (`d01/`..`d12/` from 2025+, `d01/`..`d25/` for 2015–2024, plus `.ipynb` notebooks in 2023–2024).
- [`aoc_common/`](aoc_common/aoc_commons.py) — Shared helper package installed editably into `.venv` (imported directly as `import aoc_common.aoc_commons as ac`), Rich runner (`runner.py`), and `aoc` CLI (`cli.py`).
- [`template_folder/`](template_folder/template.py) — Template v3 Python script and Jupyter notebook starters.
- [`tests/`](tests/test_aoc_commons.py) — Offline `pytest` unit test suite for `aoc_common`, the runner, and the CLI.

## Setting Up Your Environment

Dependencies and Python (`>=3.13`) are managed with [`uv`](https://docs.astral.sh/uv/) and [`pyproject.toml`](../pyproject.toml). Run these commands from the repository root:

```bash
# Install project, dev tooling, Jupyter, and legacy (2015-2024) dependencies
uv sync --dev --extra jupyter --extra legacy   # or: make install

# Inspect years or check input/sample readiness for one year
uv run aoc list
uv run aoc list 2025

# Run a puzzle via the aoc CLI (sample-only shown first; real inputs require AOC_SESSION_COOKIE)
uv run aoc run 2018d07 -s
# Optional (public clones): cp .env.template .env && make clean-inputs
uv run aoc fetch 2025d01 --write-sample
uv run aoc run 2025d01
uv run aoc new-year 2026 --dry-run

# Or run a standalone script / JupyterLab directly
uv run python src/AoC_2025/d01/d01.py
uv run jupyter lab

# Run offline checks (codespell, ruff, pyright, pytest)
make check
```
