# Advent of Code 2018 — Day 7: The Sum of Its Parts (Part 1)

## Problem Intro

Having landed slightly off course on a snowy coastline in the year **1018**, we spot a group of Elves unpacking a mysterious crate that washed ashore. Handily, our wrist device seems to double as an Ancient Nordic Elvish translator (and the Elves kindly lend us a heavy coat so we don't freeze).

Inside the crate is something destined to solve all of Santa's transport headaches: **"Sleigh kit. Some assembly required."** Essentially 11th-century flat-pack furniture — minus the little Allen key — and since the Elves can't read the manual, we're in charge of assembly.

The instructions list a series of single-letter **steps** and the dependency rules stating which steps must be finished before others can begin. For example:

```text
Step C must be finished before step A can begin.
Step C must be finished before step F can begin.
Step A must be finished before step B can begin.
Step A must be finished before step D can begin.
Step B must be finished before step E can begin.
Step D must be finished before step E can begin.
Step F must be finished before step E can begin.
```

## Dependency & Tie-Breaking Rules

- A step becomes **available** only once **all** of its prerequisite steps have been completed:

| Step | Prerequisites |
| :---: | :--- |
| `C` | *(none — ready immediately)* |
| `A` | `C` |
| `F` | `C` |
| `B` | `A` |
| `D` | `A` |
| `E` | `B`, `D`, `F` *(all three required)* |

- **Alphabetical tie-breaker**: Whenever more than one step is ready at the same time, we must always pick the step that comes **first alphabetically**.

Walking through the example above:
1. Only **`C`** has no prerequisites, so **`C`** goes first (unlocking `A` and `F`).
2. Between `{A, F}`, **`A`** comes first alphabetically, so **`A`** goes next (unlocking `B` and `D`).
3. Available steps are now `{B, D, F}` — even though `F` has been waiting since step 1, **`B`** wins alphabetically.
4. From `{D, F}` (`E` is still waiting on `D` and `F`), **`D`** goes next.
5. Only **`F`** is left, which finally unlocks **`E`**.
6. **`E`** finishes last, giving the step order **`CABDFE`**.

## Part 1 Goal

**In what order should the steps in your instructions be completed?**
