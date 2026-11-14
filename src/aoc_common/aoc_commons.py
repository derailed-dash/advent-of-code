"""Core utilities, spatial primitives, and puzzle helpers for Advent of Code solutions.

Purpose & Value:
    Provides a self-contained, zero-``dazbo-commons`` standard library for both standalone
    Template v3 scripts and interactive Jupyter/Colab notebooks. Importing this module is
    side-effect-free: ``.env`` discovery and AoC HTTP calls happen lazily only when input
    retrieval is invoked.

Mechanics & Capabilities:
    - **Paths & Input Caching**: :func:`get_aoc_locations` resolves year/day directories
      from either script paths (``__file__``) or notebook working directories (including
      Colab/Drive fallbacks). :func:`get_aoc_session_cookie` and
      :func:`write_puzzle_input_file` load ``AOC_SESSION_COOKIE`` on demand, send AoC's
      recommended ``User-Agent`` header, and cache ``input.txt``. :func:`fetch_puzzle_page`
      and :func:`parse_puzzle_html` parse puzzle descriptions and rank ``<pre><code>``
      sample candidates in memory without leaving ``desc.html`` files behind.
    - **Logging & Diagnostics**: :func:`setup_logging` configures Rich console handlers
      (targeting ``stderr`` when requested so ``--json`` stdout stays clean);
      :func:`top_and_tail` and :func:`timer` support quick inspection and profiling.
    - **2D / 3D Spatial & Grid Primitives**: :class:`Point`, :class:`Point3D`,
      :class:`Vectors`, :class:`VectorDicts`, :class:`Grid`, :func:`bounding_box`, and
      :func:`render_points` for dense grids and sparse coordinate clouds.
    - **Algorithms**: :func:`binary_search`, :func:`lower_bound`, :func:`upper_bound`,
      :func:`merge_intervals`, :func:`get_factors`, and :func:`to_base_n`.

Typical usage:
    ``import aoc_common.aoc_commons as ac`` or ``from aoc_common import Point, Grid``.
"""

from __future__ import annotations

import contextlib
import logging
import math
import operator
import os
import re
import time
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from functools import cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, ClassVar, Literal, Never, TypeGuard, overload

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

AOC_USER_AGENT = "github.com/derailed-dash/Advent-of-Code by derailed.dash@gmail.com"
_BASE_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
_TITLE_RE = re.compile(r"^---\s*Day\s+\d+:\s*(?P<title>.+?)\s*---$")
_SAMPLE_HINT_PHRASES = (
    "for example",
    "here is an example",
    "suppose you have",
    "consider the following",
)

# Logger for aoc_commons internals
logger = logging.getLogger(__name__)  # aoc_common.aoc_commons
logger.setLevel(logging.INFO)


##########################################################################
# LOGGING AND PATHS
##########################################################################


