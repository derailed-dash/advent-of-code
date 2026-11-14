"""Offline unit and integration tests for locations, puzzle runner, and the ``aoc`` CLI.

Purpose & Value:
    Verifies the end-to-end execution, sample-validation, inspection, and scaffolding
    contracts across :func:`aoc_common.get_aoc_locations`, :mod:`aoc_common.runner`, and
    :mod:`aoc_common.cli` so refactors cannot silently break standalone scripts, notebooks,
    or CI checks.

Mechanics & Coverage:
    Constructs isolated synthetic repositories under pytest's ``tmp_path`` and mocks
    external HTTP retrieval so all cases run deterministically offline without
    ``AOC_SESSION_COOKIE``:
    - Notebook/Colab location resolution and input validation
    - ``format_duration``, ``check_samples``, and ``run_puzzle`` (``-p``, ``-s``,
      ``--no-samples``, ``-d``, and pure-stdout ``--json`` mode)
    - ``aoc list`` AST/notebook completion counting (2015-2024 vs 2025+) and format detection
    - ``aoc run`` shorthands (``1``, ``01``, ``20251``, ``202501``), ``AOC_YEAR`` defaults,
      legacy subprocess fallback, and ``aoc new-year`` dry-run/skip/force behaviour
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import aoc_common.aoc_commons as ac
from aoc_common import cli, runner


def _make_locations(root: Path, year: int = 2026, day: int = 1) -> ac.Locations:
    """Create a resolved ``Locations`` object inside ``root`` for testing."""
    script_dir = root / f"d{day:02d}"
    input_dir = script_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    return ac.Locations(
        script_dir=script_dir,
        script_name=f"aoc{year}d{day:02d}",
        input_dir=input_dir,
        output_dir=script_dir / "output",
        input_file=input_dir / "input.txt",
    )


def _create_template_repo(tmp_path: Path) -> Path:
    """Create a minimal temporary repo containing ``pyproject.toml`` and Template v3."""
    repo = tmp_path / "repo"
    template_dir = repo / "src" / "template_folder"
    template_dir.mkdir(parents=True)
    (repo / "pyproject.toml").write_text('[project]\nname = "test-aoc"\n', encoding="utf-8")
    (template_dir / "template.py").write_text(
        '''"""Solving https://adventofcode.com/2026/day/1."""

from collections.abc import Sequence
import aoc_common.aoc_commons as ac

YEAR: int = 2026
DAY: int = 1
locations = ac.get_aoc_locations(YEAR, DAY, __file__)
PART1_SAMPLES: list[ac.SampleInput] = [("1\\n2", 3)]
PART2_SAMPLES: list[ac.SampleInput] = [(locations.input_dir / "sample_input_part_1.txt", None)]


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line]


def part1(data: list[int]) -> int | None:
    return sum(data)


def part2(data: list[int]) -> int | None:
    return None


