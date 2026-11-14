"""Top-level ``aoc`` repository CLI for running, inspecting, and scaffolding AoC puzzles.

Purpose & Value:
    Provides a single repository entry point (also exposed via ``Makefile`` targets) across
    all Advent of Code years, unifying Template v3 scripts, legacy 2015-2025 standalone
    solutions, and Jupyter notebooks while never reading encrypted ``input*.txt`` contents.

Subcommands & Mechanics:
    - ``aoc run <target> [day] [flags]``: resolves flexible targets—``<year> <day>``,
      compact shorthands (``202501``, ``20251``, ``2025d01``), or day-only forms (``1``,
      ``01``, ``d01`` using ``AOC_YEAR``, current year if present, or latest ``AoC_YYYY``)—
      plus descriptive folders (``d01_...``). Template v3 scripts run in-process via
      ``main(argv)`` with ``-p/-s/--no-samples/-d/--json``; legacy scripts run via subprocess.
    - ``aoc list [year] [--json]``: inspects AST structure and ``.ipynb`` cells (ignoring
      stub ``Template v3`` scaffolds returning ``None``) to report ``Standalone (.py)``,
      ``Jupyter (.ipynb)``, or ``Both`` along with ``Completed/Total`` counts (25 days for
      2015-2024, 12 days for 2025+) and input/sample file presence, and renders clickable
      OSC 8 terminal hyperlinks on ``Year`` and ``Day`` columns pointing to AoC pages.
    - ``aoc new-year <year> [--days 12] [--dry-run] [--force] [--json]``: scaffolds
      ``src/AoC_<year>/d01..d<days>`` from ``src/template_folder/template.py`` without
      creating empty ``input.txt`` placeholders.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markup import escape
from rich.table import Table

_YEAR_DIR_RE = re.compile(r"^AoC_(\d{4})$")
_DAY_DIR_RE = re.compile(r"^d(\d{1,2})(?:_.*)?$")
_SHORTHAND_YEAR_DAY_RE = re.compile(r"^(?P<year>\d{4})[-/]?d?(?P<day>\d{1,2})$", re.IGNORECASE)
_DAY_ONLY_RE = re.compile(r"^d?\d{1,2}$", re.IGNORECASE)
_YEAR_CONST_RE = re.compile(r"^YEAR: int = 2026$", re.MULTILINE)
_DAY_CONST_RE = re.compile(r"^DAY: int = 1$", re.MULTILINE)
_NOTEBOOK_DAY_HEADING_RE = re.compile(r"^##\s+Day\s+(\d+)\b", re.MULTILINE)
_NON_DAY_TOP_HEADING_RE = re.compile(r"^#{1,2}\s+(?!Day\s+\d+\b)", re.MULTILINE)
_PART_FN_NAMES = frozenset({"part1", "part2", "solve_part1", "solve_part2"})
_SCAFFOLD_FN_NAMES = _PART_FN_NAMES | frozenset({"parse_input", "main", "test_solution"})
_FORMAT_LABELS = {
    "standalone": "Standalone (.py)",
    "jupyter": "Jupyter (.ipynb)",
    "both": "Both (.py + .ipynb)",
    "none": "-",
}


def _resolve_root(root_arg: str | None) -> Path:
    """Resolve the repository root from ``--root`` or nearest parent with markers."""
    if root_arg is not None:
        return Path(root_arg).resolve()
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "src").is_dir():
            return candidate
    return cwd


def _parse_day(raw_day: str) -> int:
    """Parse ``1``, ``01``, ``d1``, or ``d01`` into an integer in ``1..25``."""
    cleaned = raw_day.strip().lower()
    if cleaned.startswith("d"):
        cleaned = cleaned[1:]
    try:
        day = int(cleaned)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid day specification: {raw_day!r}") from exc
    if not 1 <= day <= 25:
        raise argparse.ArgumentTypeError(f"Day must be between 1 and 25, got {day}")
    return day


def _parse_year(raw_year: str) -> int:
    """Parse an Advent of Code year (>= 2015)."""
    try:
        year = int(raw_year.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid year specification: {raw_year!r}") from exc
    if year < 2015:
        raise argparse.ArgumentTypeError(f"Year must be >= 2015, got {year}")
    return year


def _accepts_v3_argv(script_path: Path) -> bool:
    """Inspect top-level ``def main(...)`` via AST to detect Template v3 scripts."""
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return bool(node.args.posonlyargs or node.args.args or node.args.vararg)
    return False


def _has_nonempty_file(path: Path) -> bool:
    """Return True if ``path`` exists and is non-empty without reading its contents."""
    return path.is_file() and path.stat().st_size > 0


def _match_day_dir(name: str) -> int | None:
    """Extract day number ``1..25`` from ``dNN`` or descriptive ``dNN_<slug>`` folder names."""
    match = _DAY_DIR_RE.match(name)
    if not match:
        return None
    day = int(match.group(1))
    return day if 1 <= day <= 25 else None


def _total_days_for_year(year: int, max_day_present: int) -> int:
    """Return official event length (25 for <=2024, 12 for 2025+) or higher if present."""
    official = 25 if year <= 2024 else 12
    return max(official, max_day_present)


def _strip_leading_docstring(stmts: list[ast.stmt]) -> list[ast.stmt]:
    """Strip an optional leading string-literal docstring statement."""
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(stmts[0].value, ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        return stmts[1:]
    return stmts


def _is_stub_part_fn(node: ast.FunctionDef) -> bool:
    """Return True if a ``part*``/``solve_part*`` function only contains placeholder boilerplate."""
    body = _strip_leading_docstring(list(node.body))
    if not body:
        return True
    if len(body) > 1:
        return False
    stmt = body[0]
    if isinstance(stmt, ast.Pass):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
        return True
    if isinstance(stmt, ast.Return):
        if stmt.value is None:
            return True
        if isinstance(stmt.value, ast.Constant) and stmt.value.value in (None, "uvwxyz"):
            return True
    return False


def _is_py_script_solved(script_path: Path) -> bool:
    """Return True when ``script_path`` contains implemented puzzle logic rather than only stubs."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return False

    body = _strip_leading_docstring(list(tree.body))
    if not body:
        return False

    part_defs = [node for node in body if isinstance(node, ast.FunctionDef) and node.name in _PART_FN_NAMES]
    if part_defs:
        if any(not _is_stub_part_fn(fn) for fn in part_defs):
            return True
        if any(isinstance(node, ast.ClassDef) for node in body):
            return True
        return any(isinstance(node, ast.FunctionDef) and node.name not in _SCAFFOLD_FN_NAMES for node in body)
    return True