def setup_logging(level: int | str = logging.INFO, *, stderr: bool = False) -> None:
    """Configure the root logger with Rich console logging.

    Passes ``force=True`` so repeated calls in scripts or Jupyter notebooks
    cleanly replace existing root handlers without duplicating log output.
    Set ``stderr=True`` when structured JSON output is written to ``stdout``.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s.%(msecs)03d %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            RichHandler(
                console=Console(stderr=True) if stderr else None,
                rich_tracebacks=True,
                show_path=False,
                markup=True,
                show_time=False,  # Disable Rich's time since we format our own
            )
        ],
        force=True,
    )


@dataclass
class Locations:
    """Dataclass for storing filesystem paths associated with a puzzle script."""

    script_name: str
    script_dir: Path
    input_dir: Path
    output_dir: Path
    input_file: Path


def get_locations(calling_file_path: str | Path, sub_folder: str | Path = "") -> Locations:
    """Resolve script, input, and output paths relative to ``calling_file_path``."""
    resolved = Path(calling_file_path).resolve()
    script_dir = resolved.parent
    if sub_folder:
        script_dir = script_dir / sub_folder

    script_name = Path(calling_file_path).name
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"
    input_file = input_dir / "input.txt"

    return Locations(
        script_name=script_name,
        script_dir=script_dir,
        input_dir=input_dir,
        output_dir=output_dir,
        input_file=input_file,
    )


def get_aoc_locations(
    year: int,
    day: int,
    caller_file: str | Path | None = None,
    *,
    base_dir: str | Path | None = None,
) -> Locations:
    """Resolve AoC paths safely for both standalone scripts and Jupyter/Colab notebooks.

    When ``caller_file`` is supplied (typically ``__file__``), this delegates
    to :func:`get_locations`. When ``caller_file`` is ``None``, it walks upward
    from ``base_dir`` (or the current working directory) for a repository root
    containing both ``pyproject.toml`` and ``src/`` to target
    ``src/AoC_<year>/d<day:02d>``, falling back to ``<base_dir>/d<day:02d>`` in
    standalone environments such as Google Colab.
    """
    if year < 2015:
        raise ValueError(f"AoC year must be >= 2015, got {year}")
    if not 1 <= day <= 25:
        raise ValueError(f"AoC day must be between 1 and 25, got {day}")

    if caller_file is not None:
        return get_locations(caller_file)

    start = Path(base_dir).resolve() if base_dir is not None else Path.cwd().resolve()
    repo_root = next(
        (
            candidate
            for candidate in (start, *start.parents)
            if (candidate / "pyproject.toml").is_file() and (candidate / "src").is_dir()
        ),
        None,
    )
    day_folder = f"d{day:02d}"
    script_dir = repo_root / "src" / f"AoC_{year}" / day_folder if repo_root is not None else start / day_folder
    input_dir = script_dir / "input"
    return Locations(
        script_name=f"aoc{year}{day_folder}",
        script_dir=script_dir,
        input_dir=input_dir,
        output_dir=script_dir / "output",
        input_file=input_dir / "input.txt",
    )


def setup_file_logging(a_logger: logging.Logger, folder: str | Path = "") -> None:
    """Attach a UTF-8 ``FileHandler`` named after ``a_logger`` under ``folder``."""
    target_dir = Path(folder)
    target_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(target_dir / f"{a_logger.name}.log", mode="w", encoding="utf-8")
    file_fmt = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d:%(name)s:%(levelname)8s: %(message)s",
        datefmt="%H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    a_logger.addHandler(file_handler)


def top_and_tail(
    data: Sequence[Any] | Any,
    block_size: int = 5,
    include_line_numbers: bool = True,
    zero_indexed: bool = False,
) -> Any:
    """Summarise a sequence of lines by returning its first and last ``block_size`` items.

    Non-sequence inputs (including ``str``, ``bytes``, and ``bytearray``) are
    returned unchanged.
    """
    if not isinstance(data, Sequence) or isinstance(data, str | bytes | bytearray):
        return data
    if not data:
        return ""

    start_offset = 0 if zero_indexed else 1
    max_line_num = len(data) - 1 + start_offset
    width = len(str(max_line_num))

    def format_line(idx: int, line: Any) -> str:
        if include_line_numbers:
            return f"{idx + start_offset:>{width}}: {line}"
        return str(line)

    if len(data) <= 2 * block_size:
        return "\n".join(format_line(i, line) for i, line in enumerate(data))

    top = [format_line(i, line) for i, line in enumerate(data[:block_size])]
    tail_start = len(data) - block_size
    tail = [format_line(i, line) for i, line in enumerate(data[tail_start:], start=tail_start)]
    return "\n".join([*top, "...", *tail])


##################################################################
# RETRIEVING INPUT DATA
##################################################################

_GIT_CRYPT_HEADER: bytes = b"\x00GITCRYPT\x00"


def is_git_crypt_locked(path: str | Path) -> bool:
    """Return True if ``path`` exists on disk with a locked ``git-crypt`` header."""
    candidate = Path(path)
    if not candidate.is_file():
        return False
    try:
        with open(candidate, "rb") as handle:
            return handle.read(len(_GIT_CRYPT_HEADER)) == _GIT_CRYPT_HEADER
    except OSError:
        return False


@overload
def get_aoc_session_cookie(*, required: Literal[True] = True) -> str: ...


@overload
def get_aoc_session_cookie(*, required: Literal[False]) -> str | None: ...


@overload
def get_aoc_session_cookie(*, required: bool) -> str | None: ...


def get_aoc_session_cookie(*, required: bool = True) -> str | None:
    """Return stripped ``AOC_SESSION_COOKIE`` after lazily loading ``.env`` if needed.

    Raises ``ValueError`` when ``required=True`` and no cookie is configured; returns
    ``None`` when ``required=False`` and unset.
    """
    raw_cookie = os.getenv("AOC_SESSION_COOKIE")
    if not raw_cookie:
        load_dotenv()
        raw_cookie = os.getenv("AOC_SESSION_COOKIE")
    session_cookie = (raw_cookie or "").strip().strip("\"'")
    if not session_cookie:
        if required:
            raise ValueError("Could not retrieve session cookie.")
        return None
    return session_cookie


def _raise_input_http_error(response: requests.Response, *, resource: str = "input data") -> Never:
    """Raise an informative ``ValueError`` when downloading AoC resources fails."""
    body = response.content.decode("utf-8", errors="replace").strip()
    msg = f"Unable to retrieve {resource}.\nHTTP response: {response.status_code}\n{response.reason}: {body}"
    if response.status_code in {400, 401, 403, 500} and "log in" in body.lower():
        msg += (
            "\nHint: Your AOC_SESSION_COOKIE may have expired (~30-day AoC lifetime). "
            "Log in at https://adventofcode.com, copy the 'session' cookie from "
            "DevTools -> Application -> Cookies, update .env, and run: "
            "git-crypt-helper.sh sync-to-enc .env"
        )
    raise ValueError(msg)


def write_puzzle_input_file(year: int, day: int, locations: Locations) -> str:
    """Download the user's AoC puzzle input to ``locations.input_file`` if not cached.

    Loads ``.env`` lazily if ``AOC_SESSION_COOKIE`` is not already set in the
    environment. Returns ``locations.input_file.name`` if a non-empty file
    already exists locally; otherwise returns the downloaded puzzle text.
    Raises ``ValueError`` if the session cookie is missing or HTTP retrieval fails.
    """
    input_path = Path(locations.input_file)
    locked = is_git_crypt_locked(input_path)
    if input_path.exists() and input_path.stat().st_size > 0 and not locked:
        logger.debug("%s already exists", input_path.name)
        return input_path.name

    try:
        session_cookie = get_aoc_session_cookie(required=True)
    except ValueError as exc:
        if locked:
            raise ValueError(
                f"{input_path} is git-crypt encrypted. Set AOC_SESSION_COOKIE in .env "
                "to download your own puzzle input (or pass -s / --sample-only)."
            ) from exc
        raise
    logger.info("Session cookie retrieved: %s...%s", session_cookie[:6], session_cookie[-6:])

    locations.input_dir.mkdir(parents=True, exist_ok=True)

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookies = {"session": session_cookie}
    headers = {"User-Agent": AOC_USER_AGENT}
    response = requests.get(url, cookies=cookies, headers=headers, timeout=15)

    if response.status_code == 200:
        data = response.text
        with open(input_path, "w", encoding="utf-8") as file:
            logger.debug("Writing input file %s", input_path.name)
            file.write(data)
        return data

    _raise_input_http_error(response)


@dataclass(frozen=True)
class SampleCandidate:
    """Candidate sample input block extracted from an AoC puzzle HTML page."""

    index: int
    text: str
    context: str
    part: int
    score: int


@dataclass(frozen=True)
class PuzzlePage:
    """Parsed Advent of Code puzzle page produced in memory without temp HTML files."""

    year: int
    day: int
    title: str | None
    part1_markdown: str
    part2_markdown: str | None
    samples: tuple[SampleCandidate, ...]
    authenticated: bool


def _attrs_have_class(attrs: list[tuple[str, str | None]], target_class: str) -> bool:
    """Return True if HTML attribute list includes ``target_class`` in ``class``."""
    for name, value in attrs:
        if name == "class" and value and target_class in value.split():
            return True
    return False


class _AoCDayHTMLParser(HTMLParser):
    """Stdlib HTML parser converting AoC ``<article class="day-desc">`` blocks to Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.authenticated: bool = False
        self.articles_md: list[str] = []
        self.raw_samples: list[tuple[str, str, int]] = []
        self._in_article: bool = False
        self._article_part: int = 0
        self._blocks: list[str] = []
        self._last_context: str = ""
        self._pre_buf: list[str] | None = None
        self._elem_buf: list[str] | None = None
        self._elem_tag: str | None = None
        self._in_inline_code: bool = False

    def _finish_pre_block(self) -> None:
        raw_text = "".join(self._pre_buf or ()).strip("\r\n")
        self._pre_buf = None
        if not raw_text:
            return
        self._blocks.append(f"```\n{raw_text}\n```")
        self.raw_samples.append((raw_text, self._last_context, self._article_part))
        self._last_context = ""

    def _finish_text_block(self, tag: str) -> None:
        text = re.sub(r"\s+", " ", "".join(self._elem_buf or ())).strip()
        self._elem_buf = None
        self._elem_tag = None
        self._in_inline_code = False
        if not text:
            return
        if tag == "h2":
            self._blocks.append(f"## {text}")
        elif tag == "li":
            self._blocks.append(f"- {text}")
        else:
            self._blocks.append(text)
        self._last_context = text

    def _flush_active_elem(self) -> None:
        """Emit any buffered heading, paragraph, or list item before nested block elements."""
        if self._elem_buf is not None and self._elem_tag is not None:
            self._finish_text_block(self._elem_tag)

    def _toggle_inline_tag(self, tag: str, *, opening: bool) -> None:
        """Toggle inline code/emphasis markers while suppressing bold syntax inside code spans."""
        if self._elem_buf is None:
            return
        if tag == "code":
            self._in_inline_code = opening
            self._elem_buf.append("`")
        elif tag == "em" and not self._in_inline_code:
            self._elem_buf.append("**")

    def _handle_article_starttag(self, tag: str) -> None:
        """Handle block and inline start tags inside an active ``day-desc`` article."""
        if self._pre_buf is not None:
            return
        if tag == "pre":
            self._flush_active_elem()
            self._pre_buf = []
        elif tag in {"h2", "p", "li"}:
            self._flush_active_elem()
            self._elem_buf = []
            self._elem_tag = tag
        elif tag == "ul":
            self._flush_active_elem()
        elif self._elem_buf is not None and tag in {"code", "em"}:
            self._toggle_inline_tag(tag, opening=True)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Track authenticated user banner, ``day-desc`` articles, and Markdown inline/block tags."""
        if tag == "div" and _attrs_have_class(attrs, "user"):
            self.authenticated = True
            return
        if tag == "article" and _attrs_have_class(attrs, "day-desc"):
            self._in_article = True
            self._article_part += 1
            self._blocks = []
            self._last_context = ""
            self._in_inline_code = False
            return
        if self._in_article:
            self._handle_article_starttag(tag)

    def handle_endtag(self, tag: str) -> None:
        """Close ``day-desc`` articles, code blocks, and inline Markdown wrappers."""
        if tag == "article" and self._in_article:
            self._flush_active_elem()
            self.articles_md.append("\n\n".join(self._blocks))
            self._in_article = False
            return
        if not self._in_article:
            return
        if tag == "pre" and self._pre_buf is not None:
            self._finish_pre_block()
            return
        if self._pre_buf is not None:
            return
        if self._elem_buf is not None and tag in {"code", "em"}:
            self._toggle_inline_tag(tag, opening=False)
            return
        if self._elem_buf is not None and tag == self._elem_tag:
            self._finish_text_block(tag)

    def handle_data(self, data: str) -> None:
        """Collect unescaped text data for the active ``<pre>`` or inline block."""
        if not self._in_article:
            return
        if self._pre_buf is not None:
            self._pre_buf.append(data)
        elif self._elem_buf is not None:
            self._elem_buf.append(data)


def _extract_day_title(part1_markdown: str) -> str | None:
    """Extract the clean puzzle title from a Part 1 ``## --- Day N: Title ---`` heading."""
    for line in part1_markdown.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            match = _TITLE_RE.match(heading)
            return match.group("title") if match else heading
    return None


