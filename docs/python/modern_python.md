---
title: Modern Python Ergonomics for AoC
description: "Python 3.10 to 3.13+ idioms for cleaner puzzle code: structural pattern matching, PEP 695 generics, immutable state modelling, and underused stdlib gems."
main_img:
  name: Modern Python Ergonomics for AoC
  link: /assets/images/pj_modern_python_hero.png
tags:
  - name: Classes and Objects
    link: /python/classes
  - name: Permutations and Combinations
    link: /python/perms_combos
  - name: Comprehensions
    link: /python/comprehensions
  - name: Regular Expressions
    link: /python/regex
mathjax: false
---

## Page Contents

- [Why Modern Idioms Pay Off Under Time Pressure](#why-modern-idioms-pay-off-under-time-pressure)
- [Structural Pattern Matching (`match` / `case`)](#structural-pattern-matching-match--case)
  - [Sequence, Tuple, Class, and Guard Patterns](#sequence-tuple-class-and-guard-patterns)
  - [Watching Out for Bare-Name Capture](#watching-out-for-bare-name-capture)
- [PEP 695 Type Statements, Generics, and `typing.Self`](#pep-695-type-statements-generics-and-typingself)
- [Immutable State Modelling: `tuple` vs `NamedTuple` vs Frozen Dataclass](#immutable-state-modelling-tuple-vs-namedtuple-vs-frozen-dataclass)
- [Underused Standard Library Gems](#underused-standard-library-gems)
  - [`itertools` Pipeline Helpers Beyond Combinatorics](#itertools-pipeline-helpers-beyond-combinatorics)
  - [`collections.Counter` Multiset Algebra](#collectionscounter-multiset-algebra)
  - [`graphlib.TopologicalSorter` for Dependency DAGs](#graphlibtopologicalsorter-for-dependency-dags)
  - [Small Daily Ergonomics](#small-daily-ergonomics)
- [AoC Examples](#aoc-examples)

## Why Modern Idioms Pay Off Under Time Pressure

Halfway through a tough Advent of Code Part 2, bugs rarely come from exotic computer science — they come from sloppy boilerplate. A tangle of `if tokens[0] == ... elif len(tokens) == 3:` branches hides an inverted index. A mutable `[x, y]` coordinate gets passed into `@cache` or mutated in place inside a BFS frontier. Thirty lines of hand-rolled Kahn's algorithm introduce an off-by-one in-degree bug on a 10-line dependency parser.

Modern Python (3.10 through 3.13+) eliminates whole categories of those paper cuts without external libraries. This page assumes you already know foundational OOP from [Classes and Objects](/python/classes) and core combinatorics from [Permutations, Combinations, Products and More](/python/perms_combos), and focuses instead on the ergonomics and underused standard library gems that make puzzle code shorter, safer, and far easier to debug.

## Structural Pattern Matching (`match` / `case`)

### Sequence, Tuple, Class, and Guard Patterns

Introduced in Python 3.10, `match` / `case` goes well beyond a C-style `switch` statement, **checking structure** and **unpacking values** in one visual pass. Across recent puzzles — from cube-face transitions in [2022 Day 22](/2022/22) and operator evaluation in [2025 Day 6](/2025/6) ([`d06.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d06/d06.py){:target="_blank"}) to VM instructions, pipe mazes, and logic gates across the [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} and [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} — four matching shapes come up constantly:

1. **Sequence unpacking** (`["set", reg, val]` or `[op, *rest]`): match command names, arity, and bound operands in one step.
2. **OR patterns and `as` bindings** (`"add" | "mul" as op`): collapse symmetric instruction variants without duplicating logic.
3. **Tuple coordinate dispatch** (`match (tile, dx, dy):`): route pipe turns and directional transitions cleanly (`2023 Day 10`).
4. **Class attribute destructuring and `if` guards**: match fields inside dataclasses (e.g. `2024 Day 24`-style logic gates) or branch on computed properties like digit parity (`2024 Day 11`).

Here are those patterns working together on self-contained AoC-style helpers:

```python
from dataclasses import dataclass


class Bounds:
    """Namespace constants for dotted pattern matching."""

    WIDTH = 10


@dataclass(frozen=True, slots=True)
class Gate:
    """Logic gate node matching 2024 Day 24 style expressions."""

    op: str
    left: str
    right: str


def eval_instruction(tokens: list[str], registers: dict[str, int]) -> int:
    """Demonstrate sequence unpacking, OR patterns, and dotted constants."""
    match tokens:
        case ["set", reg, val]:
            registers[reg] = int(val)
            return registers[reg]
        case ["add" | "mul" as op, reg, rhs]:
            val = registers[rhs] if rhs in registers else int(rhs)
            registers[reg] = registers[reg] + val if op == "add" else registers[reg] * val
            return registers[reg]
        case ["clamp", val] if int(val) >= Bounds.WIDTH:
            return Bounds.WIDTH
        case ["clamp", val]:
            return int(val)
        case [op, *args]:
            raise ValueError(f"Unsupported instruction {op!r} with args {args!r}")
        case _:
            raise ValueError("Empty instruction")


def step_pipe(tile: str, heading: tuple[int, int]) -> tuple[int, int] | None:
    """Route a 2D movement vector through pipe bends (2023 Day 10 style)."""
    match (tile, heading):
        case ("|", (0, _)) | ("-", (_, 0)):
            return heading
        case ("L", (0, 1)) | ("F", (0, -1)):
            return (1, 0)
        case ("L", (-1, 0)) | ("J", (1, 0)):
            return (0, -1)
        case ("7", (1, 0)) | ("F", (-1, 0)):
            return (0, 1)
        case ("J", (0, 1)) | ("7", (0, -1)):
            return (-1, 0)
        case _:
            return None


def blink_stone(stone: int) -> list[int]:
    """Demonstrate guard patterns on integers (2024 Day 11 style)."""
    match stone:
        case 0:
            return [1]
        case x if len(str(x)) % 2 == 0:
            digits = str(x)
            mid = len(digits) // 2
            return [int(digits[:mid]), int(digits[mid:])]
        case _:
            return [stone * 2024]


def describe_gate(gate: Gate) -> str:
    """Demonstrate symmetric class attribute destructuring."""
    match gate:
        case Gate(op="XOR", left="x00", right=r) | Gate(op="XOR", left=r, right="x00"):
            return f"Half-adder sum bit paired with {r}"
        case Gate(op=op, left=left, right=right):
            return f"{left} {op} {right}"


regs = {"a": 2}
assert eval_instruction(["add", "a", "5"], regs) == 7
assert eval_instruction(["mul", "a", "a"], regs) == 49
assert eval_instruction(["clamp", "42"], regs) == 10
assert step_pipe("-", (1, 0)) == (1, 0)
assert step_pipe("L", (0, 1)) == (1, 0)
assert blink_stone(0) == [1]
assert blink_stone(1000) == [10, 0]
assert blink_stone(17) == [1, 7]
assert blink_stone(125) == [253000]
assert describe_gate(Gate("XOR", "y00", "x00")) == "Half-adder sum bit paired with y00"
```

### Watching Out for Bare-Name Capture

There is one subtle gotcha that catches almost everyone the first time they write `match` / `case`. A bare identifier like `case WIDTH:` is **always treated as a variable capture**, not a value comparison against an existing variable named `WIDTH`. Put `case WIDTH:` ahead of other branches and Python raises a `SyntaxError` (`name capture 'WIDTH' makes remaining patterns unreachable`); put it as your final branch and it silently overwrites `WIDTH` with whatever value was matched!

Whenever you want `match` to compare against a named constant by **value**, qualify it with a dot — either a small namespace class (`Bounds.WIDTH`, as shown above) or an `Enum` member (`Direction.NORTH`). In Python's pattern grammar, a dotted name (`a.b`) is always a value lookup, never a capture target.

## PEP 695 Type Statements, Generics, and `typing.Self`

Python 3.12+ (PEP 695) finally retires the awkward `T = TypeVar("T")` preamble when writing generic puzzle utilities. Combined with PEP 585 built-in generics (`list[int]`, `dict[str, int]`), PEP 604 unions (`T | None`), and Python 3.11's `typing.Self`, type hints become readable documentation instead of visual clutter:

- **`type Alias = ...`**: lazily evaluated type aliases cleanly name grid positions (`GridPos`) or generic adjacency maps (`AdjList[T]`).
- **`def fn[T](...)`**: declares type parameters inline right after the function name.
- **`typing.Self`**: tells `pyright` that an immutable method like `.translate()` returns an instance of whichever subclass called it, avoiding redundant casts if you subclass `Point`.

```python
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

type GridPos = tuple[int, int]
type AdjList[T] = dict[T, set[T]]


def first_duplicate[T](items: Iterable[T]) -> T | None:
    """Return the first repeated element in an iterable, or None if all are unique."""
    seen: set[T] = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


@dataclass(frozen=True, order=True, slots=True)
class Point:
    """Immutable, hashable, heap-sortable 2D coordinate using typing.Self."""

    x: int
    y: int

    def translate(self, dx: int, dy: int) -> Self:
        """Return a shifted coordinate of the same concrete class."""
        return type(self)(self.x + dx, self.y + dy)


assert first_duplicate([3, 1, 4, 1, 5]) == 1
assert first_duplicate(["a", "b", "c"]) is None
assert Point(2, 3).translate(-1, 1) == Point(1, 4)
```

Notice we never import deprecated `List`, `Dict`, `Optional`, `Tuple`, or `Union` from `typing` — lowercase built-ins and `|` unions work everywhere from Python 3.10 onwards (with PEP 695 syntax requiring 3.12+).

## Immutable State Modelling: `tuple` vs `NamedTuple` vs Frozen Dataclass

In grid searches, DP memoisation (`@cache`), and Dijkstra priority queues, choosing the right immutable state type affects both bug count and inner-loop speed:

![Comparison of tuple, NamedTuple, and frozen dataclass state representations](/assets/images/pj_state_types_diagram.png){: .no-mat}

| Feature | Plain `tuple` | `NamedTuple` | `@dataclass(frozen=True, slots=True)` |
| :--- | :--- | :--- | :--- |
| **Attribute readability** | None (`pos[0]`, `pos[1]`) | Good (`box.x`, `box.y`, `box.z`) | Excellent (`point.x`, `point.y`) |
| **Unpacking support** | Native (`x, y = pos`) | Native (`x, y, z = box`) | No (explicit field access only) |
| **Heap sortability** | Native element-wise | Native element-wise | Needs `order=True` |
| **`@cache` / `set` hashing** | Fastest (C tuple hash) | Nearly as fast as `tuple` | Fast with `slots=True`, slightly slower field hash |
| **Defaults & `kw_only`** | None | Trailing defaults only | Full defaults, `default_factory`, `kw_only=True` |
| **Custom methods / isolation** | None | Supports methods, but `Box(1, 2, 3) == (1, 2, 3)` | Supports `__add__` / properties; type-distinct (`Point(1, 2) != (1, 2)`) |

Notice the progression across this repository: early `2D` grids often used raw `(x, y)` tuples or `complex` numbers ([Complex Numbers](/python/complex)), [`aoc_common.Point`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/aoc_common/aoc_commons.py){:target="_blank"} uses `@dataclass(frozen=True, order=True, slots=True)` with custom arithmetic, and in [2025 Day 7](/2025/7) ([`d07.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d07/d07.py){:target="_blank"}) and [2025 Day 8](/2025/8) ([`d08.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d08/d08.py){:target="_blank"}), lightweight `NamedTuple` types (`Point`, `Box`) give you named attributes *and* zero-overhead tuple unpacking/hashing.

One rule of thumb for Dijkstra queues: whenever two states tie on priority `(cost, state)`, `heapq` falls back to comparing `state < other_state`. A `NamedTuple` gets lexicographic ordering for free; a frozen dataclass **must** pass `order=True` or `heapq.heappush` will crash with `TypeError: '<' not supported between instances` the moment a tie occurs:

```python
import heapq
from dataclasses import dataclass
from functools import cache
from typing import NamedTuple, Self


@dataclass(frozen=True, order=True, slots=True)
class Point:
    """Hashable and heap-sortable 2D coordinate."""

    x: int
    y: int

    def translate(self, dx: int, dy: int) -> Self:
        """Return a shifted coordinate."""
        return type(self)(self.x + dx, self.y + dy)


class Box(NamedTuple):
    """3D coordinate with named fields and tuple speed (2025 Day 8 style)."""

    x: int
    y: int
    z: int

    def shifted(self, dx: int, dy: int, dz: int) -> Self:
        """Return a translated 3D junction box."""
        return type(self)(self.x + dx, self.y + dy, self.z + dz)


@cache
def manhattan_steps(start: Point, goal: Point) -> int:
    """Cached distance helper proving frozen slotted dataclasses are hashable."""
    return abs(goal.x - start.x) + abs(goal.y - start.y)


# Equal distance (5) forces heapq to break ties using Point's order=True comparison
pq: list[tuple[int, Point]] = []
p1 = Point(2, 3)
p2 = p1.translate(-1, 1)  # Point(1, 4), also distance 5 from origin
heapq.heappush(pq, (manhattan_steps(Point(0, 0), p1), p1))
heapq.heappush(pq, (manhattan_steps(Point(0, 0), p2), p2))
assert heapq.heappop(pq) == (5, Point(1, 4))
assert heapq.heappop(pq) == (5, Point(2, 3))

box = Box(162, 817, 812)
assert box.x == 162 and box[0] == 162
```

(Watch out if you mix raw tuples and `NamedTuple` keys inside the same `set` or `dict`: because `NamedTuple` subclasses `tuple`, `Box(1, 2, 3) == (1, 2, 3)` evaluates to `True`, whereas `Point(1, 2) == (1, 2)` is `False`.)

## Underused Standard Library Gems

### `itertools` Pipeline Helpers Beyond Combinatorics

[Permutations, Combinations, Products and More](/python/perms_combos) already covers `product`, `permutations`, `combinations`, `chain`, and `cycle`. Beyond combinatorics, five `itertools` helpers replace index-heavy `for i in range(len(xs) - 1)` loops across AoC:

- **`itertools.pairwise`** (3.10+): yields overlapping adjacent pairs `(a, b)` — ideal for checking step differences in `2024 Day 2` without worrying about off-by-one bounds.
- **`itertools.batched(..., strict=True)`** (3.12+, with `strict=True` added in **3.13**): slices flat integer lists into fixed chunks like `(start, length)` seed pairs in `2023 Day 5`. Passing `strict=True` fails loudly if an input line ever has a trailing orphan token.
- **`itertools.accumulate`**: emits running totals or running coordinates without manually maintaining an accumulator variable.
- **`itertools.groupby`**: collapses consecutive equal items — classic for Look-and-Say sequences in [2015 Day 10](/2015/10). Just remember `groupby` only merges **adjacent** matching keys, so sort first if you want global grouping.
- **`itertools.starmap`**: unpacks each tuple in an iterable directly into positional arguments (`starmap(Point, pairs)`).

```python
import operator
from itertools import accumulate, batched, groupby, pairwise, starmap
from typing import NamedTuple


class Coord(NamedTuple):
    """Simple 2D coordinate for starmap unpacking."""

    x: int
    y: int


def is_safe_report(levels: list[int], max_step: int = 3) -> bool:
    """Check monotonic bounded steps using itertools.pairwise (2024 Day 2 style)."""
    diffs = [b - a for a, b in pairwise(levels)]
    return all(1 <= d <= max_step for d in diffs) or all(-max_step <= d <= -1 for d in diffs)


def look_and_say(seq: str) -> str:
    """Compute one Look-and-Say iteration using itertools.groupby (2015 Day 10 style)."""
    return "".join(f"{len(list(group))}{digit}" for digit, group in groupby(seq))


assert is_safe_report([7, 6, 4, 2, 1]) is True
assert is_safe_report([1, 2, 7, 8, 9]) is False

seed_ranges = list(batched([79, 14, 55, 13], 2, strict=True))
assert seed_ranges == [(79, 14), (55, 13)]
assert list(starmap(Coord, seed_ranges)) == [Coord(79, 14), Coord(55, 13)]
assert list(accumulate([3, 1, 4, 2], operator.add)) == [3, 4, 8, 10]

seq = "1"
for _ in range(4):
    seq = look_and_say(seq)
assert seq == "111221"
```

### `collections.Counter` Multiset Algebra

Most people reach for `Counter` just to tally frequencies and call `.most_common()`. Under the bonnet, `Counter` also supports full **multiset algebra** — and since Python 3.10, `.total()` sums all counts cleanly in one call:

- `a + b`: add frequencies.
- `a - b`: subtract counts and **automatically drop zero or negative keys** (ideal when tracking remaining inventory or polymer pair steps).
- `a & b`: intersection (element-wise minimum of positive counts).
- `a | b`: union (element-wise maximum of positive counts).

```python
from collections import Counter

stock = Counter({"fuel": 5, "ore": 8})
used = Counter({"fuel": 2, "ore": 10})

assert stock - used == Counter({"fuel": 3})  # 'ore' dropped automatically at <= 0
assert (stock & used) == Counter({"fuel": 2, "ore": 8})
assert (stock | used).total() == 15
```

### `graphlib.TopologicalSorter` for Dependency DAGs

Whenever a puzzle says "item A must appear before item B" (`2024 Day 5` Print Queue) or tracks which bricks support which other bricks above them (`2023 Day 22` Sand Slabs), resist the urge to hand-roll Kahn's algorithm with two dicts and a `deque`. `graphlib.TopologicalSorter` lives in the standard library:

- Call `sorter.add(node, *predecessors)` to declare dependencies (**careful**: the *target* node comes first, followed by everything that must come *before* it!).
- Call `list(sorter.static_order())` to obtain a valid linear ordering, or catch `graphlib.CycleError` if a contradiction creates a cycle.

```python
from graphlib import CycleError, TopologicalSorter


def fix_page_order(pages: list[int], rules: list[tuple[int, int]]) -> list[int]:
    """Topologically sort pages respecting ``before|after`` rules (2024 Day 5 style)."""
    page_set = set(pages)
    sorter: TopologicalSorter[int] = TopologicalSorter()
    for page in pages:
        sorter.add(page)
    for before, after in rules:
        if before in page_set and after in page_set:
            sorter.add(after, before)  # 'after' depends on 'before'
    return list(sorter.static_order())


sample_rules = [
    (47, 53), (97, 13), (97, 61), (97, 47), (75, 29), (61, 13), (75, 53),
    (29, 13), (97, 29), (53, 29), (61, 53), (97, 53), (61, 29), (47, 13),
    (75, 47), (97, 75), (47, 61), (75, 61), (47, 29), (75, 13), (53, 13),
]
assert fix_page_order([75, 97, 47, 61, 53], sample_rules) == [97, 75, 47, 61, 53]

cyclic: TopologicalSorter[str] = TopologicalSorter({"A": {"B"}, "B": {"A"}})
try:
    list(cyclic.static_order())
    raise AssertionError("Expected CycleError")
except CycleError:
    pass
```

### Small Daily Ergonomics

Finally, five tiny built-ins clean up everyday parsing and bitwork lines (pairs nicely with [Regular Expressions](/python/regex) and [Comprehensions](/python/comprehensions)):

- **Walrus `:=` in line-parsing comprehensions**: match a compiled regex and immediately extract groups without running `.match()` twice.
- **`int.bit_count()`** (3.10+): hardware-fast popcount without allocating a string via `bin(n).count("1")`.
- **`math.prod()`**: multiplies an iterable in C instead of `functools.reduce(operator.mul, ...)`.
- **`str.removeprefix()` / `str.removesuffix()`**: unlike `.lstrip("Button A: ")` — which famously strips individual characters rather than a whole prefix string — `removeprefix` matches the exact substring.
- **`next((...), None)` + `any()` / `all()`**: short-circuits cleanly on the first match without materialising an intermediate list.

```python
import math
import re

pattern = re.compile(r"mul\((\d+),(\d+)\)")
lines = ["noop", "mul(6,7)", "end"]

products = [int(m.group(1)) * int(m.group(2)) for line in lines if (m := pattern.match(line))]
assert products == [42]

assert (0b101101).bit_count() == 4
assert math.prod([123, 45, 6]) == 33210
assert "Button A: X+94".removeprefix("Button A: ") == "X+94"
assert next((n for n in [3, 5, 8, 10] if n % 2 == 0), None) == 8
```

## AoC Examples

| Puzzle | Applicable Modern Idiom | Solution Link |
| :--- | :--- | :--- |
| **2015 Day 10 — Elves Look, Elves Say** | `itertools.groupby` run-length encoding | [2015 Day 10](/2015/10) |
| **2022 Day 22 — Monkey Map** | `match` / `case` cube-face wrapping | [2022 Day 22](/2022/22) |
| **2023 Day 5, 7, 10, 20, 22** | `batched`, `match`/`case` card hands & pipes, `TopologicalSorter` DAGs | [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} ([2023 Hub](/2023/)) |
| **2024 Day 2, 5, 7, 11, 17, 24** | `pairwise`, `TopologicalSorter`, `match`/`case` stone parity & logic gates | [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} ([2024 Hub](/2024/)) |
| **2025 Day 6 — Trash Compactor** | `match` / `case` operator dispatch + `math.prod` | [2025 Day 6](/2025/6) ([`d06.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d06/d06.py){:target="_blank"}) |
| **2025 Day 7 & 8 — Laboratories & Playground** | Immutable `NamedTuple` `Point` and `Box` state modelling | [2025 Day 7](/2025/7) ([`d07.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d07/d07.py){:target="_blank"}), [2025 Day 8](/2025/8) ([`d08.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d08/d08.py){:target="_blank"}) |
| **Shared Utilities (`aoc_common`)** | Frozen slotted `@dataclass` `Point`, PEP 585/604 annotations | [`aoc_commons.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/aoc_common/aoc_commons.py){:target="_blank"} |
