---
title: Caching and Dynamic Programming
description: "Designing compact hashable state keys, closure-scoped @functools.cache, branch-and-bound pruning, Counter frequency compression, and bottom-up DP for Advent of Code in Python >=3.13."
main_img:
  name: "Caching and Dynamic Programming"
  link: /assets/images/pj_dp_hero.png
tags:
  - name: Recursion
    link: /python/recursion
  - name: Sets
    link: /python/sets
  - name: Defaultdict
    link: /python/defaultdict
  - name: Classes and Objects
    link: /python/classes
  - name: Python functools
    link: https://docs.python.org/3/library/functools.html
mathjax: true
---
## Page Contents

- [Why Memoisation Unlocks Part 2](#why-memoisation-unlocks-part-2)
  - [DAGs vs Exponential Call Trees](#dags-vs-exponential-call-trees)
  - [`@functools.cache` vs `@functools.lru_cache` and Closure Scoping](#functoolscache-vs-functoolslru_cache-and-closure-scoping)
- [Designing Compact Hashable State Keys](#designing-compact-hashable-state-keys)
  - [Bitmasks vs `frozenset`](#bitmasks-vs-frozenset)
  - [Why Cumulative Score Spoils Subproblem Sharing](#why-cumulative-score-spoils-subproblem-sharing)
- [Pattern 1 — String and Arrangement DP](#pattern-1--string-and-arrangement-dp)
  - [Prefix Substring Matching](#prefix-substring-matching)
  - [Three-Tuple Group-Run Matching](#three-tuple-group-run-matching)
- [Pattern 2 — Turn-Based Game State DP and Branch-and-Bound Pruning](#pattern-2--turn-based-game-state-dp-and-branch-and-bound-pruning)
  - [Quantum Roll Frequency Grouping](#quantum-roll-frequency-grouping)
  - [Bitmask Graph Relief DP](#bitmask-graph-relief-dp)
  - [Optimistic Upper-Bound and Resource-Cap Pruning](#optimistic-upper-bound-and-resource-cap-pruning)
- [Pattern 3 — Frequency Compression (`Counter` DP) and Bottom-Up Tabulation](#pattern-3--frequency-compression-counter-dp-and-bottom-up-tabulation)
  - [Collapsing Order-Independent Populations](#collapsing-order-independent-populations)
  - [Bottom-Up 1D Path Summation](#bottom-up-1d-path-summation)
- [AoC Examples](#aoc-examples)

---

## Why Memoisation Unlocks Part 2

Every Advent of Code veteran knows the Part 1 curveball. Part 1 hands you a cute little search problem — maybe 20 steps deep, or 25 blinks of a pebble simulation, or a handful of branching beams — and your naive recursive solver knocks it out in milliseconds. Feeling smug, you hit **Part 2**... and the depth jumps to 75, 150, or 256. Suddenly your tree has \( 2^{150} \) or \( 3^{40} \) branches, and your laptop starts sounding like a jet engine trying to outlive the heat death of the universe.

The mental shift that fixes this is simple: **stop counting paths one by one, and start collapsing identical futures**. When two different routes arrive at the exact same remaining situation, they will yield the exact same answer from that point onwards. There is zero reason to solve that subproblem twice.

If you have not read [Recursion](/python/recursion) yet, start there for base cases, call winding, `RecursionTracer`, and the classic Fibonacci warm-up. Here we skip straight past the basics into **Dynamic Programming (DP)** — designing compact state keys, scoping `@functools.cache` cleanly, pruning hopeless branches, and compressing huge populations into tiny dictionaries. Grab a fresh coffee and let's tame that exponential blow-up.

### DAGs vs Exponential Call Trees

Without caching, a recursive search unfolds as a **tree**: even if you reach the exact same node or coordinate via fifty different routes, you re-evaluate its entire downstream subtree fifty separate times. Add memoisation and those duplicate subtrees snap shut into a single **Directed Acyclic Graph (DAG)** — each unique state is evaluated **once**, and every subsequent arrival simply pulls the answer out of a hash table in \( O(1) \) time.

![Memoised DAG versus naive recursion tree](/assets/images/pj_dp_dag_memo_diagram.png){: .no-mat}

Notice the catch hiding in the word *Acyclic*: memoised recursion only works cleanly when states move **strictly forward** without cycles (e.g. remaining time ticks down, string index advances, or beam `y` increases). If your state graph can loop back onto itself, you want a shortest-path queue like BFS or Dijkstra in [Shortest Paths](/python/shortest_paths) instead.

### `@functools.cache` vs `@functools.lru_cache` and Closure Scoping

In Python `>=3.9`, `functools.cache` is the clean, idiomatic replacement for the older `@lru_cache(maxsize=None)`:

| Decorator | Memory Behaviour | Best Used When |
| :--- | :--- | :--- |
| `@functools.cache` | Unbounded dictionary; slightly faster lookup | Nearly every AoC DP problem where unique states fit easily in RAM |
| `@functools.lru_cache(maxsize=4096)` | Evicts least-recently-used entries past `maxsize` | Long-running services or massive state spaces where only recent states repeat |

You can inspect cache efficiency at any time with `.cache_info()` (returning `hits`, `misses`, `maxsize`, and `currsize`) and clear it manually with `.cache_clear()`.

Even better is **where** you put `@cache`. In Advent of Code, your solver almost always depends on parsed puzzle structures — a `Grid`, a `dict` of rules, a `set` of walls, or a list of adapters. None of those mutable containers are hashable! Try decorating a top-level function `def dp(grid, pos):` and Python immediately raises `TypeError: unhashable type`.

The cleanest pattern in Python is to **nest an inner `@cache` helper inside your `solve(...)` function**:

1. **Static puzzle data stays in the outer closure** — only the changing, hashable state parameters go into the cache key.
2. **Automatic cache isolation** — every call to `solve(...)` creates a brand-new closure with a fresh empty cache, so sample assertions never bleed stale entries into your real puzzle run (and you never forget to call `.cache_clear()`).

```python
from functools import cache


def count_grid_paths(
    rows: int,
    cols: int,
    blocked: set[tuple[int, int]],
) -> tuple[int, int, int]:
    """Count monotone right/down paths from (0, 0) to (rows - 1, cols - 1)."""

    @cache
    def ways(r: int, c: int) -> int:
        if r >= rows or c >= cols or (r, c) in blocked:
            return 0
        if (r, c) == (rows - 1, cols - 1):
            return 1
        return ways(r + 1, c) + ways(r, c + 1)

    total = ways(0, 0)
    info = ways.cache_info()
    return total, info.hits, info.misses


paths, hits, misses = count_grid_paths(6, 6, {(2, 2), (3, 1)})
assert paths == 72
assert hits > 0 and misses > 0
```

> **Class Methods vs Closures:** If you decorate a method on a [class](/python/classes) with `@cache`, Python includes `self` in the cache key. That requires the class itself to be immutable and hashable (e.g. `@dataclass(frozen=True, slots=True)` or `NamedTuple`), and keeps cached entries alive for the lifetime of the instance. For most AoC solvers, a closure inside a pure `part1()` / `part2()` function is simpler and leak-free.

---

## Designing Compact Hashable State Keys

Every parameter passed into a `@cache` function forms part of the lookup key. Good DP design comes down to two questions: **what is the smallest tuple that completely determines future decisions**, and **is every element hashable and fast to compare**?

- Keep static lookup maps (`valves`, `towels`, `workflows`) in the enclosing scope, never in the parameter list.
- Replace mutable `list` or `set` arguments with `tuple`, `frozenset`, or an integer bitmask.
- Avoid passing anything derived or cosmetic (such as the full path history when the puzzle only asks for a count or cost).

### Bitmasks vs `frozenset`

When your state needs to remember *which subset* of items you have already collected or activated (e.g. open valves in [2022 Day 16](/2022/16) or collected keys in a dungeon), you have two hashable choices:

| Representation | Pros | Cons |
| :--- | :--- | :--- |
| **`int` bitmask** | \( O(1) \) hash/equality, zero object allocation, trivially fast | Requires mapping up to ~30 items onto indices `0..k-1` |
| **`frozenset[str]`** | Zero indexing setup, readable in logs, arbitrary item count | Slower hashing and higher memory per state than a single `int` |

With a bitmask, testing item `i` is `mask & (1 << i)` and toggling it on is `mask | (1 << i)`:

```python
from functools import cache


def max_weighted_visit(
    edges: dict[int, list[tuple[int, int]]],
    rewards: tuple[int, ...],
    budget: int,
) -> int:
    """Maximise collected rewards within a step budget using an int bitmask."""

    @cache
    def best_remaining(node: int, visited_mask: int, steps_left: int) -> int:
        if steps_left <= 0:
            return 0

        best = 0
        # Option A: collect reward at the current node (costs 1 step)
        if rewards[node] > 0 and not (visited_mask & (1 << node)):
            new_mask = visited_mask | (1 << node)
            best = max(
                best,
                rewards[node] + best_remaining(node, new_mask, steps_left - 1),
            )

        # Option B: move to an adjacent node
        for nxt, cost in edges[node]:
            if cost <= steps_left:
                best = max(
                    best,
                    best_remaining(nxt, visited_mask, steps_left - cost),
                )

        return best

    return best_remaining(0, 0, budget)


sample_edges = {
    0: [(1, 1), (2, 2)],
    1: [(0, 1), (2, 1)],
    2: [(0, 2), (1, 1)],
}
assert max_weighted_visit(sample_edges, (0, 10, 25), budget=4) == 35
```

### Why Cumulative Score Spoils Subproblem Sharing

Watch closely at how `best_remaining` above adds `rewards[node] + best_remaining(...)` **on the way back up** instead of passing `score_so_far` **down** as an argument. That distinction makes or breaks memoisation!

Suppose Route 1 reaches `(node=4, visited_mask=0b101, steps_left=12)` with `score_so_far=80`, and Route 2 reaches the exact same `(node=4, visited_mask=0b101, steps_left=12)` with `score_so_far=95`. If `score_so_far` sits inside the `@cache` signature, Python treats `(4, 0b101, 12, 80)` and `(4, 0b101, 12, 95)` as **two unrelated cache keys**, wrecking your cache hit rate.

By returning the **remaining** optimum from `(node, visited_mask, steps_left)` onwards, the answer depends purely on the future — never on how you got there.

---

## Pattern 1 — String and Arrangement DP

String puzzles in Advent of Code often start by asking *"Can this string be built?"* in Part 1, then immediately pivot to *"In how many ways can it be built?"* in Part 2. The moment you need a total count rather than the first valid match, DP steps in.

### Prefix Substring Matching

In **2024 Day 19** (*Linen Layout*, in [AoC 2024](/2024/) — see [the 2024 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}), we are given a set of available striped towel patterns and asked how many ways each target design can be assembled by concatenating them.

Rather than slicing `design[len(towel):]` and copying new string objects on every recursive call, passing a single integer cursor `idx: int` keeps the state key tiny (`int` instead of `str`) and uses `str.startswith(towel, idx)` for zero-copy prefix checks:

```python
from functools import cache


def count_arrangements(design: str, towels: tuple[str, ...]) -> int:
    """Count how many ways ``design`` can be formed by concatenating ``towels``."""

    @cache
    def ways(idx: int) -> int:
        if idx == len(design):
            return 1
        return sum(
            ways(idx + len(towel))
            for towel in towels
            if design.startswith(towel, idx)
        )

    return ways(0)


sample_towels = ("r", "wr", "b", "g", "bwu", "rb", "gb", "br")
sample_designs = (
    "brwrr",
    "bggr",
    "gbbr",
    "rrbgbr",
    "ubwu",
    "bwurrg",
    "brgr",
    "bbrgwb",
)
per_design = [count_arrangements(d, sample_towels) for d in sample_designs]
assert sum(1 for c in per_design if c > 0) == 6
assert sum(per_design) == 16
```

Look how concise that is: `ways(idx)` answers *"how many ways can we finish `design[idx:]`?"*, and because `towels` sits cleanly in the outer scope as a `tuple[str, ...]`, the cache key is literally a single integer `idx`.

### Three-Tuple Group-Run Matching

Sometimes you cannot just chop off fixed prefixes — you have wildcard characters (`?`) constrained by contiguous run lengths. In **2023 Day 12** (*Hot Springs*, in [AoC 2023](/2023/) — see [the 2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}), Part 2 unfolds every spring record five times over, blowing past brute-force substitution.

Building full candidate strings explodes as \( O(2^q) \) for \( q \) question marks. Instead, ask what minimal state is actually needed to validate the rest of a record from left to right:

1. `char_idx`: current index in `record`
2. `group_idx`: index of the damaged `#` group we are currently matching (or waiting to start)
3. `run_len`: length of the contiguous `#` run accumulated so far

That 3-tuple `(char_idx, group_idx, run_len)` collapses an exponential tree down to at most \( L \times G \times M \) integer states:

```python
from functools import cache


def count_spring_arrangements(record: str, groups: tuple[int, ...]) -> int:
    """Count valid spring configurations matching damaged ``groups`` lengths."""

    @cache
    def count(char_idx: int, group_idx: int, run_len: int) -> int:
        if char_idx == len(record):
            if group_idx == len(groups) and run_len == 0:
                return 1
            if group_idx == len(groups) - 1 and groups[group_idx] == run_len:
                return 1
            return 0

        total = 0
        ch = record[char_idx]

        # Branch 1: treat current position as operational '.'
        if ch in ".?":
            if run_len == 0:
                total += count(char_idx + 1, group_idx, 0)
            elif group_idx < len(groups) and run_len == groups[group_idx]:
                total += count(char_idx + 1, group_idx + 1, 0)

        # Branch 2: treat current position as damaged '#'
        if ch in "#?" and group_idx < len(groups) and run_len < groups[group_idx]:
            total += count(char_idx + 1, group_idx, run_len + 1)

        return total

    return count(0, 0, 0)


spring_samples = [
    ("???.###", (1, 1, 3)),
    (".??..??...?##.", (1, 1, 3)),
    ("?#?#?#?#?#?#?#?", (1, 3, 1, 6)),
    ("????.#...#...", (4, 1, 1)),
    ("????.######..#####.", (1, 6, 5)),
    ("?###????????", (3, 2, 1)),
]
assert sum(count_spring_arrangements(rec, grp) for rec, grp in spring_samples) == 21
unfolded_total = sum(
    count_spring_arrangements("?".join([rec] * 5), grp * 5)
    for rec, grp in spring_samples
)
assert unfolded_total == 525152
```

Notice the subtle guard on Branch 2: `run_len < groups[group_idx]` stops any over-long `#` run immediately rather than wasting cache entries on doomed states.

---

## Pattern 2 — Turn-Based Game State DP and Branch-and-Bound Pruning

What if your puzzle branches into multiple universes on every turn, or lets one or two agents roam a graph optimising a score under a strict time budget?

![Fractured parallel timelines (from 2021 Day 21 — Dirac Dice)](/assets/images/splitting_time.png){: .no-mat}

### Quantum Roll Frequency Grouping

In **[2021 Day 21 (Dirac Dice)](/2021/21)**, Part 2 replaces a deterministic die with a 3-sided quantum die rolled three times per turn. That creates \( 3^3 = 27 \) branching universes every single turn — easily over \( 10^{14} \) distinct games!

Two insights turn this from impossible into ~50 milliseconds:

1. **Collapsing outcome multiplicities**: Three rolls of `(1, 2, 3)` yield 27 paths, yet only **7 distinct sums** (`3` through `9`). Precomputing `Counter(map(sum, product((1, 2, 3), repeat=3)))` turns 27 recursive calls per node into 7 weighted calls — multiplying each returned win tuple by the roll frequency `freq`.
2. **Symmetric player swapping**: There are only \( 10 \times 10 \times 21 \times 21 = 44{,}100 \) non-winning `(pos_active, pos_other, score_active, score_other)` states! By always putting the *active* player first and swapping arguments `(pos_other, nxt_pos, score_other, score_active + nxt_pos)` on recursion, we do not even need a `turn` flag in the state key.

```python
from collections import Counter
from functools import cache
from itertools import product

QUANTUM_ROLLS: dict[int, int] = dict(
    Counter(map(sum, product((1, 2, 3), repeat=3)))
)


def dirac_wins(
    start_p1: int,
    start_p2: int,
    target: int = 21,
) -> tuple[int, int]:
    """Return (p1_wins, p2_wins) across all quantum Dirac Dice universes."""

    @cache
    def play(
        pos_active: int,
        pos_other: int,
        score_active: int,
        score_other: int,
    ) -> tuple[int, int]:
        if score_active >= target:
            return (1, 0)
        if score_other >= target:
            return (0, 1)

        wins_active = wins_other = 0
        for roll_sum, freq in QUANTUM_ROLLS.items():
            nxt_pos = (pos_active + roll_sum - 1) % 10 + 1
            sub_other, sub_active = play(
                pos_other,
                nxt_pos,
                score_other,
                score_active + nxt_pos,
            )
            wins_active += freq * sub_active
            wins_other += freq * sub_other

        return wins_active, wins_other

    return play(start_p1, start_p2, 0, 0)


assert dirac_wins(4, 8) == (444356092776315, 341960390180808)
```

### Bitmask Graph Relief DP

In **[2022 Day 16 (Proboscidea Volcanium)](/2022/16)**, walking step-by-step across zero-flow corridor valves bloats the search tree unnecessarily. Instead, run a quick all-pairs BFS upfront to build a compressed `dists` matrix connecting only the start node and valves with `rate > 0`. From there, each transition jumps straight to an unopened valuable valve and opens it in one step, packing the opened valves into an `int` bitmask:

```python
from functools import cache


def max_pressure_relief(
    rates: tuple[int, ...],
    dists: list[list[int]],
    start_idx: int,
    minutes: int,
) -> int:
    """Find max pressure released across non-zero valves indexed ``0..k-1``."""
    num_valves = len(rates)

    @cache
    def search(curr: int, open_mask: int, time_left: int) -> int:
        best = 0
        for nxt in range(num_valves):
            if rates[nxt] == 0 or (open_mask & (1 << nxt)):
                continue
            rem = time_left - dists[curr][nxt] - 1
            if rem > 0:
                released = rates[nxt] * rem
                best = max(
                    best,
                    released + search(nxt, open_mask | (1 << nxt), rem),
                )
        return best

    return search(start_idx, 0, minutes)


# Minimal 3-node graph: 0 (AA, rate 0), 1 (DD, rate 20), 2 (BB, rate 13)
mini_rates = (0, 20, 13)
mini_dists = [
    [0, 1, 1],
    [1, 0, 2],
    [1, 2, 0],
]
assert max_pressure_relief(mini_rates, mini_dists, start_idx=0, minutes=30) == 885
```

And for Part 2 — where you and an elephant split the 26-minute budget over disjoint valve subsets — you can evaluate `best_for_mask` across reachable subsets or pass an `elephants_left` boolean into the base case to restart the second actor from `start_idx` with the remaining closed valves (`open_mask` preserved!).

### Optimistic Upper-Bound and Resource-Cap Pruning

Sometimes pure memoisation is still not enough: when a state carries 8 or 9 resource counters (like **[2022 Day 19 (Not Enough Minerals)](/2022/19)**) or complex board configurations (like **[2021 Day 23 (Amphipod)](/2021/23)**), the number of reachable states itself runs into the tens of millions unless you apply **Branch-and-Bound pruning** and **state normalisation**:

1. **Optimistic upper-bound pruning**: Suppose with `t` minutes left you already have `geo` geodes and `r_geo` geode robots. Even in a fantasy scenario where you build a brand-new geode robot on *every single remaining minute*, your final geode total cannot exceed:

   $$
   \text{upper\_bound} = \text{geo} + r_{\text{geo}} \cdot t + \frac{t(t - 1)}{2}
   $$

   If that optimistic ceiling is already `<= best` found so far, abandon the entire branch immediately — it can mathematically never beat your incumbent best!

2. **Resource-cap normalisation**: Because a robot factory can build at most one robot per minute, you never gain anything by building more ore/clay/obsidian robots than the highest single-turn cost (`max_cost`) for that mineral. Similarly, if you already hold more stockpiled `ore` than you could possibly spend in the remaining `t` minutes (`t * max_cost - r_ore * (t - 1)`), clamp `ore` down to that ceiling. Clamping turns thousands of functionally identical resource surpluses into the **exact same visited state key**:

```python
from typing import NamedTuple


class Blueprint(NamedTuple):
    """Mineral costs for one robot factory blueprint."""

    ore_ore: int
    clay_ore: int
    obs_ore: int
    obs_clay: int
    geo_ore: int
    geo_obs: int


def max_geodes(bp: Blueprint, minutes: int) -> int:
    """Return max geodes using optimistic upper-bound and resource-cap pruning."""
    max_ore = max(bp.ore_ore, bp.clay_ore, bp.obs_ore, bp.geo_ore)
    best = 0
    seen: set[tuple[int, ...]] = set()

    def dfs(
        t: int,
        ore: int,
        clay: int,
        obs: int,
        geo: int,
        r_ore: int,
        r_clay: int,
        r_obs: int,
        r_geo: int,
    ) -> None:
        nonlocal best
        best = max(best, geo + r_geo * t)
        if t <= 1 or geo + r_geo * t + (t * (t - 1)) // 2 <= best:
            return

        # Normalise excess robots and stockpiles that can never be spent
        r_ore = min(r_ore, max_ore)
        r_clay = min(r_clay, bp.obs_clay)
        r_obs = min(r_obs, bp.geo_obs)
        ore = min(ore, t * max_ore - r_ore * (t - 1))
        clay = min(clay, t * bp.obs_clay - r_clay * (t - 1))
        obs = min(obs, t * bp.geo_obs - r_obs * (t - 1))

        state = (t, ore, clay, obs, geo, r_ore, r_clay, r_obs, r_geo)
        if state in seen:
            return
        seen.add(state)

        if ore >= bp.geo_ore and obs >= bp.geo_obs:
            dfs(
                t - 1,
                ore - bp.geo_ore + r_ore,
                clay + r_clay,
                obs - bp.geo_obs + r_obs,
                geo + r_geo,
                r_ore,
                r_clay,
                r_obs,
                r_geo + 1,
            )
        if ore >= bp.obs_ore and clay >= bp.obs_clay and r_obs < bp.geo_obs:
            dfs(
                t - 1,
                ore - bp.obs_ore + r_ore,
                clay - bp.obs_clay + r_clay,
                obs + r_obs,
                geo + r_geo,
                r_ore,
                r_clay,
                r_obs + 1,
                r_geo,
            )
        if ore >= bp.clay_ore and r_clay < bp.obs_clay:
            dfs(
                t - 1,
                ore - bp.clay_ore + r_ore,
                clay + r_clay,
                obs + r_obs,
                geo + r_geo,
                r_ore,
                r_clay + 1,
                r_obs,
                r_geo,
            )
        if ore >= bp.ore_ore and r_ore < max_ore:
            dfs(
                t - 1,
                ore - bp.ore_ore + r_ore,
                clay + r_clay,
                obs + r_obs,
                geo + r_geo,
                r_ore + 1,
                r_clay,
                r_obs,
                r_geo,
            )
        dfs(
            t - 1,
            ore + r_ore,
            clay + r_clay,
            obs + r_obs,
            geo + r_geo,
            r_ore,
            r_clay,
            r_obs,
            r_geo,
        )

    dfs(minutes, 0, 0, 0, 0, 1, 0, 0, 0)
    return best


bp1 = Blueprint(4, 2, 3, 14, 2, 7)
bp2 = Blueprint(2, 3, 3, 8, 3, 12)
assert max_geodes(bp1, 24) == 9
assert max_geodes(bp2, 24) == 12
```

(Note that for minimum-energy rearrangement puzzles like **[2021 Day 23](/2021/23)**, Dijkstra or A\* over immutable burrow states often pairs even more naturally with an admissible lower-bound heuristic — see [Shortest Paths](/python/shortest_paths) for the `heapq` A\* pattern.)

---

## Pattern 3 — Frequency Compression (`Counter` DP) and Bottom-Up Tabulation

Top-down `@cache` recursion is wonderfully expressive, yet sometimes **bottom-up DP** is even simpler, faster, and immune to Python's default recursion limit (`1000` frames).

### Collapsing Order-Independent Populations

Whenever a puzzle asks *"How many items exist after `N` generations?"* and items evolve **independently** of their neighbours, maintaining a giant `list` of individuals is wasted effort. Track a `collections.Counter` mapping each distinct item state to its population count!

- **[2021 Day 6 (Lanternfish)](/2021/6)**: Simulating 256 days individually produces trillions of fish and exhausts RAM. Grouping fish into 9 timer buckets (`0..8`) via `Counter[int]` runs in well under 1 millisecond.
- **2024 Day 11** (*Plutonian Pebbles*, in [AoC 2024](/2024/) — see [the 2024 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}): Even though stone numbers split and multiply by `2024`, the set of *unique* numbers reachable within 75 blinks stays tiny (a few thousand keys at most!). Stepping a `Counter[int]` layer by layer — or memoising `(stone, blinks_left)` top-down — turns trillions of pebbles into a few milliseconds.
- **[2021 Day 14 (Extended Polymerization)](/2021/14)**: Even when order matters locally for adjacent characters (`XY -> XZY`), each pair `XY` independently spawns two overlapping pairs (`XZ` and `ZY`). Tracking `Counter[str]` of adjacent pairs via `itertools.pairwise` solves 40 steps in microseconds — just remember to count `pair[0]` per pair plus `1` for the unchanging final character of the template!

```python
from collections import Counter
from itertools import pairwise


def lanternfish_population(initial_timers: list[int], days: int) -> int:
    """Simulate exponential lanternfish growth in O(days) via timer buckets."""
    counts: Counter[int] = Counter(initial_timers)
    for _ in range(days):
        spawning = counts[0]
        counts = Counter(
            {timer - 1: qty for timer, qty in counts.items() if timer > 0}
        )
        counts[6] += spawning
        counts[8] += spawning
    return counts.total()


def step_stone(stone: int) -> tuple[int, ...]:
    """Apply one blink transformation rule to a single pebble."""
    if stone == 0:
        return (1,)
    digits = str(stone)
    if len(digits) % 2 == 0:
        mid = len(digits) // 2
        return (int(digits[:mid]), int(digits[mid:]))
    return (stone * 2024,)


def count_pebbles_after(initial: list[int], blinks: int) -> int:
    """Count pebbles after ``blinks`` using order-independent frequency counts."""
    counts: Counter[int] = Counter(initial)
    for _ in range(blinks):
        nxt: Counter[int] = Counter()
        for stone, qty in counts.items():
            for child in step_stone(stone):
                nxt[child] += qty
        counts = nxt
    return counts.total()


def polymer_spread(template: str, rules: dict[str, str], steps: int) -> int:
    """Return max minus min element frequency after ``steps`` pair insertions."""
    pairs: Counter[str] = Counter(a + b for a, b in pairwise(template))
    for _ in range(steps):
        nxt: Counter[str] = Counter()
        for pair, qty in pairs.items():
            if mid := rules.get(pair):
                nxt[pair[0] + mid] += qty
                nxt[mid + pair[1]] += qty
            else:
                nxt[pair] += qty
        pairs = nxt

    elements: Counter[str] = Counter({template[-1]: 1})
    for pair, qty in pairs.items():
        elements[pair[0]] += qty
    freqs = elements.values()
    return max(freqs) - min(freqs)


assert lanternfish_population([3, 4, 3, 1, 2], 80) == 5934
assert lanternfish_population([3, 4, 3, 1, 2], 256) == 26984457539
assert count_pebbles_after([125, 17], 25) == 55312
assert count_pebbles_after([125, 17], 75) == 65601038650482

sample_poly_rules = {
    "CH": "B", "HH": "N", "CB": "H", "NH": "C",
    "HB": "C", "HC": "B", "HN": "C", "NN": "C",
    "BH": "H", "NC": "B", "NB": "B", "BN": "B",
    "BB": "N", "BC": "B", "CC": "N", "CN": "C",
}
assert polymer_spread("NNCB", sample_poly_rules, 10) == 1588
assert polymer_spread("NNCB", sample_poly_rules, 40) == 2188189693529
```

### Bottom-Up 1D Path Summation

In **2020 Day 10** (*Adapter Array*, [`jolts.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d10_jolts_with_defaultdict/jolts.py){:target="_blank"} in [AoC 2020](/2020/)), every joltage adapter can connect to any adapter 1, 2, or 3 jolts lower. Once sorted, the dependency order is trivial — each rating depends strictly on smaller ratings already computed! Using a [`defaultdict(int)`](/python/defaultdict) seeded with `{0: 1}` computes the astronomical Part 2 combination count in a single linear loop:

```python
from collections import defaultdict


def count_adapter_chains(adapters: list[int]) -> int:
    """Count distinct valid chains from outlet 0 to device (max + 3)."""
    sorted_ratings = sorted(adapters)
    device = sorted_ratings[-1] + 3
    ways: defaultdict[int, int] = defaultdict(int, {0: 1})

    for rating in [*sorted_ratings, device]:
        ways[rating] = ways[rating - 1] + ways[rating - 2] + ways[rating - 3]

    return ways[device]


assert count_adapter_chains([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4]) == 8
assert count_adapter_chains([
    28, 33, 18, 42, 31, 14, 46, 20, 48, 47, 24, 23, 49, 45, 19, 38,
    39, 11, 1, 32, 25, 35, 8, 17, 7, 9, 4, 2, 34, 10, 3,
]) == 19208
```

This is the exact same DAG path-summation principle behind **[2025 Day 7 (Laboratories)](/2025/7)** (summing quantum beam timelines downward through splitters) and **[2025 Day 11 (Reactor)](/2025/11)** (multiplying path counts across mandatory waypoints `svr -> dac -> fft -> out`):

| Approach | When to Prefer It |
| :--- | :--- |
| **Top-Down `@cache` Closure** | Sparse state space where many theoretical states are unreachable, or branching transitions are easier to express recursively |
| **Bottom-Up `Counter` / `defaultdict` Tabulation** | Dense generation-by-generation evolution (`Counter` population DP), strictly ordered 1D sweeps, or deep DAGs exceeding Python's recursion limit |

---

## AoC Examples

| Puzzle | DP Technique | Solution Link |
| :--- | :--- | :--- |
| **2020 Day 10 — Adapter Array** | Bottom-up 1D `defaultdict(int)` path summation | [2020 Day 10 (`jolts.py`)](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d10_jolts_with_defaultdict/jolts.py){:target="_blank"} · [AoC 2020](/2020/) |
| **2021 Day 6 — Lanternfish** | Order-independent `Counter` / `deque` bucket rotation | [2021 Day 6](/2021/6) |
| **2021 Day 14 — Extended Polymerization** | `Counter` pair-frequency transitions over 40 steps | [2021 Day 14](/2021/14) |
| **2021 Day 21 — Dirac Dice** | Turn-based game DP with quantum roll multiplicity grouping | [2021 Day 21](/2021/21) |
| **2021 Day 23 — Amphipod** | Immutable burrow state compression and heuristic search | [2021 Day 23](/2021/23) |
| **2022 Day 16 — Proboscidea Volcanium** | Closure-scoped `@cache` graph DP with opened-valve state | [2022 Day 16](/2022/16) |
| **2022 Day 19 — Not Enough Minerals** | Resource-cap state normalisation and branch pruning | [2022 Day 19](/2022/19) |
| **2023 Day 12 — Hot Springs** | `@cache` 3-tuple `(char_idx, group_idx, run_len)` matching | [AoC 2023](/2023/) · [2023 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2024 Day 11 — Plutonian Pebbles** | Frequency compression / memoised `(stone, blinks)` counting | [AoC 2024](/2024/) · [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
| **2024 Day 19 — Linen Layout** | Closure-scoped `@cache` prefix arrangement counting | [AoC 2024](/2024/) · [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
| **2025 Day 7 — Laboratories** | Recursive DAG timeline counting with `@cache` | [2025 Day 7](/2025/7) |
| **2025 Day 11 — Reactor** | Closure-scoped `@cache` DAG path counting across waypoints | [2025 Day 11](/2025/11) |