def _score_sample_block(text: str, context: str, *, is_first_in_part: bool) -> int:
    """Heuristically rank how likely a ``<pre><code>`` block is the main sample input."""
    score = 0
    lowered_ctx = context.lower()
    if any(phrase in lowered_ctx for phrase in _SAMPLE_HINT_PHRASES):
        score += 50
    if context.rstrip().endswith(":"):
        score += 20
    if "\n" in text:
        score += 15
    if is_first_in_part:
        score += 10
    return score


def parse_puzzle_html(html: str, *, year: int, day: int) -> PuzzlePage:
    """Parse an AoC day HTML page in memory into Markdown sections and scored sample candidates."""
    parser = _AoCDayHTMLParser()
    parser.feed(html)
    parser.close()

    part1_md = parser.articles_md[0] if parser.articles_md else ""
    part2_md = parser.articles_md[1] if len(parser.articles_md) > 1 else None
    seen_parts: set[int] = set()
    samples: list[SampleCandidate] = []
    for idx, (text, context, part) in enumerate(parser.raw_samples, start=1):
        is_first = part not in seen_parts
        seen_parts.add(part)
        samples.append(
            SampleCandidate(
                index=idx,
                text=text,
                context=context,
                part=part,
                score=_score_sample_block(text, context, is_first_in_part=is_first),
            )
        )

    return PuzzlePage(
        year=year,
        day=day,
        title=_extract_day_title(part1_md),
        part1_markdown=part1_md,
        part2_markdown=part2_md,
        samples=tuple(samples),
        authenticated=parser.authenticated,
    )


