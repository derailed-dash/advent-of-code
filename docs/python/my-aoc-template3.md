---
title: My AoC Template, Version 3
description: "Dazbo's current Advent of Code Python >=3.13 starter template — pure parse/part1/part2 functions, declarative SampleInput checks, Rich runner, and the uv run aoc CLI."
redirect_from:
  - /python/my-aoc-template2
  - /python/my-aoc-template2.html
tags:
  - name: My AoC Template (v1)
    link: /python/my-aoc-template
  - name: Reusable Code
    link: /python/reusable_code
  - name: Logging
    link: /python/logging
  - name: Using Colours
    link: /python/colours
  - name: Unit Testing
    link: /python/unit_test
---

## Page Contents

- [From Version 1 to Version 3 — Why It Evolved](#from-version-1-to-version-3--why-it-evolved)
- [Template v3 Source Code](#template-v3-source-code)
- [Key Architectural Improvements Explained](#key-architectural-improvements-explained)
- [Running with the `aoc` CLI and `Makefile`](#running-with-the-aoc-cli-and-makefile)
- [Daily Workflow](#daily-workflow)

## From Version 1 to Version 3 — Why It Evolved

Over several years of Advent of Code, my starter template went through three generations:

1. **[Template v1 (2021)](/python/my-aoc-template)**: Plain `logging.basicConfig`, `# INPUT_FILE = ...` comment toggling between sample and real data, and manual `time.perf_counter()` calls around a single monolithic `main()`.
2. **Template v2 (2023)**: Extracted shared path, HTTP download, and geometry helpers into [`aoc_common`](/python/reusable_code), adding `Locations`, automatic `write_puzzle_input_file(...)`, and `colorama`-coloured logging (`ColouredFormatter`) — though it still executed downloads eagerly at import time and relied on commenting lines in `main()` to switch inputs.
3. **Template v3 (2026 — Current)**: Separates pure puzzle logic (`parse_input`, `part1`, `part2`) from I/O and CLI orchestration via `ac.run_puzzle()`, replaces comment-toggling with declarative `SampleInput` verification, swaps `colorama` for `Rich`, and integrates directly with `uv run aoc`.

| Capability | Template v1 (2021) | Template v2 (2023) | Template v3 (2026) | Why Version 3 Is Better |
| :--- | :--- | :--- | :--- | :--- |
| **Input Retrieval** | Manual copy-paste | Import-time `write_puzzle_input_file()` | Lazy download inside `run_puzzle()` + `uv run aoc fetch` | Importing a script in tests no longer triggers HTTP calls or fails without `.env`. |
| **Sample vs Real Data** | Comment/uncomment `INPUT_FILE` | Comment/uncomment `locations.sample_input_file` | Declarative `PART1_SAMPLES` / `PART2_SAMPLES` + `-s` / `--no-samples` | Zero accidental edits before running real input; sample mismatches fail fast before touching `input.txt`. |
| **Code Structure** | Monolithic `main()` | Monolithic `main()` | Pure `parse_input(raw)`, `part1(data)`, `part2(data)` | Keeps Part 1 intact while developing Part 2 and passes fresh parsed copies to each part so mutations cannot leak. |
| **Logging & Output** | Plain `logging.basicConfig` | `colorama` `ColouredFormatter` | `RichHandler` via `ac.setup_logging(stderr=...)` + Rich summary table | Coloured console tracebacks, automatic `DEBUG` during sample checks, and clean `--json` `stdout` streams. |
| **Timing & Profiling** | Manual `t2 - t1` | Manual `t2 - t1` | Automatic per-part `perf_counter` via `run_puzzle()` (`format_duration`) | Separate Part 1 and Part 2 timings formatted adaptively in `µs`, `ms`, or `s`. |
| **Automation & Scaffolding** | Copy files by hand | `./scripts/create_year.sh` | `uv run aoc new-year` (12-day default) & `aoc run` / `aoc list` | Works uniformly across standalone scripts, agents (`--json`), and Colab/Jupyter notebooks (`check_samples`). |

## Template v3 Source Code

This is the live starter template stored at [`src/template_folder/template.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/template_folder/template.py){:target="_blank"}:

```python
"""Author: Darren
Date: 01/12/2026

Solving https://adventofcode.com/2026/day/1

Template v3 standalone solution module powered by :func:`aoc_common.run_puzzle`.

How This Module Works:
    1. Paste the example input into ``input/sample_input_part_1.txt`` and update
       ``PART1_SAMPLES`` (replacing ``None`` with the example's expected answer).
    2. Implement ``parse_input(raw)`` — called fresh before each sample and before each
       real part so mutating parsed data in Part 1 cannot affect Part 2.
    3. Implement ``part1(data)`` and ``part2(data)``. Returning ``None`` marks a part as
       not started so it skips cleanly without failing.
    4. Run via ``make run <day>``, ``uv run --no-sync aoc run <year> <day> [flags]``,
       or directly with ``uv run --no-sync python <script.py> [flags]``:
       - ``-s`` / ``--sample-only``: validate sample assertions only (uses ``DEBUG`` logs)
       - ``-p {1,2,all}``: run Part 1, Part 2, or both (defaults to ``all``)
       - ``--no-samples``: skip sample validation before running on ``input.txt``
       - ``-d`` / ``--debug``: keep ``DEBUG`` logging active on real ``input.txt``
       - ``--json``: emit machine-readable JSON on stdout and Rich logs on stderr

    Real puzzle input (``input/input.txt``) is downloaded lazily on demand when running
    against real data and ``AOC_SESSION_COOKIE`` is configured.

Part 1:

Part 2:
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle (updated automatically by scripts/create_year.sh and `aoc new-year`)
YEAR: int = 2026
DAY: int = 1

locations = ac.get_aoc_locations(YEAR, DAY, __file__)
logger = logging.getLogger(locations.script_name)

# Sample checks: list of (sample_source, expected_answer) pairs verified before real input.
# - sample_source: Path to a file in input/ (e.g. locations.input_dir / "sample_input_part_1.txt")
#                  or a raw inline string (e.g. "1abc2\npqr3stu8vwx").
# - expected_answer: expected result for that sample (e.g. 142 or "xyz").
#                    Leave as None while scaffolding — entries with None are skipped rather
#                    than failing. Replace None with the puzzle's example answer once known.
PART1_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", None),  # e.g. (..., 142) or ("inline\nsample", 142)
]
PART2_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", None),  # or sample_input_part_2.txt if Part 2 differs
]


def parse_input(raw: str) -> list[str]:
    """Parse raw puzzle input into a fresh structure per part."""
    return raw.splitlines()


def part1(data: list[str]) -> int | str | None:
    """Solve Part 1 and return the answer (or ``None`` while unimplemented)."""
    return None


def part2(data: list[str]) -> int | str | None:
    """Solve Part 2 and return the answer (or ``None`` while unimplemented)."""
    return None


def main(argv: Sequence[str] | None = None) -> int:
    """Run sample validation and puzzle parts via the shared Rich runner."""
    return ac.run_puzzle(
        year=YEAR,
        day=DAY,
        part1=part1,
        part2=part2,
        parse_input=parse_input,
        part1_samples=PART1_SAMPLES,
        part2_samples=PART2_SAMPLES,
        locations=locations,
        logger=logger,
        argv=argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

## Key Architectural Improvements Explained

### 1. Import-Safe Modules (`get_aoc_locations` Without Import-Time I/O)

In Version 2, calling `write_puzzle_input_file()` at module scope meant merely importing a solution from a test runner or inspection script tried to hit `adventofcode.com` or read `.env`. Version 3 computes paths only via `ac.get_aoc_locations(YEAR, DAY, __file__)`, leaving `.env` loading, `git-crypt` lock checks, and HTTP caching inside `ac.run_puzzle()`.

### 2. Pure `parse_input` and Isolated `part1` / `part2`

Separating parsing from solving ensures that:

- Developing Part 2 cannot accidentally break Part 1's input representation.
- `run_puzzle()` calls `parse_input(raw)` freshly for Part 1 and again for Part 2, so in-place mutations (e.g. modifying a [`Grid`](/python/reusable_code) or popping from a `list`) in Part 1 never corrupt Part 2.
- Unimplemented parts return `None`, which `check_samples()` and `run_puzzle()` cleanly skip without failing CI or scaffolds.

### 3. Declarative `SampleInput` Pairs

`SampleInput` is a type alias for `tuple[Path | str, Any]` — meaning a sample entry can reference either a file on disk (`locations.input_dir / "sample_input_part_1.txt"`) or an inline multi-line string directly in Python. Setting the expected value to `None` skips assertion while scaffolding; once you read the puzzle example, replacing `None` with the expected answer turns every subsequent run into an automatic regression test:

```python
PART1_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", 42),
    ("small-inline-edge-case\n1 2 3\n", 6),
]
```

### 4. Built-In Runner Flags, Rich Tables, and `--json` Mode

Passing `argv` into `ac.run_puzzle()` equips every day script with consistent CLI flags:

- `-s` / `--sample-only`: Run sample checks with automatic `DEBUG` logging without requiring or downloading `input.txt`.
- `-p {1,2,all}` / `--part {1,2,all}`: Focus on Part 1, Part 2, or both.
- `--no-samples`: Skip sample checks when iterating on real input performance.
- `-d` / `--debug`: Keep `DEBUG` logging enabled when running against real `input.txt` (by default, real runs drop back to `INFO` so verbose sample traces don't flood your terminal).
- `--json`: Route Rich logs to `stderr` and emit a clean JSON execution summary to `stdout` for scripts and AI coding agents.

## Running with the `aoc` CLI and `Makefile`

Rather than invoking deeply nested paths by hand, [`pyproject.toml`](https://github.com/derailed-dash/Advent-of-Code/blob/master/pyproject.toml){:target="_blank"} exposes a repository-wide `aoc` entry point via `uv run aoc` (with matching shortcuts in [`Makefile`](https://github.com/derailed-dash/Advent-of-Code/blob/master/Makefile){:target="_blank"}):

```bash
uv run aoc new-year 2026                # Scaffold AoC_2026/d01..d12 from Template v3 (default: 12 days for 2025+)
uv run aoc fetch 2026d01 --write-sample # Fetch puzzle description in memory and populate sample_input_part_1.txt
uv run aoc run 2026d01 -s -d            # Run sample checks with DEBUG logging (or: make run 2026d01 ARGS="-s -d")
uv run aoc run 2026 1 -p 2              # Run Part 2 on real input.txt
uv run aoc list 2026                    # Rich progress table with clickable OSC 8 links to adventofcode.com
```

Notice that Advent of Code moved from a 25-day event (`2015`–`2024`) to a **12-day event from `2025` onwards**, so `uv run aoc new-year` defaults to `--days 12` unless you pass `--days 25` for a legacy year.

Running a scaffolded script in sample-only mode (`uv run aoc run 2018d07 -s`) emits clean Rich logs followed by a colour-coded summary table:

```text
INFO     22:31:59.334 Part 1 returned None (not implemented yet); skipping sample check
DEBUG    22:31:59.336 Part 2 sample 1 skipped (expected answer is None)
```

**Advent of Code 2018 Day 07**

| Part | Status | Samples | Answer | Time |
| :--- | :--- | :---: | :--- | :--- |
| Part 1 | `ok` | `0` | `-` | `-` |
| Part 2 | `ok` | `0` | `-` | `-` |

## Daily Workflow

1. **Fetch description & sample**: `uv run aoc fetch 2026d01 --write-sample`
2. **Wire expected sample value** into `PART1_SAMPLES` and implement `parse_input()` + `part1()`.
3. **Iterate offline-first**: `uv run aoc run 2026d01 -s -d` until Part 1 passes every sample.
4. **Solve real input**: `uv run aoc run 2026d01 -p 1`, submit manually on [adventofcode.com](https://adventofcode.com/), then repeat for Part 2 (`-p 2`).
5. **Verify quality**: `make check` (`codespell`, `ruff`, `pyright`, and `pytest src/tests`).
