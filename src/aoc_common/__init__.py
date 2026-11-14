"""Shared Advent of Code toolkit for standalone scripts and Jupyter/Colab notebooks.

Purpose & Value:
    Eliminates duplicated boilerplate across puzzle years without depending on external
    personal packages such as ``dazbo-commons``. All public symbols import cleanly
    offline without ``AOC_SESSION_COOKIE`` set, both from the editable local ``.venv``
    and when installed directly in Google Colab via ``git+https``.

Package Layout:
    - :mod:`aoc_common.aoc_commons`: Path resolution (:func:`get_aoc_locations`), lazy
      ``.env`` loading and compliant AoC HTTP caching (:func:`get_aoc_session_cookie`,
      :func:`write_puzzle_input_file`, :func:`fetch_puzzle_page`, :func:`parse_puzzle_html`),
      Rich logging (:func:`setup_logging`), 2D/3D spatial primitives (:class:`Point`,
      :class:`Point3D`, :class:`Vectors`, :class:`VectorDicts`, :class:`Grid`), sparse
      point-cloud rendering, and search/interval/number-theory helpers.
    - :mod:`aoc_common.runner`: Notebook-safe sample verification (:func:`check_samples`),
      adaptive duration formatting (:func:`format_duration`), and standard standalone CLI
      orchestration (:func:`run_puzzle`).
    - :mod:`aoc_common.cli`: Repository-wide ``aoc`` console entry point (``run``,
      ``list``, ``fetch``, ``new-year``, ``clean-inputs``).

Typical usage:
    ``import aoc_common.aoc_commons as ac`` or ``from aoc_common import Point, Grid``.
"""

from aoc_common.aoc_commons import (
    AOC_USER_AGENT,
    Grid,
    Locations,
    PartRunSummary,
    Point,
    Point3D,
    PuzzlePage,
    PuzzleRunSummary,
    SampleCandidate,
    SampleInput,
    VectorDicts,
    Vectors,
    binary_search,
    bounding_box,
    check_samples,
    cls,
    fetch_puzzle_page,
    format_duration,
    get_aoc_locations,
    get_aoc_session_cookie,
    get_factors,
    get_locations,
    is_git_crypt_locked,
    lower_bound,
    merge_intervals,
    parse_puzzle_html,
    render_points,
    run_puzzle,
    setup_file_logging,
    setup_logging,
    timer,
    to_base_n,
    top_and_tail,
    upper_bound,
    validate,
    write_puzzle_input_file,
)

__all__ = [
    "AOC_USER_AGENT",
    "Grid",
    "Locations",
    "PartRunSummary",
    "Point",
    "Point3D",
    "PuzzlePage",
    "PuzzleRunSummary",
    "SampleCandidate",
    "SampleInput",
    "VectorDicts",
    "Vectors",
    "binary_search",
    "bounding_box",
    "check_samples",
    "cls",
    "fetch_puzzle_page",
    "format_duration",
    "get_aoc_locations",
    "get_aoc_session_cookie",
    "get_factors",
    "get_locations",
    "is_git_crypt_locked",
    "lower_bound",
    "merge_intervals",
    "parse_puzzle_html",
    "render_points",
    "run_puzzle",
    "setup_file_logging",
    "setup_logging",
    "timer",
    "to_base_n",
    "top_and_tail",
    "upper_bound",
    "validate",
    "write_puzzle_input_file",
]