def _is_day_py_solved(day_dir: Path) -> bool:
    """Return True if any non-test Python script in ``day_dir`` has implemented logic."""
    return any(
        _is_py_script_solved(item)
        for item in day_dir.iterdir()
        if item.is_file() and item.suffix == ".py" and item.name != "__init__.py" and not item.name.startswith("test_")
    )


def _cell_source(cell: dict[str, Any]) -> str:
    """Extract raw text from a Jupyter notebook cell dict."""
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(str(part) for part in src)
    return str(src)


def _update_day_heading_cursor(text: str, current_day: int | None, day_code_cells: dict[int, list[str]]) -> int | None:
    """Track which day section (``1..25``) a notebook markdown cell belongs to."""
    match = _NOTEBOOK_DAY_HEADING_RE.search(text)
    if match:
        day_num = int(match.group(1))
        if 1 <= day_num <= 25:
            day_code_cells.setdefault(day_num, [])
            return day_num
        return None
    if _NON_DAY_TOP_HEADING_RE.search(text):
        return None
    return current_day


def _collect_notebook_day_cells(cells: list[Any]) -> dict[int, list[str]]:
    """Group non-empty Python code cells by notebook ``## Day N`` section."""
    current_day: int | None = None
    day_code_cells: dict[int, list[str]] = {}
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_type = cell.get("cell_type")
        text = _cell_source(cell)
        if cell_type == "markdown":
            current_day = _update_day_heading_cursor(text, current_day, day_code_cells)
        elif cell_type == "code" and current_day is not None:
            cleaned = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("%", "!")))
            if cleaned.strip():
                day_code_cells[current_day].append(cleaned)
    return day_code_cells


