# Welcome to the source for my Advent of Code Solutions

If you'd like to peruse this code along with my solution walkthroughs, then take a look at [aoc.just2good.co.uk](https://aoc.just2good.co.uk/).

## Setting Up Your Environment

Dependencies and Python (`>=3.13`) are managed with [`uv`](https://docs.astral.sh/uv/) and [`pyproject.toml`](../pyproject.toml):

```bash
# Install project, dev tooling, and Jupyter dependencies
uv sync --dev --extra jupyter   # or: make install

# Run a puzzle solution
uv run python src/AoC_2025/d01/d01.py

# Run offline checks (codespell, ruff, pyright, pytest)
make check
```
