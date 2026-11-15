---
title: Interval and Range Algebra
description: "Half-open Span(NamedTuple) arithmetic, interval subtraction and gap finding, piecewise mapping pipelines, 4D hypercuboid splitting, and coordinate compression in Python >=3.13."
main_img:
  name: "Interval and Range Algebra"
  link: /assets/images/pj_intervals_hero.png
tags:
  - name: Useful Algorithms
    link: /python/useful_algorithms
  - name: Sets
    link: /python/sets
  - name: Classes and Objects
    link: /python/classes
mathjax: true
---
## Page Contents

- [Why Range Algebra Beats Brute Force](#why-range-algebra-beats-brute-force)
- [Half-Open `[start, stop)` vs Inclusive `[lo, hi]`](#half-open-start-stop-vs-inclusive-lo-hi)
  - [Building a Reusable `Span` Toolkit](#building-a-reusable-span-toolkit)
- [1D Coverage, Subtraction and Gap Finding](#1d-coverage-subtraction-and-gap-finding)
- [Multi-Stage Piecewise Transformation Pipelines](#multi-stage-piecewise-transformation-pipelines)
- [N-Dimensional Hypercuboid Splitting](#n-dimensional-hypercuboid-splitting)
- [Coordinate Compression and Sparse Axis Scaling](#coordinate-compression-and-sparse-axis-scaling)
  - [3D Cuboid Compression](#3d-cuboid-compression)
  - [1D Empty-Row and Column Gap Inflation](#1d-empty-row-and-column-gap-inflation)
- [AoC Examples](#aoc-examples)

---

## Why Range Algebra Beats Brute Force

Part 1 lulls you into thinking everything is tiny. You are given a few hundred ingredient IDs or a neat little `[-50, 50]` bounding cube, so you chuck the integers into a Python `set`, take unions and differences, and collect your gold star in under a second.

Then Part 2 arrives. Suddenly those seed ranges span \( 10^{14} \) integers, or 3D reactor cuboids stretch across hundreds of thousands of units per axis. Try building an element-level `set` of \( 10^{14} \) coordinates and Python will politely ask for a few hundred terabytes of RAM before crashing out.

The mental shift is to **stop modelling individual elements and start doing arithmetic on boundary endpoints**. With \( R \) intervals, sorting and sweeping endpoints runs in \( O(R \log R) \) time and \( O(R) \) memory — completely indifferent to whether a range spans ten numbers or ten trillion!

If you just need basic sorting and coalescing of overlapping `[start, end]` pairs, start with `merge_intervals` in [Useful Algorithms](/python/useful_algorithms#merging-overlapping-intervals). Here we build a complete **half-open range algebra** toolkit for subtracting, splitting, shifting, and compressing multi-dimensional intervals.

---

## Half-Open `[start, stop)` vs Inclusive `[lo, hi]`

Advent of Code inputs almost always write ranges **inclusively** (`3-5`, `x=10..12`), meaning both endpoints belong to the range. Yet if you keep both endpoints inclusive inside your algebra code, off-by-one `+ 1` / `- 1` adjustments infest every single comparison:

| Operation | Inclusive `[lo, hi]` | Half-Open `[start, stop)` |
| :--- | :--- | :--- |
| **Element count** | `hi - lo + 1` | `stop - start` |
| **Empty interval** | `lo > hi` | `start >= stop` |
| **Overlap condition** | `max(lo1, lo2) <= min(hi1, hi2)` | `max(s1, s2) < min(e1, e2)` |
| **Touching / adjacent** | `hi1 + 1 == lo2` (easy to forget `+ 1`) | `e1 == s2` (endpoints match directly) |
| **Split at threshold `k`** | `[lo, k - 1]` and `[k, hi]` | `[start, k)` and `[k, stop)` |

Convert inclusive puzzle bounds `lo-hi` immediately at parse time into **half-open** `[lo, hi + 1)` intervals — matching Python's own `range(start, stop)` and slice syntax `seq[start:stop]` — and those fencepost bugs vanish overnight.

### Building a Reusable `Span` Toolkit

Subclassing `NamedTuple` gives us an immutable, hashable, zero-overhead two-integer interval with clean dot-notation methods:

```python
from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple


class Span(NamedTuple):
    """Half-open integer interval ``[start, stop)``."""

    start: int
    stop: int

    @classmethod
    def from_inclusive(cls, lo: int, hi: int) -> Span:
        """Convert an inclusive ``[lo, hi]`` range to half-open ``[lo, hi + 1)``."""
        return cls(lo, hi + 1)

    @property
    def length(self) -> int:
        """Return number of integers covered, or 0 if empty."""
        return max(0, self.stop - self.start)

    def overlaps(self, other: Span) -> bool:
        """Return True if the two half-open spans share at least one integer."""
        return max(self.start, other.start) < min(self.stop, other.stop)

    def intersect(self, other: Span) -> Span | None:
        """Return overlapping sub-span, or None when disjoint."""
        lo = max(self.start, other.start)
        hi = min(self.stop, other.stop)
        return Span(lo, hi) if lo < hi else None

    def subtract(self, other: Span) -> list[Span]:
        """Return 0, 1, or 2 sub-spans remaining after removing ``other``."""
        if not self.overlaps(other):
            return [self] if self.length > 0 else []

        pieces: list[Span] = []
        if self.start < other.start:
            pieces.append(Span(self.start, other.start))
        if other.stop < self.stop:
            pieces.append(Span(other.stop, self.stop))
        return pieces

    def shift(self, offset: int) -> Span:
        """Translate both endpoints by ``offset``."""
        return Span(self.start + offset, self.stop + offset)


def merge_spans(spans: Iterable[Span]) -> list[Span]:
    """Coalesce overlapping and touching half-open spans in ascending order."""
    ordered = sorted(s for s in spans if s.length > 0)
    if not ordered:
        return []

    merged: list[Span] = [ordered[0]]
    for cur in ordered[1:]:
        prev = merged[-1]
        if cur.start <= prev.stop:  # <= coalesces overlapping and adjacent spans
            merged[-1] = Span(prev.start, max(prev.stop, cur.stop))
        else:
            merged.append(cur)
    return merged


s1 = Span.from_inclusive(3, 5)
s2 = Span.from_inclusive(6, 8)
assert s1 == Span(3, 6)
assert s1.length == 3
assert not s1.overlaps(s2)
assert merge_spans([s1, s2]) == [Span(3, 9)]
assert Span(0, 10).subtract(Span(3, 7)) == [Span(0, 3), Span(7, 10)]
assert Span(2, 8).intersect(Span(5, 12)) == Span(5, 8)
```

Notice how `merge_spans` uses `cur.start <= prev.stop`: because `[3, 6)` and `[6, 9)` touch right at `6`, `<=` coalesces both overlapping and contiguous intervals in one pass.

---

## 1D Coverage, Subtraction and Gap Finding

Once you have `Span.subtract` and `merge_spans`, three classic AoC puzzle patterns fall over immediately:

- **[2016 Day 20 (Firewall Rules)](/2016/20)**: Subtract merged blacklist `Span`s from `[0, 2**32)` to reveal every allowed IP span — giving both the lowest valid IP (`allowed[0].start`) and the total allowed count (`sum(s.length for s in allowed)`).
- **[2022 Day 15 (Beacon Exclusion Zone)](/2022/15)**: For a candidate row `y`, each sensor at `(sx, sy)` with Manhattan radius `r` projects a horizontal slice `[sx - reach, sx + reach + 1)` where `reach = r - abs(sy - y)`. Merging those spans counts excluded positions on `y=2_000_000`, and finding a row where `merge_spans` inside `[0, 4_000_001)` leaves two spans pinpoints the lone hidden beacon at `merged[0].stop`!
- **[2025 Day 5 (Cafeteria)](/2025/5)**: Merge overlapping fresh-ingredient ID ranges spanning \( 10^{14}+ \) values and sum `s.length` in microseconds.

```python
from collections.abc import Iterable, Sequence

# Reuses Span and merge_spans defined above


def find_allowed_spans(blocked: Iterable[Span], bound: Span) -> list[Span]:
    """Return sorted uncovered sub-spans inside ``bound``."""
    if bound.length == 0:
        return []
    allowed: list[Span] = [bound]
    for block in merge_spans(blocked):
        if not allowed or block.start >= bound.stop:
            break
        allowed.extend(allowed.pop().subtract(block))
    return allowed


def find_beacon_gap(
    sensors: Sequence[tuple[int, int, int]],
    bound: Span,
) -> tuple[int, int] | None:
    """Locate the first uncovered ``(x, y)`` inside ``bound`` on each row."""
    for y in range(bound.start, bound.stop):
        covered: list[Span] = []
        for sx, sy, radius in sensors:
            reach = radius - abs(sy - y)
            if reach >= 0:
                lo = max(bound.start, sx - reach)
                hi = min(bound.stop, sx + reach + 1)
                if lo < hi:
                    covered.append(Span(lo, hi))
        merged = merge_spans(covered)
        if not merged or merged[0].start > bound.start:
            return (bound.start, y)
        if merged[0].stop < bound.stop:
            return (merged[0].stop, y)
    return None


blocked_sample = [
    Span.from_inclusive(5, 8),
    Span.from_inclusive(0, 2),
    Span.from_inclusive(4, 7),
]
allowed_sample = find_allowed_spans(blocked_sample, Span(0, 10))
assert allowed_sample == [Span(3, 4), Span(9, 10)]
assert allowed_sample[0].start == 3
assert sum(s.length for s in allowed_sample) == 2
assert find_allowed_spans(blocked_sample, Span(5, 5)) == []

sample_sensors_raw = [
    (2, 18, -2, 15), (9, 16, 10, 16), (13, 2, 15, 3), (12, 14, 10, 16),
    (10, 20, 10, 16), (14, 17, 10, 16), (8, 7, 2, 10), (2, 0, 2, 10),
    (0, 11, 2, 10), (20, 14, 25, 17), (17, 20, 21, 22), (16, 7, 15, 3),
    (14, 3, 15, 3), (20, 1, 15, 3),
]
sample_sensors = [
    (sx, sy, abs(sx - bx) + abs(sy - by))
    for sx, sy, bx, by in sample_sensors_raw
]
assert find_beacon_gap(sample_sensors, Span(0, 21)) == (14, 11)
assert find_beacon_gap([], Span(0, 5)) == (0, 0)
```

---

## Multi-Stage Piecewise Transformation Pipelines

Now for a classic interval headache: **2023 Day 5** (*If You Give A Seed A Fertilizer*, in [AoC 2023](/2023/) — see [the 2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}). Part 1 pushes individual seed IDs through seven mapping tables (`seed -> soil -> ... -> location`). Part 2 turns those numbers into `(start, length)` pairs covering hundreds of millions of seeds!

Instead of pushing individual IDs, push entire `Span`s through each mapping stage. Whenever an input `Span` meets a rule `(src_start, src_stop, offset)`, it slices cleanly into at most three half-open pieces:

1. **Before**: `[span.start, min(span.stop, src_start))` — untouched by this rule; stays in `remaining` to be tested against later rules in the **same** stage.
2. **Overlap + Shift**: `[max(span.start, src_start), min(span.stop, src_stop))` shifted by `+offset` — mapped! Crucially, move this straight into `mapped` so **no subsequent rule in the same stage can double-shift it**.
3. **After**: `[max(span.start, src_stop), span.stop)` — untouched by this rule; stays in `remaining` for later rules in the same stage.

![Splitting an input interval through a rule window into Before, Shifted, and After segments](/assets/images/pj_interval_pipeline_diagram.png){: .no-mat}

Whatever remains unmapped after checking every rule in the stage passes straight through unchanged (`offset = 0`) into `mapped + remaining`:

```python
from collections.abc import Sequence
from typing import NamedTuple

# Reuses Span and merge_spans defined above


class MapRule(NamedTuple):
    """Piecewise shift rule applying ``offset`` across ``[src_start, src_stop)``."""

    src_start: int
    src_stop: int
    offset: int


def apply_stage(spans: list[Span], rules: Sequence[MapRule]) -> list[Span]:
    """Propagate ``spans`` through one mapping stage without double-shifting."""
    mapped: list[Span] = []
    remaining = list(spans)

    for src_start, src_stop, offset in rules:
        next_remaining: list[Span] = []
        for span in remaining:
            before = Span(span.start, min(span.stop, src_start))
            overlap = Span(max(span.start, src_start), min(span.stop, src_stop))
            after = Span(max(span.start, src_stop), span.stop)

            if before.length > 0:
                next_remaining.append(before)
            if overlap.length > 0:
                mapped.append(overlap.shift(offset))
            if after.length > 0:
                next_remaining.append(after)
        remaining = next_remaining

    return merge_spans(mapped + remaining)


seed_spans = [Span(79, 79 + 14), Span(55, 55 + 13)]
almanac_stages = [
    [MapRule(98, 100, 50 - 98), MapRule(50, 98, 52 - 50)],
    [MapRule(15, 52, 0 - 15), MapRule(52, 54, 37 - 52), MapRule(0, 15, 39 - 0)],
    [MapRule(53, 61, 49 - 53), MapRule(11, 53, 0 - 11), MapRule(0, 7, 42 - 0), MapRule(7, 11, 57 - 7)],
    [MapRule(18, 25, 88 - 18), MapRule(25, 95, 18 - 25)],
    [MapRule(77, 100, 45 - 77), MapRule(45, 64, 81 - 45), MapRule(64, 77, 68 - 64)],
    [MapRule(69, 70, 0 - 69), MapRule(0, 69, 1 - 0)],
    [MapRule(56, 93, 60 - 56), MapRule(93, 97, 56 - 93)],
]
cur = seed_spans
for stage in almanac_stages:
    cur = apply_stage(cur, stage)
assert cur[0].start == 46
```

Look how clean that three-way slice is: no tangled `if/elif` overlap cases — `before`, `overlap`, and `after` handle disjoint, contained, straddling, and full-cover intervals with the exact same three lines of arithmetic.

---

## N-Dimensional Hypercuboid Splitting

What if instead of shifting 1D intervals linearly, your rules branch across **multiple independent dimensions**?

In **2023 Day 19** (*Aplenty*, in [AoC 2023](/2023/) — see [the 2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}), Part 2 asks how many distinct `(x, m, a, s)` combinations in `1..4000` reach Accepted (`A`). That is \( 4000^4 = 2.56 \times 10^{14} \) points — impossible to test one by one!

Instead, push a **4D hypercuboid** `Box` (`type Box = dict[str, Span]`) starting with `Span(1, 4001)` on every axis through the workflow decision tree. Whenever a rule compares a single axis (`a < 2006` or `m > 2090`), split only that axis into its `True` (matching) and `False` (remainder) sub-spans:

![Branching range conditions split intervals into True and False sub-ranges](/assets/images/2019_range_splitting.png)

- Send a copy of the box with the `True` sub-span down the target workflow (`cur_box | {cat: yes_span}`).
- Narrow the current box to the `False` sub-span (`cur_box | {cat: no_span}`) and continue to the next rule in the current workflow.
- Whenever a box hits `"A"`, its distinct integer points equal the product of its axis lengths via `math.prod(s.length for s in box.values())`. Because every conditional split partitions the box disjointly, no combination is ever double-counted!

```python
import math

# Reuses Span defined above

type Box = dict[str, Span]
type Rule = tuple[str | None, str | None, int | None, str]


def split_span(span: Span, op: str, threshold: int) -> tuple[Span, Span]:
    """Split ``span`` into ``(matching, non_matching)`` sub-spans."""
    if op == "<":
        return (
            Span(span.start, min(span.stop, threshold)),
            Span(max(span.start, threshold), span.stop),
        )
    if op == ">":
        return (
            Span(max(span.start, threshold + 1), span.stop),
            Span(span.start, min(span.stop, threshold + 1)),
        )
    raise ValueError(f"Unsupported comparison operator: {op!r}")


def count_accepted_boxes(workflows: dict[str, list[Rule]]) -> int:
    """Count distinct 4D points accepted by branching workflow rules."""

    def walk(name: str, box: Box) -> int:
        if name == "R":
            return 0
        if name == "A":
            return math.prod(s.length for s in box.values())

        total = 0
        cur_box = box
        for cat, op, threshold, target in workflows[name]:
            if cat is None or op is None or threshold is None:
                total += walk(target, cur_box)
                break

            yes_span, no_span = split_span(cur_box[cat], op, threshold)
            if yes_span.length > 0:
                total += walk(target, cur_box | {cat: yes_span})
            if no_span.length == 0:
                break
            cur_box = cur_box | {cat: no_span}
        return total

    initial_box: Box = {axis: Span.from_inclusive(1, 4000) for axis in "xmas"}
    return walk("in", initial_box)


sample_wf_text = """px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}"""

parsed_wf: dict[str, list[Rule]] = {}
for line in sample_wf_text.splitlines():
    name, body = line[:-1].split("{")
    rules_list: list[Rule] = []
    for token in body.split(","):
        if ":" in token:
            cond, target = token.split(":")
            rules_list.append((cond[0], cond[1], int(cond[2:]), target))
        else:
            rules_list.append((None, None, None, token))
    parsed_wf[name] = rules_list

assert count_accepted_boxes(parsed_wf) == 167409079868000
```

---

## Coordinate Compression and Sparse Axis Scaling

### 3D Cuboid Compression

In **[2021 Day 22 (Reactor Reboot)](/2021/22)**, hundreds of `on` and `off` 3D cuboids overlap across vast coordinate ranges (`[-100_000, 100_000]` on each axis). Even though huge spans of empty or uniform space exist between cuboid edges, storing individual `(x, y, z)` points is hopeless.

The cure is **Coordinate Compression**:

1. Collect every half-open boundary endpoint (`start` and `stop`) from every instruction along each axis, sort them, and deduplicate (`x_0 < x_1 < ...`).
2. Those \( M \) unique boundary coordinates partition space into \( M - 1 \) non-uniform intervals `[xs[i], xs[i + 1])` — **nothing ever changes partway inside a single cell**!
3. Map each instruction's bounds onto compact dense grid indices via `bisect.bisect_left` and toggle voxels `(i, j, k)` inside a dense `bytearray`.
4. Sum the real physical volume of every active compressed voxel:

$$
V = \sum_{(i, j, k) \in \text{on}} (x_{i+1} - x_i) \cdot (y_{j+1} - y_j) \cdot (z_{k+1} - z_k)
$$

![2D coordinate compression collapsing sparse coordinates onto non-uniform grid cells](/assets/images/2d-reactor-compression.png)

Using a flat `bytearray` with slice assignment (`active[base + iz0 : base + iz1] = ...`) keeps memory compact and finishes dramatically faster than inserting millions of tuples into a Python `set`:

```python
from bisect import bisect_left
from collections.abc import Sequence
from typing import NamedTuple

# Reuses Span defined above


class CuboidStep(NamedTuple):
    """Reactor instruction toggling a 3D half-open cuboid ``on`` or ``off``."""

    on: bool
    x: Span
    y: Span
    z: Span


def count_active_voxels(steps: Sequence[CuboidStep]) -> int:
    """Count total active unit cubes via 3D coordinate compression."""
    valid_steps = [s for s in steps if s.x.length > 0 and s.y.length > 0 and s.z.length > 0]
    if not valid_steps:
        return 0
    xs = sorted({coord for step in valid_steps for coord in (step.x.start, step.x.stop)})
    ys = sorted({coord for step in valid_steps for coord in (step.y.start, step.y.stop)})
    zs = sorted({coord for step in valid_steps for coord in (step.z.start, step.z.stop)})

    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    active = bytearray(nx * ny * nz)

    for on, sx, sy, sz in valid_steps:
        ix0, ix1 = bisect_left(xs, sx.start), bisect_left(xs, sx.stop)
        iy0, iy1 = bisect_left(ys, sy.start), bisect_left(ys, sy.stop)
        iz0, iz1 = bisect_left(zs, sz.start), bisect_left(zs, sz.stop)
        val = 1 if on else 0
        for ix in range(ix0, ix1):
            base_x = ix * ny * nz
            for iy in range(iy0, iy1):
                base = base_x + iy * nz
                active[base + iz0 : base + iz1] = bytes([val]) * (iz1 - iz0)

    total = 0
    for ix in range(nx):
        dx = xs[ix + 1] - xs[ix]
        base_x = ix * ny * nz
        for iy in range(ny):
            dxy = dx * (ys[iy + 1] - ys[iy])
            base = base_x + iy * nz
            for iz in range(nz):
                if active[base + iz]:
                    total += dxy * (zs[iz + 1] - zs[iz])
    return total


mini_cuboids = [
    CuboidStep(True, Span.from_inclusive(10, 12), Span.from_inclusive(10, 12), Span.from_inclusive(10, 12)),
    CuboidStep(True, Span.from_inclusive(11, 13), Span.from_inclusive(11, 13), Span.from_inclusive(11, 13)),
    CuboidStep(False, Span.from_inclusive(9, 11), Span.from_inclusive(9, 11), Span.from_inclusive(9, 11)),
    CuboidStep(True, Span.from_inclusive(10, 10), Span.from_inclusive(10, 10), Span.from_inclusive(10, 10)),
]
assert count_active_voxels(mini_cuboids) == 39
assert count_active_voxels([]) == 0
```

### 1D Empty-Row and Column Gap Inflation

The exact same sparse-axis idea works in reverse when a puzzle asks you to *expand* empty space by a million rows or columns, as in **2023 Day 11** (*Cosmic Expansion*, in [AoC 2023](/2023/) — see [the 2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}).

Never allocate a million empty strings! Instead, build a 1D prefix-sum coordinate table along rows and columns where occupied lines advance by `1` and empty lines advance by `expansion`. Computing the expanded Manhattan distance between any pair of galaxies becomes two \( O(1) \) array lookups:

```python
from collections.abc import Sequence


def expanded_galaxy_distances(grid: Sequence[str], expansion: int) -> int:
    """Sum pairwise Manhattan distances with empty rows/cols scaled to ``expansion``."""
    row_coords: list[int] = [0]
    for row in grid:
        step = expansion if "#" not in row else 1
        row_coords.append(row_coords[-1] + step)

    col_coords: list[int] = [0]
    for col in zip(*grid):
        step = expansion if "#" not in col else 1
        col_coords.append(col_coords[-1] + step)

    galaxies = [
        (col_coords[c], row_coords[r])
        for r, row in enumerate(grid)
        for c, ch in enumerate(row)
        if ch == "#"
    ]
    return sum(
        abs(ax - bx) + abs(ay - by)
        for i, (ax, ay) in enumerate(galaxies)
        for bx, by in galaxies[i + 1 :]
    )


galaxy_sample = [
    "...#......",
    ".......#..",
    "#.........",
    "..........",
    "......#...",
    ".#........",
    ".........#",
    "..........",
    ".......#..",
    "#...#.....",
]
assert expanded_galaxy_distances(galaxy_sample, expansion=2) == 374
assert expanded_galaxy_distances(galaxy_sample, expansion=100) == 8410
```

---

## AoC Examples

| Puzzle | Interval / Range Technique | Solution Link |
| :--- | :--- | :--- |
| **2016 Day 20 — Firewall Rules** | Bounded 1D interval subtraction and gap counting | [2016 Day 20](/2016/20) |
| **2021 Day 22 — Reactor Reboot** | 3D coordinate compression onto non-uniform voxel grids | [2021 Day 22](/2021/22) |
| **2022 Day 15 — Beacon Exclusion Zone** | Row-slice interval projection, merging, and gap detection | [2022 Day 15](/2022/15) |
| **2023 Day 5 — If You Give A Seed A Fertilizer** | Multi-stage piecewise interval slicing (`Before` / `Shifted` / `After`) | [AoC 2023](/2023/) · [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2023 Day 11 — Cosmic Expansion** | 1D prefix-sum sparse coordinate scaling for empty rows/columns | [AoC 2023](/2023/) · [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2023 Day 19 — Aplenty** | Recursive 4D hypercuboid splitting across workflow predicates | [AoC 2023](/2023/) · [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2025 Day 5 — Cafeteria** | Merging huge overlapping 1D fresh-ingredient ID ranges | [2025 Day 5](/2025/5) |
