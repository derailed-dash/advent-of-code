---
layout: default
title: "Python Journey"
topic: "The Python Journey"
description: "Dazbo's 48-chapter Python curriculum built through Advent of Code — covering uv workflows, Template v3, modern Python ergonomics, dynamic programming, interval algebra, modular cycles, grid geometry, integer optimisation, graphs, pathfinding, cellular automata, virtual machines, and testing."
---
# {{ page.topic }}

Follow the guides below to go from setting up a modern Python `>=3.13` environment with `uv` to mastering the algorithms, libraries, and reusable patterns behind my Advent of Code solutions.

- **Tooling & Structure**: Environment setup with `uv`, Git encryption with `git-crypt`, project layout, [Modern Python Ergonomics](/python/modern_python), and the evolution from [Template v1](/python/my-aoc-template) to [Template v3](/python/my-aoc-template3).
- **Standard Library & Toolkits**: Collections, comprehensions, regex, recursion, `heapq`, `Rich`, `NetworkX`, `Parsimonious`, `SymPy`, and `scipy.optimize.milp` ([Constraint Solving and Integer Optimisation](/python/linear_optimisation)).
- **Reusable Patterns & Algorithms**: Shared 2D/3D spatial primitives ([`aoc_common`](/python/reusable_code)), [Caching and Dynamic Programming](/python/dynamic_programming), [Interval and Range Algebra](/python/intervals), [Cycle Detection and Modular Arithmetic](/python/cycles_modular), [Grid Geometry](/python/grid_geometry), [Cellular Automata](/python/cellular_automata), [Virtual Machines](/python/virtual_machines), graph traversal, and [shortest-path search](/python/shortest_paths).

## Chapters Index

<ol>
  {% assign top_level = site.data.navigation.pages | where: 'name', page.title %}
  {% for member in top_level[0].members %}
      <li><a href="{{ member.link | relative_url }}">{{ member.name }}</a></li>
  {% endfor %}
</ol>
