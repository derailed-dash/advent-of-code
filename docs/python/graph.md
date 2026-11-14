---
title: Graphs and Graph Theory
description: "Graph theory fundamentals in Python >=3.13 — directed vs undirected graphs, weighted edges, trees, and clean adjacency list representations for Advent of Code."
main_img:
  name: Graphs
  link: /assets/images/graph_theory.png
tags:
  - name: Graph Theory (Wikipedia)
    link: https://en.wikipedia.org/wiki/Graph_(abstract_data_type)
  - name: NetworkX
    link: /python/networkx
  - name: Shortest Path Algorithms
    link: /python/shortest_paths
  - name: Defaultdict
    link: /python/defaultdict
---

## Page Contents

- [Graph Theory Overview](#graph-theory-overview)
  - [Graph Types](#graph-types)
  - [Tree](#tree)
- [Adjacency Lists](#adjacency-lists)
  - [Unweighted Graphs](#unweighted-graphs)
  - [Weighted Graphs](#weighted-graphs)
- [Examples](#examples)

## Graph Theory Overview

Here we're talking about discrete mathematical **graphs** — not scatter plots — meaning an **abstract model representing a set of *vertices* (nodes), linked together by *edges* (connections).**

### Graph Types

Graphs are typically classified along two orthogonal axes:

- **Undirected** (edges go both ways symmetrically) vs **Directed / Digraph** (edges follow a one-way arrow from `u -> v`).
- **Unweighted** (every step costs `1`) vs **Weighted** (each edge carries a numeric magnitude, distance, or cost).

| Graph Type | Description | Illustration |
| :--- | :--- | :--- |
| *Unweighted Undirected ("graph")* | Symmetric relationships with uniform step cost. | ![Undirected unweighted](/assets/images/undirected_unweighted.png) |
| *Unweighted Directed ("digraph")* | Ordered one-way edges (`u -> v` does not imply `v -> u`). | ![Directed unweighted](/assets/images/directed_unweighted.png) |
| *Weighted Undirected ("weighted graph")* | Symmetric edges carrying distance, time, or capacity weights. | ![Undirected weighted](/assets/images/undirected_weighted.png) |
| *Weighted Directed ("weighted digraph")* | Directed edges with weights — `A -> B` can cost more or less than `B -> A`. | ![Directed weighted](/assets/images/directed_weighted.png){:width="300"} |

Undirected graphs can be either unweighted or weighted, and directed graphs can equally be unweighted or weighted.

### Tree

A **tree** is a connected, ***acyclic* graph** (one containing no cycles or loops), meaning any two vertices are joined by a single unique path. Notice that when you unroll a graph search into a traversal tree (below), the same underlying node can appear on multiple branches unless you track visited states:

![Tree](/assets/images/graph_tree.png)

## Adjacency Lists

The cleanest and most memory-efficient way to store sparse graphs in Python is an **adjacency list** backed by [`collections.defaultdict`](/python/defaultdict): a dictionary mapping each node to its neighbouring nodes (or `{neighbour: weight}` for weighted graphs).

### Unweighted Graphs

Consider an undirected edge list `[(1, 2), (1, 5), (2, 3), (2, 5), (3, 4), (4, 5), (4, 6)]`. Using `defaultdict(set)` automatically avoids duplicate neighbours:

```python
from collections import defaultdict

raw_edges: list[tuple[int, int]] = [
    (1, 2),
    (1, 5),
    (2, 3),
    (2, 5),
    (3, 4),
    (4, 5),
    (4, 6),
]

# Undirected graph: insert both directions cleanly
adjacency: defaultdict[int, set[int]] = defaultdict(set)
for u, v in raw_edges:
    adjacency[u].add(v)
    adjacency[v].add(u)

for vertex, neighbours in sorted(adjacency.items()):
    print(f"{vertex}: {sorted(neighbours)}")
```

Output:

```text
1: [2, 5]
2: [1, 3, 5]
3: [2, 4]
4: [3, 5, 6]
5: [1, 2, 4]
6: [4]
```

*(For a **directed** graph, simply omit the reverse `adjacency[v].add(u)` line.)*

### Weighted Graphs

When edges carry weights or costs (e.g. distances between valves or seating happiness deltas), use a nested dictionary `defaultdict[str, dict[str, int]]` where inner keys are neighbours and values are edge weights:

```python
from collections import defaultdict

weighted_edges: list[tuple[str, str, int]] = [
    ("A", "B", 4),
    ("A", "C", 2),
    ("B", "C", 5),
]

graph: defaultdict[str, dict[str, int]] = defaultdict(dict)
for u, v, cost in weighted_edges:
    graph[u][v] = cost
    graph[v][u] = cost  # Omit for a directed graph
```

Once your graph is in an adjacency structure, you can traverse it directly using [BFS, Dijkstra, or A\*](/python/shortest_paths), hand it to [NetworkX](/python/networkx) for cliques/min-cuts/TSP, or merge connected clusters with [Disjoint Set (`Union-Find`)](/python/useful_algorithms#disjoint-set--union-find-disjointset).

## Examples

- [Adjacency maps for cyclic seating happiness — 2015 Day 13](/2015/13)
- [Adjacency lists for cave path counting — 2021 Day 12](/2021/12)
- [Network minimum-cut graph partitioning — 2023 Day 25](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}
- [LAN party cliques via adjacency sets — 2024 Day 23](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}
- [Connected junction-box circuits — 2025 Day 8](/2025/8)
- [Server-rack DAG path counting — 2025 Day 11](/2025/11)
