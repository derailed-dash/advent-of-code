---
title: Virtual Machines and Bytecode Decompilation
description: "Designing clean Python >=3.13 virtual machines with match/case dispatch, cycle-accurate generator telemetry, peephole loop folding, 3-bit DFS decompilation, and ripple-carry adder diagnostics."
main_img:
  name: "Virtual Machines and Bytecode Decompilation"
  link: /assets/images/pj_vm_hero.png
tags:
  - name: Binary & Other Bases
    link: /python/binary
  - name: Modern Python
    link: /python/modern_python
  - name: Cycles & Modular Arithmetic
    link: /python/cycles_modular
  - name: Eval & Literal Eval
    link: /python/eval
mathjax: false
---
## Page Contents

- [Why Naive Simulators Hit a Brick Wall in Part 2](#why-naive-simulators-hit-a-brick-wall-in-part-2)
- [AoC's Recurring Assembly and Hardware Genre](#aocs-recurring-assembly-and-hardware-genre)
- [Clean Fetch-Decode-Execute Architecture](#clean-fetch-decode-execute-architecture)
- [Cycle-Accurate Clock Telemetry](#cycle-accurate-clock-telemetry)
- [Part 2 Survival — Peephole Optimisation and Backward Decompilation](#part-2-survival--peephole-optimisation-and-backward-decompilation)
  - [Peephole Optimisation for Nested Loops](#peephole-optimisation-for-nested-loops)
  - [Backward 3-Bit DFS Decompilation](#backward-3-bit-dfs-decompilation)
- [Boolean Gate Networks and Structural Adder Diagnostics](#boolean-gate-networks-and-structural-adder-diagnostics)
  - [Lazy Memoised Evaluation of Combinational Wires](#lazy-memoised-evaluation-of-combinational-wires)
  - [Validating a Ripple-Carry Adder by Gate Role](#validating-a-ripple-carry-adder-by-gate-role)
- [AoC Examples](#aoc-examples)

---

## Why Naive Simulators Hit a Brick Wall in Part 2

Every Advent of Code veteran recognises the moment an assembly puzzle drops. Part 1 looks welcoming — parse a handful of opcodes (`cpy`, `inc`, `jnz`, `addx`), wire up a small register dictionary, run a `while` loop until the instruction pointer falls off the end, and collect your gold star.

Then Part 2 arrives and flips the table. Suddenly:

- Register `a` changes from `7` to `12`, turning an innocent nested decrement loop into `12!` ticks of pure CPU spinning ([2016 Day 23](/2016/23)).
- A 14-digit serial validator ([2021 Day 24](/2021/24)) or a self-replicating 3-bit computer ([2024 Day 17](/2024/)) demands searching trillions of initial inputs — a brute-force estimate that once prompted me to tell a `tqdm` progress bar *"we're going to need a bigger boat"*.
- Four pairs of wires are crossed inside a 200-gate hardware circuit, where checking every `200 choose 8` swap combination would outlast the sun ([2024 Day 24](/2024/)).

> *"So writing a faster Python loop won't save Part 2?"*
> *"Not when the complexity is factorial or combinatorial. You win by writing a clean simulator first, then knowing when to stop simulating and start decompiling."*

The architectural fix has two halves. First, build a **clean, decoupled VM** with typed instructions, `match`/`case` dispatch, loop-state detection, and `yield` generators so Part 1 is rock-solid and easy to instrument. Second, recognise the three Part 2 escape hatches — **peephole loop folding**, **backward DFS decompilation**, and **structural circuit validation**.

---

## AoC's Recurring Assembly and Hardware Genre

Hardware and bytecode puzzles turn up in Advent of Code every couple of years because they test two complementary engineering skills: clean state encapsulation in Part 1, and code comprehension when raw execution stops scaling in Part 2.

![CPU registers, control unit, and fetch-decode-execute cycle](/assets/images/CPU-registers.png)

Across the repository, the genre splits neatly into sequential fetch-decode-execute machines and combinational logic circuits:

- **Early Register CPUs**: [2015 Day 23](/2015/23) introduces a classic two-register Turing lock (`hlf`, `tpl`, `inc`, `jmp`, `jie`, `jio`), followed by the Assembunny trilogy in [2016 Day 12](/2016/12), [2016 Day 23](/2016/23), and [2016 Day 25](/2016/25).
- **Bootloaders and Telemetry**: [2020 Day 8](/2020/) ([`runboot.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d08_basic_CPU_sim/runboot.py){:target="_blank"}) hinges on detecting infinite loops before repairing a corrupted instruction, while [2022 Day 10](/2022/10) asks for cycle-by-cycle register snapshots to draw a CRT display.
- **Bytecode and Circuit Reverse-Engineering**: [2021 Day 24](/2021/24) reduces an 18-line-per-digit ALU into stack constraints, and [2024 Days 17 and 24](/2024/) ([Jupyter Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}) revisit 3-bit octal quines and ripple-carry adders building directly on [2015 Day 7](/2015/7).

---

## Clean Fetch-Decode-Execute Architecture

In my older walkthroughs, I occasionally leaned on `__getattribute__` introspection to map opcode strings onto `_op_cpy()` methods dynamically. It worked, yet it hid method signatures from type checkers and mixed string parsing right into the execution hot loop.

With Python `>=3.13`, we can make the entire fetch-decode-execute pipeline cleaner, faster, and `pyright`-strict:

1. **Parse once into immutable records**: Decode raw text lines up front into `@dataclass(frozen=True, slots=True)` `Instruction` objects.
2. **Dispatch with `match`/`case`**: Pattern-match `(instr.op, instr.args)` directly — no dynamic attribute lookup, no `eval()` hazards (see [Eval and Literal Eval](/python/eval)).
3. **Resolve operands uniformly**: One tiny helper `arg(token, regs)` handles both register names (`"a"`) and signed integer literals (`"-4"`).
4. **Track full machine state for loop detection**: When jumps only depend on static code (like [2020 Day 8](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d08_basic_CPU_sim/runboot.py){:target="_blank"}), repeating `ip` alone proves an infinite loop. Once conditional jumps (`jnz`, `jio`, `jie`) enter the picture, you **must** track `(ip, tuple(regs.values()))`.
5. **Stream outputs lazily with `yield`**: Instead of buffering outputs into a list or raising custom `StopIteration` hacks from inside an opcode method ([2016 Day 25](/2016/25)), turn the VM into a generator. Better still, record `seen_states[state] = emitted` — if the machine returns to an identical `(ip, regs)` state *without* emitting any new output in between, it is stuck in a silent infinite loop; if `emitted` grew, it is producing a periodic signal that callers can slice safely with `itertools.islice`.

```python
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import islice


@dataclass(frozen=True, slots=True)
class Instruction:
    """Immutable decoded assembly instruction."""

    op: str
    args: tuple[str, ...]


def parse_program(raw: str) -> list[Instruction]:
    """Parse assembly lines into typed Instruction records."""
    program: list[Instruction] = []
    for line in raw.strip().splitlines():
        parts = line.split()
        if parts:
            program.append(Instruction(parts[0], tuple(parts[1:])))
    return program


def arg(token: str, regs: dict[str, int]) -> int:
    """Resolve an operand token as either a register value or an integer literal."""
    return regs[token] if token in regs else int(token)


def step_vm(instr: Instruction, ip: int, regs: dict[str, int]) -> tuple[int, int | None]:
    """Execute one instruction, returning ``(next_ip, optional_output)``."""
    match instr.op, instr.args:
        case "cpy", (src, dst):
            if dst in regs:
                regs[dst] = arg(src, regs)
            return ip + 1, None
        case "inc", (reg,):
            if reg in regs:
                regs[reg] += 1
            return ip + 1, None
        case "dec", (reg,):
            if reg in regs:
                regs[reg] -= 1
            return ip + 1, None
        case "jnz", (cond, offset):
            jump = arg(offset, regs) if arg(cond, regs) != 0 else 1
            return ip + jump, None
        case "out", (src,):
            return ip + 1, arg(src, regs)
        case _:
            raise ValueError(f"Unsupported instruction: {instr}")


def execute_vm(
    program: list[Instruction],
    initial_regs: dict[str, int] | None = None,
) -> Iterator[int]:
    """Run an Assembunny-style VM, lazily yielding values emitted by ``out``.

    Raises ``RuntimeError`` if an identical ``(ip, regs)`` state repeats without
    producing any output since the previous visit.
    """
    regs: dict[str, int] = {"a": 0, "b": 0, "c": 0, "d": 0}
    if initial_regs:
        regs.update(initial_regs)

    ip = 0
    emitted = 0
    seen_states: dict[tuple[int, tuple[int, ...]], int] = {}

    while 0 <= ip < len(program):
        state = (ip, tuple(regs.values()))
        if seen_states.get(state) == emitted:
            raise RuntimeError(f"Infinite loop detected at ip={ip}, regs={regs}")
        seen_states[state] = emitted

        ip, output = step_vm(program[ip], ip, regs)
        if output is not None:
            emitted += 1
            yield output


def is_valid_clock(program: list[Instruction], candidate_a: int, sample_len: int = 20) -> bool:
    """Verify the VM emits at least ``sample_len`` alternating ``0, 1, 0, 1, ...`` ticks."""
    try:
        stream = execute_vm(program, {"a": candidate_a})
        return all(next(stream, None) == idx % 2 for idx in range(sample_len))
    except RuntimeError:
        return False


clock_prog = parse_program(
    """
    cpy 0 a
    out a
    cpy 1 a
    out a
    jnz 1 -4
    """
)
assert list(islice(execute_vm(clock_prog), 6)) == [0, 1, 0, 1, 0, 1]
assert is_valid_clock(clock_prog, 0)
assert not is_valid_clock(parse_program("cpy 0 a"), 0)
assert not is_valid_clock(parse_program("out 0"), 0)
```

Notice how `is_valid_clock()` pulls values lazily via `next(stream, None)`. If a candidate halts early (returning `None`) or emits `0, 0`, `all(...)` short-circuits immediately, the generator closes, and we move straight on to `candidate_a + 1` without wasting a single extra tick.

---

## Cycle-Accurate Clock Telemetry

Not every VM puzzle runs one instruction per step. In [2022 Day 10](/2022/10) (*Cathode-Ray Tube*), `noop` takes one clock cycle whereas `addx v` takes **two** cycles — and register `X` only updates *after* the second cycle finishes.

Trying to manage partial instruction timers inside an imperative `tick()` state machine makes it remarkably easy to suffer an off-by-one bug between *during cycle N* and *after cycle N*. Flipping the design to a generator removes that entire class of bug: **yield `x` once per clock cycle before applying the post-instruction mutation**.

```python
from collections.abc import Iterator


def clock_states(raw: str) -> Iterator[int]:
    """Yield register X during each individual clock tick (1-based sequence)."""
    x = 1
    for line in raw.strip().splitlines():
        match line.split():
            case ["noop"]:
                yield x
            case ["addx", value]:
                yield x
                yield x
                x += int(value)
            case other:
                raise ValueError(f"Unexpected CRT instruction: {other}")


def render_crt(raw: str, *, width: int = 8) -> list[str]:
    """Render pixels where a 3-pixel sprite centred at X overlaps beam column."""
    rows: list[str] = []
    current_row: list[str] = []
    for cycle, x in enumerate(clock_states(raw), start=1):
        col = (cycle - 1) % width
        current_row.append("#" if abs(x - col) <= 1 else ".")
        if len(current_row) == width:
            rows.append("".join(current_row))
            current_row.clear()
    if current_row:
        rows.append("".join(current_row))
    return rows


crt_sample = """
noop
addx 3
addx -5
noop
addx 4
"""
signals = {cycle: cycle * x for cycle, x in enumerate(clock_states(crt_sample), start=1)}
assert signals[3] == 3
assert signals[4] == 16
assert render_crt(crt_sample, width=8) == ["#####..."]
```

Because `clock_states()` knows nothing about signal strengths or pixel sprites, the CPU timing logic and CRT rendering stay completely decoupled — each piece is a dozen readable lines.

---

## Part 2 Survival — Peephole Optimisation and Backward Decompilation

Once a clean simulator hits a wall in Part 2, reach for one of two structural shortcuts depending on what the bytecode is doing.

### Peephole Optimisation for Nested Loops

Assembunny ([2016 Day 12](/2016/12) and [2016 Day 23](/2016/23)) has `inc` and `dec`, yet no `mul` instruction. So the puzzle author compiles `a += b * d` into a six-instruction nested loop:

```text
cpy b c
inc a
dec c
jnz c -2
dec d
jnz d -5
```

When `a = 12` triggers a factorial-style countdown, executing that inner loop one increment at a time burns hundreds of millions of Python iterations.

There is a subtle catch in [2016 Day 23](/2016/23): the `tgl` instruction mutates opcodes in memory at runtime! Pre-compiling static regex replacements over the raw text works if `tgl` never touches the multiply block, whereas **runtime peephole matching** inside the VM loop stays safe even when instructions self-modify — whenever `ip` lands on an untouched multiply window, execute `regs[acc] += arg(src, regs) * regs[outer]` directly, zero the two loop counters, and leap `ip + 6`:

```python
type Op = tuple[str, list[str]]


def arg(token: str, regs: dict[str, int]) -> int:
    """Resolve an operand token as either a register value or an integer literal."""
    return regs[token] if token in regs else int(token)


def try_fold_multiply(ops: list[Op], ip: int, regs: dict[str, int]) -> int | None:
    """Fold a 6-instruction multiply-accumulate loop at ``ip`` into a direct update."""
    if ip + 5 >= len(ops):
        return None
    match ops[ip : ip + 6]:
        case [
            ("cpy", [src, c1]),
            ("inc", [acc]),
            ("dec", [c2]),
            ("jnz", [c3, "-2"]),
            ("dec", [outer]),
            ("jnz", [outer2, "-5"]),
        ] if (
            c1 == c2 == c3
            and outer == outer2
            and acc in regs
            and c1 in regs
            and outer in regs
            and len({acc, c1, outer, src}) == 4
            and arg(src, regs) > 0
            and regs[outer] > 0
        ):
            regs[acc] += arg(src, regs) * regs[outer]
            regs[c1] = 0
            regs[outer] = 0
            return ip + 6
    return None


def toggle_at(ops: list[Op], target: int) -> None:
    """Toggle a single instruction in memory using 2016 Day 23 rules."""
    if not 0 <= target < len(ops):
        return
    t_op, t_args = ops[target]
    if len(t_args) == 1:
        new_op = "dec" if t_op == "inc" else "inc"
    else:
        new_op = "cpy" if t_op == "jnz" else "jnz"
    ops[target] = (new_op, t_args)


def step_assembunny(ops: list[Op], ip: int, regs: dict[str, int]) -> int:
    """Execute one Assembunny instruction (supporting ``tgl``) and return next ``ip``."""
    op, args = ops[ip]
    match op, args:
        case "cpy", [src, dst]:
            if dst in regs:
                regs[dst] = arg(src, regs)
        case "inc", [reg]:
            if reg in regs:
                regs[reg] += 1
        case "dec", [reg]:
            if reg in regs:
                regs[reg] -= 1
        case "jnz", [cond, off]:
            if arg(cond, regs) != 0:
                return ip + arg(off, regs)
        case "tgl", [off]:
            toggle_at(ops, ip + arg(off, regs))
        case _:
            raise ValueError(f"Unknown instruction: {op} {args}")
    return ip + 1


def run_assembunny_folded(raw: str, initial_a: int) -> int:
    """Execute Assembunny with runtime peephole folding and self-modifying ``tgl``."""
    regs: dict[str, int] = {"a": initial_a, "b": 0, "c": 0, "d": 0}
    ops: list[Op] = []
    for line in raw.strip().splitlines():
        if parts := line.split():
            ops.append((parts[0], parts[1:]))

    ip = 0
    while 0 <= ip < len(ops):
        folded_ip = try_fold_multiply(ops, ip, regs)
        ip = folded_ip if folded_ip is not None else step_assembunny(ops, ip, regs)

    return regs["a"]


mul_prog = """
cpy a b
dec b
cpy a d
cpy 0 a
cpy b c
inc a
dec c
jnz c -2
dec d
jnz d -5
"""
assert run_assembunny_folded(mul_prog, 12) == 132

# Aliased src == outer computes 4 + 3 + 2 + 1 = 10, so the folder must NOT rewrite it to 16
triangular_prog = """
cpy a d
cpy 0 a
cpy d c
inc a
dec c
jnz c -2
dec d
jnz d -5
"""
assert run_assembunny_folded(triangular_prog, 4) == 10
```

Notice the extra guards `len({acc, c1, outer, src}) == 4` and positive loop counts in the pattern match — ensuring aliased registers (such as `cpy d c` computing a triangular sum) or non-positive counters fall back cleanly to single-step execution.

### Backward 3-Bit DFS Decompilation

Sometimes the inner loop is already fast, yet Part 2 asks you to invert a 16-stage output program over trillions of candidates. That is the exact twist in [2024 Day 17](/2024/) (*Chronospatial Computer*, in [`Dazbo's_Advent_of_Code_2024.ipynb`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}).

When you translate the bytecode instructions by hand into plain Python, a striking structure emerges:

1. Every pass of the `while a:` loop computes one 3-bit output digit purely from the current value of `A` (`B` and `C` are overwritten inside each iteration, never carried across iterations).
2. At the end of the pass, `A` is right-shifted by three bits (`a >>= 3`, equivalent to `adv 3`), and the loop halts when `A == 0`.

For a 16-digit program, the initial `A` must therefore be a 46-to-48-bit integer (`8**15` up to `8**16 - 1`). Counting upwards from `1` is hopeless — yet working **backwards** from the final digit turns `8**16` possibilities into a tiny tree of 3-bit choices (`0..7`) per digit!

At the final output digit, `A` becomes `0` right after the shift, meaning the previous `A` was `(0 << 3) | d` for some `d` in `0..7`. Working from `len(program) - 1` down to `0`, we test each candidate `(current_a << 3) | octet` against the decompiled single-pass `step_output(candidate)` function and recurse with DFS whenever it matches `program[index]`:

```python
def find_quine_a(program: list[int]) -> int | None:
    """Reconstruct the lowest positive initial A for sample 0,3,5,4,3,0 via backward DFS."""

    def step_output(a: int) -> int:
        return (a >> 3) & 7

    def dfs(index: int, current_a: int) -> int | None:
        if index < 0:
            return current_a
        target = program[index]
        for octet in range(8):
            candidate = (current_a << 3) | octet
            if candidate == 0:
                continue
            if step_output(candidate) == target:
                found = dfs(index - 1, candidate)
                if found is not None:
                    return found
        return None

    return dfs(len(program) - 1, 0)


assert find_quine_a([0, 3, 5, 4, 3, 0]) == 117440
```

Because `dfs()` tries `octet` in ascending `0..7` order, the very first leaf that reaches `index < 0` is guaranteed to be the **lowest** valid positive `A`. Even when the loop body scrambles `B` and `C` with bitwise shifts and XORs — where high bits of `A` influence the output of lower octets — backtracking with DFS handles dead ends automatically:

```python
def run_scrambled(a: int) -> list[int]:
    """Synthetic 3-bit XOR-shifted loop emulating a Chronospatial kernel."""
    out: list[int] = []
    while a:
        b = (a & 7) ^ 3
        c = a >> b
        b = b ^ c ^ 5
        out.append(b & 7)
        a >>= 3
    return out


def find_scrambled_a(program: list[int]) -> int | None:
    """Reconstruct smallest A for the synthetic XOR-shifted 3-bit loop."""

    def step_output(a: int) -> int:
        b = (a & 7) ^ 3
        c = a >> b
        return (b ^ c ^ 5) & 7

    def dfs(index: int, current_a: int) -> int | None:
        if index < 0:
            return current_a
        target = program[index]
        for octet in range(8):
            candidate = (current_a << 3) | octet
            if candidate == 0:
                continue
            if step_output(candidate) == target:
                found = dfs(index - 1, candidate)
                if found is not None:
                    return found
        return None

    return dfs(len(program) - 1, 0)


sample_target = run_scrambled(42_197)
recovered_a = find_scrambled_a(sample_target)
assert recovered_a is not None
assert recovered_a <= 42_197
assert run_scrambled(recovered_a) == sample_target
```

Notice how `find_scrambled_a` recovers an exact matching seed in microseconds instead of scanning tens of thousands — or tens of trillions — of integers forward.

---

## Boolean Gate Networks and Structural Adder Diagnostics

Advent of Code's other favourite hardware puzzle swaps CPUs and instruction pointers for **wires and combinational logic gates** (`AND`, `OR`, `XOR`, `NOT`, `LSHIFT`, `RSHIFT`).

### Lazy Memoised Evaluation of Combinational Wires

In [2015 Day 7](/2015/7) (*Some Assembly Required*), gate definitions appear in arbitrary order (`x AND y -> d` long before `456 -> y` gives `y` a value). An iterative queue pass works, yet it rescans blocked rules over and over.

Since an acyclic wire graph is just a DAG, turning it inside out with [`@functools.cache`](/python/recursion#optimising-memoisation) evaluates each wire **on demand and at most once**. Remember one Python bitwise gotcha from [Working with Binary and Other Bases](/python/binary): Python integers have arbitrary precision, so `~x` produces negative values unless masked with `& 0xFFFF` for 16-bit wires.

```python
from functools import cache


def evaluate_circuit(lines: list[str]) -> dict[str, int]:
    """Build and lazily evaluate a 16-bit combinational gate circuit."""
    expressions: dict[str, list[str]] = {}
    for line in lines:
        expr, target = line.split(" -> ")
        expressions[target] = expr.split()

    @cache
    def eval_wire(token: str) -> int:
        if token.isdigit():
            return int(token)
        match expressions[token]:
            case [src]:
                return eval_wire(src)
            case ["NOT", src]:
                return ~eval_wire(src) & 0xFFFF
            case [left, "AND", right]:
                return eval_wire(left) & eval_wire(right)
            case [left, "OR", right]:
                return eval_wire(left) | eval_wire(right)
            case [left, "LSHIFT", shift]:
                return (eval_wire(left) << int(shift)) & 0xFFFF
            case [left, "RSHIFT", shift]:
                return eval_wire(left) >> int(shift)
            case other:
                raise ValueError(f"Unsupported gate expression: {other}")

    return {wire: eval_wire(wire) for wire in expressions}


day7_sample = [
    "123 -> x",
    "456 -> y",
    "x AND y -> d",
    "x OR y -> e",
    "x LSHIFT 2 -> f",
    "y RSHIFT 2 -> g",
    "NOT x -> h",
    "NOT y -> i",
]
circuit = evaluate_circuit(day7_sample)
assert circuit["d"] == 72
assert circuit["h"] == 65412
```

### Validating a Ripple-Carry Adder by Gate Role

Nearly a decade after 2015 Day 7, [2024 Day 24](/2024/) (*Crossed Wires*) used the exact same wire-evaluation model in Part 1, then dropped a classic hardware debugging challenge in Part 2: the circuit is supposed to be a multi-bit **ripple-carry adder** computing `z = x + y`, except four pairs of gate output wires have been swapped.

![1-bit full adder inputs, sum, and carry chain](/assets/images/1-bit-fa.png)

Chaining 1-bit full adders together creates the multi-bit ripple-carry topology below — every carry output `C_{n-1}` feeds directly into bit `n`:

![4-bit ripple-carry full adder topology](/assets/images/ripple-adder.png)

Why can't we brute-force all swaps? With roughly 220 gates, picking 8 wires out of 220 is `220 choose 8` — tens of trillions of combinations. Instead, look at the **structural invariants** that every clean ripple-carry full adder obeys:

- **Sum and final carry outputs**: `S_n = (x_n ^ y_n) ^ C_{n-1}`, so every `z_n` output wire (`n < max`) must come from `XOR`, while the final carry-out `z_max` must come from `OR` (with bit 0 computed directly as `z00 = x00 ^ y00`).
- **Internal `XOR` placement**: Any `XOR` gate whose inputs are *not* direct `x_n` / `y_n` wires is computing `S_n` (`n > 0`), so it must output to a `z_n` wire (`!= z00`).
- **Half-sum and intermediate carry fan-out**: Both the half-sum `h_n = x_n ^ y_n` (`n > 0`) and every non-final carry wire `C_n` (`OR` gate not driving `z_max`) have exact consumer set `{"XOR", "AND"}`.
- **Carry `AND` fan-out**: Both carry terms `g_n = x_n & y_n` and `p_n = h_n & C_{n-1}` (`n > 0`) must have consumer set `{"OR"}`, whereas bit-0 carry `c00 = x00 & y00` has consumer set `{"XOR", "AND"}`.

Checking those four topological rules over the static gate list finds every crossed output wire in `O(G)` linear time — without simulating a single test vector:

```python
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Gate:
    """Two-input combinational logic gate."""

    left: str
    op: str
    right: str
    out: str


def find_swapped_adder_wires(gates: list[Gate], highest_z: str) -> list[str]:
    """Flag wires violating 4-rule ripple-carry full-adder topology."""
    consumers: dict[str, set[str]] = defaultdict(set)
    for g in gates:
        consumers[g.left].add(g.op)
        consumers[g.right].add(g.op)

    suspicious: set[str] = set()
    for g in gates:
        inputs = {g.left, g.right}
        is_xy = all(w[0] in ("x", "y") and w[1:].isdigit() for w in inputs)
        is_bit0 = "x00" in inputs and "y00" in inputs

        # Rule 1: z_n outputs must come from XOR, except final carry-out highest_z (from OR).
        expected_z_op = "OR" if g.out == highest_z else "XOR"
        if g.out.startswith("z") and g.op != expected_z_op:
            suspicious.add(g.out)

        # Rule 2: Non-x/y XORs must drive z_n (n > 0); bit-0 XOR(x00, y00) must drive z00.
        if g.op == "XOR" and (
            (not is_xy and (not g.out.startswith("z") or g.out == "z00"))
            or (is_bit0 and g.out != "z00")
        ):
            suspicious.add(g.out)

        # Rule 3: Half-sum XOR(x_n, y_n) (n > 0) and non-final carry OR must feed {XOR, AND}.
        if (
            (g.op == "XOR" and is_xy and not is_bit0)
            or (g.op == "OR" and g.out != highest_z)
        ) and consumers[g.out] != {"XOR", "AND"}:
            suspicious.add(g.out)

        # Rule 4: Bit-0 carry AND feeds {XOR, AND}; all other AND gates must feed {OR}.
        expected_and_consumers = {"XOR", "AND"} if is_bit0 else {"OR"}
        if g.op == "AND" and consumers[g.out] != expected_and_consumers:
            suspicious.add(g.out)

    return sorted(suspicious)


valid_adder_lines = [
    ("x00", "XOR", "y00", "z00"),
    ("x00", "AND", "y00", "c00"),
    ("x01", "XOR", "y01", "h01"),
    ("h01", "XOR", "c00", "z01"),
    ("x01", "AND", "y01", "g01"),
    ("h01", "AND", "c00", "p01"),
    ("g01", "OR", "p01", "c01"),
    ("x02", "XOR", "y02", "h02"),
    ("h02", "XOR", "c01", "z02"),
    ("x02", "AND", "y02", "g02"),
    ("h02", "AND", "c01", "p02"),
    ("g02", "OR", "p02", "z03"),
]
clean_gates = [Gate(l_w, op, r_w, out) for l_w, op, r_w, out in valid_adder_lines]
assert find_swapped_adder_wires(clean_gates, highest_z="z03") == []

for swap_map, expected in (
    ({"z01": "c01", "c01": "z01"}, ["c01", "z01"]),
    ({"h01": "z02", "z02": "h01"}, ["h01", "z02"]),
    ({"g02": "z03", "z03": "g02"}, ["g02", "z03"]),
    ({"c01": "g02", "g02": "c01"}, ["c01", "g02"]),
):
    broken_gates = [Gate(l_w, op, r_w, swap_map.get(out, out)) for l_w, op, r_w, out in valid_adder_lines]
    assert find_swapped_adder_wires(broken_gates, highest_z="z03") == expected
```

Pair structural rule checking with a quick recursive graph print (or Graphviz plot, as in [`Dazbo's_Advent_of_Code_2024.ipynb`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"}) and hardware faults jump right off the page.

---

## AoC Examples

| Puzzle | Machine / Circuit Style | Key Part 2 Technique | Walkthrough / Code |
| :--- | :--- | :--- | :--- |
| **2015 Day 7** | 16-bit bitwise logic DAG | Memoised recursive wire evaluation + `0xFFFF` mask | [2015 Day 7](/2015/7) |
| **2015 Day 23** | Two-register CPU (`hlf`/`tpl`/`jio`/`jie`) | Clean `ip` dispatch and initial register override | [2015 Day 23](/2015/23) |
| **2016 Day 12** | Assembunny 4-register VM | Register vs immediate `arg()` resolution | [2016 Day 12](/2016/12) |
| **2016 Day 23** | Self-modifying Assembunny (`tgl`) | Runtime peephole multiply-accumulate folding | [2016 Day 23](/2016/23) |
| **2016 Day 25** | Clock-signal Assembunny (`out`) | Lazy `yield` stream + early prefix verification | [2016 Day 25](/2016/25) |
| **2020 Day 8** | Handheld boot console (`acc`/`jmp`/`nop`) | Visited-state loop detection + single-op patching | [2020 Index](/2020/) / [`runboot.py`](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d08_basic_CPU_sim/runboot.py){:target="_blank"} |
| **2021 Day 24** | 14-block MONAD ALU (`w`/`x`/`y`/`z`) | Decompiling repeating blocks into base-26 stack constraints | [2021 Day 24](/2021/24) |
| **2022 Day 10** | Cycle-accurate CRT CPU (`noop`/`addx`) | Per-tick generator decoupled from sprite rendering | [2022 Day 10](/2022/10) |
| **2024 Day 17** | 3-bit Chronospatial Computer | Backward 3-bit `(a << 3) | d` DFS decompilation | [2024 Index](/2024/) / [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
| **2024 Day 24** | Crossed Wires ripple-carry adder | Gate-role structural diagnostics (`O(G)`) | [2024 Index](/2024/) / [2024 Notebook](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2024/Dazbo's_Advent_of_Code_2024.ipynb){:target="_blank"} |
