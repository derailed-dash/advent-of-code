---
title: Reusable Code & aoc_common
description: Architecture and API guide for the reusable aoc_common Python package — logging, notebook-safe AoC paths, PuzzlePage retrieval, Point/Point3D/Grid geometry, search/interval utilities, and the Template v3 puzzle runner.
---
## Why Build a Reusable Toolkit?

Across years of Advent of Code puzzles, the same supporting chores appear on almost every day:

- Parsing environment configuration and fetching puzzle inputs without committing private data or hammering `adventofcode.com`
- Resolving file paths reliably whether a solution runs as a `.py` script, via `uv run aoc run`, or inside a Jupyter notebook
- Configuring readable terminal logs and high-resolution execution timers
- Modelling 2D/3D coordinates, directional vectors, rectangular grids, flood fills, and binary search bounds

Early in this repository, helper classes were copied from day to day or imported from an external shared library (`type_defs`, later `dazbo_commons`). That created tight coupling and made older solutions drift whenever utility signatures changed.

Today, all shared AoC infrastructure lives directly inside this repository in the [`src/aoc_common/`](https://github.com/derailed-dash/Advent-of-Code/tree/main/src/aoc_common) package, installed editably into the `.venv` managed by [`uv`](https://docs.astral.sh/uv/) and tested offline with `pytest`. Legacy extras (`dazbo-commons` and `colorama`) remain opt-in only so untouched 2015–2024 scripts keep working without rewriting history.

---

## Package Evolution (`type_defs` -> `dc` -> `aoc_common`)

| Era | Approach | Trade-offs |
| :--- | :--- | :--- |
| **2015–2021** | Copy-pasted boilerplate (`Template v1`) & local helper snippets | Quick to start, hard to fix bugs across days |
| **2022–2024** | External `dazbo_commons` (`dc`) package + `Template v2` | Reduced duplication, but coupled AoC to unrelated utilities, `colorama`, and eager `.env` side effects |
| **2025+** | Local [`aoc_common`](https://github.com/derailed-dash/Advent-of-Code/tree/main/src/aoc_common) (`ac`) + `runner` + CLI + `Template v3` | Zero external `dazbo_commons` dependency, Python >= 3.13, `Rich` logging, offline test suite, notebook-safe paths, and automatic sample verification |

---

## Package Layout

[`src/aoc_common/`](https://github.com/derailed-dash/Advent-of-Code/tree/main/src/aoc_common) is split into three cohesive modules, with key symbols re-exported at package level (`import aoc_common as ac`):

| Module | Responsibility |
| :--- | :--- |
| `aoc_commons.py` | Logging (`RichHandler`), path resolution (`Locations`), input/HTML retrieval (`write_puzzle_input_file`, `fetch_puzzle_page`), `git-crypt` detection, geometry (`Point`, `Point3D`, `Vectors`, `VectorDicts`, `Grid`), search, interval merging, factors, base conversion, timing |
| `runner.py` | Sample verification (`check_samples`), timing summaries (`PartRunSummary`, `PuzzleRunSummary`), formatting (`format_duration`), and standard CLI execution (`run_puzzle`) |
| `cli.py` | Entrypoint for `uv run aoc` (`run`, `list`, `fetch`, `new-year`, `clean-inputs`) |

---

## Logging & Output Hygiene

Older template helpers built custom ANSI formatters (`ColouredFormatter`) and `colorama` wrappers. Modern `aoc_common` replaces those with [`Rich`](https://rich.readthedocs.io/) via `RichHandler`:

```python
import logging
import aoc_common as ac

ac.setup_logging(logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Parsed %d instructions", 42)
```

Key design details:

- `setup_logging(level: int | str = logging.INFO, *, stderr: bool = False) -> None` configures the root logger cleanly. Passing `stderr=True` routes logs to standard error so `uv run aoc run ... --json` keeps standard output purely machine-readable.
- `setup_file_logging(a_logger: logging.Logger, folder: str | Path = "") -> None` adds a file handler when you want persistent log output alongside console logs.
- See [Logging in Python](/python/logging) and [Terminal Colours & Rich](/python/colours) for deeper coverage.

---

## Paths & Notebook-Safe Locations

Because `__file__` is undefined inside Jupyter notebooks and scripts may be invoked from the repository root or a day folder, `aoc_common` encapsulates filesystem paths in a memory-efficient dataclass (`slots=True`):

- `Locations(script_name: str, script_dir: Path, input_dir: Path, output_dir: Path, input_file: Path)`

Two helpers build `Locations` depending on context:

```python
import aoc_common as ac

# Inside a standard Python script (Template v3 uses runner automatically):
locs = ac.get_locations(__file__)

# Inside a Jupyter notebook cell (safe when __file__ does not exist):
locs = ac.get_aoc_locations(2025, 1)
```

- `get_locations(calling_file_path: str | Path, sub_folder: str | Path = "") -> Locations` resolves paths relative to a script file (with an optional subfolder such as `"input"`).
- `get_aoc_locations(year: int, day: int, caller_file: str | Path | None = None, *, base_dir: str | Path | None = None) -> Locations` locates `src/AoC_<year>/d<dd>/` cleanly from notebooks, test runners, or explicit `base_dir` overrides.

Notice that `Locations` stores `input_file` rather than legacy `sample_input_file` attributes — sample cases in Template v3 are declared explicitly per part and verified by `check_samples` or `run_puzzle`.

---

## Secrets, Puzzle Retrieval & `git-crypt` Safety

Importing `aoc_common` performs **no** network I/O and eagerly reads no `.env` files. Instead, retrieval utilities load configuration only when invoked:

- `get_aoc_session_cookie(*, required: bool = True) -> str | None`: reads `AOC_SESSION_COOKIE` from environment variables or local `.env`.
- `write_puzzle_input_file(year: int, day: int, locations: Locations) -> str`: downloads your personal puzzle input once (caching on disk at `locations.input_file`) with the required polite AoC `User-Agent` header.
- `fetch_puzzle_page(year: int, day: int, *, session_cookie: str | None = None) -> PuzzlePage` and `parse_puzzle_html(html: str, *, year: int, day: int) -> PuzzlePage`: extract puzzle statements and ranked sample-input candidates cleanly in memory without writing temporary `desc.html` clutter.
- `is_git_crypt_locked(path: str | Path) -> bool`: detects `git-crypt` binary headers (`\x00GITCRYPT\x00`) on `input*.txt` files so tools fail with an actionable unlock hint rather than crashing on invalid UTF-8 bytes.

---

## 2D/3D Coordinates & Vectors

`Point` and `Point3D` are immutable, sortable, hashable dataclasses (`frozen=True, order=True, slots=True`), making them safe keys in `dict`s and members of `set`s or `heapq` heaps:

```python
from aoc_common import Point, Point3D, Vectors, VectorDicts

origin = Point(0, 0)
step = Vectors.E.to_point(y_down=True)  # Point(1, 0)
target = origin + step * 5              # Point(5, 0)

assert origin.manhattan_distance_from(target) == 5
assert len(list(origin.orthogonal_neighbours())) == 4
assert len(list(origin.neighbours())) == 8  # includes diagonals

p3 = Point3D(1, 2, 3)
assert p3.chebyshev_distance_from(Point3D(4, 3, 5)) == 3
```

Core vector and rendering helpers:

- `Point` / `Point3D`: support `+`, `-`, scalar/component-wise `*`, `yield_neighbours`, `neighbours`, `orthogonal_neighbours`, `get_specific_neighbours`, `manhattan_distance`, `manhattan_distance_from`, `chebyshev_distance_from`, and `euclidean_distance_from`.
- `Vectors(Enum)`: `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW` with `.y_inverted` and `.to_point(*, y_down=False)`.
- `VectorDicts`: prebuilt arrow/letter mappings (`ARROWS`, `DIRS`, `ARROWS_Y_DOWN`, `DIRS_Y_DOWN`, `NINE_BOX`).
- `bounding_box(points: Iterable[Point]) -> tuple[Point, Point]` and `render_points(points: Mapping[Point, Any] | Iterable[Point], *, empty_char: str = ".", fill_char: str = "#", y_down: bool = True) -> str` for visualising sparse coordinate sets.

---

## Generic 2D `Grid[T]`

`Grid[T]` wraps rectangular 2D inputs using `y`-down screen coordinates (`Point(x, y)` where `x` is column and `y` is row) and supports Python's container protocol alongside transformation and search methods:

```python
from aoc_common import Grid, Point

raw = """\
#...#
..S..
#...#
"""
grid = Grid.from_text(raw)

start = grid.find_one("S")  # raises ValueError unless exactly one match exists
assert start in grid        # bounds check without catching exceptions
assert grid[start] == "S"   # indexing raises IndexError if negative or out of bounds

open_region = grid.flood_fill(start, predicate=lambda ch: ch != "#")
```

Key `Grid[T]` capabilities:

- **Construction & copying**: `Grid(grid_array)`, `Grid.from_text(raw_text)`, `copy()`
- **Element access & bounds**: `grid[pt]`, `grid[pt] = val`, `pt in grid`, `valid_location(pt)`, `value_at_point(pt)`, `set_value_at_point(pt, val)`, `width`, `height`, `cols`
- **Iteration & lookup**: `all_points()`, `items()`, `find_points_with_value(val)`, `find_first(val)` (returns `Point | None`), `find_one(val)` (asserts unique match)
- **Topology & traversal**: `neighbours_of(pt, *, include_diagonals=True, include_self=False)`, `flood_fill(start, *, include_diagonals=False, predicate=None)`
- **String formatting & symmetry**: `rows_as_str()`, `cols_as_str()`, `transpose()`, `flip_vertical()`, `flip_horizontal()`, `rotate_90(ccw=False)`

---

## Algorithmic & Timing Helpers

`aoc_common` also bundles concise, reusable primitives explored in detail on [Useful Algorithms](/python/useful_algorithms) and [Timing & Benchmarking](/python/timing):

- **Binary search**: `binary_search`, `lower_bound`, `upper_bound`
- **Intervals & number theory**: `merge_intervals`, `get_factors`, `to_base_n`
- **Diagnostics & formatting**: `timer` context manager, `top_and_tail`, `validate`, `cls`

---

## Puzzle Runner & Template v3

Every modern solution uses the shared `runner` module (`SampleInput`, `PartRunSummary`, `PuzzleRunSummary`, `format_duration`, `check_samples`, `run_puzzle`), exposed directly from `aoc_common`:

```python
from aoc_common import Grid, run_puzzle

def part1(grid: Grid[str]) -> int:
    return len(grid.find_points_with_value("#"))

def part2(grid: Grid[str]) -> int:
    return 0

if __name__ == "__main__":
    run_puzzle(
        year=2025,
        day=1,
        part1=part1,
        part2=part2,
        parse_input=Grid.from_text,
        part1_samples=[("#.#\n...", 2)],
    )
```

For the full script structure, `--json` telemetry, sample assertions, and CLI flags (`uv run aoc run`), see [My AoC Template, Version 3](/python/my-aoc-template3).

---

## Offline Testing & Static Gate

All shared modules are backed by an offline `pytest` suite in [`src/tests/`](https://github.com/derailed-dash/Advent-of-Code/tree/main/src/tests) (`test_aoc_commons.py` and `test_runner_and_cli.py`) that uses temporary directories and mock HTTP responses so it never touches real secrets or hits `adventofcode.com`:

```bash
# Run the full offline static & test gate (codespell, ruff, pyright, pytest):
make check
```

See [Unit Testing](/python/unit_test) for patterns used to keep AoC tests fast, isolated, and deterministic.