def _scan_code_block_ast(block: str, part_defs: list[ast.FunctionDef]) -> bool:
    """Collect part definitions from one code block and report any custom classes/functions."""
    try:
        tree = ast.parse(block)
    except SyntaxError:
        return False

    has_custom_def = False
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            has_custom_def = True
        elif isinstance(node, ast.FunctionDef):
            if node.name in _PART_FN_NAMES:
                part_defs.append(node)
            elif node.name != "parse_input":
                has_custom_def = True
    return has_custom_def


def _is_notebook_day_solved(code_blocks: list[str]) -> bool:
    """Return True when a notebook day section contains implemented solution code."""
    part_defs: list[ast.FunctionDef] = []
    has_custom_def = any(_scan_code_block_ast(block, part_defs) for block in code_blocks)
    if part_defs:
        return any(not _is_stub_part_fn(fn) for fn in part_defs) or has_custom_def
    return has_custom_def or len(code_blocks) >= 3


def _solved_days_in_notebook(nb_path: Path) -> set[int]:
    """Detect solved day numbers (``1..25``) inside a year Jupyter notebook via cell AST."""
    try:
        payload = json.loads(nb_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return set()

    cells = payload.get("cells") if isinstance(payload, dict) else None
    if not isinstance(cells, list):
        return set()

    day_code_cells = _collect_notebook_day_cells(cells)
    return {day_num for day_num, blocks in day_code_cells.items() if _is_notebook_day_solved(blocks)}


def _format_progress(completed: int, total: int) -> str:
    """Format ``completed/total`` days with Rich colour emphasis."""
    label = f"{completed}/{total}"
    if completed >= total and total > 0:
        return f"[green]{label}[/green]"
    if completed > 0:
        return f"[yellow]{label}[/yellow]"
    return f"[dim]{label}[/dim]"


def _scan_day_dir_entries(day_dir: Path) -> tuple[bool, bool, set[int]]:
    """Inspect files inside one day folder for ``.py`` scripts and ``.ipynb`` notebooks."""
    has_py = False
    has_ipynb = False
    solved: set[int] = set()
    for item in day_dir.iterdir():
        if not item.is_file():
            continue
        if item.suffix == ".py" and item.name != "__init__.py":
            has_py = True
        elif item.suffix == ".ipynb":
            has_ipynb = True
            solved.update(_solved_days_in_notebook(item))
    return has_py, has_ipynb, solved


def _classify_year_format(*, has_py: bool, has_ipynb: bool) -> str:
    """Classify a year's solution format from discovered script and notebook presence."""
    if has_py and has_ipynb:
        return "both"
    if has_py:
        return "standalone"
    if has_ipynb:
        return "jupyter"
    return "none"


def _inspect_year(year: int, year_dir: Path) -> tuple[list[tuple[int, Path]], list[str], str, set[int], int]:
    """Collect day directories, notebooks, format, solved day numbers, and official total."""
    day_dirs: list[tuple[int, Path]] = []
    year_notebooks: list[str] = []
    solved_days: set[int] = set()
    has_py = False
    has_ipynb = False

    for entry in sorted(year_dir.iterdir()):
        if entry.is_file():
            if entry.suffix == ".ipynb":
                has_ipynb = True
                year_notebooks.append(entry.name)
                solved_days.update(_solved_days_in_notebook(entry))
            elif entry.suffix == ".py" and entry.name != "__init__.py":
                has_py = True
            continue
        if not entry.is_dir():
            continue
        day_num = _match_day_dir(entry.name)
        if day_num is None:
            continue
        day_dirs.append((day_num, entry))
        if _is_day_py_solved(entry):
            solved_days.add(day_num)
        day_has_py, day_has_ipynb, nb_solved = _scan_day_dir_entries(entry)
        has_py = has_py or day_has_py
        has_ipynb = has_ipynb or day_has_ipynb
        solved_days.update(nb_solved)

    day_dirs.sort(key=lambda item: (item[0], item[1].name))
    year_notebooks.sort()
    max_day = max((day_num for day_num, _ in day_dirs), default=0)
    total_days = _total_days_for_year(year, max(max_day, max(solved_days, default=0)))
    fmt = _classify_year_format(has_py=has_py, has_ipynb=has_ipynb)
    return day_dirs, year_notebooks, fmt, solved_days, total_days


def _aoc_year_url(year: int) -> str:
    """Return the Advent of Code event URL for ``year``."""
    return f"https://adventofcode.com/{year}"


def _aoc_day_url(year: int, day: int) -> str:
    """Return the Advent of Code puzzle URL for ``year`` and unpadded ``day``."""
    return f"https://adventofcode.com/{year}/day/{day}"


def _collect_year_summary_rows(root: Path, src_dir: Path) -> list[dict[str, Any]]:
    """Collect sorted summary dictionaries for each ``AoC_YYYY`` directory."""
    years: list[dict[str, Any]] = []
    for entry in sorted(src_dir.iterdir()):
        if not entry.is_dir():
            continue
        match = _YEAR_DIR_RE.match(entry.name)
        if not match:
            continue
        year_num = int(match.group(1))
        day_dirs, year_notebooks, fmt, solved_days, total_days = _inspect_year(year_num, entry)
        years.append(
            {
                "year": year_num,
                "days": len(day_dirs),
                "completed_days": len(solved_days),
                "total_days": total_days,
                "format": fmt,
                "notebooks": year_notebooks,
                "path": str(entry.relative_to(root)),
            }
        )
    years.sort(key=lambda item: item["year"])
    return years


def _list_all_years(root: Path, src_dir: Path, *, as_json: bool) -> int:
    """Render an overview table or JSON summary across all AoC years."""
    years = _collect_year_summary_rows(root, src_dir)
    if as_json:
        print(json.dumps({"root": str(root), "years": years}, indent=2))
        return 0

    table = Table(title="Advent of Code Years")
    table.add_column("Year", style="cyan")
    table.add_column("Completed", justify="right")
    table.add_column("Format")
    table.add_column("Path")
    for item in years:
        year_link = f"[link={_aoc_year_url(item['year'])}]{item['year']}[/link]"
        table.add_row(
            year_link,
            _format_progress(item["completed_days"], item["total_days"]),
            _FORMAT_LABELS[item["format"]],
            item["path"],
        )
    Console().print(table)
    return 0


def _list_single_year(year: int, year_dir: Path, *, as_json: bool) -> int:
    """Render per-day solution status and readiness for a single AoC year."""
    if not year_dir.is_dir():
        msg = f"Year directory not found: {year_dir}"
        if as_json:
            print(json.dumps({"year": year, "error": msg, "days": []}, indent=2))
        else:
            Console(stderr=True).print(f"[red]{msg}[/red]")
        return 1

    day_dirs, year_notebooks, fmt, solved_days, total_days = _inspect_year(year, year_dir)
    days_summary: list[dict[str, Any]] = []
    for day_num, entry in day_dirs:
        scripts = sorted(p.name for p in entry.iterdir() if p.is_file() and p.suffix in {".py", ".ipynb"})
        input_dir = entry / "input"
        days_summary.append(
            {
                "day": day_num,
                "folder": entry.name,
                "completed": day_num in solved_days,
                "scripts": scripts,
                "has_input": _has_nonempty_file(input_dir / "input.txt"),
                "has_sample": _has_nonempty_file(input_dir / "sample_input_part_1.txt"),
            }
        )

    if as_json:
        print(
            json.dumps(
                {
                    "year": year,
                    "completed_days": len(solved_days),
                    "total_days": total_days,
                    "format": fmt,
                    "notebooks": year_notebooks,
                    "days": days_summary,
                },
                indent=2,
            )
        )
        return 0

    caption = f"Notebooks: {', '.join(year_notebooks)}" if year_notebooks else None
    year_link = f"[link={_aoc_year_url(year)}]Advent of Code {year}[/link]"
    table = Table(
        title=f"{year_link} — {_FORMAT_LABELS[fmt]} ({len(solved_days)}/{total_days} completed)",
        caption=caption,
    )
    table.add_column("Day", style="cyan")
    table.add_column("Solved", justify="center")
    table.add_column("Scripts")
    table.add_column("Input", justify="center")
    table.add_column("Sample 1", justify="center")
    for item in days_summary:
        day_link = f"[link={_aoc_day_url(year, item['day'])}]{escape(item['folder'])}[/link]"
        table.add_row(
            day_link,
            "[green]yes[/green]" if item["completed"] else "[dim]no[/dim]",
            ", ".join(item["scripts"]) or "-",
            "[green]yes[/green]" if item["has_input"] else "[dim]no[/dim]",
            "[green]yes[/green]" if item["has_sample"] else "[dim]no[/dim]",
        )
    Console().print(table)
    return 0


def _cmd_list(root: Path, year: int | None, *, as_json: bool) -> int:
    """List AoC years or days under ``root / 'src'``."""
    src_dir = root / "src"
    if not src_dir.is_dir():
        Console(stderr=True).print(f"[red]Source directory not found: {src_dir}[/red]")
        return 1

    if year is None:
        return _list_all_years(root, src_dir, as_json=as_json)
    return _list_single_year(year, src_dir / f"AoC_{year}", as_json=as_json)


def _cmd_new_year(
    root: Path,
    year: int,
    *,
    days: int,
    dry_run: bool,
    force: bool,
    as_json: bool,
) -> int:
    """Scaffold ``src/AoC_<year>/d01..d<days>`` from ``src/template_folder/template.py``."""
    if not 1 <= days <= 25:
        Console(stderr=True).print(f"[red]--days must be between 1 and 25, got {days}[/red]")
        return 2

    template_path = root / "src" / "template_folder" / "template.py"
    if not template_path.is_file():
        msg = f"Template file not found: {template_path}"
        if as_json:
            print(json.dumps({"year": year, "status": "error", "error": msg}, indent=2))
        else:
            Console(stderr=True).print(f"[red]{msg}[/red]")
        return 1

    template_text = template_path.read_text(encoding="utf-8")
    year_dir = root / "src" / f"AoC_{year}"
    actions: list[dict[str, str]] = []

    for day in range(1, days + 1):
        day_dir = year_dir / f"d{day:02d}"
        input_dir = day_dir / "input"
        target_script = day_dir / f"d{day:02d}.py"
        sample_file = input_dir / "sample_input_part_1.txt"

        existed = target_script.exists()
        if existed and not force:
            actions.append({"day": f"d{day:02d}", "script": str(target_script), "action": "skipped"})
            continue

        action_label = ("would_overwrite" if existed else "would_create") if dry_run else ("overwrote" if existed else "created")
        actions.append({"day": f"d{day:02d}", "script": str(target_script), "action": action_label})
        if dry_run:
            continue

        rendered = _YEAR_CONST_RE.sub(f"YEAR: int = {year}", template_text)
        rendered = _DAY_CONST_RE.sub(f"DAY: int = {day}", rendered)
        rendered = rendered.replace("adventofcode.com/2026/day/1", f"adventofcode.com/{year}/day/{day}")

        input_dir.mkdir(parents=True, exist_ok=True)
        target_script.write_text(rendered, encoding="utf-8")
        if not sample_file.exists():
            sample_file.touch()

    if as_json:
        print(json.dumps({"year": year, "days": days, "dry_run": dry_run, "actions": actions}, indent=2))
        return 0

    console = Console()
    mode_tag = " [yellow](dry run)[/yellow]" if dry_run else ""
    console.print(f"[bold]Scaffold AoC {year} ({days} days){mode_tag}[/bold]")
    for item in actions:
        console.print(f"  {item['day']}: {item['action']} -> {item['script']}")
    return 0


def _find_day_dir(year_dir: Path, day: int) -> Path:
    """Return ``dNN`` or the first matching ``dNN_<slug>`` directory inside ``year_dir``."""
    day_dir = year_dir / f"d{day:02d}"
    if not day_dir.is_dir() and year_dir.is_dir():
        matched = sorted(entry for entry in year_dir.iterdir() if entry.is_dir() and _match_day_dir(entry.name) == day)
        if matched:
            return matched[0]
    return day_dir


def _discover_day_py_script(year: int, day: int, year_dir: Path, day_dir: Path) -> tuple[Path | None, str | None, int]:
    """Locate a standalone Python solution script for ``day`` or report notebook-only status."""
    default_script = day_dir / f"d{day:02d}.py"
    if default_script.is_file():
        return default_script, None, 0

    if day_dir.is_dir():
        py_scripts = sorted(
            p
            for p in day_dir.iterdir()
            if p.is_file() and p.suffix == ".py" and p.name != "__init__.py" and not p.name.startswith("test_")
        )
        if len(py_scripts) == 1:
            return py_scripts[0], None, 0
        if len(py_scripts) > 1:
            choices = ", ".join(p.name for p in py_scripts)
            return None, f"Multiple scripts found in {day_dir.name} ({choices}); specify one with --script <filename>.", 2

    if year_dir.is_dir():
        notebooks = sorted(p.name for p in year_dir.iterdir() if p.is_file() and p.suffix == ".ipynb")
        if notebooks:
            return (
                None,
                f"AoC {year} Day {day:02d} is solved in Jupyter notebook ({', '.join(notebooks)}), not a standalone .py script.",
                1,
            )

    return None, f"Puzzle script not found: {default_script}", 1


def _resolve_day_script(root: Path, year: int, day: int, explicit_script: str | None) -> tuple[Path | None, str | None, int]:
    """Resolve the target Python script inside ``dNN`` or ``dNN_<slug>``."""
    year_dir = root / "src" / f"AoC_{year}"
    day_dir = _find_day_dir(year_dir, day)

    if explicit_script is not None:
        candidate = day_dir / explicit_script
        if candidate.is_file():
            return candidate, None, 0
        return None, f"Puzzle script not found: {candidate}", 1

    return _discover_day_py_script(year, day, year_dir, day_dir)


def _resolve_default_year(root: Path) -> int:
    """Resolve the default AoC year from ``AOC_YEAR``, current year if present, or latest on disk."""
    env_year = os.environ.get("AOC_YEAR", "").strip()
    if env_year:
        return _parse_year(env_year)

    now_year = datetime.now().year
    src_dir = root / "src"
    if (src_dir / f"AoC_{now_year}").is_dir():
        return now_year

    if src_dir.is_dir():
        years = [
            int(match.group(1)) for entry in src_dir.iterdir() if entry.is_dir() and (match := _YEAR_DIR_RE.match(entry.name))
        ]
        if years:
            return max(years)

    return now_year


def _resolve_run_target(root: Path, target: str, day_arg: str | None) -> tuple[int, int]:
    """Parse ``<year> <day>`` or shorthands ``YYYYDD`` (``202501``), ``YYYYD`` (``20251``), ``1``, ``01``."""
    cleaned = target.strip()
    if day_arg is not None:
        return _parse_year(cleaned), _parse_day(day_arg)

    match = _SHORTHAND_YEAR_DAY_RE.match(cleaned)
    if match:
        return _parse_year(match.group("year")), _parse_day(match.group("day"))

    if _DAY_ONLY_RE.match(cleaned):
        return _resolve_default_year(root), _parse_day(cleaned)

    raise argparse.ArgumentTypeError(
        f"Invalid run target {target!r}. Expected e.g. '1', '01', '20251', '202501', or '<year> <day>'."
    )


def _emit_cli_error(payload: dict[str, Any], message: str, *, as_json: bool, code: int) -> int:
    """Emit a CLI error either as JSON on stdout or red text on stderr."""
    if as_json:
        print(json.dumps({**payload, "status": "error", "error": message}, indent=2))
    else:
        Console(stderr=True).print(f"[red]{message}[/red]")
    return code


def _build_forwarded_argv(args: argparse.Namespace) -> list[str]:
    """Translate ``aoc run`` options into Template v3 per-script CLI flags."""
    forwarded: list[str] = []
    if args.part is not None:
        forwarded.extend(["-p", args.part])
    for attr, flag in (
        ("sample_only", "-s"),
        ("no_samples", "--no-samples"),
        ("debug", "-d"),
        ("json", "--json"),
    ):
        if getattr(args, attr, False):
            forwarded.append(flag)
    return forwarded


def _run_v3_in_process(script_path: Path, mod_name: str, forwarded: list[str]) -> int:
    """Load and execute a Template v3 solution module's ``main(argv)`` entry point."""
    spec = importlib.util.spec_from_file_location(mod_name, script_path)
    if spec is None or spec.loader is None:
        Console(stderr=True).print(f"[red]Unable to load Python module: {script_path}[/red]")
        return 1
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    try:
        spec.loader.exec_module(module)
        result = module.main(forwarded)
        return int(result) if isinstance(result, int) else 0
    finally:
        sys.modules.pop(mod_name, None)


def _cmd_run(root: Path, args: argparse.Namespace) -> int:
    """Run a day's puzzle script (Template v3 in-process or legacy subprocess)."""
    try:
        year, day = _resolve_run_target(root, args.target, args.day)
    except argparse.ArgumentTypeError as exc:
        return _emit_cli_error({"target": args.target}, str(exc), as_json=args.json, code=2)

    day_folder = f"d{day:02d}"
    script_path, err_msg, err_code = _resolve_day_script(root, year, day, args.script)
    if script_path is None:
        return _emit_cli_error(
            {"year": year, "day": day},
            err_msg or f"Puzzle script not found for {year} {day_folder}.",
            as_json=args.json,
            code=err_code,
        )

    forwarded = _build_forwarded_argv(args)
    if _accepts_v3_argv(script_path):
        mod_name = f"aoc_cli_target_{year}_{day_folder}_{script_path.stem}"
        return _run_v3_in_process(script_path, mod_name, forwarded)

    if forwarded:
        Console(stderr=True).print(
            f"[red]Legacy script {script_path.name} does not accept Template v3 flags ({' '.join(forwarded)}).[/red]"
        )
        return 2

    completed = subprocess.run([sys.executable, str(script_path)], cwd=script_path.parent, check=False)
    return completed.returncode


def _build_parser() -> argparse.ArgumentParser:
    """Create the top-level ``aoc`` CLI parser."""
    parser = argparse.ArgumentParser(
        prog="aoc",
        description="CLI utilities for Dazbo's Advent of Code repository.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Optional repository root path (auto-detected from current directory by default).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Run a puzzle script (e.g. `aoc run 2025 1`, `aoc run 202501`, `aoc run 20251`, `aoc run 01`).",
    )
    run_parser.add_argument(
        "target",
        help="Year (with day arg) or shorthand: YYYYDD (202501), YYYYD (20251), or day (1 / 01 / d01).",
    )
    run_parser.add_argument(
        "day",
        nargs="?",
        default=None,
        help="Puzzle day when year is supplied separately (e.g. 1 or d01).",
    )
    run_parser.add_argument("-p", "--part", choices=("1", "2", "all"), default=None, help="Run only one part or all.")
    sample_group = run_parser.add_mutually_exclusive_group()
    sample_group.add_argument("-s", "--sample-only", action="store_true", help="Run sample checks only.")
    sample_group.add_argument("--no-samples", action="store_true", help="Skip sample checks.")
    run_parser.add_argument("-d", "--debug", action="store_true", help="Keep DEBUG logging active for real input.")
    run_parser.add_argument("--json", action="store_true", help="Emit JSON output on stdout and logs on stderr.")
    run_parser.add_argument("--script", default=None, help="Override target script filename inside dNN/ (e.g. d01_alt.py).")

    list_parser = subparsers.add_parser("list", help="List available AoC years or days for a given year.")
    list_parser.add_argument("year", nargs="?", type=_parse_year, default=None, help="Optional year to inspect.")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON output on stdout.")

    new_year_parser = subparsers.add_parser("new-year", help="Scaffold src/AoC_<year>/d01..d<days> from Template v3.")
    new_year_parser.add_argument("year", type=_parse_year, help="Year to scaffold (e.g. 2026).")
    new_year_parser.add_argument("--days", type=int, default=12, help="Number of days to create (1..25, default: 12).")
    new_year_parser.add_argument("--dry-run", action="store_true", help="Preview scaffold actions without writing files.")
    new_year_parser.add_argument("--force", action="store_true", help="Overwrite existing dNN.py scripts.")
    new_year_parser.add_argument("--json", action="store_true", help="Emit JSON summary on stdout.")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``aoc`` CLI returning a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    root = _resolve_root(args.root)

    if args.command == "list":
        return _cmd_list(root, args.year, as_json=args.json)
    if args.command == "new-year":
        return _cmd_new_year(root, args.year, days=args.days, dry_run=args.dry_run, force=args.force, as_json=args.json)
    if args.command == "run":
        return _cmd_run(root, args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
