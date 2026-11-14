---
title: Shortest Paths (BFS, Dijkstra, and A*)
description: Modern Python shortest-path patterns for Advent of Code — unweighted BFS with collections.deque, weighted Dijkstra with heapq and itertools.count tie-breakers, A* heuristics, and Grid integration.
---
## Overview

Shortest-path puzzles are among the most common and rewarding problems in Advent of Code. Choosing the right traversal strategy depends on whether every move has equal cost and whether you have an informative heuristic towards the goal:

| Algorithm | Edge Weights | Heuristic | Queue Structure | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **BFS** | Uniform (e.g. cost `1`) | None | `collections.deque` (`O(1)` popleft) | Simple mazes, flood-fill step counting, fewest moves |
| **Dijkstra** | Non-negative (`cost >= 0`) | None | `heapq` min-heap (`O(log n)` push/pop) | Variable terrain costs, state spaces with turn penalties |
| **A\*** | Non-negative (`cost >= 0`) | Admissible (`h(n) <= true_cost`) | `heapq` (`priority = g(n) + h(n)`) | Large grids with a single known destination (faster convergence) |

This guide builds cleanly on [LIFO & FIFO Queues](/python/lifo_fifo), [Graphs](/python/graph), and [Priority Queues (`heapq`)](/python/priority_queues). Credit to Amit Patel's classic [Red Blob Games: Introduction to the A* Algorithm](https://www.redblobgames.com/pathfinding/a-star/introduction.html) for the visual intuition behind cost-vs-heuristic search.

---

## Breadth-First Search (BFS)

![Breadth-First Search Tree](/assets/images/bfs_tree.png)

When every step has identical cost (`1`), **Breadth-First Search (BFS)** visits states strictly in order of increasing distance from the start. Using [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque) gives true `O(1)` appends and left pops — never use `list.pop(0)` or `heapq` when plain unweighted BFS suffices.

Key implementation rules:

- Store `(state, distance)` tuples cleanly (note: `deque.append(...)` takes a single item, so pack `(state, dist)` as a tuple!).
- Mark states visited **as soon as you enqueue them**, not when you pop them, otherwise the same neighbour can be queued multiple times before being visited.

```python
from collections import deque
from aoc_common import Grid, Point


def bfs_shortest_distance(
    grid: Grid[str],
    start: Point,
    goal: Point,
    *,
    wall: str = "#",
) -> int | None:
    """Return minimum orthogonal steps from start to goal, or None if unreachable."""
    if start == goal:
        return 0

    frontier: deque[tuple[Point, int]] = deque([(start, 0)])
    visited: set[Point] = {start}

    while frontier:
        current, steps = frontier.popleft()
        for nxt in grid.neighbours_of(current, include_diagonals=False):
            if nxt in visited or grid[nxt] == wall:
                continue
            if nxt == goal:
                return steps + 1
            visited.add(nxt)
            frontier.append((nxt, steps + 1))

    return None
```

Notice how `Grid.neighbours_of(..., include_diagonals=False)` already guarantees every yielded `Point` satisfies `nxt in grid`.

---

## Weighted Search with Dijkstra's Algorithm

![Dijkstra Cost Expansion](/assets/images/dijkstra.png)

When moves carry different weights — such as energy penalties per tile, teleport costs, or rotation penalties — BFS is no longer sufficient because fewer steps can cost more than a longer low-weight route. **Dijkstra's algorithm** resolves this by expanding the lowest total cumulative cost (`g_score`) first using a binary min-heap (`heapq`).

Three Python 3.13+ best practices keep Dijkstra implementations bug-free:

1. **Tie-breaker with `itertools.count()`**: If two items on the heap have the same cost, Python tries to compare the second tuple element (`state`). Arbitrary tuples or unorderable objects raise `TypeError`! Adding a monotonic sequence number `(cost, next(tie_breaker), state)` guarantees ties never touch `state`.
2. **Lazy deletion (stale-entry skip)**: Checking `if cost > best_cost[current]: continue` upon popping avoids deleting or mutating entries already inside the heap.
3. **Separate cost vs step tracking**: If your puzzle asks for the minimum **cost**, store `cost`; if it asks for the path itself, maintain a `came_from: dict[State, State | None]` map.

```python
from collections.abc import Callable, Iterable
from heapq import heappop, heappush
from itertools import count


def dijkstra[State](
    start: State,
    is_goal: Callable[[State], bool],
    neighbours: Callable[[State], Iterable[tuple[State, int]]],
) -> tuple[int, list[State]] | None:
    """Find lowest-cost path using Dijkstra's algorithm, or return None."""
    tie_breaker = count()
    frontier: list[tuple[int, int, State]] = [(0, next(tie_breaker), start)]
    best_cost: dict[State, int] = {start: 0}
    came_from: dict[State, State | None] = {start: None}

    while frontier:
        cost, _, current = heappop(frontier)
        if cost > best_cost[current]:
            continue  # Skip stale heap entry superseded by a cheaper route
        if is_goal(current):
            return cost, reconstruct_path(came_from, current)

        for nxt, step_cost in neighbours(current):
            new_cost = cost + step_cost
            if nxt not in best_cost or new_cost < best_cost[nxt]:
                best_cost[nxt] = new_cost
                came_from[nxt] = current
                heappush(frontier, (new_cost, next(tie_breaker), nxt))

    return None


def reconstruct_path[State](
    came_from: dict[State, State | None],
    goal_state: State,
) -> list[State]:
    """Walk parent links back to start and return path in forward order."""
    path: list[State] = []
    cur: State | None = goal_state
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path
```

