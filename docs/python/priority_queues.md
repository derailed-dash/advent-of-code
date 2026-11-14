---
title: Priority Queues and Heaps
description: "Understanding priority queues, binary heaps, Python's heapq module, and tie-breaking patterns with itertools.count() for Advent of Code."
main_img:
  name: Heapq
  link: /assets/images/heapq.png
tags:
  - name: Graphs and Graph Theory
    link: /python/graph
  - name: heapq
    link: https://docs.python.org/3/library/heapq.html
  - name: Shortest Path Algorithms
    link: /python/shortest_paths
---

## Page Contents

- [Overview](#overview)
- [When To Use a Priority Queue?](#when-to-use-a-priority-queue)
- [Abstract Data Structure?](#abstract-data-structure)
- [Heaps](#heaps)
- [Heapq](#heapq)
  - [Heapq Methods](#heapq-methods)
  - [Heapq Elements, Priority, and Tie-Breaking](#heapq-elements-priority-and-tie-breaking)
- [Examples](#examples)

## Overview

Whilst a Python `list` is great for storing elements and accessing them quickly by index, it performs poorly when you repeatedly need to extract the smallest or largest item from thousands of changing candidates. Scanning an unsorted list each step costs \( O(n) \) per pop — \( O(n^2) \) overall.

A **priority queue** is an *abstract data structure* built to pop the minimum (or maximum) priority item in \( O(\log n) \) time, no matter how large the queue grows.

## When To Use a Priority Queue?

- If you need random index lookups over unordered data, use a `list`.
- If you repeatedly push items with changing costs and always need the lowest-cost (or highest-priority) item next, use a **priority queue**.

Typical AoC use cases include:

- Finding the cheapest path through a weighted maze (Dijkstra and A\*).
- Event-driven simulations ordered by timestamp.
- Merging sorted sequences or greedy scheduling puzzles.

## Abstract Data Structure?

Calling something an *abstract data structure* specifies *what* operations it supports rather than how it lays out bytes in memory:

- Check if it is empty (`bool(pq)`).
- Push a new `(priority, item)` entry.
- Pop and remove the entry with the **highest priority** (in Python's `heapq`, that means the **smallest** key — negate numeric priorities if you need a max-heap).

## Heaps

Heaps are the standard backing implementation for priority queues because they guarantee \( O(\log n) \) push and pop performance by arranging elements as a complete **binary tree**:

![Binary Tree](/assets/images/binary-tree.png){:style="width: 480px"}

Recall from [graphs](/python/graph) that a tree is an *acyclic graph* where every non-root node has a single parent. A **min-heap** enforces two invariants:

- **Shape property**: Every level of the tree is filled left-to-right before starting a new depth.
- **Heap property**: Every parent is `<=` both of its children, guaranteeing the overall minimum sits at index `0`.

## Heapq

Python's standard library provides the [heapq](https://docs.python.org/3/library/heapq.html){:target="_blank"} module: a binary min-heap implemented **directly on top of a regular `list`**.

![Heapq](/assets/images/heapq.png)

In the array layout above, a parent at index `i` always has children at indices `2 * i + 1` and `2 * i + 2`, so no pointer objects or extra wrappers are allocated.

### Heapq Methods

- `heapq.heapify(items)`: Reorder a list into a valid heap in-place in \( O(n) \) linear time.
- `heapq.heappush(heap, element)`: Push an element while restoring the heap property in \( O(\log n) \).
- `heapq.heappop(heap)`: Pop and return the smallest item in \( O(\log n) \).
- `heapq.heappushpop(heap, element)`: Faster combined push followed by pop.
- `heapq.nsmallest(k, iterable)` / `heapq.nlargest(k, iterable)`: Extract top-k items cleanly.

### Heapq Elements, Priority, and Tie-Breaking

Because `heapq` compares tuples element-by-element from left to right, pushing `(cost, state)` automatically orders the heap by `cost`:

```python
import heapq
from itertools import count

frontier: list[tuple[int, int, object]] = []
tie_breaker = count()

# Safe even if two states share the exact same cost and `state` itself is non-comparable!
heapq.heappush(frontier, (0, next(tie_breaker), {"pos": (0, 0), "keys": frozenset()}))
```

Notice why `next(tie_breaker)` matters:

- If you push `(priority, state)` directly and two entries happen to share the same `priority`, Python compares `state_a < state_b` to break the tie.
- If `state` is a `dict`, `frozenset`, `Enum`, or custom class without `__lt__`, Python raises `TypeError: '<' not supported between instances`.
- Inserting a strictly increasing sequence number via `itertools.count()` as the middle tuple element (`(priority, next(tie_breaker), state)`) guarantees ties are always resolved cleanly in FIFO order without ever comparing `state`.

Alternatively, if your state objects are immutable value types (like [`aoc_common.Point`](/python/reusable_code)), decorating with `@dataclass(frozen=True, order=True, slots=True)` with `cost: int` as the first field makes the object itself directly sortable in `heapq` without tuple unpacking:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True, slots=True)
class SearchNode:
    cost: int
    pos: tuple[int, int]
    heading: tuple[int, int] = field(compare=True)
```

Head over to [Shortest Path Algorithms](/python/shortest_paths) to see `heapq` powering Dijkstra and A\* in full AoC pathfinders.

## Examples

- [Risk maze weighted shortest path — 2021 Day 15](/2021/15)
- [Rearranging amphipods state-space search (Dijkstra / A\*) — 2021 Day 23](/2021/23)
- [Clumsy Crucible constrained turning pathfinder — 2023 Day 17](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}
- [Reindeer Maze shortest paths with turn penalties — 2024 Day 16](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}
- [RAM Run falling-bytes pathfinder — 2024 Day 18](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}