def fetch_puzzle_page(year: int, day: int, *, session_cookie: str | None = None) -> PuzzlePage:
    """Fetch and parse ``https://adventofcode.com/<year>/day/<day>`` without disk temp files.

    Uses ``AOC_SESSION_COOKIE`` when available so Part 2 is included if solved, while
    still allowing Part 1 fetches anonymously when no cookie is configured.
    """
    if year < 2015:
        raise ValueError(f"AoC year must be >= 2015, got {year}")
    if not 1 <= day <= 25:
        raise ValueError(f"AoC day must be between 1 and 25, got {day}")

    cookie = session_cookie.strip().strip("\"'") if session_cookie is not None else get_aoc_session_cookie(required=False)
    cookies = {"session": cookie} if cookie else None
    headers = {"User-Agent": AOC_USER_AGENT}
    url = f"https://adventofcode.com/{year}/day/{day}"
    response = requests.get(url, cookies=cookies, headers=headers, timeout=15)

    if response.status_code == 200:
        return parse_puzzle_html(response.text, year=year, day=day)

    _raise_input_http_error(response, resource="puzzle description")


#################################################################
# TESTING
#################################################################


def validate(test: Any, answer: Any) -> None:
    """Assert that a sample test result matches the expected answer."""
    if test != answer:
        raise AssertionError(f"{test} != {answer}")