### Modelling Rich State Nodes

In many AoC puzzles, the graph node is **not** just a `Point(x, y)` coordinate! For example, when movement rules impose turning costs or consecutive step limits, model the **state** as a compact hashable tuple or frozen dataclass:

- `(point, heading)` — classic maze with turn penalties (2024 Day 16)
- `(point, heading, straight_streak)` — constrained crucible movement (2023 Day 17)
- `(point, frozenset_of_keys)` — lock-and-key dungeon exploration (2019 Day 18)

Because `@dataclass(frozen=True, slots=True)` or plain `tuple[...]` states are immutable and hashable, the exact same generic `dijkstra` function solves all of them without changing a line of queue logic.

---

## Guided Search with A*

**A\*** extends Dijkstra by prioritising nodes using:

```text
f(n) = g(n) + h(n)
```

- `g(n)`: exact cumulative cost from `start` to `n`
- `h(n)`: heuristic estimate from `n` to the goal

As long as `h(n)` never **overestimates** the true remaining cost (an **admissible** heuristic), A\* is guaranteed to find an optimal shortest path while typically exploring far fewer states than Dijkstra. On orthogonal 2D grids with unit or minimum step cost `1`, **Manhattan distance** (`point.manhattan_distance_from(goal)`) is both fast and admissible.

```python
from collections.abc import Callable, Iterable
from heapq import heappop, heappush
from itertools import count
from aoc_common import Grid, Point


def astar[State](
    start: State,
    is_goal: Callable[[State], bool],
    neighbours: Callable[[State], Iterable[tuple[State, int]]],
    heuristic: Callable[[State], int],
) -> int | None:
    """Return optimal path cost from start to any goal state using A*."""
    tie_breaker = count()
    # Heap items: (f_score, g_score, sequence, state)
    frontier: list[tuple[int, int, int, State]] = [
        (heuristic(start), 0, next(tie_breaker), start)
    ]
    best_g: dict[State, int] = {start: 0}

    while frontier:
        _, g_score, _, current = heappop(frontier)
        if g_score > best_g[current]:
            continue
        if is_goal(current):
            return g_score

        for nxt, step_cost in neighbours(current):
            tentative_g = g_score + step_cost
            if nxt not in best_g or tentative_g < best_g[nxt]:
                best_g[nxt] = tentative_g
                f_score = tentative_g + heuristic(nxt)
                heappush(frontier, (f_score, tentative_g, next(tie_breaker), nxt))

    return None


def grid_astar_cost(grid: Grid[str], start: Point, goal: Point) -> int | None:
    """Find minimum cost through integer-weighted Grid cells using Manhattan A*."""
    return astar(
        start=start,
        is_goal=lambda pt: pt == goal,
        neighbours=lambda pt: (
            (nxt, int(grid[nxt]))
            for nxt in grid.neighbours_of(pt, include_diagonals=False)
            if grid[nxt] != "#"
        ),
        heuristic=lambda pt: pt.manhattan_distance_from(goal),
    )
```

Notice how setting `heuristic=lambda _: 0` turns `astar` directly back into Dijkstra!

---

## Choosing Between BFS, Dijkstra, and A*

| Situation | Recommended Choice | Why |
| :--- | :--- | :--- |
| Unweighted maze or minimum number of moves | **BFS (`deque`)** | `O(V + E)` without heap overhead |
| Find shortest distances to **all** nodes or multiple unknown goals | **BFS** (unweighted) or **Dijkstra** (weighted) | Heuristics require a specific target estimate |
| Single target with variable tile costs or turn penalties | **Dijkstra** or **A\*** | Admissible heuristic trims wasted exploration away from the target |
| Reconstruct **all tied** optimal paths (e.g. counting every tile on any best route) | **Modified Dijkstra** tracking `parents: dict[State, list[State]]` on `new_cost == best_cost[nxt]` | Standard single-parent maps only trace one winner |

---

## AoC Examples in This Repository

- **[2016 Day 11](/2016/11)** — State-space BFS over floor-and-chip configurations with symmetry pruning
- **[2018 Day 15](https://github.com/derailed-dash/Advent-of-Code/tree/main/src/AoC_2018)** — Grid BFS with deterministic reading-order tie-breaking
- **[2021 Day 15](/2021/15)** — Weighted risk grid solved with Dijkstra (`heapq`)
- **[2022 Day 12](/2022/12)** — Heightmap hill-climbing with `Grid` + BFS
- **[2023 Day 17](https://github.com/derailed-dash/Advent-of-Code/blob/main/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb)** — Crucible shortest path with `(point, direction, streak)` state nodes
- **[2024 Day 16](https://github.com/derailed-dash/Advent-of-Code/blob/main/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb)** — Reindeer Maze: weighted `(point, heading)` Dijkstra plus tracking all tied optimal paths
- **[2024 Day 18](https://github.com/derailed-dash/Advent-of-Code/blob/main/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb)** — BFS combined with `binary_search` over falling byte coordinates
