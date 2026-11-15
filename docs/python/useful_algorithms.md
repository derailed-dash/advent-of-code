---
title: Useful Algorithms
description: "Canonical Python >=3.13 implementations and aoc_common helpers for interval merging, monotonic binary search, Disjoint Set (Union-Find), factors, base conversion, and timing."
main_img:
  name: Algorithms
  link: /assets/images/algorithms.png
tags:
  - name: Reusable Code
    link: /python/reusable_code
  - name: Merging Intervals
    link: https://www.geeksforgeeks.org/merging-intervals/
  - name: Binary Search (RealPython)
    link: https://realpython.com/binary-search-python/
  - name: Shortest Path Algorithms
    link: /python/shortest_paths
  - name: Interval and Range Algebra
    link: /python/intervals
mathjax: true
---

## Page Contents

- [Overview](#overview)
- [Merging Overlapping Intervals](#merging-overlapping-intervals)
- [Binary Search, `lower_bound`, and `upper_bound`](#binary-search-lower_bound-and-upper_bound)
- [Disjoint Set / Union-Find (`DisjointSet`)](#disjoint-set--union-find-disjointset)
- [Get Factors](#get-factors)
- [Base-N Conversion (`to_base_n`)](#base-n-conversion-to_base_n)
- [Timing with `timer()` and `run_puzzle()`](#timing-with-timer-and-run_puzzle)
- [AoC Examples](#aoc-examples)

## Overview

Across Advent of Code years, a handful of core algorithms come up again and again — sweeping overlapping intervals, binary-searching huge monotonic domains, merging connected clusters, factorising integers, and formatting numbers in arbitrary bases.

All of the reusable helpers below (apart from the copy-ready `DisjointSet` recipe, which we include here for problems like clustering and Kruskal's MST) live directly in [`aoc_common.aoc_commons`](/python/reusable_code) and are tested offline in `src/tests/test_aoc_commons.py`.

## Merging Overlapping Intervals

Given unsorted closed intervals `[start, end]`, sort by start coordinate and coalesce overlaps in a single \( O(n \log n) \) pass without mutating the caller's list. Note how `aoc_common.merge_intervals` also normalises unit-step `range(a, b)` objects cleanly and supports `merge_adjacent=True` when `[1, 5]` and `[6, 8]` should merge into `[1, 8]`:

```python
from collections.abc import Iterable, Sequence


def merge_intervals(
    intervals: Iterable[Sequence[int]],
    *,
    merge_adjacent: bool = False,
) -> list[list[int]]:
    """Merge overlapping closed integer ``[start, end]`` intervals in ascending order."""
    normalised = sorted([int(lo), int(hi)] for lo, hi in intervals)
    if not normalised:
        return []

    gap = 1 if merge_adjacent else 0
    merged: list[list[int]] = [normalised[0].copy()]
    for start, end in normalised[1:]:
        if start <= merged[-1][1] + gap:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


assert merge_intervals([[6, 8], [1, 9], [2, 4], [4, 7]]) == [[1, 9]]
assert merge_intervals([[1, 5], [6, 8]], merge_adjacent=True) == [[1, 8]]
```

When a puzzle goes beyond coalescing overlapping pairs — e.g. splitting half-open `[lo, hi)` ranges across piecewise rules, chaining transformation pipelines, subtracting 3D cuboids, or compressing sparse coordinates — see [Interval and Range Algebra](/python/intervals).

## Binary Search, `lower_bound`, and `upper_bound`

When an input space spans \( 10^{12}+ \) values but a monotonic property flips from `False` to `True` at a single threshold, \( O(\log n) \) binary search solves it in microseconds.

Use **exact-match search** (`binary_search`) when looking for a candidate returning an exact target value, and use **monotonic predicate bounds** (`lower_bound` / `upper_bound`) when looking for the minimum passing input or maximum passing budget:

```python
import operator
from collections.abc import Callable
from typing import Any


def binary_search(
    target: Any,
    low: int,
    high: int,
    func: Callable[..., Any],
    *func_args: Any,
    reverse_search: bool = False,
) -> int | None:
    """Search integers ``[low, high]`` where ``func(candidate, *func_args) == target``."""
    comp = operator.lt if not reverse_search else operator.gt
    while low <= high:
        candidate = (low + high) // 2
        res = func(candidate, *func_args)
        if res == target:
            return candidate
        if comp(res, target):
            low = candidate + 1
        else:
            high = candidate - 1
    return None


def lower_bound(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Return the smallest integer in ``[low, high]`` where monotonic ``predicate(x)`` is True."""
    best: int | None = None
    while low <= high:
        mid = (low + high) // 2
        if predicate(mid):
            best = mid
            high = mid - 1
        else:
            low = mid + 1
    return best


def upper_bound(low: int, high: int, predicate: Callable[[int], bool]) -> int | None:
    """Return the largest integer in ``[low, high]`` where monotonic ``predicate(x)`` is True."""
    best: int | None = None
    while low <= high:
        mid = (low + high) // 2
        if predicate(mid):
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best


assert binary_search(225, 0, 20, lambda x: x**2) == 15
assert lower_bound(0, 20, lambda x: x**2 >= 200) == 15
assert upper_bound(0, 20, lambda x: x**2 <= 200) == 14
```

*(A subtle trap in naive binary search: setting `low = candidate` instead of `low = candidate + 1` or looping `while low < high` can stall infinitely when `high - low == 1`. Always step strictly past `candidate` with `candidate + 1` / `candidate - 1` and loop `while low <= high`.)*

## Disjoint Set / Union-Find (`DisjointSet`)

Whenever a puzzle asks you to incrementally connect nodes and query component sizes or track when everything forms a single cluster (such as wiring junction boxes in [2025 Day 8](/2025/8) or Kruskal's minimum spanning tree), a **Disjoint Set Union (DSU)** tracks connected components in near-\( O(1) \) amortised time (`α(n)`) with zero third-party dependencies.

Here is a clean, copy-ready Python `>=3.13` generic implementation using path halving and union-by-size:

```python
class DisjointSet[T]:
    """Union-Find structure with path halving and union-by-size in O(alpha(n)) time."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self._parent: dict[T, T] = {}
        self._size: dict[T, int] = {}
        self._components: int = 0
        for item in items:
            self.add(item)

    def add(self, item: T) -> None:
        """Ensure ``item`` is registered as its own singleton component."""
        if item not in self._parent:
            self._parent[item] = item
            self._size[item] = 1
            self._components += 1

    def find(self, item: T) -> T:
        """Return the canonical root representative of ``item``."""
        self.add(item)
        curr = item
        while self._parent[curr] != curr:
            # Path halving keeps trees nearly flat without recursion limits
            self._parent[curr] = self._parent[self._parent[curr]]
            curr = self._parent[curr]
        return curr

    def union(self, a: T, b: T) -> bool:
        """Merge components containing ``a`` and ``b``; return True if they were separate."""
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self._size[root_a] < self._size[root_b]:
            root_a, root_b = root_b, root_a
        self._parent[root_b] = root_a
        self._size[root_a] += self._size[root_b]
        self._components -= 1
        return True

    @property
    def num_components(self) -> int:
        """Return the current number of disjoint components."""
        return self._components

    def component_sizes(self) -> list[int]:
        """Return component sizes sorted descending."""
        roots = {self.find(node) for node in self._parent}
        return sorted((self._size[root] for root in roots), reverse=True)
```

## Get Factors

To enumerate all positive divisors of `num` in \( O(\sqrt{n}) \), iterate up to `math.isqrt(num)` and add each divisor pair `(i, num // i)`. Wrapping with [`@functools.cache`](/python/recursion#optimising-memoisation) avoids recomputing divisors in repeated inner loops:

```python
import math
from functools import cache


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


assert get_factors(12) == {1, 2, 3, 4, 6, 12}
```

*(Using `math.isqrt(num)` stays in exact integer arithmetic, avoiding floating-point precision issues for very large integers.)*

## Base-N Conversion (`to_base_n`)

Python provides built-ins `bin()`, `oct()`, and `hex()` for bases `2`, `8`, and `16`, plus `int(text, base)` in the reverse direction. For arbitrary bases such as base-5 ([SNAFU numbers](/2022/25)) or base-3 operator brute-forcing ([2024 Day 7](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}), `divmod` constructs any base `2 <= base <= 36`:

```python
_BASE_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


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


assert to_base_n(38, 5) == "123"
assert to_base_n(-255, 16) == "-ff"
```

## Timing with `timer()` and `run_puzzle()`

To time arbitrary blocks of code cleanly without wrapping everything in manual `t1 = time.perf_counter()` pairs, `aoc_common` provides a `timer()` **context manager** powered by `@contextlib.contextmanager`:

```python
import contextlib
import logging
import time
from collections.abc import Iterator

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def timer(description: str = "Execution time") -> Iterator[None]:
    """Context manager to log elapsed wall-clock execution time for a block."""
    t1 = time.perf_counter()
    try:
        yield
    finally:
        logger.info("%s: %.3f seconds", description, time.perf_counter() - t1)
```

In a notebook or standalone block, invoke it with `with ac.timer("Part 1"):`:

```python
import aoc_common.aoc_commons as ac

with ac.timer("Part 1"):
    answer = part1(parsed_input)
```

*(Note: When writing standalone scripts using [Template v3](/python/my-aoc-template3), `ac.run_puzzle()` already measures Part 1 and Part 2 independently using `time.perf_counter()` and renders adaptive durations with `ac.format_duration()`, so no manual `with ac.timer()` wrapper is needed around `main()`.)*

## AoC Examples

- [Interval merging to rule out beacon columns — 2022 Day 15](/2022/15)
- [Range & interval overlap compression — 2025 Day 5](/2025/5)
- [Factor pairs and repeated digit substrings — 2025 Day 2](/2025/2)
- [Binary-searching minimum obstruction step (`lower_bound`) — 2024 Day 18](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}
- [Base-3 operator search (`to_base_n` vs DFS) — 2024 Day 7](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}
- [Connected components & Union-Find circuits (`DisjointSet`) — 2025 Day 8](/2025/8)
