---
title: Cellular Automata and Sparse Grids
description: "Double-buffered grid evolution, dimension-agnostic sparse Conway stepping with collections.Counter, toggling infinite void polarity, and multi-phase cascade automata in Python >=3.13."
main_img:
  name: "Cellular Automata and Sparse Grids"
  link: /assets/images/pj_automata_hero.png
tags:
  - name: Sets
    link: /python/sets
  - name: Reusable Code
    link: /python/reusable_code
  - name: Comprehensions
    link: /python/comprehensions
  - name: Permutations & Combinations
    link: /python/perms_combos
mathjax: false
---
## Page Contents

- [Why Naive Grid Loops Collapse in Part 2](#why-naive-grid-loops-collapse-in-part-2)
- [Simultaneous Grid Evolution](#simultaneous-grid-evolution)
- [The `Counter` Neighbour-Convolution Trick for Sparse N-Dimensional Grids](#the-counter-neighbour-convolution-trick-for-sparse-n-dimensional-grids)
  - [Proposal-Collision Sparse Movement with `Counter`](#proposal-collision-sparse-movement-with-counter)
- [Infinite Grids with Alternating Void Polarity](#infinite-grids-with-alternating-void-polarity)
- [Cascading Flash Waves and Multi-Phase Automata](#cascading-flash-waves-and-multi-phase-automata)
  - [Intra-Step Queue Cascades](#intra-step-queue-cascades)
  - [Line-of-Sight Ray Scanning](#line-of-sight-ray-scanning)
  - [Alternating Directional Substeps](#alternating-directional-substeps)
- [AoC Examples](#aoc-examples)

---

## Why Naive Grid Loops Collapse in Part 2

Cellular automata puzzles start out deceptively cosy. You parse a neat little 2D map of `#` and `.`, check each cell's eight neighbours, and update a grid.

Then Part 2 pulls the rug out from under your array:

- The universe grows a **fourth dimension** ([2020 Day 17](/2020/)), turning a modest cube into an expanding 4D hypercube where an unoptimised nested loop easily leaves you grabbing a coffee while Python chews through millions of dead empty coordinates.
- An infinite image toggles its entire background from dark to blindingly **lit** on every odd step ([2021 Day 20](/2021/20)), breaking any sparse solver that assumes everything outside the bounding box stays `.`.
- Sparse agents scatter outward across an unbounded grove ([2022 Day 23](/2022/23)) until nobody has a neighbour left within reach.

> *"Can't I just allocate a bigger NumPy array and pad the edges?"*
> *"Sure — until a puzzle adds a 4th dimension, goes unbounded, or wastes 99% of your runtime scanning empty space."*

The clean architectural fix rests on two habits: **strict double-buffering** (always read generation `t` while writing generation `t + 1`) and **sparse coordinate sets paired with `collections.Counter`** so your simulation only ever touches active cells and their immediate neighbourhood.

---

## Simultaneous Grid Evolution

The golden invariant of every cellular automaton is **simultaneous state transition**: every cell in generation `t + 1` depends strictly on generation `t`. Mutating a list-of-lists or `Grid` in place breaks that invariant mid-loop — top-left updates silently bleed into bottom-right neighbour counts during the same step.

Before writing a single loop, decide whether your puzzle wants a **dense `Grid`** (from [`aoc_common`](/python/reusable_code)) or a **sparse `set[tuple[int, ...]]`**:

| Representation | Best Fit | Examples | Why It Wins |
| :--- | :--- | :--- | :--- |
| **Dense `Grid[T]`** | Fixed rectangular arena where every cell holds rich state (energy levels `0..9`, walls, floors, seats) | [2021 Day 11](/2021/11), [2020 Day 11](/2020/) | Built-in bounds checks (`neighbours_of`) and `O(1)` coordinate indexing |
| **Sparse `set[Coord]`** | Unbounded space, 3D/4D coordinates, sparse moving agents, binary active/inactive cells | [2015 Day 18](/2015/18), [2020 Day 17](/2020/), [2022 Day 23](/2022/23) | Zero memory wasted on empty void; dimension-agnostic tuple coordinates |

*(Even with dense grids, build a fresh snapshot or separate `flashed` tracking set rather than overwriting generation `t` while still reading it.)*

---

## The `Counter` Neighbour-Convolution Trick for Sparse N-Dimensional Grids

Back in 2020, my first Conway Cubes implementation checked every active cell's neighbours, then re-checked *their* neighbours using repeated set intersections. It worked — yet inspecting overlapping inactive regions repeatedly wastes huge amounts of work.

Flipping the direction of work is much cleaner. Instead of asking *"how many live neighbours does every candidate cell have?"*, let every **active cell emit `+1`** to each of its `3^d - 1` neighbours inside a `collections.Counter`:

![Sparse Conway L-tromino active cells emitting +1 neighbour increments to activate count 3](/assets/images/pj_automata_neighbours_diagram.png){: .no-mat}

Look closely at the L-tromino example above:

1. On the left, each of the three active cells emits `+1` into its eight surrounding cells via `Counter`.
2. On the right, the three original live cells (gold) each tally a neighbour count of `2`, so all three **survive**.
3. Meanwhile, the single inactive corner cell highlighted in **teal** collects a count of `3` and **activates**, turning the L-tromino into a stable 2x2 block in a single pass. Every empty cell across the rest of the infinite plane collects `0` votes and is never even instantiated!

Better yet, `itertools.product((-1, 0, 1), repeat=dimensions)` generates all neighbour offsets for **any** number of dimensions (`2D`, `3D`, `4D`, or higher). Using a PEP 695 `type Coord = tuple[int, ...]` alias gives us one clean, dimension-agnostic function:

```python
from collections import Counter
from itertools import product

type Coord = tuple[int, ...]


def step_conway(active: set[Coord], dimensions: int) -> set[Coord]:
    """Advance an N-dimensional Conway grid by one simultaneous generation."""
    offsets = [delta for delta in product((-1, 0, 1), repeat=dimensions) if any(delta)]
    counts: Counter[Coord] = Counter(
        tuple(c + d for c, d in zip(cell, delta, strict=True))
        for cell in active
        for delta in offsets
    )
    return {
        cell
        for cell, n in counts.items()
        if n == 3 or (n == 2 and cell in active)
    }


def parse_sparse(lines: list[str], dimensions: int) -> set[Coord]:
    """Convert 2D ASCII lines into sparse N-dimensional coordinates."""
    pad = (0,) * (dimensions - 2)
    return {
        (x, y, *pad)
        for y, row in enumerate(lines)
        for x, ch in enumerate(row)
        if ch == "#"
    }


# 1. Verify the L-tromino diagram transition in 2D
tromino: set[Coord] = {(1, 1), (1, 2), (2, 2)}
assert step_conway(tromino, dimensions=2) == {(1, 1), (1, 2), (2, 1), (2, 2)}

# 2. Switch from 3D to 4D (2020 Day 17) with zero algorithm changes
sample_cube = [".#.", "..#", "###"]

cubes_3d = parse_sparse(sample_cube, dimensions=3)
for _ in range(6):
    cubes_3d = step_conway(cubes_3d, dimensions=3)
assert len(cubes_3d) == 112

cubes_4d = parse_sparse(sample_cube, dimensions=4)
for _ in range(6):
    cubes_4d = step_conway(cubes_4d, dimensions=4)
assert len(cubes_4d) == 848
```

![Sparse 3D active cubes evolving over Conway generations](/assets/images/conway_3d.png)

Changing `dimensions=2` (as in [2015 Day 18](/2015/18), simply clipping to `0 <= x < width and 0 <= y < height` plus OR-ing stuck corners) to `dimensions=3` or `dimensions=4` ([`hypercube_v2_only_active.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d17_conway_cubes_cell_knows_neighbours/hypercube_v2_only_active.py){:target="_blank"}) takes **zero** changes to `step_conway`. That is the payoff of keeping coordinate tuples dimension-agnostic.

### Proposal-Collision Sparse Movement with `Counter`

The exact same `Counter` trick shines in sparse agent-movement automata like [2022 Day 23](/2022/23) (*Unstable Diffusion*). Every round splits cleanly into two phases:

1. **Propose**: Each elf checks its 8 neighbours in the `elves` set; if isolated, it stays put. Otherwise, it checks the 4 rotating directional rules (`collections.deque` rotated by `-1` each round) and records `proposals[elf] = target`.
2. **Resolve collisions with `Counter`**: Count `dest_counts = Counter(proposals.values())`. Only elves whose proposed destination has `dest_counts[target] == 1` actually move — anyone colliding stays put!

```python
from collections import Counter, deque

type Point2D = tuple[int, int]

ALL_8_DIRS: tuple[Point2D, ...] = (
    (-1, -1), (0, -1), (1, -1),
    (-1, 0),           (1, 0),
    (-1, 1),  (0, 1),  (1, 1),
)


def simulate_diffusion(lines: list[str], rounds: int) -> int:
    """Simulate sparse proposal-collision movement and return empty tiles in bounding box."""
    elves: set[Point2D] = {
        (x, y)
        for y, row in enumerate(lines)
        for x, ch in enumerate(row)
        if ch == "#"
    }
    rules: deque[tuple[tuple[Point2D, ...], Point2D]] = deque([
        (((-1, -1), (0, -1), (1, -1)), (0, -1)),  # North
        (((-1, 1), (0, 1), (1, 1)), (0, 1)),      # South
        (((-1, -1), (-1, 0), (-1, 1)), (-1, 0)),  # West
        (((1, -1), (1, 0), (1, 1)), (1, 0)),      # East
    ])

    for _ in range(rounds):
        proposals: dict[Point2D, Point2D] = {}
        for x, y in elves:
            if not any((x + dx, y + dy) in elves for dx, dy in ALL_8_DIRS):
                continue
            for checks, (mx, my) in rules:
                if not any((x + cx, y + cy) in elves for cx, cy in checks):
                    proposals[(x, y)] = (x + mx, y + my)
                    break

        if not proposals:
            break

        dest_counts = Counter(proposals.values())
        elves = {
            target if (target := proposals.get(elf)) is not None and dest_counts[target] == 1 else elf
            for elf in elves
        }
        rules.rotate(-1)

    xs = [x for x, _ in elves]
    ys = [y for _, y in elves]
    area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    return area - len(elves)


grove_sample = [
    "....#..",
    "..###.#",
    "#...#.#",
    ".#...##",
    "#.###..",
    "##.#.##",
    ".#..#..",
]
assert simulate_diffusion(grove_sample, rounds=10) == 110
```

---

## Infinite Grids with Alternating Void Polarity

Sparse sets normally rely on one cosy assumption: *the infinite void outside our bounding box is empty and stays empty*.

In [2021 Day 20](/2021/20) (*Trench Map*), each pixel looks at its 3x3 window (9 bits -> index `0..511`) into an enhancement lookup table. On the puzzle's sample input, index `0` (`000000000`) maps to `.` and index `511` (`111111111`) maps to `#`, so the void stays dark forever. On the **real** input, index `0` maps to `#` and index `511` maps to `.`!

On step 1, every infinite pixel far from your image sees `000000000` -> `#` and flashes **ON**. On step 2, every infinite pixel sees `111111111` -> `.` and flashes **OFF** again!

The clean pattern is tracking `(lit, bounds, void_lit)`:

- `lit` stores all `#` pixels strictly inside the current finite bounding box `(min_x, max_x, min_y, max_y)`.
- `void_lit` records the uniform polarity (`False` for `.`, `True` for `#`) of every pixel outside those bounds.
- On each step, expand the box by `1` in every direction, evaluate each cell inside the expanded box (reading `lit` inside the old bounds and `void_lit` outside them), and flip `void_lit = algo[511 if void_lit else 0] == "#"`.

```python
type Point2D = tuple[int, int]


def enhance_step(
    lit: set[Point2D],
    bounds: tuple[int, int, int, int],
    void_lit: bool,
    algo: str,
) -> tuple[set[Point2D], tuple[int, int, int, int], bool]:
    """Enhance an infinite 2D pixel grid while tracking toggling void polarity."""
    min_x, max_x, min_y, max_y = bounds
    new_bounds = (min_x - 1, max_x + 1, min_y - 1, max_y + 1)
    new_lit: set[Point2D] = set()

    for y in range(new_bounds[2], new_bounds[3] + 1):
        for x in range(new_bounds[0], new_bounds[1] + 1):
            idx = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if min_x <= nx <= max_x and min_y <= ny <= max_y:
                        bit = 1 if (nx, ny) in lit else 0
                    else:
                        bit = 1 if void_lit else 0
                    idx = (idx << 1) | bit
            if algo[idx] == "#":
                new_lit.add((x, y))

    next_void_lit = algo[511 if void_lit else 0] == "#"
    return new_lit, new_bounds, next_void_lit


toggling_algo = "#" + "." * 510 + "."
tiny_lit: set[Point2D] = {(0, 0)}
tiny_bounds = (0, 0, 0, 0)
tiny_void = False

tiny_lit, tiny_bounds, tiny_void = enhance_step(tiny_lit, tiny_bounds, tiny_void, toggling_algo)
assert tiny_void is True  # Infinite dark background flipped ON

tiny_lit, tiny_bounds, tiny_void = enhance_step(tiny_lit, tiny_bounds, tiny_void, toggling_algo)
assert tiny_void is False  # Infinite lit background flipped OFF again
assert tiny_lit == {(0, 0)}  # Centre cell saw 9 dark neighbours (index 0 -> '#')
```

Always check `assert not void_lit` before reporting `len(lit)` — on odd steps with a toggling lookup rule, the number of lit pixels in the universe is infinite!

---

## Cascading Flash Waves and Multi-Phase Automata

Not every grid automaton fits a single simultaneous sweep. Three recurring variations deserve their own clean idioms:

### Intra-Step Queue Cascades

In [2021 Day 11](/2021/11) (*Dumbo Octopus*), cells gain `+1` energy together, then any cell exceeding `9` **flashes**, boosting all eight neighbours — potentially triggering a chain reaction within the *same* step, while each octopus may flash **at most once** per step.

Instead of rescanning the entire grid in a `while changed:` loop, use a FIFO `collections.deque` (see [LIFO, FIFO, and deques](/python/lifo_fifo)) plus a `flashed: set[Point]` guard on top of `aoc_common.Grid`:

```python
from collections import deque

from aoc_common import Grid, Point


def step_octopi(grid: Grid[int]) -> int:
    """Advance octopus energy levels by one step and process BFS-style flash cascades."""
    flashed: set[Point] = set()
    queue: deque[Point] = deque()

    for pt in grid.all_points():
        grid[pt] += 1
        if grid[pt] > 9:
            flashed.add(pt)
            queue.append(pt)

    while queue:
        pt = queue.popleft()
        for nbr in grid.neighbours_of(pt, include_diagonals=True):
            if nbr not in flashed:
                grid[nbr] += 1
                if grid[nbr] > 9:
                    flashed.add(nbr)
                    queue.append(nbr)

    for pt in flashed:
        grid[pt] = 0
    return len(flashed)


octo_grid = Grid([
    [int(c) for c in row]
    for row in [
        "5483143223",
        "2745854711",
        "5264556173",
        "6141336146",
        "6357385478",
        "4167524645",
        "2176841721",
        "6882881134",
        "4846848554",
        "5283751526",
    ]
])
assert sum(step_octopi(octo_grid) for _ in range(100)) == 1656
```

### Line-of-Sight Ray Scanning

In [2020 Day 11](/2020/) ([`seat_modelling.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d11_seat_modelling_with_vectors_and_slicing/seat_modelling.py){:target="_blank"}), Part 1 checks the eight immediate neighbours around each seat (`L`/`#`). Part 2 switches to **line-of-sight** visibility: floor tiles `.` are transparent, so each seat looks outward along all eight unit vectors until it hits the grid edge or the first chair.

A clean speed-up when geometry is static: precompute `visible_neighbours[seat]` **once** before the simulation loop starts. Chairs never turn into floor, so every subsequent generation simply counts occupied chairs in that precomputed list.

### Alternating Directional Substeps

In [2021 Day 25](/2021/25) (*Sea Cucumber*), two herds migrate on a toroidal wrap-around grid (`(x + 1) % width`, `(y + 1) % height`) — first **all** east-facing cucumbers (`>`) step simultaneously, and *only then* do **all** south-facing cucumbers (`v`) step simultaneously against the updated snapshot:

```python
type Point2D = tuple[int, int]


def step_cucumbers(
    east: set[Point2D],
    south: set[Point2D],
    width: int,
    height: int,
) -> tuple[set[Point2D], set[Point2D], bool]:
    """Run east-then-south toroidal substeps and report whether any herd moved."""
    occupied = east | south
    next_east: set[Point2D] = set()
    moved = False
    for x, y in east:
        nxt = ((x + 1) % width, y)
        if nxt not in occupied:
            next_east.add(nxt)
            moved = True
        else:
            next_east.add((x, y))

    occupied = next_east | south
    next_south: set[Point2D] = set()
    for x, y in south:
        nxt = (x, (y + 1) % height)
        if nxt not in occupied:
            next_south.add(nxt)
            moved = True
        else:
            next_south.add((x, y))

    return next_east, next_south, moved


cucumber_sample = [
    "v...>>.vv>",
    ".vv>>.vv..",
    ">>.>v>...v",
    ">>v>>.>.v.",
    "v>v.vv.v..",
    ">.>>..v...",
    ".vv..>.>v.",
    "v.v..>>v.v",
    "....v..v.>",
]
h, w = len(cucumber_sample), len(cucumber_sample[0])
e_herd = {(x, y) for y, row in enumerate(cucumber_sample) for x, ch in enumerate(row) if ch == ">"}
s_herd = {(x, y) for y, row in enumerate(cucumber_sample) for x, ch in enumerate(row) if ch == "v"}
steps = 0
while True:
    steps += 1
    e_herd, s_herd, did_move = step_cucumbers(e_herd, s_herd, w, h)
    if not did_move:
        break
assert steps == 58
```

Representing each herd as a `set` keeps membership testing `O(1)`, guarantees east moves never collide with stale snapshots, and checks convergence with a single `did_move` boolean.

---

## AoC Examples

| Puzzle | Automaton Pattern | Key Data Structure | Walkthrough / Code |
| :--- | :--- | :--- | :--- |
| **2015 Day 18** | Bounded 2D Game of Life + stuck corners | Sparse `set[Coord]` + `Counter` | [2015 Day 18](/2015/18) |
| **2020 Day 11** | Adjacent seats -> 8-ray line-of-sight | Static `visible` neighbour cache + double buffer | [2020 Index](/2020/) / [`seat_modelling.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d11_seat_modelling_with_vectors_and_slicing/seat_modelling.py){:target="_blank"} |
| **2020 Day 17** | 3D & 4D Conway Cubes | Dimension-agnostic `Counter` convolution | [2020 Index](/2020/) / [`hypercube_v2_only_active.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d17_conway_cubes_cell_knows_neighbours/hypercube_v2_only_active.py){:target="_blank"} |
| **2021 Day 11** | Dumbo Octopus energy flashes | `Grid[int]` + `deque` cascade + `flashed` set | [2021 Day 11](/2021/11) |
| **2021 Day 20** | Infinite image enhancement | `(lit, bounds, void_lit)` polarity toggle | [2021 Day 20](/2021/20) |
| **2021 Day 25** | Toroidal east-then-south herds | Two sparse `set[Point2D]` snapshots | [2021 Day 25](/2021/25) |
| **2022 Day 23** | Unstable Diffusion scattering | Rotating `deque` rules + `Counter` collisions | [2022 Day 23](/2022/23) |
