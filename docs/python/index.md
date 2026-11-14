---
layout: default
title: "Python Journey"
topic: "The Python Journey"
description: "Dazbo's Python curriculum built through Advent of Code — covering uv workflows, Template v3, Rich, spatial grids, graphs, pathfinding, PEG grammars, and testing."
---
# {{ page.topic }}

Follow the guides below to go from setting up a modern Python `>=3.13` environment with `uv` to mastering the algorithms, libraries, and reusable patterns behind my Advent of Code solutions.

- **Tooling & Structure**: Environment setup with `uv`, Git encryption with `git-crypt`, project layout, and the evolution from [Template v1](/python/my-aoc-template) to [Template v3](/python/my-aoc-template3).
- **Standard Library & Toolkits**: Collections, comprehensions, regex, recursion, `heapq`, `Rich`, `NetworkX`, `Parsimonious`, and `SymPy`.
- **Reusable Patterns**: Shared 2D/3D spatial primitives ([`aoc_common`](/python/reusable_code)), graph traversal, and [shortest-path search](/python/shortest_paths).

## Chapters Index

<ol>
  {% assign top_level = site.data.navigation.pages | where: 'name', page.title %}
  {% for member in top_level[0].members %}
      <li><a href="{{ member.link | relative_url }}">{{ member.name }}</a></li>
  {% endfor %}
</ol>
