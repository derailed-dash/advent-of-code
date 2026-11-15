---
title: Grid Geometry — Shoelace Formula and Pick's Theorem
description: "Computational geometry in Python >=3.13 for huge Advent of Code grids — integer Shoelace area, Pick's Theorem, scanline parity, sparse odd-even ray casting, corner-counting for polygon sides, and 45-degree Manhattan rotation."
main_img:
  name: "Grid Geometry — Shoelace Formula and Pick's Theorem"
  link: /assets/images/pj_geometry_hero.png
tags:
  - name: Reusable Code
    link: /python/reusable_code
  - name: Useful Algorithms
    link: /python/useful_algorithms
  - name: Complex Numbers
    link: /python/complex
  - name: Visualisation
    link: /python/visualisation
mathjax: true
---

## Page Contents

- [When Grid Flood-Fill Breaks](#when-grid-flood-fill-breaks)
- [Unit Squares vs Lattice Vertices](#unit-squares-vs-lattice-vertices)
- [The Shoelace Formula and Pick's Theorem](#the-shoelace-formula-and-picks-theorem)
- [Point-in-Polygon Scanlines, Ray Casting, and Inscribed Rectangles](#point-in-polygon-scanlines-ray-casting-and-inscribed-rectangles)
  - [Scanline Parity Flipping](#scanline-parity-flipping)
  - [Sparse Ray Casting and Inscribed Rectangles](#sparse-ray-casting-and-inscribed-rectangles)
- [Sides Equal Corners and Manhattan Diamond Geometry](#sides-equal-corners-and-manhattan-diamond-geometry)
  - [Counting Polygon Sides via 2x2 Corners](#counting-polygon-sides-via-2x2-corners)
  - [Manhattan Voronoi Regions and 45-Degree Chebyshev Rotation](#manhattan-voronoi-regions-and-45-degree-chebyshev-rotation)
- [AoC Examples](#aoc-examples)

---

## When Grid Flood-Fill Breaks

In Part 1 of an Advent of Code grid puzzle, a `set` of coordinates and a quick `collections.deque` flood-fill feels effortless. Trace a loop of a few hundred tiles, flood-fill the interior or exterior, call `len()`, grab your star, and move on.

Then Part 2 scales the coordinates up by six orders of magnitude:

- In `2023 Day 18` (*Lavaduct Lagoon*), the real dig distances come from six-digit hex values. Even the sample lagoon holds **952,408,144,115** cubic metres of lava — nearly a *trillion* tiles.
- In [2025 Day 9 (*Movie Theater*)](/2025/9), red tiles sit on a `100_000 x 100_000` tiled floor (`10**10` cells), yet there are only a few hundred corner vertices.

Trying to allocate a `10**12`-tile `Grid` or `set[Point]` will swallow every byte of RAM on your machine before you have even finished walking the first trench!

The insight that makes these problems collapse to milliseconds is **switching from cells to vertices and edges**. Instead of filling every individual square inside a polygon, represent the shape solely by its \(V\) boundary corners and evaluate area, containment, sides, and distances directly in \(O(V)\) or \(O(V^2)\) integer arithmetic.

---

## Unit Squares vs Lattice Vertices

Before jumping into the Shoelace formula, there is a subtle coordinate mismatch that catches almost everyone the first time they apply polygon maths to a discrete grid puzzle.

Suppose a digger carves a `7 x 6` rectangular trench of `1 x 1` unit squares: `R 6`, `D 5`, `L 6`, `U 5`. How many total tiles are excavated (trench + interior)? Obviously `7 * 6 = 42`.

Now pass the centre coordinates `(0, 0) -> (6, 0) -> (6, 5) -> (0, 5)` straight into the Shoelace formula. What area does it return? **`30`** (`6 * 5`), not `42`!

![Unit squares centred on lattice points along the 2023 Day 18 sample lagoon](/assets/images/lava_lagoon_1-by-1_squares.png)

Why are 12 tiles missing from that `7 x 6` rectangle? Look at how each `1 x 1` grid cell sits **centred** on its lattice point (illustrated above on the `2023 Day 18` sample lagoon), straddling the mathematical polygon boundary:

- Along every straight edge, **half** of each `1 x 1` perimeter cell sticks outside the centreline polygon.
- At convex outer corners, **three-quarters** of the corner cell sticks outside; at concave inner bends, only **one-quarter** sticks outside.
- Around any closed loop, four more convex bends occur than concave ones — contributing four extra quarter-tiles (`+ 1` whole tile!).

Rather than manually pushing every vertex outward by `0.5` units depending on turn direction, keep your clean integer centrelines and combine **Shoelace** with **Pick's Theorem** to recover the missing `b // 2 + 1` perimeter contribution in exact integer maths.

---

## The Shoelace Formula and Pick's Theorem

![Exact Pick's Theorem lattice diagram showing A = 14, b = 18 boundary dots, and i = 6 interior dots](/assets/images/pj_shoelace_picks_diagram.png){: .no-mat}

Given a simple closed polygon with \(n\) integer vertices \((x_0, y_0), (x_1, y_1), \dots, (x_{n-1}, y_{n-1})\) in clockwise or anti-clockwise order (with \((x_n, y_n) = (x_0, y_0)\)), the **Shoelace Formula** calculates twice the geometric area as an exact integer:

$$2A = \left| \sum_{k=0}^{n-1} \left( x_k y_{k+1} - x_{k+1} y_k \right) \right|$$

Keeping `twice_area` as a pure Python `int` right up until the final `// 2` avoids floating-point precision loss when coordinates reach \(10^{12}\) or higher.

Next, **Pick's Theorem** connects that geometric area \(A\) to the number of integer lattice points strictly **inside** the polygon (\(i\)) and **on** its boundary (\(b\)):

$$A = i + \frac{b}{2} - 1$$

Look at the L-shaped lattice diagram above to see Pick's Theorem in action:

- Geometric area: \(A = 14\) (`twice_area = 28`)
- Boundary lattice points: \(b = 18\)
- Interior lattice points: \(i = 6\), satisfying \(6 + \frac{18}{2} - 1 = 14\)

Rearranging Pick's equation gives us both AoC answers directly in integer arithmetic:

- **Strictly interior lattice cells**: `(twice_area - boundary_points) // 2 + 1`
- **Inclusive cells (trench + interior, as in `2023 Day 18`)**: `interior + boundary = (twice_area + boundary_points) // 2 + 1`

Using `itertools.pairwise` and `math.gcd` (which works even for diagonal integer steps, and equals the Manhattan step length along axis-aligned edges), the whole toolkit takes 15 lines of stdlib Python:

```python
import math
from collections.abc import Sequence
from itertools import pairwise


def shoelace_twice_area(vertices: Sequence[tuple[int, int]]) -> int:
    """Return twice the polygon area as an exact integer using itertools.pairwise."""
    if len(vertices) < 3:
        return 0
    closed = [*vertices, vertices[0]]
    cross_sum = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pairwise(closed))
    return abs(cross_sum)


def boundary_lattice_points(vertices: Sequence[tuple[int, int]]) -> int:
    """Count integer lattice points lying on all edges of a lattice polygon."""
    if len(vertices) < 2:
        return len(vertices)
    if len(vertices) == 2:
        (x1, y1), (x2, y2) = vertices
        return math.gcd(abs(x2 - x1), abs(y2 - y1)) + 1
    closed = [*vertices, vertices[0]]
    return sum(math.gcd(abs(x2 - x1), abs(y2 - y1)) for (x1, y1), (x2, y2) in pairwise(closed))


def pick_lattice_counts(vertices: Sequence[tuple[int, int]]) -> tuple[int, int, int]:
    """Return ``(area, interior_points, inclusive_points)`` via Shoelace and Pick's Theorem."""
    twice_area = shoelace_twice_area(vertices)
    if len(vertices) < 3 or twice_area == 0:
        raise ValueError("Pick's Theorem requires a non-degenerate simple polygon (>= 3 vertices)")
    boundary = boundary_lattice_points(vertices)
    interior = (twice_area - boundary) // 2 + 1
    inclusive = (twice_area + boundary) // 2 + 1
    return twice_area // 2, interior, inclusive


# Verify directly against the diagram L-polygon: A = 14, b = 18, i = 6
l_polygon = [(0, 0), (5, 0), (5, 2), (2, 2), (2, 4), (0, 4)]
assert boundary_lattice_points(l_polygon) == 18
assert pick_lattice_counts(l_polygon) == (14, 6, 24)
```

Applied to the public `2023 Day 18` sample dig plan in [`/2023/`](/2023/) (see the [2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}), tracking `boundary += dist` as we trace the orthogonal vertices verifies both Part 1 (`62` cells) and the massive Part 2 hex plan (`952_408_144_115` cells) in microseconds:

```python
from itertools import pairwise


def lagoon_volume(steps: list[tuple[str, int]]) -> int:
    """Compute inclusive 1x1 cell volume directly from orthogonal dig steps."""
    dirs = {"R": (1, 0), "D": (0, 1), "L": (-1, 0), "U": (0, -1)}
    x = y = boundary = 0
    vertices: list[tuple[int, int]] = [(0, 0)]
    for direction, dist in steps:
        dx, dy = dirs[direction]
        x += dx * dist
        y += dy * dist
        boundary += dist
        vertices.append((x, y))

    twice_area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pairwise(vertices)))
    return (twice_area + boundary) // 2 + 1


dig_sample = [
    ("R", 6, "#70c710"), ("D", 5, "#0dc571"), ("L", 2, "#5713f0"), ("D", 2, "#d2c081"),
    ("R", 2, "#59c680"), ("D", 2, "#411b91"), ("L", 5, "#8ceee2"), ("U", 2, "#caa173"),
    ("L", 1, "#1b58a2"), ("U", 2, "#caa171"), ("R", 2, "#7807d2"), ("U", 3, "#a77fa3"),
    ("L", 2, "#015232"), ("U", 2, "#7a21e3"),
]
hex_dirs = {"0": "R", "1": "D", "2": "L", "3": "U"}

assert lagoon_volume([(d, n) for d, n, _ in dig_sample]) == 62
assert lagoon_volume([(hex_dirs[h[-1]], int(h[1:-1], 16)) for _, _, h in dig_sample]) == 952408144115
```

---

## Point-in-Polygon Scanlines, Ray Casting, and Inscribed Rectangles

Sometimes you don't just need the *count* of enclosed tiles — you need to ask **which specific tiles** or **which candidate rectangles** lie inside a winding, non-convex loop.

![Contained interior grid cells inside a closed orthogonal loop](/assets/images/contained_points.png)

### Scanline Parity Flipping

In `2023 Day 10` (*Pipe Maze*, [`/2023/`](/2023/)), pipes can run shoulder-to-shoulder (`||`) without leaving an open grid cell between them — yet the space between them still connects to the outside! Naive grid flood-fill treats `||` as an impenetrable wall unless you double the grid resolution first.

**Scanline parity** solves this on the original grid in a single \(O(H \cdot W)\) pass. Walk left-to-right across each row maintaining an `inside = False` toggle:

- Every vertical wall `|` crosses the scanline once and flips `inside = not inside`.
- Horizontal pipe segments `-` never flip parity.
- **How bends pair up**: imagine shifting your horizontal ray a fraction of a tile *north* of the row centreline (`y - 0.5`). Only pipe tiles with an arm pointing **north** (`|`, `L`, `J`) cross that shifted ray!
  - `L---7` crosses at `L` and misses `7` (1 crossing -> **flips parity**).
  - `F---J` misses `F` and crosses at `J` (1 crossing -> **flips parity**).
  - `L---J` crosses both `L` and `J` (2 crossings -> **tangent U-turn, parity unchanged**).
  - `F---7` misses both (0 crossings -> **tangent U-turn, parity unchanged**).

Once you replace the starting `S` marker with its real pipe symbol, the entire parity rule collapses to `ch in {"|", "L", "J"}`:

```python
from collections.abc import Sequence


def count_enclosed_scanline(grid_lines: Sequence[str], loop_coords: set[tuple[int, int]]) -> int:
    """Count non-loop tiles enclosed by an orthogonal pipe loop via scanline parity."""
    enclosed = 0
    for y, row in enumerate(grid_lines):
        inside = False
        for x, ch in enumerate(row):
            if (x, y) in loop_coords:
                if ch == "S":
                    raise ValueError("Replace 'S' with its inferred pipe symbol first")
                # Shifting the scanline slightly north crosses '|', 'L', and 'J' once each.
                if ch in {"|", "L", "J"}:
                    inside = not inside
            elif inside:
                enclosed += 1
    return enclosed


pipe_sample = [
    "...........",
    ".F-------7.",
    ".|F-----7|.",
    ".||.....||.",
    ".||.....||.",
    ".|L-7.F-J|.",
    ".|..|.|..|.",
    ".L--J.L--J.",
    "...........",
]
loop_tiles = {(x, y) for y, row in enumerate(pipe_sample) for x, ch in enumerate(row) if ch != "."}
assert count_enclosed_scanline(pipe_sample, loop_tiles) == 4
```

*(Note the important lookup optimisation Dazbo spotted in his notebook: keep `loop_coords` as a `set`, never a `list` — checking `(x, y) in loop_coords` inside the inner loop drops runtime from minutes to milliseconds.)*

### Sparse Ray Casting and Inscribed Rectangles

Now scale up again to [2025 Day 9 (*Movie Theater*)](/2025/9) ([`d09.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d09/d09.py){:target="_blank"}). The polygon vertices span a `100_000 x 100_000` floor, so a row-by-row scanline over every cell is out of the question.

Instead, store only the polygon's **vertical and horizontal edges** and apply two geometric checks for any candidate rectangle spanned by opposite corners `p1` and `p2`:

1. **Odd-even ray casting (`is_point_inside`)**: Cast a horizontal ray right from an interior sample point `(r_min_x + 0.5, r_min_y + 0.5)` and count crossings against vertical edges `(vx, y_min, y_max)` satisfying `vx > px` and `y_min <= py < y_max`. Using half-open intervals `[y_min, y_max)` avoids double-counting shared corners, and adding `+ 0.5` keeps the probe strictly off integer edges.
2. **Edge-intersection clearance (`rect_strictly_inside_polygon`)**: A non-convex polygon can have dents — a rectangle's test point might lie inside while a concave bay slices right across the rectangle! Checking that **no polygon edge passes strictly inside** `(r_min_x, r_max_x) x (r_min_y, r_max_y)` guarantees the whole rectangle stays inside.

```python
from collections.abc import Sequence
from itertools import combinations, pairwise
from typing import NamedTuple


class Vertex(NamedTuple):
    """Immutable 2D integer vertex."""

    x: int
    y: int


type VerticalEdge = tuple[int, int, int]    # (x, y_min, y_max)
type HorizontalEdge = tuple[int, int, int]  # (x_min, x_max, y)


def extract_orthogonal_edges(
    vertices: Sequence[Vertex],
) -> tuple[list[VerticalEdge], list[HorizontalEdge]]:
    """Split an orthogonal vertex loop into vertical and horizontal axis-aligned edges."""
    vertical: list[VerticalEdge] = []
    horizontal: list[HorizontalEdge] = []
    for p1, p2 in pairwise([*vertices, vertices[0]]):
        if p1.x == p2.x:
            vertical.append((p1.x, min(p1.y, p2.y), max(p1.y, p2.y)))
        elif p1.y == p2.y:
            horizontal.append((min(p1.x, p2.x), max(p1.x, p2.x), p1.y))
        else:
            raise ValueError(f"Non-orthogonal segment from {p1} to {p2}")
    return vertical, horizontal


def is_point_inside(
    px: float,
    py: float,
    vertical_edges: Sequence[VerticalEdge],
) -> bool:
    """Return True if ``(px, py)`` lies inside the polygon using horizontal odd-even ray casting."""
    crossings = 0
    for vx, y_min, y_max in vertical_edges:
        if vx > px and y_min <= py < y_max:
            crossings += 1
    return crossings % 2 == 1


def _point_in_or_on(
    px: float,
    py: float,
    vertical_edges: Sequence[VerticalEdge],
    horizontal_edges: Sequence[HorizontalEdge],
) -> bool:
    """Return True if ``(px, py)`` lies on a boundary edge or strictly inside the polygon."""
    on_edge = any(vx == px and vy1 <= py <= vy2 for vx, vy1, vy2 in vertical_edges) or any(
        hy == py and hx1 <= px <= hx2 for hx1, hx2, hy in horizontal_edges
    )
    return on_edge or is_point_inside(px, py, vertical_edges)


def rect_strictly_inside_polygon(
    p1: Vertex,
    p2: Vertex,
    vertical_edges: Sequence[VerticalEdge],
    horizontal_edges: Sequence[HorizontalEdge],
) -> bool:
    """Return True when the rectangle bounded by ``p1`` and ``p2`` stays inside the polygon."""
    r_min_x, r_max_x = min(p1.x, p2.x), max(p1.x, p2.x)
    r_min_y, r_max_y = min(p1.y, p2.y), max(p1.y, p2.y)

    if r_min_y == r_max_y:
        # Degenerate horizontal strip: split at crossing vertical edges and test all segments.
        xs = sorted({
            r_min_x,
            r_max_x,
            *(vx for vx, vy1, vy2 in vertical_edges if r_min_x < vx < r_max_x and vy1 <= r_min_y <= vy2),
        })
        return all(_point_in_or_on(float(x), float(r_min_y), vertical_edges, horizontal_edges) for x in xs) and all(
            _point_in_or_on((x1 + x2) / 2, float(r_min_y), vertical_edges, horizontal_edges)
            for x1, x2 in pairwise(xs)
        )

    if r_min_x == r_max_x:
        # Degenerate vertical strip: split at crossing horizontal edges and test all segments.
        ys = sorted({
            r_min_y,
            r_max_y,
            *(hy for hx1, hx2, hy in horizontal_edges if r_min_y < hy < r_max_y and hx1 <= r_min_x <= hx2),
        })
        return all(_point_in_or_on(float(r_min_x), float(y), vertical_edges, horizontal_edges) for y in ys) and all(
            _point_in_or_on(float(r_min_x), (y1 + y2) / 2, vertical_edges, horizontal_edges)
            for y1, y2 in pairwise(ys)
        )

    if not is_point_inside(r_min_x + 0.5, r_min_y + 0.5, vertical_edges):
        return False

    # Reject if any polygon boundary cuts through the rectangle's strict interior.
    for vx, vy_min, vy_max in vertical_edges:
        if r_min_x < vx < r_max_x and max(vy_min, r_min_y) < min(vy_max, r_max_y):
            return False
    for hx_min, hx_max, hy in horizontal_edges:
        if r_min_y < hy < r_max_y and max(hx_min, r_min_x) < min(hx_max, r_max_x):
            return False

    return True


red_tiles = [
    Vertex(7, 1), Vertex(11, 1), Vertex(11, 7), Vertex(9, 7),
    Vertex(9, 5), Vertex(2, 5), Vertex(2, 3), Vertex(7, 3),
]
v_edges, h_edges = extract_orthogonal_edges(red_tiles)
max_area = max(
    (abs(a.x - b.x) + 1) * (abs(a.y - b.y) + 1)
    for a, b in combinations(red_tiles, 2)
    if rect_strictly_inside_polygon(a, b, v_edges, h_edges)
)
assert max_area == 24

# Degenerate 1-tile strip across a U-shaped concavity must be rejected
u_poly = [
    Vertex(0, 0), Vertex(10, 0), Vertex(10, 6), Vertex(9, 6),
    Vertex(9, 2), Vertex(7, 2), Vertex(7, 6), Vertex(0, 6),
]
u_v, u_h = extract_orthogonal_edges(u_poly)
assert not rect_strictly_inside_polygon(Vertex(0, 6), Vertex(10, 6), u_v, u_h)
assert rect_strictly_inside_polygon(Vertex(0, 6), Vertex(7, 6), u_v, u_h)
```

---

## Sides Equal Corners and Manhattan Diamond Geometry

Two final geometric identities show up again and again across Advent of Code — turning fiddly edge-tracing into tiny, elegant functions.

### Counting Polygon Sides via 2x2 Corners

In `2024 Day 12` (*Garden Groups*, [`/2024/`](/2024/)), Part 2 prices each connected crop region by `area * number_of_sides`, where an entire straight fence run counts as one side.

My first working solution tracked four directional perimeter sets (`N`, `E`, `S`, `W`) and ran a separate BFS flood-fill inside each set to count contiguous straight edges. It works, sure — until you step back and remember a fundamental property of closed polygons:

> **Every closed polygon (including regions with internal holes!) has the exact same number of straight sides as it has corners.**

And you can count every corner of a 4-connected `region: set[tuple[int, int]]` locally around each cell `(x, y)` by checking its four `2 x 2` corner triplets `(orthogonal_1, orthogonal_2, diagonal)`:

- **Outer (convex) corner**: Neither `orthogonal_1` nor `orthogonal_2` belongs to `region`. (For a single isolated `1 x 1` plot, all four corners trigger — giving `4` sides automatically.)
- **Inner (concave) corner**: Both `orthogonal_1` and `orthogonal_2` belong to `region`, **but** the `diagonal` cell between them does not!

```python
from collections import deque

_CORNER_OFFSETS: tuple[tuple[tuple[int, int], tuple[int, int], tuple[int, int]], ...] = (
    ((0, -1), (-1, 0), (-1, -1)),  # North-West
    ((0, -1), (1, 0), (1, -1)),    # North-East
    ((0, 1), (-1, 0), (-1, 1)),    # South-West
    ((0, 1), (1, 0), (1, 1)),      # South-East
)


def count_polygon_corners(region: set[tuple[int, int]]) -> int:
    """Count straight polygon sides of a 4-connected grid region via 2x2 corners."""
    corners = 0
    for x, y in region:
        for (dx1, dy1), (dx2, dy2), (dxd, dyd) in _CORNER_OFFSETS:
            in_n1 = (x + dx1, y + dy1) in region
            in_n2 = (x + dx2, y + dy2) in region
            in_diag = (x + dxd, y + dyd) in region
            if (not in_n1 and not in_n2) or (in_n1 and in_n2 and not in_diag):
                corners += 1
    return corners


# Verify on the 2024 Day 12 10x10 sample map -> 1206
garden_sample = [
    "RRRRIICCFF", "RRRRIICCCF", "VVRRRCCFFF", "VVRCCCJFFF", "VVVVCJJCFE",
    "VVIVCCJJEE", "VVIIICJJEE", "MIIIIIJJEE", "MIIISIJEEE", "MMMISSJEEE",
]
rows, cols = len(garden_sample), len(garden_sample[0])
visited: set[tuple[int, int]] = set()
bulk_price = 0

for y in range(rows):
    for x in range(cols):
        if (x, y) in visited:
            continue
        crop = garden_sample[y][x]
        region: set[tuple[int, int]] = {(x, y)}
        queue: deque[tuple[int, int]] = deque([(x, y)])
        visited.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited and garden_sample[ny][nx] == crop:
                    visited.add((nx, ny))
                    region.add((nx, ny))
                    queue.append((nx, ny))
        bulk_price += len(region) * count_polygon_corners(region)

assert bulk_price == 1206
```

Not bad for 11 lines of corner arithmetic, right?

### Manhattan Voronoi Regions and 45-Degree Chebyshev Rotation

![Taxicab geometry vs Euclidean straight line on a city block grid](/assets/images/taxicab-geometry.png){: .no-mat}

On orthogonal city-block grids, shortest distance isn't a straight Euclidean crow-fly line — it is **Manhattan (\(L_1\)) distance** (`|x1 - x2| + |y1 - y2|`, built right into [`aoc_common.Point.manhattan_distance_from`](/python/reusable_code)).

In [2018 Day 6 (*Chronal Coordinates*)](/2018/6) ([`d06.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2018/d06/d06.py){:target="_blank"}), we partition the grid into Manhattan **Voronoi regions** by assigning every coordinate to its unique closest seed. How do you know which seeds expand infinitely without searching forever?

Just check `aoc_common.bounding_box(seeds)`: any seed whose closest-point region touches the bounding box edge (`x in (tl.x, br.x)` or `y in (tl.y, br.y)`) extends to infinity, because stepping straight outward away from the box adds `1` to the distance from *every* seed equally — so whichever seed is closest on the border stays closest forever:

```python
from collections import Counter
from collections.abc import Sequence

from aoc_common import Point, bounding_box


def largest_finite_voronoi_area(seeds: Sequence[Point]) -> int:
    """Find the largest finite Manhattan Voronoi area inside the seeds' bounding box."""
    tl, br = bounding_box(seeds)
    areas: Counter[Point] = Counter()
    infinite: set[Point] = set()

    for y in range(tl.y, br.y + 1):
        for x in range(tl.x, br.x + 1):
            cell = Point(x, y)
            dists = [(cell.manhattan_distance_from(seed), seed) for seed in seeds]
            min_dist = min(dist for dist, _ in dists)
            nearest = [seed for dist, seed in dists if dist == min_dist]
            if len(nearest) == 1:
                owner = nearest[0]
                areas[owner] += 1
                if x in (tl.x, br.x) or y in (tl.y, br.y):
                    infinite.add(owner)

    return max((area for seed, area in areas.items() if seed not in infinite), default=0)


sample_seeds = [Point(1, 1), Point(1, 6), Point(8, 3), Point(3, 4), Point(5, 5), Point(8, 9)]
assert largest_finite_voronoi_area(sample_seeds) == 17
```

And here is one last Manhattan trick worth keeping in your back pocket: **the \(45^\circ\) Chebyshev Rotation**.

All points within Manhattan distance \(r\) of a sensor form a tilted \(45^\circ\) **diamond**, which is awkward to intersect or bound. Transform every `(x, y)` coordinate into `(u, v) = (x + y, x - y)`:

$$|x_1 - x_2| + |y_1 - y_2| = \max\left(|u_1 - u_2|,\; |v_1 - v_2|\right)$$

Under that rotation, every tilted Manhattan diamond of radius \(r\) becomes an ordinary **axis-aligned Chebyshev (\(L_\infty\)) square** of half-width \(r\)! That immediately turns intersection of sensor diamonds into plain interval overlap — and finds the maximum pairwise Manhattan distance across \(N\) points in \(O(N)\) linear time instead of \(O(N^2)\):

```python
from collections.abc import Sequence


def to_chebyshev(x: int, y: int) -> tuple[int, int]:
    """Rotate Manhattan coordinates 45 degrees so L1 diamonds become axis-aligned squares."""
    return (x + y, x - y)


def max_manhattan_distance(points: Sequence[tuple[int, int]]) -> int:
    """Compute maximum pairwise Manhattan distance in O(n) via Chebyshev rotation."""
    if len(points) < 2:
        return 0
    rotated = [to_chebyshev(x, y) for x, y in points]
    us = [u for u, _ in rotated]
    vs = [v for _, v in rotated]
    return max(max(us) - min(us), max(vs) - min(vs))


pts = [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
assert max_manhattan_distance(pts) == 15
```

---

## AoC Examples

| Puzzle | Technique | Link / Source |
| :--- | :--- | :--- |
| **2018 Day 6** — Chronal Coordinates | Manhattan Voronoi regions & bounding-box infinity detection | [Walkthrough](/2018/6) / [`d06.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2018/d06/d06.py){:target="_blank"} |
| **2023 Day 10** — Pipe Maze | Scanline parity (`|` vs `L`/`J` bends) & enclosed-tile counting | [2023 Index](/2023/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2023 Day 18** — Lavaduct Lagoon | Integer Shoelace + Pick's Theorem for \(9.5 \times 10^{11}+\) areas | [2023 Index](/2023/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2024 Day 12** — Garden Groups | Counting straight polygon sides via 2x2 corners | [2024 Index](/2024/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
| **2025 Day 9** — Movie Theater | Sparse odd-even ray casting & inscribed rectangle intersection checks | [Walkthrough](/2025/9) / [`d09.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d09/d09.py){:target="_blank"} |
