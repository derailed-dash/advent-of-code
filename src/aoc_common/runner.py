"""Rich-formatted and agent-friendly Advent of Code puzzle runner.

Purpose & Value:
    Removes per-day ``argparse``, timing, sample-assertion, and formatting boilerplate from
    Template v3 scripts while offering one consistent CLI across humans and coding agents
    (via structured ``--json`` output and clean ``stderr`` logging). Sample validation also
    works directly inside Jupyter notebooks without calling ``sys.exit``.

Mechanics & Execution Flow:
    - :data:`SampleInput`: ``(sample_source, expected_answer)`` tuple where ``sample_source``
      is a :class:`pathlib.Path` or inline ``str``. Setting ``expected_answer=None`` skips
      that sample check cleanly while scaffolding.
    - :func:`check_samples`: runs ``part_fn(parse_fn(raw))`` under temporary ``DEBUG``
      logging, ignores unimplemented parts returning ``None``, and raises
      ``AssertionError`` on mismatch so notebook cells fail visibly without killing kernels.
    - :func:`run_puzzle`: parses ``-p/--part``, ``-s/--sample-only``, ``--no-samples``,
      ``-d/--debug``, and ``--json``; runs samples first (halting before touching real
      ``input.txt`` on failure); fetches/reads ``input.txt`` lazily; passes a fresh
      ``parse_input(raw)`` copy to each enabled part; and prints either a Rich summary
      table (:func:`format_duration`) or pure JSON on ``stdout``.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from aoc_common.aoc_commons import Locations

type SampleInput = tuple[Path | str, Any]


@dataclass(frozen=True, slots=True)
class PartRunSummary:
    """Execution summary and timing metadata for one puzzle part."""

    part: int
    status: str
    answer: Any = None
    elapsed_seconds: float | None = None
    samples_checked: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise the part summary to a JSON-compatible dictionary."""
        return {
            "part": self.part,
            "status": self.status,
            "answer": self.answer,
            "elapsed_seconds": round(self.elapsed_seconds, 6) if self.elapsed_seconds is not None else None,
            "elapsed_display": format_duration(self.elapsed_seconds) if self.elapsed_seconds is not None else None,
            "samples_checked": self.samples_checked,
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class PuzzleRunSummary:
    """Aggregate execution summary for a puzzle run."""

    year: int
    day: int
    status: str
    sample_only: bool
    parts: tuple[PartRunSummary, ...]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise the puzzle run summary to a JSON-compatible dictionary."""
        return {
            "year": self.year,
            "day": self.day,
            "status": self.status,
            "sample_only": self.sample_only,
            "parts": [part.to_dict() for part in self.parts],
            "error": self.error,
        }


def format_duration(seconds: float) -> str:
    """Format elapsed seconds using adaptive ``µs``, ``ms``, or ``s`` units."""
    if seconds < 1e-3:
        return f"{seconds * 1_000_000:.1f} µs"
    if seconds < 1.0:
        return f"{seconds * 1_000:.2f} ms"
    return f"{seconds:.3f} s"


def _default_parse(raw: str) -> list[str]:
    """Split raw puzzle text into lines."""
    return raw.splitlines()


def check_samples(
    part_fn: Callable[[Any], Any],
    samples: Sequence[SampleInput],
    *,
    parse_fn: Callable[[str], Any] = _default_parse,
    part_label: str = "Part 1",
    logger: logging.Logger | None = None,
) -> int:
    """Validate ``part_fn`` against inline or file-based sample inputs.

    Temporarily sets ``logger`` to ``logging.DEBUG`` during sample execution and
    always restores its original level. Skips samples whose expected value is
    ``None``, returns ``0`` without error if ``part_fn`` returns ``None``, and
    raises ``AssertionError`` (never ``sys.exit``) on mismatch so notebook cells
    remain safe.
    """
    active_logger = logger or logging.getLogger(part_fn.__module__)
    previous_level = active_logger.level
    active_logger.setLevel(logging.DEBUG)
    checked = 0
    try:
        for index, (source, expected) in enumerate(samples, start=1):
            if expected is None:
                active_logger.debug("%s sample %d skipped (expected answer is None)", part_label, index)
                continue

            if isinstance(source, Path):
                if not source.exists():
                    raise FileNotFoundError(f"{part_label} sample {index} file not found: {source}")
                if source.stat().st_size == 0:
                    raise ValueError(f"{part_label} sample {index} file is empty: {source}")
                raw = source.read_text(encoding="utf-8")
            else:
                raw = source

            parsed = parse_fn(raw)
            actual = part_fn(parsed)
            if actual is None:
                active_logger.info("%s returned None (not implemented yet); skipping sample check", part_label)
                return 0

            validate(actual, expected)
            checked += 1

        if checked > 0:
            active_logger.info("%s sample checks passed (%d)", part_label, checked)
        return checked
    finally:
        active_logger.setLevel(previous_level)


def _build_parser(year: int, day: int) -> argparse.ArgumentParser:
    """Construct the standard Template v3 argument parser."""
    parser = argparse.ArgumentParser(
        description=f"Advent of Code {year} Day {day:02d}",
    )
    parser.add_argument(
        "-p",
        "--part",
        choices=("1", "2", "all"),
        default="all",
        help="Puzzle part to execute (default: all).",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Keep DEBUG logging active while running real puzzle input.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print structured JSON output to stdout and route logs to stderr.",
    )
    sample_group = parser.add_mutually_exclusive_group()
    sample_group.add_argument(
        "-s",
        "--sample-only",
        action="store_true",
        help="Validate sample inputs only without downloading or reading real input.",
    )
    sample_group.add_argument(
        "--no-samples",
        action="store_true",
        help="Skip sample validation and run directly against real puzzle input.",
    )
    return parser


def _emit_summary(summary: PuzzleRunSummary, *, as_json: bool) -> None:
    """Render ``summary`` as JSON on stdout or as a Rich table."""
    if as_json:
        print(json.dumps(summary.to_dict(), indent=2, default=str))
        return

    table = Table(title=f"Advent of Code {summary.year} Day {summary.day:02d}")
    table.add_column("Part", style="cyan")
    table.add_column("Status")
    table.add_column("Samples", justify="right")
    table.add_column("Answer", style="bold green")
    table.add_column("Time", justify="right")

    status_styles = {"ok": "green", "skipped": "yellow", "failed": "red", "error": "red"}
    for part in summary.parts:
        style = status_styles.get(part.status, "white")
        answer_str = "-" if part.answer is None else str(part.answer)
        time_str = format_duration(part.elapsed_seconds) if part.elapsed_seconds is not None else "-"
        table.add_row(
            f"Part {part.part}",
            f"[{style}]{part.status}[/{style}]",
            str(part.samples_checked),
            answer_str,
            time_str,
        )
    Console().print(table)


def run_puzzle(
    *,
    year: int,
    day: int,
    part1: Callable[[Any], Any],
    part2: Callable[[Any], Any] | None = None,
    parse_input: Callable[[str], Any] = _default_parse,
    part1_samples: Sequence[SampleInput] = (),
    part2_samples: Sequence[SampleInput] = (),
    locations: Locations | None = None,
    caller_file: str | Path | None = None,
    logger: logging.Logger | None = None,
    argv: Sequence[str] | None = None,
) -> int:
    """Execute a Template v3 AoC puzzle solution with standard CLI flags and Rich output."""
    args = _build_parser(year, day).parse_args(list(argv) if argv is not None else None)
    run_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(level=run_level, stderr=args.json)

    active_logger = logger or logging.getLogger(f"aoc{year}d{day:02d}")
    active_logger.setLevel(run_level)
    resolved_locations = locations or get_aoc_locations(year, day, caller_file)

    selected_parts = [1, 2] if args.part == "all" else [int(args.part)]
    part_fns: dict[int, Callable[[Any], Any] | None] = {1: part1, 2: part2}
    part_samples: dict[int, Sequence[SampleInput]] = {1: part1_samples, 2: part2_samples}
    samples_checked: dict[int, int] = {1: 0, 2: 0}

    # 1. Sample checks first (never touches real input on failure or --sample-only)
    if not args.no_samples:
        for part_num in selected_parts:
            fn = part_fns[part_num]
            samples = part_samples[part_num]
            if fn is None or not samples:
                continue
            try:
                samples_checked[part_num] = check_samples(
                    fn,
                    samples,
                    parse_fn=parse_input,
                    part_label=f"Part {part_num}",
                    logger=active_logger,
                )
            except (AssertionError, FileNotFoundError, ValueError) as exc:
                err_msg = f"Part {part_num} sample check failed: {exc}"
                failed_part = PartRunSummary(
                    part=part_num,
                    status="failed",
                    samples_checked=samples_checked[part_num],
                    error=str(exc),
                )
                summary = PuzzleRunSummary(
                    year=year,
                    day=day,
                    status="failed",
                    sample_only=bool(args.sample_only),
                    parts=(failed_part,),
                    error=err_msg,
                )
                if args.json:
                    _emit_summary(summary, as_json=True)
                else:
                    Console(stderr=True).print(f"[red]{err_msg}[/red]")
                return 1

    if args.sample_only:
        sample_parts = tuple(
            PartRunSummary(
                part=part_num,
                status="skipped" if part_fns[part_num] is None else "ok",
                samples_checked=samples_checked[part_num],
            )
            for part_num in selected_parts
        )
        _emit_summary(
            PuzzleRunSummary(year=year, day=day, status="ok", sample_only=True, parts=sample_parts),
            as_json=args.json,
        )
        return 0

    # 2. Ensure and read real puzzle input
    try:
        write_puzzle_input_file(year, day, resolved_locations)
        raw_real = resolved_locations.input_file.read_text(encoding="utf-8")
    except (ValueError, FileNotFoundError, OSError) as exc:
        err_msg = (
            f"Could not read puzzle input ({resolved_locations.input_file}): {exc}. "
            "Check AOC_SESSION_COOKIE in your environment or .env file."
        )
        summary = PuzzleRunSummary(
            year=year,
            day=day,
            status="error",
            sample_only=False,
            parts=(),
            error=err_msg,
        )
        if args.json:
            _emit_summary(summary, as_json=True)
        else:
            Console(stderr=True).print(f"[red]{err_msg}[/red]")
        return 1

    # 3. Execute real parts cleanly with fresh parsed input per part
    active_logger.setLevel(run_level)
    real_parts: list[PartRunSummary] = []
    for part_num in selected_parts:
        fn = part_fns[part_num]
        if fn is None:
            real_parts.append(PartRunSummary(part=part_num, status="skipped", samples_checked=samples_checked[part_num]))
            continue

        parsed_real = parse_input(raw_real)
        started = time.perf_counter()
        answer = fn(parsed_real)
        elapsed = time.perf_counter() - started
        if answer is None:
            real_parts.append(
                PartRunSummary(
                    part=part_num,
                    status="skipped",
                    elapsed_seconds=elapsed,
                    samples_checked=samples_checked[part_num],
                )
            )
        else:
            active_logger.info("Part %d soln=%s (%s)", part_num, answer, format_duration(elapsed))
            real_parts.append(
                PartRunSummary(
                    part=part_num,
                    status="ok",
                    answer=answer,
                    elapsed_seconds=elapsed,
                    samples_checked=samples_checked[part_num],
                )
            )

    _emit_summary(
        PuzzleRunSummary(
            year=year,
            day=day,
            status="ok",
            sample_only=False,
            parts=tuple(real_parts),
        ),
        as_json=args.json,
    )
    return 0


# Imported after public definitions to avoid circular import when runner is imported before aoc_commons.
from aoc_common.aoc_commons import (  # noqa: E402
    get_aoc_locations,
    setup_logging,
    validate,
    write_puzzle_input_file,
)

__all__ = [
    "PartRunSummary",
    "PuzzleRunSummary",
    "SampleInput",
    "check_samples",
    "format_duration",
    "run_puzzle",
]