#################################################################
# POINTS, VECTORS AND GRIDS
#################################################################


def _is_int_not_bool(value: object) -> TypeGuard[int]:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True, order=True)
class Point:
    """Immutable, hashable, ordered 2D integer coordinate ``(x, y)``."""

    x: int
    y: int

    def __add__(self, other: Point) -> Point:
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return NotImplemented

    @overload
    def __mul__(self, other: Point) -> Point: ...

    @overload
    def __mul__(self, other: int) -> Point: ...

    def __mul__(self, other: Point | int) -> Point:
        """Multiply elementwise with another ``Point`` or scale by an integer."""
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        if _is_int_not_bool(other):
            return Point(self.x * other, self.y * other)
        return NotImplemented

    def __rmul__(self, other: int) -> Point:
        """Scale this ``Point`` when written as ``scalar * point``."""
        if _is_int_not_bool(other):
            return Point(self.x * other, self.y * other)
        return NotImplemented

    def __sub__(self, other: Point) -> Point:
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return NotImplemented

    def yield_neighbours(
        self,
        include_diagonals: bool = True,
        include_self: bool = False,
    ) -> Iterator[Point]:
        """Yield neighbouring ``Point``s in 8-way or 4-way orthogonal order."""
        deltas: list[tuple[int, int]]
        if not include_diagonals:
            deltas = [vector.value for vector in Vectors if abs(vector.value[0]) != abs(vector.value[1])]
        else:
            deltas = [vector.value for vector in Vectors]

        if include_self:
            deltas.append((0, 0))

        for dx, dy in deltas:
            yield Point(self.x + dx, self.y + dy)

    def neighbours(
        self,
        include_diagonals: bool = True,
        include_self: bool = False,
    ) -> list[Point]:
        """Return all neighbouring ``Point``s matching the given constraints."""
        return list(self.yield_neighbours(include_diagonals=include_diagonals, include_self=include_self))

    def get_specific_neighbours(self, directions: Iterable[Vectors]) -> list[Point]:
        """Return neighbours obtained by stepping along each vector in ``directions``."""
        return [Point(self.x + vector.value[0], self.y + vector.value[1]) for vector in directions]

    @staticmethod
    def manhattan_distance(a_point: Point) -> int:
        """Return the L1 Manhattan norm ``|x| + |y|`` of ``a_point``."""
        return abs(a_point.x) + abs(a_point.y)

    def manhattan_distance_from(self, other: Point) -> int:
        """Return the Manhattan distance between ``self`` and ``other``."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __repr__(self) -> str:
        return f"P({self.x},{self.y})"


_ORTHOGONAL_3D_DELTAS: tuple[tuple[int, int, int], ...] = (
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
)
_ALL_3D_DELTAS: tuple[tuple[int, int, int], ...] = tuple(
    (dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dy, dz) != (0, 0, 0)
)


@dataclass(frozen=True, order=True)
class Point3D:
    """Immutable, hashable, ordered 3D integer coordinate ``(x, y, z)``."""

    x: int
    y: int
    z: int

    def __add__(self, other: Point3D) -> Point3D:
        if isinstance(other, Point3D):
            return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    def __sub__(self, other: Point3D) -> Point3D:
        if isinstance(other, Point3D):
            return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    @overload
    def __mul__(self, other: Point3D) -> Point3D: ...

    @overload
    def __mul__(self, other: int) -> Point3D: ...

    def __mul__(self, other: Point3D | int) -> Point3D:
        """Multiply elementwise with another ``Point3D`` or scale by an integer."""
        if isinstance(other, Point3D):
            return Point3D(self.x * other.x, self.y * other.y, self.z * other.z)
        if _is_int_not_bool(other):
            return Point3D(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __rmul__(self, other: int) -> Point3D:
        """Scale this ``Point3D`` when written as ``scalar * point``."""
        if _is_int_not_bool(other):
            return Point3D(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def yield_neighbours(
        self,
        include_diagonals: bool = True,
        include_self: bool = False,
    ) -> Iterator[Point3D]:
        """Yield 26-way or 6-way orthogonal neighbouring ``Point3D``s."""
        deltas = _ALL_3D_DELTAS if include_diagonals else _ORTHOGONAL_3D_DELTAS
        for dx, dy, dz in deltas:
            yield Point3D(self.x + dx, self.y + dy, self.z + dz)
        if include_self:
            yield self

    def neighbours(
        self,
        include_diagonals: bool = True,
        include_self: bool = False,
    ) -> list[Point3D]:
        """Return neighbouring ``Point3D``s matching the given constraints."""
        return list(self.yield_neighbours(include_diagonals=include_diagonals, include_self=include_self))

    @staticmethod
    def manhattan_distance(a_point: Point3D) -> int:
        """Return the L1 Manhattan norm ``|x| + |y| + |z|`` of ``a_point``."""
        return abs(a_point.x) + abs(a_point.y) + abs(a_point.z)

    def manhattan_distance_from(self, other: Point3D) -> int:
        """Return the Manhattan distance between ``self`` and ``other``."""
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)

    def __repr__(self) -> str:
        return f"P3D({self.x},{self.y},{self.z})"


class Vectors(Enum):
    """Enumeration of 8 compass directions using Cartesian ``y``-up orientation (``N = (0, 1)``)."""

    N = (0, 1)
    NE = (1, 1)
    E = (1, 0)
    SE = (1, -1)
    S = (0, -1)
    SW = (-1, -1)
    W = (-1, 0)
    NW = (-1, 1)

    @property
    def y_inverted(self) -> tuple[int, int]:
        """Return vector tuple with ``y`` inverted for top-left grid coordinates (``N = (0, -1)``)."""
        x, y = self.value
        return (x, -y)

    def to_point(self, *, y_down: bool = False) -> Point:
        """Convert this direction vector into a ``Point`` step."""
        x, y = self.y_inverted if y_down else self.value
        return Point(x, y)


class VectorDicts:
    """Direction-character lookup tables for Cartesian (``y``-up) and grid (``y``-down) coordinates."""

    ARROWS: ClassVar[dict[str, tuple[int, int]]] = {
        "^": Vectors.N.value,
        ">": Vectors.E.value,
        "v": Vectors.S.value,
        "<": Vectors.W.value,
    }

    DIRS: ClassVar[dict[str, tuple[int, int]]] = {
        "U": Vectors.N.value,
        "R": Vectors.E.value,
        "D": Vectors.S.value,
        "L": Vectors.W.value,
    }

    ARROWS_Y_DOWN: ClassVar[dict[str, tuple[int, int]]] = {
        "^": Vectors.N.y_inverted,
        ">": Vectors.E.y_inverted,
        "v": Vectors.S.y_inverted,
        "<": Vectors.W.y_inverted,
    }

    DIRS_Y_DOWN: ClassVar[dict[str, tuple[int, int]]] = {
        "U": Vectors.N.y_inverted,
        "R": Vectors.E.y_inverted,
        "D": Vectors.S.y_inverted,
        "L": Vectors.W.y_inverted,
    }

    NINE_BOX: ClassVar[dict[str, tuple[int, int]]] = {
        # (x, y) vector for adjacent locations in a 3x3 neighbourhood
        "tr": (1, 1),
        "mr": (1, 0),
        "br": (1, -1),
        "bm": (0, -1),
        "bl": (-1, -1),
        "ml": (-1, 0),
        "tl": (-1, 1),
        "tm": (0, 1),
    }


def bounding_box(points: Iterable[Point]) -> tuple[Point, Point]:
    """Return the inclusive ``(min_point, max_point)`` corners spanning ``points``."""
    iterator = iter(points)
    first = next(iterator, None)
    if first is None:
        raise ValueError("Cannot compute bounding box of empty point collection.")

    min_x = max_x = first.x
    min_y = max_y = first.y
    for point in iterator:
        if point.x < min_x:
            min_x = point.x
        elif point.x > max_x:
            max_x = point.x
        if point.y < min_y:
            min_y = point.y
        elif point.y > max_y:
            max_y = point.y

    return Point(min_x, min_y), Point(max_x, max_y)


def render_points(
    points: Mapping[Point, Any] | Iterable[Point],
    *,
    empty_char: str = ".",
    fill_char: str = "#",
    y_down: bool = True,
) -> str:
    """Render a sparse ``Point`` mapping or collection as a multiline string grid."""
    if isinstance(points, Mapping):
        grid_map: dict[Point, str] = {point: str(value) for point, value in points.items()}
    else:
        grid_map = dict.fromkeys(points, fill_char)

    if not grid_map:
        return ""

    min_pt, max_pt = bounding_box(grid_map)
    y_range = range(min_pt.y, max_pt.y + 1) if y_down else range(max_pt.y, min_pt.y - 1, -1)
    x_range = range(min_pt.x, max_pt.x + 1)
    return "\n".join("".join(grid_map.get(Point(x, y), empty_char) for x in x_range) for y in y_range)


class Grid[T]:
    """2D rectangular grid indexed by ``Point(x, y)`` with top-left origin."""

    def __init__(self, grid_array: Sequence[Iterable[T]]) -> None:
        self.array: list[list[T]] = [list(row) for row in grid_array]
        self._height: int = len(self.array)
        self._width: int = len(self.array[0]) if self._height > 0 else 0
        if any(len(row) != self._width for row in self.array):
            raise ValueError("All grid rows must have equal length.")

    def value_at_point(self, point: Point) -> T:
        """Return the cell value at ``point``."""
        return self.array[point.y][point.x]

    def set_value_at_point(self, point: Point, value: T) -> None:
        """Set the cell value at ``point``."""
        self.array[point.y][point.x] = value

    def valid_location(self, point: Point) -> bool:
        """Return ``True`` if ``point`` lies within the grid bounds."""
        return 0 <= point.x < self._width and 0 <= point.y < self._height

    @property
    def width(self) -> int:
        """Grid width (number of columns)."""
        return self._width

    @property
    def height(self) -> int:
        """Grid height (number of rows)."""
        return self._height

    @property
    def cols(self) -> list[list[T]]:
        """Return columns as a list of mutable column lists."""
        if not self.array or self._width == 0:
            return []
        return [list(col) for col in zip(*self.array)]

    def all_points(self) -> list[Point]:
        """Return all ``Point`` coordinates contained within the grid."""
        return [Point(x, y) for y in range(self.height) for x in range(self.width)]

    def find_points_with_value(self, value: T) -> list[Point]:
        """Return all grid coordinates whose current cell value equals ``value``."""
        return [Point(x, y) for y, row in enumerate(self.array) for x, cell in enumerate(row) if cell == value]

    def neighbours_of(
        self,
        point: Point,
        *,
        include_diagonals: bool = True,
        include_self: bool = False,
    ) -> list[Point]:
        """Return in-bounds neighbours of ``point`` inside this grid."""
        return [
            candidate
            for candidate in point.yield_neighbours(include_diagonals=include_diagonals, include_self=include_self)
            if self.valid_location(candidate)
        ]

    def rows_as_str(self) -> list[str]:
        """Render each row as a concatenated string."""
        return ["".join(str(cell) for cell in row) for row in self.array]

    def cols_as_str(self) -> list[str]:
        """Render each column as a concatenated string."""
        return ["".join(str(cell) for cell in col) for col in self.cols]

    def transpose(self) -> Grid[T]:
        """Return a new ``Grid`` with rows and columns swapped."""
        return Grid(self.cols)

    def flip_vertical(self) -> Grid[T]:
        """Flip the grid horizontally (left-to-right mirror across the vertical axis)."""
        return Grid([row[::-1] for row in self.array])

    def flip_horizontal(self) -> Grid[T]:
        """Flip the grid vertically (top-to-bottom mirror across the horizontal axis)."""
        return Grid(self.array[::-1])

    def rotate_90(self, ccw: bool = False) -> Grid[T]:
        """Rotate the grid 90 degrees clockwise, or counter-clockwise when ``ccw=True``."""
        flipped = self.flip_vertical() if ccw else self.flip_horizontal()
        return flipped.transpose()

    def __repr__(self) -> str:
        return f"Grid(size={self.width}*{self.height})"

    def __str__(self) -> str:
        return "\n".join("".join(map(str, row)) for row in self.array)


#################################################################
# CONSOLE UTILITIES
#################################################################


def cls() -> None:
    """Clear the terminal console."""
    os.system("cls" if os.name == "nt" else "clear")


#################################################################
# ALGORITHMS AND TIMING
#################################################################


def binary_search(
    target: Any,
    low: int,
    high: int,
    func: Callable[..., Any],
    *func_args: Any,
    reverse_search: bool = False,
) -> int | None:
    """Search integers ``[low, high]`` for ``candidate`` where ``func(candidate, *func_args) == target``.

    Assumes ``func`` is monotonically increasing (or decreasing when
    ``reverse_search=True``). Returns ``None`` if no integer in ``[low, high]``
    evaluates to ``target``.
    """
    low_i = int(low)
    high_i = int(high)
    comp = operator.lt if not reverse_search else operator.gt

    while low_i <= high_i:
        candidate = (low_i + high_i) // 2
        res = func(candidate, *func_args)
        logger.debug("%d -> %s", candidate, res)
        if res == target:
            return candidate

        if comp(res, target):
            low_i = candidate + 1
        else:
            high_i = candidate - 1

    return None


def lower_bound(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Find the smallest integer in ``[low, high]`` where monotonic ``predicate(x)`` is True.

    Assumes ``predicate`` transitions from ``False`` to ``True`` as ``x``
    increases. Returns ``None`` if ``predicate(x)`` is never ``True`` in ``[low, high]``.
    """
    low_i = int(low)
    high_i = int(high)
    best: int | None = None

    while low_i <= high_i:
        mid = (low_i + high_i) // 2
        if predicate(mid):
            best = mid
            high_i = mid - 1
        else:
            low_i = mid + 1

    return best