def main(argv: Sequence[str] | None = None) -> int:
    return ac.run_puzzle(
        year=YEAR,
        day=DAY,
        part1=part1,
        part2=part2,
        parse_input=parse_input,
        part1_samples=PART1_SAMPLES,
        part2_samples=PART2_SAMPLES,
        locations=locations,
        argv=argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
''',
        encoding="utf-8",
    )
    return repo


# ---------------------------------------------------------------------------
# get_aoc_locations & format_duration
# ---------------------------------------------------------------------------


def test_get_aoc_locations_with_caller_file(tmp_path: Path) -> None:
    script = tmp_path / "src" / "AoC_2026" / "d05" / "d05.py"
    script.parent.mkdir(parents=True)
    script.write_text("", encoding="utf-8")

    locs = ac.get_aoc_locations(2026, 5, script)
    expected = ac.get_locations(script)

    assert locs == expected
    assert locs.script_dir == script.parent
    assert locs.input_file == script.parent / "input" / "input.txt"
    assert locs.script_name == "d05.py"


def test_get_aoc_locations_walks_up_to_repo_root(tmp_path: Path) -> None:
    repo = tmp_path / "advent-of-code"
    (repo / "src").mkdir(parents=True)
    (repo / "pyproject.toml").write_text('[project]\nname = "aoc"\n', encoding="utf-8")
    nested = repo / "notebooks" / "scratch"
    nested.mkdir(parents=True)

    locs = ac.get_aoc_locations(2026, 5, base_dir=nested)

    assert locs.script_dir == repo / "src" / "AoC_2026" / "d05"
    assert locs.input_dir == locs.script_dir / "input"
    assert locs.input_file == locs.input_dir / "input.txt"
    assert locs.script_name == "aoc2026d05"


def test_get_aoc_locations_standalone_fallback(tmp_path: Path) -> None:
    colab_dir = tmp_path / "colab_content"
    colab_dir.mkdir()

    locs = ac.get_aoc_locations(2026, 5, base_dir=colab_dir)

    assert locs.script_dir == colab_dir / "d05"
    assert locs.input_dir == colab_dir / "d05" / "input"
    assert locs.input_file == colab_dir / "d05" / "input" / "input.txt"
    assert locs.script_name == "aoc2026d05"


def test_format_duration_units() -> None:
    us = runner.format_duration(5e-5)
    ms = runner.format_duration(0.0125)
    sec = runner.format_duration(1.234)

    assert us.endswith("µs")
    assert ms.endswith("ms")
    assert sec.endswith("s") and not sec.endswith("ms") and not sec.endswith("µs")


# ---------------------------------------------------------------------------
# check_samples
# ---------------------------------------------------------------------------


def test_check_samples_inline_and_path_restores_logger_level(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("10\n20\n", encoding="utf-8")
    observed_levels: list[int] = []

    test_logger = logging.getLogger("test.check_samples.restore")
    test_logger.setLevel(logging.WARNING)

    def solver(nums: list[int]) -> int:
        observed_levels.append(test_logger.level)
        return sum(nums)

    checked = runner.check_samples(
        solver,
        [("1\n2", 3), (sample_file, 30)],
        parse_fn=lambda raw: [int(x) for x in raw.splitlines() if x],
        part_label="Part 1",
        logger=test_logger,
    )

    assert checked == 2
    assert observed_levels == [logging.DEBUG, logging.DEBUG]
    assert test_logger.level == logging.WARNING


def test_check_samples_mismatch_raises_assertion_not_system_exit() -> None:
    test_logger = logging.getLogger("test.check_samples.mismatch")
    test_logger.setLevel(logging.INFO)

    with pytest.raises(AssertionError):
        runner.check_samples(
            lambda data: 99,
            [("abc", 42)],
            parse_fn=lambda raw: raw,
            logger=test_logger,
        )

    assert test_logger.level == logging.INFO


def test_check_samples_skips_none_expected_and_none_actual(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.txt"
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    # expected is None -> skips even if file doesn't exist
    assert runner.check_samples(lambda x: 1, [(missing_file, None)], parse_fn=lambda s: s) == 0

    # actual is None -> unimplemented, skips without failing even with expected answer
    assert runner.check_samples(lambda x: None, [("abc", 123)], parse_fn=lambda s: s) == 0

    # expected is not None + missing or empty file -> explicit errors
    with pytest.raises(FileNotFoundError):
        runner.check_samples(lambda x: 1, [(missing_file, 1)], parse_fn=lambda s: s)

    with pytest.raises(ValueError):
        runner.check_samples(lambda x: 1, [(empty_file, 1)], parse_fn=lambda s: s)


# ---------------------------------------------------------------------------
# run_puzzle
# ---------------------------------------------------------------------------


def test_run_puzzle_fresh_parse_per_part_and_none_skipped(tmp_path: Path) -> None:
    locs = _make_locations(tmp_path, 2026, 2)
    locs.input_file.write_text("1\n2\n3\n", encoding="utf-8")
    part2_seen: list[int] = []

    def parse_nums(raw: str) -> list[int]:
        return [int(line) for line in raw.splitlines() if line]

    def part1(data: list[int]) -> int:
        # Mutating data in-place must NOT affect part2
        total = sum(data)
        data.clear()
        return total

    def part2(data: list[int]) -> int | None:
        part2_seen.extend(data)
        return None

    rc = runner.run_puzzle(
        year=2026,
        day=2,
        part1=part1,
        part2=part2,
        parse_input=parse_nums,
        part1_samples=[("4\n5", 9)],
        locations=locs,
        argv=["--json"],
    )

    assert rc == 0
    assert part2_seen == [1, 2, 3]


def test_run_puzzle_part_filter_debug_and_sample_flags(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    locs = _make_locations(tmp_path, 2026, 3)
    locs.input_file.write_text("alpha\nbeta\n", encoding="utf-8")
    calls: list[str] = []
    real_levels: list[int] = []

    def p1(lines: list[str]) -> int:
        calls.append("p1")
        real_levels.append(logging.getLogger("test.run_puzzle.flags").level)
        return len(lines)

    def p2(lines: list[str]) -> int:
        calls.append("p2")
        return len(lines) * 2

    test_logger = logging.getLogger("test.run_puzzle.flags")

    # Part 2 only with --no-samples
    rc = runner.run_puzzle(
        year=2026,
        day=3,
        part1=p1,
        part2=p2,
        part1_samples=[("bad", 999)],  # skipped via --no-samples and -p 2
        locations=locs,
        logger=test_logger,
        argv=["-p", "2", "--no-samples", "--json"],
    )
    assert rc == 0
    assert calls == ["p2"]
    payload = json.loads(capsys.readouterr().out)
    assert [p["part"] for p in payload["parts"]] == [2]

    # Debug flag preserves DEBUG on real input
    calls.clear()
    real_levels.clear()
    rc = runner.run_puzzle(
        year=2026,
        day=3,
        part1=p1,
        part2=p2,
        locations=locs,
        logger=test_logger,
        argv=["-p", "1", "-d", "--no-samples"],
    )
    assert rc == 0
    assert calls == ["p1"]
    assert real_levels == [logging.DEBUG]

    # Mutually exclusive flags (-s and --no-samples)
    with pytest.raises(SystemExit) as exc:
        runner.run_puzzle(
            year=2026,
            day=3,
            part1=p1,
            locations=locs,
            argv=["-s", "--no-samples"],
        )
    assert exc.value.code == 2


def test_run_puzzle_sample_only_never_downloads_and_returns_status(tmp_path: Path) -> None:
    locs = _make_locations(tmp_path, 2026, 4)

    with patch("aoc_common.runner.write_puzzle_input_file") as mock_fetch:
        rc_ok = runner.run_puzzle(
            year=2026,
            day=4,
            part1=lambda lines: len(lines),
            part1_samples=[("a\nb", 2)],
            locations=locs,
            argv=["-s"],
        )
        rc_fail = runner.run_puzzle(
            year=2026,
            day=4,
            part1=lambda lines: len(lines),
            part1_samples=[("a\nb", 99)],
            locations=locs,
            argv=["--sample-only"],
        )

    mock_fetch.assert_not_called()
    assert rc_ok == 0
    assert rc_fail == 1


def test_run_puzzle_json_keeps_stdout_clean_and_handles_missing_cookie(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    locs = _make_locations(tmp_path, 2026, 5)
    locs.input_file.write_text("hello\n", encoding="utf-8")
    p_logger = logging.getLogger("test.run_puzzle.json")

    def noisy_part1(lines: list[str]) -> int:
        p_logger.debug("debug log noise")
        p_logger.info("info log noise")
        return len(lines)

    rc = runner.run_puzzle(
        year=2026,
        day=5,
        part1=noisy_part1,
        part1_samples=[("x", 1)],
        locations=locs,
        logger=p_logger,
        argv=["--json"],
    )
    captured = capsys.readouterr()
    assert rc == 0
    data: dict[str, Any] = json.loads(captured.out)
    assert data["year"] == 2026
    assert data["day"] == 5
    assert data["status"] == "ok"
    assert len(data["parts"]) == 2
    assert "info log noise" in captured.err

    # Missing AOC_SESSION_COOKIE error
    missing_locs = _make_locations(tmp_path, 2026, 6)
    with patch(
        "aoc_common.runner.write_puzzle_input_file",
        side_effect=ValueError("AOC_SESSION_COOKIE is required"),
    ):
        rc_err = runner.run_puzzle(
            year=2026,
            day=6,
            part1=lambda lines: len(lines),
            locations=missing_locs,
            logger=p_logger,
            argv=[],
        )
        err_cap = capsys.readouterr()
        assert rc_err == 1
        assert "AOC_SESSION_COOKIE" in err_cap.err
        assert ".env" in err_cap.err


# ---------------------------------------------------------------------------
# aoc CLI
# ---------------------------------------------------------------------------


def test_cli_new_year_dry_run_scaffold_and_force(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _create_template_repo(tmp_path)

    # --dry-run writes nothing
    rc_dry = cli.main(["--root", str(repo), "new-year", "2026", "--days", "3", "--dry-run"])
    assert rc_dry == 0
    assert not (repo / "src" / "AoC_2026").exists()
    capsys.readouterr()

    # Actual scaffold creates d01..d03
    rc_create = cli.main(["--root", str(repo), "new-year", "2026", "--days", "3"])
    assert rc_create == 0
    for day in range(1, 4):
        day_dir = repo / "src" / "AoC_2026" / f"d{day:02d}"
        script = day_dir / f"d{day:02d}.py"
        sample_file = day_dir / "input" / "sample_input_part_1.txt"
        assert script.is_file()
        assert sample_file.is_file()
        assert not (day_dir / "input" / "input.txt").exists()
        text = script.read_text(encoding="utf-8")
        assert "YEAR: int = 2026" in text
        assert f"DAY: int = {day}" in text
        assert f"adventofcode.com/2026/day/{day}" in text

    # Existing modified script is preserved without --force
    d01 = repo / "src" / "AoC_2026" / "d01" / "d01.py"
    d01.write_text("# custom solution\n", encoding="utf-8")
    rc_skip = cli.main(["--root", str(repo), "new-year", "2026", "--days", "3"])
    assert rc_skip == 0
    assert d01.read_text(encoding="utf-8") == "# custom solution\n"

    # --force overwrites
    rc_force = cli.main(["--root", str(repo), "new-year", "2026", "--days", "3", "--force"])
    assert rc_force == 0
    assert "DAY: int = 1" in d01.read_text(encoding="utf-8")


def test_cli_list_and_run_v3_and_legacy(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _create_template_repo(tmp_path)
    cli.main(["--root", str(repo), "new-year", "2026", "--days", "2"])

    # Populate sample/input files for d01 without touching d02
    d01_input = repo / "src" / "AoC_2026" / "d01" / "input"
    (d01_input / "sample_input_part_1.txt").write_text("sample-secret\n", encoding="utf-8")
    (d01_input / "input.txt").write_text("puzzle-secret\n", encoding="utf-8")
    capsys.readouterr()

    # list years
    assert cli.main(["--root", str(repo), "list"]) == 0
    out_years = capsys.readouterr().out
    assert "2026" in out_years

    # list year --json
    assert cli.main(["--root", str(repo), "list", "2026", "--json"]) == 0
    list_json = json.loads(capsys.readouterr().out)
    assert list_json["year"] == 2026
    d01_entry = next(item for item in list_json["days"] if item["day"] == 1)
    d02_entry = next(item for item in list_json["days"] if item["day"] == 2)
    assert d01_entry["has_input"] is True
    assert d01_entry["has_sample"] is True
    assert d02_entry["has_input"] is False
    assert d02_entry["has_sample"] is False
    assert "puzzle-secret" not in json.dumps(list_json)

    # run v3 script with both "1" and "d01"
    assert cli.main(["--root", str(repo), "run", "2026", "1", "--sample-only", "--json"]) == 0
    run_payload = json.loads(capsys.readouterr().out)
    assert run_payload["status"] == "ok"

    assert cli.main(["--root", str(repo), "run", "2026", "d01", "--sample-only", "--json"]) == 0
    capsys.readouterr()


def test_cli_run_legacy_script_subprocess(tmp_path: Path, capfd: pytest.CaptureFixture[str]) -> None:
    repo = _create_template_repo(tmp_path)
    legacy_dir = repo / "src" / "AoC_2025" / "d01"
    legacy_dir.mkdir(parents=True)
    legacy_script = legacy_dir / "d01.py"
    legacy_script.write_text(
        'def main():\n    print("legacy ok")\n\nif __name__ == "__main__":\n    main()\n',
        encoding="utf-8",
    )

    assert cli.main(["--root", str(repo), "run", "2025", "1"]) == 0
    captured = capfd.readouterr()
    assert "legacy ok" in captured.out

    # V3-only flag on legacy script exits cleanly with code 2
    assert cli.main(["--root", str(repo), "run", "2025", "1", "--sample-only"]) == 2
    capfd.readouterr()


def test_cli_list_detects_formats_and_historical_day_dirs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _create_template_repo(tmp_path)
    src = repo / "src"

    # 2016: standalone with descriptive folder names (zero-padded and single-digit) + non-day util/
    d01_2016 = src / "AoC_2016" / "d01_taxicab"
    d01_2016.mkdir(parents=True)
    (d01_2016 / "distance.py").write_text('print("2016 d01 ok")\n', encoding="utf-8")
    d02_2016 = src / "AoC_2016" / "d2_keypad"
    d02_2016.mkdir(parents=True)
    (d02_2016 / "variant_a.py").write_text("", encoding="utf-8")
    (src / "AoC_2016" / "util").mkdir(parents=True)

    # 2023: jupyter-only with input-only d01 folder and year notebook
    (src / "AoC_2023" / "d01" / "input").mkdir(parents=True)
    (src / "AoC_2023" / "Dazbo's_Advent_of_Code_2023.ipynb").write_text("{}", encoding="utf-8")

    # 2024: both standalone script and notebook
    (src / "AoC_2024" / "d01").mkdir(parents=True)
    (src / "AoC_2024" / "d01" / "d01.py").write_text("", encoding="utf-8")
    (src / "AoC_2024" / "Dazbo's_Advent_of_Code_2024.ipynb").write_text("{}", encoding="utf-8")

    # Summary JSON lists formats accurately and ignores util/
    assert cli.main(["--root", str(repo), "list", "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    by_year = {item["year"]: item for item in summary["years"]}
    assert by_year[2016]["days"] == 2
    assert by_year[2016]["format"] == "standalone"
    assert by_year[2023]["days"] == 1
    assert by_year[2023]["format"] == "jupyter"
    assert by_year[2023]["notebooks"] == ["Dazbo's_Advent_of_Code_2023.ipynb"]
    assert by_year[2024]["format"] == "both"

    # Rich table displays human-readable Format labels
    assert cli.main(["--root", str(repo), "list"]) == 0
    table_out = capsys.readouterr().out
    assert "Standalone (.py)" in table_out
    assert "Jupyter (.ipynb)" in table_out
    assert "Both (.py + .ipynb)" in table_out

    # Per-year JSON exposes format and notebooks
    assert cli.main(["--root", str(repo), "list", "2023", "--json"]) == 0
    y2023 = json.loads(capsys.readouterr().out)
    assert y2023["format"] == "jupyter"
    assert y2023["notebooks"] == ["Dazbo's_Advent_of_Code_2023.ipynb"]


def test_cli_run_resolves_descriptive_day_dirs(
    tmp_path: Path,
    capfd: pytest.CaptureFixture[str],
) -> None:
    repo = _create_template_repo(tmp_path)
    src = repo / "src"
    d01_2016 = src / "AoC_2016" / "d01_taxicab"
    d01_2016.mkdir(parents=True)
    (d01_2016 / "distance.py").write_text('print("2016 d01 ok")\n', encoding="utf-8")
    d02_2016 = src / "AoC_2016" / "d2_keypad"
    d02_2016.mkdir(parents=True)
    (d02_2016 / "variant_a.py").write_text("", encoding="utf-8")
    (d02_2016 / "variant_b.py").write_text("", encoding="utf-8")

    # Resolves single script in descriptive folder automatically
    assert cli.main(["--root", str(repo), "run", "2016", "1"]) == 0
    assert "2016 d01 ok" in capfd.readouterr().out

    # Ambiguous multiple scripts in descriptive folder returns exit code 2 without --script
    assert cli.main(["--root", str(repo), "run", "2016", "2"]) == 2
    capfd.readouterr()


def test_cli_list_reports_completed_and_total_days(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _create_template_repo(tmp_path)
    src = repo / "src"
    # Use unstarted Template v3 stubs (part1/part2 returning None) to test 0/12 scaffold state
    (src / "template_folder" / "template.py").write_text(
        '''"""Solving https://adventofcode.com/2026/day/1."""

YEAR: int = 2026
DAY: int = 1


def parse_input(raw: str) -> list[str]:
    return raw.splitlines()


def part1(data: list[str]) -> int | None:
    return None


def part2(data: list[str]) -> int | None:
    return None


def main(argv=None) -> int:
    return 0
''',
        encoding="utf-8",
    )

    # 1. Freshly scaffolded 2026 (12 days total, all Template v3 stubs -> 0/12)
    assert cli.main(["--root", str(repo), "new-year", "2026", "--days", "12"]) == 0
    capsys.readouterr()

    assert cli.main(["--root", str(repo), "list", "--json"]) == 0
    summary = json.loads(capsys.readouterr().out)
    y2026 = next(item for item in summary["years"] if item["year"] == 2026)
    assert y2026["completed_days"] == 0
    assert y2026["total_days"] == 12

    assert cli.main(["--root", str(repo), "list"]) == 0
    assert "0/12" in capsys.readouterr().out

    # Solve d01 part1 while keeping part2 as None -> 1/12
    d01_2026 = src / "AoC_2026" / "d01" / "d01.py"
    d01_2026.write_text(
        "def part1(data):\n    return len(data)\n\ndef part2(data):\n    return None\n",
        encoding="utf-8",
    )

    assert cli.main(["--root", str(repo), "list", "2026", "--json"]) == 0
    details_2026 = json.loads(capsys.readouterr().out)
    assert details_2026["completed_days"] == 1
    assert details_2026["total_days"] == 12
    by_day_2026 = {d["day"]: d for d in details_2026["days"]}
    assert by_day_2026[1]["completed"] is True
    assert by_day_2026[2]["completed"] is False

    # 2. Legacy 2018: uvwxyz stub is unstarted; solved part1 + uvwxyz part2 counts as solved (1/25)
    for day, code in [
        (1, 'def part1(data):\n    return 42\n\ndef part2(data):\n    return "uvwxyz"\n'),
        (2, 'def part1(data):\n    return "uvwxyz"\n\ndef part2(data):\n    return "uvwxyz"\n'),
    ]:
        day_dir = src / "AoC_2018" / f"d{day:02d}"
        day_dir.mkdir(parents=True)
        (day_dir / f"d{day:02d}.py").write_text(code, encoding="utf-8")

    assert cli.main(["--root", str(repo), "list", "2018", "--json"]) == 0
    details_2018 = json.loads(capsys.readouterr().out)
    assert details_2018["completed_days"] == 1
    assert details_2018["total_days"] == 25
    by_day_2018 = {d["day"]: d for d in details_2018["days"]}
    assert by_day_2018[1]["completed"] is True
    assert by_day_2018[2]["completed"] is False

    # 3. Jupyter 2017: Day 1 solved (`solve` fn), Day 2 unstarted (`solve_part1: pass`), template `Day n` ignored -> 1/25
    (src / "AoC_2017" / "d01").mkdir(parents=True)
    (src / "AoC_2017" / "d02").mkdir(parents=True)
    nb_payload = {
        "cells": [
            {"cell_type": "markdown", "source": ["## Day n: title"]},
            {"cell_type": "code", "source": ["def solve_part1(data):\n", "    pass"]},
            {"cell_type": "markdown", "source": ["## Day 1: Inverse Captcha"]},
            {"cell_type": "code", "source": ["%%time\n", "def solve(data):\n", "    return 1\n"]},
            {"cell_type": "markdown", "source": ["## Day 2: Corruption Checksum"]},
            {"cell_type": "code", "source": ["def solve_part1(data):\n", "    pass"]},
        ]
    }
    (src / "AoC_2017" / "Dazbo's_Advent_of_Code_2017.ipynb").write_text(json.dumps(nb_payload), encoding="utf-8")

    assert cli.main(["--root", str(repo), "list"]) == 0
    table_out = capsys.readouterr().out
    assert "1/12" in table_out
    assert "1/25" in table_out

    assert cli.main(["--root", str(repo), "list", "2017", "--json"]) == 0
    details_2017 = json.loads(capsys.readouterr().out)
    assert details_2017["completed_days"] == 1
    assert details_2017["total_days"] == 25


def test_cli_run_shorthands_and_default_year(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _create_template_repo(tmp_path)
    src = repo / "src"
    assert cli.main(["--root", str(repo), "new-year", "2025", "--days", "2"]) == 0
    capsys.readouterr()

    # 1. Default year falls back to latest existing AoC_YYYY (2025) when current calendar year isn't scaffolded
    monkeypatch.delenv("AOC_YEAR", raising=False)
    now_year = datetime.now().year
    # Ensure AoC_<now_year> does not already exist in this temp repo
    assert not (src / f"AoC_{now_year}").exists() or now_year == 2025

    for shorthand in ("1", "01", "d01"):
        assert cli.main(["--root", str(repo), "run", shorthand, "--sample-only", "--json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["year"] == 2025
        assert payload["day"] == 1

    # 2. Scaffold AoC_<now_year> (e.g. 2026) -> day-only shorthand picks current calendar year over older 2025
    target_year = now_year if now_year >= 2015 else 2026
    assert cli.main(["--root", str(repo), "new-year", str(target_year), "--days", "1"]) == 0
    capsys.readouterr()

    assert cli.main(["--root", str(repo), "run", "01", "--sample-only", "--json"]) == 0
    payload_now = json.loads(capsys.readouterr().out)
    assert payload_now["year"] == target_year
    assert payload_now["day"] == 1

    # 3. AOC_YEAR environment variable overrides disk auto-detection
    monkeypatch.setenv("AOC_YEAR", "2025")
    assert cli.main(["--root", str(repo), "run", "1", "--sample-only", "--json"]) == 0
    payload_env = json.loads(capsys.readouterr().out)
    assert payload_env["year"] == 2025
    assert payload_env["day"] == 1
    monkeypatch.delenv("AOC_YEAR", raising=False)

    # 4. Combined single-token shorthands: YYYYDD, YYYYD, YYYYdDD
    for combined in (f"{target_year}01", f"{target_year}1", f"{target_year}d01"):
        assert cli.main(["--root", str(repo), "run", combined, "--sample-only", "--json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["year"] == target_year
        assert payload["day"] == 1

    # 5. Invalid shorthands return exit code 2 cleanly
    for bad in ("2026", "202699", "not-a-day"):
        assert cli.main(["--root", str(repo), "run", bad]) == 2
        capsys.readouterr()


def test_cli_list_renders_osc8_hyperlinks(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from rich.console import Console as RichConsole

    repo = _create_template_repo(tmp_path)
    cli.main(["--root", str(repo), "new-year", "2025", "--days", "2"])
    d01_2020 = repo / "src" / "AoC_2020" / "d01_expense"
    d01_2020.mkdir(parents=True)
    (d01_2020 / "solve.py").write_text("print(1)\n", encoding="utf-8")
    capsys.readouterr()

    def _terminal_console(*args: Any, **kwargs: Any) -> RichConsole:
        return RichConsole(*args, force_terminal=True, color_system="truecolor", legacy_windows=False, **kwargs)

    with patch("aoc_common.cli.Console", _terminal_console):
        assert cli.main(["--root", str(repo), "list"]) == 0
        years_out = capsys.readouterr().out
        assert "\x1b]8;" in years_out
        assert ";https://adventofcode.com/2025\x1b\\" in years_out
        assert ";https://adventofcode.com/2020\x1b\\" in years_out

        assert cli.main(["--root", str(repo), "list", "2025"]) == 0
        y2025_out = capsys.readouterr().out
        assert "\x1b]8;" in y2025_out
        assert ";https://adventofcode.com/2025\x1b\\" in y2025_out
        assert ";https://adventofcode.com/2025/day/1\x1b\\" in y2025_out
        assert ";https://adventofcode.com/2025/day/2\x1b\\" in y2025_out
        assert "/day/01" not in y2025_out

        assert cli.main(["--root", str(repo), "list", "2020"]) == 0
        y2020_out = capsys.readouterr().out
        assert ";https://adventofcode.com/2020/day/1\x1b\\" in y2020_out
        assert "d01_expense" in y2020_out
