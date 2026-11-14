"""Author: Darren
Date: 14/11/2026

Solving https://adventofcode.com/2018/day/18

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
YEAR: int = 2018
DAY: int = 18

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