def upper_bound(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Find the largest integer in ``[low, high]`` where monotonic ``predicate(x)`` is True.

    Assumes ``predicate`` transitions from ``True`` to ``False`` as ``x``
    increases. Returns ``None`` if ``predicate(x)`` is never ``True`` in ``[low, high]``.
    """
    low_i = int(low)
    high_i = int(high)
    best: int | None = None

    while low_i <= high_i:
        mid = (low_i + high_i) // 2
        if predicate(mid):
            best = mid
            low_i = mid + 1
        else:
            high_i = mid - 1

    return best


def _normalise_interval(interval: Sequence[int] | range) -> list[int] | None:
    """Convert one ``range`` or 2-item sequence to a closed ``[start, end]`` list."""
    if isinstance(interval, range):
        if interval.step != 1:
            raise ValueError(f"range intervals must have step == 1, got {interval.step}")
        return [interval.start, interval.stop - 1] if interval else None

    if len(interval) != 2:
        raise ValueError(f"Intervals must have length 2, got {len(interval)}")
    start, end = int(interval[0]), int(interval[1])
    if start > end:
        raise ValueError(f"Invalid interval with start > end: [{start}, {end}]")
    return [start, end]


def merge_intervals(
    intervals: Iterable[Sequence[int] | range],
    *,
    merge_adjacent: bool = False,
) -> list[list[int]]:
    """Merge overlapping integer intervals into sorted ``[start, end]`` lists without mutating inputs.

    Unit-step ``range(a, b)`` objects are normalised to closed ``[a, b - 1]`` intervals,
    skipping empty ranges. Pass ``merge_adjacent=True`` to also coalesce adjacent
    integer intervals such as ``[1, 5]`` and ``[6, 8]``.
    """
    normalised = [item for interval in intervals if (item := _normalise_interval(interval)) is not None]
    if not normalised:
        return []

    normalised.sort()
    gap = 1 if merge_adjacent else 0
    merged: list[list[int]] = [normalised[0].copy()]

    for start, end in normalised[1:]:
        if start <= merged[-1][1] + gap:
            if end > merged[-1][1]:
                merged[-1][1] = end
        else:
            merged.append([start, end])

    return merged


@cache
def get_factors(num: int) -> set[int]:
    """Return all positive integer divisors of ``num``."""
    if num < 1:
        raise ValueError(f"num must be a positive integer, got {num}")

    factors: set[int] = set()
    for i in range(1, math.isqrt(num) + 1):
        if num % i == 0:
            factors.add(i)
            factors.add(num // i)
    return factors


def to_base_n(number: int, base: int) -> str:
    """Convert any integer into its base-``n`` string representation for ``2 <= base <= 36``."""
    if not 2 <= base <= 36:
        raise ValueError(f"Base must be between 2 and 36 inclusive, got {base}")
    if number == 0:
        return "0"

    sign = "-" if number < 0 else ""
    curr = abs(number)
    digits: list[str] = []
    while curr:
        curr, rem = divmod(curr, base)
        digits.append(_BASE_DIGITS[rem])

    return f"{sign}{''.join(reversed(digits))}"


@contextlib.contextmanager
def timer(description: str = "Execution time") -> Iterator[None]:
    """Context manager to log the elapsed wall-clock execution time of a block."""
    t1 = time.perf_counter()
    try:
        yield
    finally:
        t2 = time.perf_counter()
        logger.info("%s: %.3f seconds", description, t2 - t1)


from aoc_common.runner import (  # noqa: E402, F401
    PartRunSummary,
    PuzzleRunSummary,
    SampleInput,
    check_samples,
    format_duration,
    run_puzzle,
)
