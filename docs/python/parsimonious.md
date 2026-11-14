---
title: Parsing with Parsimonious
description: "Declarative PEG grammar parsing in Advent of Code using Parsimonious — Grammar syntax, typed NodeVisitor traversal, error handling, and performance trade-offs."
tags:
  - name: Parsimonious (GitHub)
    link: https://github.com/erikrose/parsimonious
  - name: Parsing Expression Grammar (Wikipedia)
    link: https://en.wikipedia.org/wiki/Parsing_expression_grammar
  - name: Regular Expressions
    link: /python/regex
  - name: Recursion
    link: /python/recursion
---

## Page Contents

- [When Regex Isn't Enough](#when-regex-isnt-enough)
- [Installation](#installation)
- [Defining a PEG Grammar](#defining-a-peg-grammar)
- [Evaluating Parse Trees with `NodeVisitor`](#evaluating-parse-trees-with-nodevisitor)
- [Validation Without a Visitor](#validation-without-a-visitor)
- [Trade-Offs: PEG vs Hand-Rolled Parsers](#trade-offs-peg-vs-hand-rolled-parsers)
- [AoC Examples](#aoc-examples)

## When Regex Isn't Enough

[Regular expressions](/python/regex) are brilliant for flat, single-line patterns such as `"Step A must be finished before step B"`. Where regex breaks down is **arbitrarily nested or recursive structure**: balanced brackets inside brackets, parenthesised maths with custom operator precedence, or self-referential message rules.

A **Parsing Expression Grammar (PEG)** lets you write grammar rules declaratively — including recursive rules that refer back to themselves — and then either validate input strings or transform the resulting parse tree into Python values.

[Parsimonious](https://github.com/erikrose/parsimonious){:target="_blank"} is a lightweight Python PEG library that acts like regex with superpowers:

- **Ordered choice (`/`)**: Tries alternatives left-to-right and commits cleanly to the first match (unlike context-free ambiguities).
- **Familiar quantifiers**: `?` (optional), `*` (zero or more), `+` (one or more), and `~r"..."` inline regex terminals.
- **Explicit AST evaluation**: Subclass `NodeVisitor` and define `visit_<rule_name>()` methods to evaluate each grammar node bottom-up.

## Installation

`parsimonious` is already declared in [`pyproject.toml`](https://github.com/derailed-dash/Advent-of-Code/blob/master/pyproject.toml){:target="_blank"} (installed automatically via `make install`). To add it to a separate `uv` project:

```bash
uv add parsimonious
```

## Defining a PEG Grammar

Suppose a puzzle gives us nested expressions using `+` and `*`, where brackets `(...)` can nest to any depth:

```python
from parsimonious.grammar import Grammar

EXPR_GRAMMAR = Grammar(
    r"""
    expr               = term (op term)*
    term               = brackets / number
    brackets           = "(" ws? expr ws? ")"
    op                 = ws? ~r"[+*]" ws?
    number             = ~r"\d+"
    ws                 = ~r"\s+"
    """
)
```

Notice the key building blocks:

- **Left-to-right ordered choice**: `term = brackets / number` tries `brackets` first; only if no `(` matches does it try `number`.
- **Mutual recursion**: `brackets` references `expr`, which references `term`, which can match `brackets` again cleanly.
- **Whitespace rules**: Naming an optional whitespace terminal (`ws = ~r"\s+"`) keeps rules readable instead of scattering `\s*` everywhere.

## Evaluating Parse Trees with `NodeVisitor`

`grammar.parse(line)` returns a tree of `Node` objects. Rather than walking raw children manually, subclass `NodeVisitor` and implement one method per rule name (`visit_<rule>`).

Here is a clean Python `>=3.13` `NodeVisitor` adapted from [2020 Day 18](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d18_weird_maths_peg_and_int_subclass/weird_maths_using_peg.py){:target="_blank"}, evaluating `+` and `*` strictly left-to-right (Part 1), and then subclassing it to give `+` higher precedence than `*` (Part 2):

```python
from __future__ import annotations

import math
from typing import Any

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

EXPR_GRAMMAR = Grammar(
    r"""
    expr     = term (op term)*
    term     = brackets / number
    brackets = "(" ws expr ws ")"
    op       = ws ~r"[+*]" ws
    number   = ~r"\d+"
    ws       = ~r"\s*"
    """
)


class LeftToRightVisitor(NodeVisitor):
    """Evaluate nested arithmetic expressions strictly from left to right."""

    def visit_expr(self, _node: Node, visited_children: list[Any]) -> int:
        first_val, rest = visited_children
        total = int(first_val)
        for op, rhs in rest:
            total = total + rhs if op == "+" else total * rhs
        return total

    def visit_term(self, _node: Node, visited_children: list[Any]) -> int:
        return int(visited_children[0])

    def visit_brackets(self, _node: Node, visited_children: list[Any]) -> int:
        # Children: '(', ws, expr, ws, ')'
        return int(visited_children[2])

    def visit_op(self, node: Node, _visited_children: list[Any]) -> str:
        return node.text.strip()

    def visit_number(self, node: Node, _visited_children: list[Any]) -> int:
        return int(node.text)

    def generic_visit(self, node: Node, visited_children: list[Any]) -> Any:
        return visited_children or node


class AdditionFirstVisitor(LeftToRightVisitor):
    """Override only expr evaluation to apply addition before multiplication."""

    def visit_expr(self, _node: Node, visited_children: list[Any]) -> int:
        first_val, rest = visited_children
        product_terms = [int(first_val)]
        for op, rhs in rest:
            if op == "+":
                product_terms[-1] += rhs
            else:
                product_terms.append(rhs)
        return math.prod(product_terms)


visitor = AdditionFirstVisitor()
assert visitor.visit(EXPR_GRAMMAR.parse("((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6)")) == 11664
```

Why this pattern is so clean:

- Putting `ws = ~r"\s*"` once into the grammar eliminates repeated `.strip()` boilerplate everywhere else.
- Unpacking `first_val, rest = visited_children` (instead of indexing opaque nested arrays) makes rule structure self-documenting.
- Extending `LeftToRightVisitor` lets Part 2 reuse every leaf rule untouched and override only `visit_expr`.

## Validation Without a Visitor

Sometimes you don't need to build a value from the parse tree at all — you only care **whether** an input line obeys the grammar, and **where** it failed if not.

Parsimonious distinguishes two failure exceptions cleanly:

- `IncompleteParseError`: A prefix of the input matched `expr`, so more characters remain unconsumed (useful for detecting valid-so-far truncated inputs).
- `ParseError`: Matching failed at `err.pos` (`0 <= err.pos <= len(text)`). When `err.pos == len(text)`, the parser reached the end of input expecting a closing token (incomplete); when `err.pos < len(text)`, it encountered an unexpected token (corrupted).

```python
from parsimonious.exceptions import IncompleteParseError, ParseError
from parsimonious.grammar import Grammar

CHUNK_GRAMMAR = Grammar(
    r"""
    expr   = chunk+
    chunk  = round / square / curly / angle
    round  = "(" chunk* ")"
    square = "[" chunk* "]"
    curly  = "{" chunk* "}"
    angle  = "<" chunk* ">"
    """
)


def classify_bracket_line(line: str) -> str:
    """Return 'valid', 'incomplete', or 'corrupted' for a bracket sequence."""
    try:
        CHUNK_GRAMMAR.parse(line)
    except IncompleteParseError:
        return "incomplete"
    except ParseError as err:
        return "incomplete" if err.pos == len(line) else f"corrupted@{err.pos}"
    return "valid"
```

*(Watch out for left recursion in PEG grammars! Rules like `A = A "x" / "y"` recurse infinitely in top-down PEG parsers because ordered choice tries `A` before consuming input. Rewrite left-recursive rules using repetition `A = "y" "x"*` or right-hand grouping `A = "42" A / "42"` — or bounded expansion where depth is finite.)*

## Trade-Offs: PEG vs Hand-Rolled Parsers

Parsimonious shines during fast prototyping when a puzzle defines a miniature DSL or complex rule set — letting you express the grammar in 10 lines instead of 60 lines of tokenizer boilerplate. That expressiveness comes with constant-factor overhead from building full parse trees on every line. In [2021 Day 10](/2021/10), validating brackets via PEG took measurably longer than a simple LIFO stack (`collections.deque`) once syntax errors were checked at scale. Use Parsimonious to get clarity and correctness fast; swap to a tight stack or state machine only if profiling shows parsing is your bottleneck.

## AoC Examples

- [Bitwise logic gates parsed with Grammar + `NodeVisitor` — 2015 Day 7](/2015/7)
- [Custom `+`/`*` operator precedence via subclassed `NodeVisitor` — 2020 Day 18](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d18_weird_maths_peg_and_int_subclass/weird_maths_using_peg.py){:target="_blank"}
- [Translating puzzle rules directly into a Parsimonious grammar — 2020 Day 19](https://github.com/derailed-dash/Advent-of-Code/blob/master/src/AoC_2020/d19_peg_message_processing/monster_message_PEG.py){:target="_blank"}
- [Bracket syntax validation (`IncompleteParseError` vs `ParseError`) — 2021 Day 10](/2021/10)
