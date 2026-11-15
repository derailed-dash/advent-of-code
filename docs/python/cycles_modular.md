---
title: Cycle Detection and Modular Arithmetic
description: "Canonical Python >=3.13 patterns for jumping across trillion-iteration simulations — state hashing with divmod, cumulative delta cycle jumps, math.lcm synchronisation, modular ring wrapping, and the Chinese Remainder Theorem."
main_img:
  name: "Cycle Detection and Modular Arithmetic"
  link: /assets/images/pj_cycles_hero.png
tags:
  - name: Working with Binary and Other Bases
    link: /python/binary
  - name: Graphs and Graph Theory
    link: /python/graph
  - name: Defaultdict
    link: /python/defaultdict
  - name: Recursion
    link: /python/recursion
mathjax: true
---

## Page Contents

- [Jumping Across a Trillion Iterations](#jumping-across-a-trillion-iterations)
- [Cycle Detection via State Hashing](#cycle-detection-via-state-hashing)
  - [Generic Cycle Extrapolation](#generic-cycle-extrapolation)
  - [Cumulative Delta Cycle Jumping](#cumulative-delta-cycle-jumping)
  - [Choosing a Minimal Snapshot Key](#choosing-a-minimal-snapshot-key)
- [Synchronising Independent Cycles with `math.lcm`](#synchronising-independent-cycles-with-mathlcm)
- [Modular Ring Wrapping, LCM Modulus, and Modular Inverses](#modular-ring-wrapping-lcm-modulus-and-modular-inverses)
- [The Chinese Remainder Theorem](#the-chinese-remainder-theorem)
  - [Iterative LCM Step-Sieving](#iterative-lcm-step-sieving)
  - [Closed-Form CRT with Modular Inverses](#closed-form-crt-with-modular-inverses)
- [AoC Examples](#aoc-examples)

---

## Jumping Across a Trillion Iterations

Here is a familiar Advent of Code story. Part 1 asks you to run a clean little simulation for 20 rounds, 100 seconds, or 2,022 falling rocks. Your naive loop finishes in 10 milliseconds, prints the right answer, and you feel like an absolute hero.

Then you unlock Part 2:

> *"Do the exact same thing `1_000_000_000` times."*
> Or `1_000_000_000_000` times.
> Or wait until six parallel walkers collide at step \( 10^{13} \).

If you just change `2022` to `1_000_000_000_000` and hit run, you are not watching a fast algorithm anymore — you are watching your terminal sit blank half an hour later while a single CPU core melts. (Ask me how I know — my first brute-force attempt on `2023 Day 8` was still chugging 30 minutes later before I finally hit `Ctrl+C`.)

The insight that shatters Part 2 scale is the **Pigeonhole Principle**. Whenever a simulation is **deterministic** (the next state depends *only* on the current state) and operates over a **finite** state space of size \( N \), it cannot produce new states forever. By step \( N + 1 \) at the absolute latest, it *must* revisit a state it has already seen. From that moment onward, every subsequent transition is locked into a repeating loop forever.

![State transition path entering a periodic repeat cycle](/assets/images/pj_cycle_rho_diagram.png){: .no-mat}

Notice the classic "rho" (\(\rho\)) shape in the diagram above. Every deterministic finite system splits neatly into two phases:

1. **A lead-in (transient tail)** of length \(\mu\) steps before the system first touches its eventual cycle.
2. **A repeating cycle** of period \(P = t - \mu\), starting the first time a state repeats at step \(t\).

Once you catch that first repeat, simulating a trillion steps is pointless. Any target step \(T \ge \mu\) maps straight onto an already-visited step inside the first cycle using remainder arithmetic:

$$T_{\text{equiv}} = \mu + ((T - \mu) \bmod P)$$

Instead of running \(10^{12}\) iterations, you simulate \(\mu + P\) iterations and jump across the rest in \(O(1)\).

---

## Cycle Detection via State Hashing

![Lead-in states before periodic repetition](/assets/images/repeating_configs.png)

Depending on what the puzzle is asking for at step \(T\), you will reach for one of two cycle-jumping patterns:

- **Direct state lookup**: The answer depends only on the system configuration *at* step \(T\) — e.g. the north support load on a tilted reflector dish in `2023 Day 14`, or memory bank loop size in `2017 Day 6`.
- **Cumulative delta jumping**: Something keeps *growing* monotonically across cycles — e.g. the rock tower height in [2022 Day 17](/2022/17) — so the global state never repeats verbatim, even though the active top profile does.

### Generic Cycle Extrapolation

For direct state lookup, store `seen: dict[S, int]` mapping each hashable state to its first step index alongside a `history: list[R]` list of step values. As soon as `state in seen`, compute `lead_in`, `period = step - lead_in`, and use `divmod(target - lead_in, period)` to index `history[lead_in + remaining]` in O(1):

```python
from collections.abc import Callable, Hashable


def extrapolate_cycle[S: Hashable, R](
    initial_state: S,
    step_fn: Callable[[S], S],
    value_fn: Callable[[S], R],
    target: int,
) -> R:
    """Run ``step_fn`` until a state repeats and extrapolate ``value_fn`` at ``target``."""
    if target < 0:
        raise ValueError(f"target must be non-negative, got {target}")

    state = initial_state
    seen: dict[S, int] = {state: 0}
    history: list[R] = [value_fn(state)]
    if target == 0:
        return history[0]

    for step in range(1, target + 1):
        state = step_fn(state)
        if state in seen:
            lead_in = seen[state]
            period = step - lead_in
            _, remaining = divmod(target - lead_in, period)
            return history[lead_in + remaining]

        val = value_fn(state)
        if step == target:
            return val
        seen[state] = step
        history.append(val)

    return history[-1]


def reallocate_banks(banks: tuple[int, ...]) -> tuple[int, ...]:
    """Perform one AoC 2017 Day 6 memory reallocation cycle."""
    arr = list(banks)
    idx, blocks = max(enumerate(arr), key=lambda pair: pair[1])
    arr[idx] = 0
    count = len(arr)
    full_passes, extra = divmod(blocks, count)
    if full_passes:
        arr = [v + full_passes for v in arr]
    for offset in range(1, extra + 1):
        arr[(idx + offset) % count] += 1
    return tuple(arr)


# Example 1: Lead-in 0 -> 1 -> 2, then period-3 loop 2 -> 3 -> 4 -> 2
transitions = {0: 1, 1: 2, 2: 3, 3: 4, 4: 2}
assert extrapolate_cycle(0, lambda s: transitions[s], lambda s: s * 10, 1_000_000_000) == 40

# Example 2: 2017 Day 6 sample banks [0, 2, 7, 0] repeat [2, 4, 1, 2] at step 5
assert extrapolate_cycle((0, 2, 7, 0), reallocate_banks, lambda b: b, 5) == (2, 4, 1, 2)
```

Notice why `2017 Day 6` (see [`/2017/`](/2017/) and the [2017 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2017/Dazbo's_Advent_of_Code_2017.ipynb){:target="_blank"}) and `2023 Day 14` ([`/2023/`](/2023/) and the [2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}) both lean on immutable tuples for dictionary keys: a mutable `list[int]` or NumPy `ndarray` raises `TypeError: unhashable type`, whereas `tuple(banks)` or `tuple(map(tuple, grid))` hashes immediately.

### Cumulative Delta Cycle Jumping

What if the metric you care about keeps increasing on every loop, like the growing rock tower in [2022 Day 17 (*Pyroclastic Flow*)](/2022/17)?

You cannot look up step `1_000_000_000_000` directly in `seen` because the absolute tower height grows with every cycle. Instead, cache `(step, height)` keyed by the local repeating state `(rock_idx, jet_idx, skyline)`. When that key repeats:

1. Compute `period = step - prev_step` and `delta = metric - prev_metric`.
2. Split the remaining steps with `full_cycles, remaining = divmod(target - step, period)`.
3. Fast-forward the accumulated height by `full_cycles * delta`, then run only the final `remaining` steps on the actual simulation!

```python
from collections.abc import Callable, Hashable


def jump_cumulative_cycle[K: Hashable, State](
    initial_state: State,
    step_fn: Callable[[State], tuple[State, K, int]],
    target: int,
) -> int:
    """Simulate until key repeats, jump whole periods with divmod, and finish remainder."""
    if target <= 0:
        return 0

    seen: dict[K, tuple[int, int]] = {}
    state = initial_state
    metric = 0
    skipped_gain = 0
    jumped = False
    step = 0

    while step < target:
        step += 1
        state, key, metric = step_fn(state)
        if not jumped and key in seen:
            prev_step, prev_metric = seen[key]
            period = step - prev_step
            delta = metric - prev_metric
            full_cycles, remaining = divmod(target - step, period)
            skipped_gain = full_cycles * delta
            step = target - remaining
            jumped = True
        else:
            seen[key] = (step, metric)

    return metric + skipped_gain


def toy_growing_step(state: tuple[int, int]) -> tuple[tuple[int, int], int, int]:
    """Toy tower: lead-in +5 height over 2 steps, then period-3 cycle adding +10 per cycle."""
    pos, total_height = state
    deltas = {0: (1, 4), 1: (2, 1), 2: (3, 3), 3: (4, 5), 4: (2, 2)}
    nxt, dh = deltas[pos]
    new_height = total_height + dh
    return (nxt, new_height), nxt, new_height


assert jump_cumulative_cycle((0, 0), toy_growing_step, 123) == 408
```

Notice the `jumped` boolean flag: if `remaining` steps are left to simulate after the jump and `full_cycles` happened to be `0` (for example on a small test target), guarding with `not jumped` guarantees we never trigger a second jump mid-remainder.

### Choosing a Minimal Snapshot Key

Selecting the right dictionary key is where cycle detection usually succeeds or quietly breaks:

| What to include or exclude | Why it matters | Example |
| :--- | :--- | :--- |
| **Include every input cursor** | Two identical boards behave differently if the next rock or jet index differs | `(rock_idx % 5, jet_idx % len(jets), ...)` in [2022 Day 17](/2022/17) |
| **Normalise growing coordinates** | Absolute `y` height never repeats — store distances *relative* to `top` | Top column depth offsets or top `k` rows in [`tetris.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2022/d17_pyroclastic_flow/tetris.py){:target="_blank"} |
| **Convert mutable structures** | `list` and `ndarray` are unhashable | `tuple(banks)` in `2017 Day 6`; `tuple(map(tuple, grid))` in `2023 Day 14` |
| **Exclude step counters** | Including `step` makes every state unique — zero cache hits ever! | Keep `step` in the dict *value*, never in the dict *key* |
| **Don't under-specify** | Caching only the top 1 row misses falling pieces slipping down a 3-cell chimney | Use column depths `(top - col_max_y)` or a reachable surface window |

---

## Synchronising Independent Cycles with `math.lcm`

Sometimes a single global snapshot won't save you because the combined system period is *still* \( 10^{13} \) or \( 10^{14} \) — far too large to reach even a single repeat of the whole machine.

When that happens, step back and inspect the input topology. Often the system is actually **several small, independent sub-cycles** running side by side, and you only win when they all fire at once.

Two classic examples in [`/2023/`](/2023/) (see the [2023 notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"}) show this beautifully:

- **2023 Day 8 (*Haunted Wasteland*)**: Multiple ghost paths start at `??A` nodes and walk until they all land on `??Z` on the same step. Each ghost lives in its own isolated loop.
- **2023 Day 20 (*Pulse Propagation*)**: Plotting the module wiring with Graphviz reveals why brute-force button pressing stalls — `broadcaster` splits into **four completely independent 12-bit binary counter subgraphs** feeding one final conjunction `ns -> rx`:

![Conjunction counter subgraphs from Pulse Propagation](/assets/images/graphviz_module_graph.png)

Instead of simulating \( 10^{14} \) steps for all four counters together, measure the cycle period \(P_i\) of each subgraph independently and combine them with `math.lcm(*periods)` (built into Python's standard library since Python 3.9).

### Always Verify Zero Phase Offset First

Here is the crucial catch that trips people up every December: **`math.lcm(*periods)` ONLY works when `phase_offset == 0`** — meaning each loop reaches its trigger at exact integer multiples \(k \cdot P_i\) (so `first_hit == period`, with no non-zero lead-in shift and no multiple goal hits per cycle).

Never blindly break on the first goal hit and call `math.lcm`. Walk until the underlying state repeats in `seen`, then assert that the full state loop period is a multiple of the first goal hit and that goal hits occur at exact multiples of that period:

```python
import math
from collections.abc import Callable, Hashable, Sequence


def synchronise_zero_offset_cycles[S: Hashable](
    starts: Sequence[S],
    step_fn: Callable[[S], S],
    is_goal: Callable[[S], bool],
) -> int:
    """Combine independent loop periods via math.lcm after verifying zero phase offset."""
    if not starts:
        raise ValueError("starts must not be empty")

    periods: list[int] = []
    for start in starts:
        state = start
        seen: dict[S, int] = {state: 0}
        goal_steps: list[int] = []
        steps = 0

        while True:
            state = step_fn(state)
            steps += 1
            if is_goal(state):
                goal_steps.append(steps)
            if state in seen:
                state_period = steps - seen[state]
                break
            seen[state] = steps

        if not goal_steps:
            raise ValueError(f"Cycle from {start!r} never visits a goal state")

        period = goal_steps[0]
        if state_period % period != 0 or goal_steps != list(range(period, steps + 1, period)):
            raise ValueError(
                f"Non-zero offset or irregular goals (state_period={state_period}, hits={goal_steps}); use CRT instead."
            )
        periods.append(period)

    return math.lcm(*periods)


# Sample graph from 2023 Day 8 Part 2
sample_graph = {
    "11A": ("11B", "XXX"),
    "11B": ("XXX", "11Z"),
    "11Z": ("11B", "XXX"),
    "22A": ("22B", "XXX"),
    "22B": ("22C", "22C"),
    "22C": ("22Z", "22Z"),
    "22Z": ("22B", "22B"),
    "XXX": ("XXX", "XXX"),
}
instr = "LR"


def ghost_step(node_step: tuple[str, int]) -> tuple[str, int]:
    node, idx = node_step
    left, right = sample_graph[node]
    return (left if instr[idx] == "L" else right, (idx + 1) % len(instr))


assert synchronise_zero_offset_cycles(
    [("11A", 0), ("22A", 0)],
    ghost_step,
    lambda st: st[0].endswith("Z"),
) == 6

# Reject non-zero phase offsets (lead-in before period-3 loop: hits at t=2, 5, 8, ...)
shifted_loop = {0: 1, 1: 2, 2: 3, 3: 1}
try:
    synchronise_zero_offset_cycles([0], lambda s: shifted_loop[s], lambda s: s == 2)
    raise AssertionError("Expected ValueError for non-zero phase offset")
except ValueError:
    pass
```

When `phase_offset != 0`, `math.lcm` silently gives the wrong answer — which is the exact boundary where you switch to the **Chinese Remainder Theorem**.

---

## Modular Ring Wrapping, LCM Modulus, and Modular Inverses

Before tackling CRT, three everyday modular arithmetic habits in Python remove whole categories of off-by-one bugs and integer explosions:

### 1. Python's Euclidean `%` Handles Negative Steps Cleanly

In C, Java, or Rust, `-3 % 100` evaluates to `-3` (truncation toward zero), forcing defensive `(x % m + m) % m` wrappers everywhere. Python's `%` operator uses **floor division**, so the remainder always matches the sign of a positive modulus:

```python
assert (-3) % 100 == 97
```

That makes circular wrapping effortless:

- **Circular dial rotation ([2025 Day 1](/2025/1))**: Turning a `0..99` dial left or right wraps cleanly with `(pos - steps) % 100`, and using mirror symmetry turns left-turn zero-crossing counts into a single `divmod` without nested `if/elif` branches!
- **Toroidal robot teleportation (`2024 Day 14`, [`/2024/`](/2024/))**: A robot starting at \((p_x, p_y)\) with velocity \((v_x, v_y)\) — even negative velocities — jumps straight to second \(t\) in \(O(1)\) via:

```python
def turn_dial(pos: int, direction: str, steps: int, dial_size: int = 100) -> tuple[int, int]:
    """Rotate a circular dial and return ``(new_pos, zero_crossings)`` using ``divmod``."""
    if direction == "R":
        crossings, new_pos = divmod(pos + steps, dial_size)
        return new_pos, crossings
    mirrored = (dial_size - pos) % dial_size
    crossings, _ = divmod(mirrored + steps, dial_size)
    return (pos - steps) % dial_size, crossings


# 2025 Day 1 dial wrapping (L5 from 2 -> 97, 1 crossing; L100 from 0 -> 0, 1 crossing)
assert turn_dial(2, "L", 5) == (97, 1)
assert turn_dial(0, "L", 100) == (0, 1)

# 2024 Day 14 sample: p=(2, 4), v=(2, -3) on an 11x7 grid at t=5 -> (1, 3)
assert ((2 + 2 * 5) % 11, (4 + (-3) * 5) % 7) == (1, 3)
```

### 2. Clamping Exploding Integers with `lcm_modulus = math.lcm(*divisors)`

In [2022 Day 11 (*Monkey in the Middle*)](/2022/11) (see [`monkey.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2022/d11_monkey_in_the_middle/monkey.py){:target="_blank"}), Part 2 removes the `// 3` relief division and raises rounds from 20 to 10,000. Without clamping, squaring worry values repeatedly creates numbers with hundreds of thousands of digits, stalling Python's arbitrary-precision arithmetic.

Because only addition and multiplication occur (no division!), modular congruence holds across every monkey's divisibility check simultaneously if we reduce modulo \(M = \operatorname{lcm}(d_1, d_2, \dots, d_k)\):

$$(a + b) \bmod M = ((a \bmod M) + b) \bmod M, \qquad (a \cdot b) \bmod M = ((a \bmod M) \cdot b) \bmod M$$

```python
import math

divisors = (23, 19, 13, 17)
lcm_modulus = math.lcm(*divisors)

raw_worry = 79
clamped_worry = 79
for _ in range(6):
    raw_worry = raw_worry * raw_worry + 3
    clamped_worry = (clamped_worry * clamped_worry + 3) % lcm_modulus
    assert all((raw_worry % d) == (clamped_worry % d) for d in divisors)
```

Since every divisor \(d_i\) divides `lcm_modulus`, reducing `worry %= lcm_modulus` leaves every `worry % d_i == 0` branch 100% identical while keeping `worry` small enough to fit inside a single 64-bit integer.

### 3. Fast Exponentiation and Modular Inverses (`pow`)

Never write `(base ** exp) % mod` when `exp` is large — Python will try to materialise `base ** exp` in RAM before `%` ever runs. Always use the built-in three-argument `pow(base, exp, mod)` for \(O(\log \text{exp})\) modular exponentiation.

Better still, since Python 3.8+, passing `-1` as the exponent computes the **modular multiplicative inverse** \(a^{-1} \bmod m\) natively (raising `ValueError` if \(\gcd(a, m) \neq 1\)):

```python
# 2020 Day 25 sample Diffie-Hellman handshake (subject=7, loop=8, mod=20201227)
card_pub = pow(7, 8, 20201227)
assert card_pub == 5764801
assert pow(17807724, 8, 20201227) == 14897079

# Modular multiplicative inverse via built-in pow(a, -1, mod)
inv = pow(3, -1, 11)
assert (3 * inv) % 11 == 1
```

---

## The Chinese Remainder Theorem

Now suppose your sub-cycles *do* have non-zero phase offsets — the classic AoC setup where you want the earliest timestamp \(t \ge 0\) satisfying a list of simultaneous congruences:

$$t \equiv r_i \pmod{m_i} \quad \text{for } i = 1, \dots, k$$

This pattern turns up directly in two standout puzzles in this repository:

- **[2016 Day 15 (*Timing is Everything*)](/2016/15)** ([`rotating_discks.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2016/d15_rotating_discs_re_map_dataclass/rotating_discks.py){:target="_blank"}): Dropping a capsule at time \(t\) reaches disc \(i\) (with \(m_i\) positions, initially at \(p_i\)) at time \(t + i\), so slot `0` aligns when \(p_i + t + i \equiv 0 \pmod{m_i}\), i.e. \(t \equiv -(p_i + i) \pmod{m_i}\).
- **2020 Day 13 (*Shuttle Search*)** ([`/2020/`](/2020/) and [`bus_schedule_pt2_primes_only.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d13_bus_schedule_primes_and_lcm/bus_schedule_pt2_primes_only.py){:target="_blank"}): Bus \(b_i\) at index offset \(i\) departs at \(t + i\), requiring \(t + i \equiv 0 \pmod{b_i}\), i.e. \(t \equiv -i \pmod{b_i}\).

### Iterative LCM Step-Sieving

The cleanest everyday AoC solver is **iterative LCM step-sieving**. You start with `t = 0` and `step = 1`, then incorporate one congruence `(rem, mod)` at a time:

1. Advance `t += step` until `t % mod == rem % mod`. Because `step` is already a multiple of every previous modulus, *every* step preserves all earlier congruences!
2. Once aligned, update `step = math.lcm(step, mod)` and move to the next congruence.

Even better, using `math.lcm` instead of plain multiplication means this 12-line sieve handles **both coprime and compatible non-coprime moduli** gracefully, and detects impossible systems cleanly instead of looping forever:

```python
import math
from collections.abc import Sequence


def solve_congruences_sieve(congruences: Sequence[tuple[int, int]]) -> tuple[int, int]:
    """Solve t == rem (mod m) iteratively via LCM step-sieving.

    Works for both pairwise coprime and compatible non-coprime moduli.
    Returns ``(earliest_t, combined_period)``.
    """
    t = 0
    step = 1
    for rem, mod in congruences:
        if mod <= 0:
            raise ValueError(f"Modulus must be positive, got {mod}")
        target_rem = rem % mod
        next_step = math.lcm(step, mod)
        while t % mod != target_rem:
            t += step
            if t >= next_step:
                raise ValueError(f"Incompatible congruence: t == {rem} (mod {mod})")
        step = next_step
    return t, step


# 2020 Day 13 sample schedule: "7,13,x,x,59,x,31,19" -> 1068781
buses = [(-offset, int(b)) for offset, b in enumerate("7,13,x,x,59,x,31,19".split(",")) if b != "x"]
assert solve_congruences_sieve(buses)[0] == 1068781

# 2016 Day 15 sample discs: (5 pos at 4, 2 pos at 1) -> t = 5
discs = [(-(4 + 1), 5), (-(1 + 2), 2)]
assert solve_congruences_sieve(discs)[0] == 5

# Non-coprime moduli: t == 3 (mod 6) and t == 5 (mod 8) -> t = 21, period 24
assert solve_congruences_sieve([(3, 6), (5, 8)]) == (21, 24)
```

### Closed-Form CRT with Modular Inverses

When all moduli \(m_1, m_2, \dots, m_k\) are **pairwise coprime** (for example the prime bus IDs in 2020 Day 13), you can compute \(t\) directly in closed form without any `while` loop at all. Let \(M = \prod_{i} m_i\) and \(M_i = M / m_i\):

$$t \equiv \sum_{i=1}^{k} r_i \cdot M_i \cdot (M_i^{-1} \bmod m_i) \pmod M$$

Thanks to Python's built-in `pow(partial, -1, mod)`, that closed-form textbook formula takes just six lines of code:

```python
import math
from collections.abc import Sequence


def solve_crt_coprime(congruences: Sequence[tuple[int, int]]) -> int:
    """Closed-form CRT using pow(M_i, -1, m_i) for pairwise coprime moduli."""
    total_mod = math.prod(mod for _, mod in congruences)
    total = 0
    for rem, mod in congruences:
        partial = total_mod // mod
        inverse = pow(partial, -1, mod)  # Raises ValueError if not coprime
        total += (rem % mod) * partial * inverse
    return total % total_mod


buses = [(-offset, int(b)) for offset, b in enumerate("7,13,x,x,59,x,31,19".split(",")) if b != "x"]
assert solve_crt_coprime(buses) == 1068781
assert solve_crt_coprime([(-(4 + 1), 5), (-(1 + 2), 2)]) == 5
```

> **Which one should you reach for?** In practice, `solve_congruences_sieve` handles 99% of Advent of Code inputs in microseconds and won't break if two periods happen to share a common factor — whereas `solve_crt_coprime` shines when moduli are astronomically huge primes where even iterating up to `mod` inside a `while` loop would take too long.

---

## AoC Examples

| Puzzle | Technique | Link / Source |
| :--- | :--- | :--- |
| **2016 Day 15** — Timing is Everything | Simultaneous congruences (CRT / step-sieving) | [Walkthrough](/2016/15) / [`rotating_discks.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2016/d15_rotating_discs_re_map_dataclass/rotating_discks.py){:target="_blank"} |
| **2017 Day 6** — Memory Reallocation | Lead-in + cycle period via `tuple` state hashing | [2017 Index](/2017/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2017/Dazbo's_Advent_of_Code_2017.ipynb){:target="_blank"} |
| **2020 Day 13** — Shuttle Search | Iterative LCM sieving & closed-form CRT | [2020 Index](/2020/) / [`bus_schedule_pt2_primes_only.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d13_bus_schedule_primes_and_lcm/bus_schedule_pt2_primes_only.py){:target="_blank"} |
| **2020 Day 25** — Combo Breaker | Modular exponentiation `pow(base, exp, mod)` | [2020 Index](/2020/) / [`door_handshake.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d25_door_handshake_modulus/door_handshake.py){:target="_blank"} |
| **2022 Day 11** — Monkey in the Middle | Clamping worry explosion via `math.lcm(*divisors)` | [Walkthrough](/2022/11) / [`monkey.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2022/d11_monkey_in_the_middle/monkey.py){:target="_blank"} |
| **2022 Day 17** — Pyroclastic Flow | Cumulative height-delta jumping with `(rock_idx, jet_idx, skyline)` | [Walkthrough](/2022/17) / [`tetris.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2022/d17_pyroclastic_flow/tetris.py){:target="_blank"} |
| **2023 Day 8** — Haunted Wasteland | Synchronising zero-offset ghost loops via `math.lcm` | [2023 Index](/2023/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2023 Day 14** — Parabolic Reflector Dish | `1_000_000_000` tilt cycles via hashed 2D grid tuples | [2023 Index](/2023/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2023 Day 20** — Pulse Propagation | Four independent binary-counter subgraphs via `math.lcm` | [2023 Index](/2023/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2023/Dazbo's_Advent_of_Code_2023.ipynb){:target="_blank"} |
| **2024 Day 14** — Restroom Redoubt | Toroidal `(p + v * t) % size` wrapping with negative velocities | [2024 Index](/2024/) / [Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
| **2025 Day 1** — Secret Entrance | Circular dial wrapping & `divmod` boundary crossings | [Walkthrough](/2025/1) / [`d01.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2025/d01/d01.py){:target="_blank"} |
