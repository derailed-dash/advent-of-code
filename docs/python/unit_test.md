---
title: Unit Testing
description: Unit testing in Python with pytest, unittest, and Template v3 declarative sample validation for Advent of Code.
tags: 
  - name: Unit Testing in Python
    link: https://realpython.com/python-testing/
  - name: pytest Documentation
    link: https://docs.pytest.org/
  - name: Assertion
    link: /python/assertion
---
## Page Contents

- [Why Unit Test?](#why-unit-test)
- [Testing in This Repository](#testing-in-this-repository)
- [Declarative Sample Validation in Template v3](#declarative-sample-validation-in-template-v3)
- [The Repository Test Suite with pytest](#the-repository-test-suite-with-pytest)
- [The Python unittest Framework](#the-python-unittest-framework)
  - [Overview](#overview)
  - [Assertion Methods](#assertion-methods)
  - [Example: Testing with unittest.TestCase](#example-testing-with-unittesttestcase)

## Why Unit Test?

Unit tests are small, automated, repeatable tests that execute an isolated component of our code and [assert](/python/assertion) that the code produces the expected result.

Unit tests are quick to execute. We use them to:

- Validate that components of our code behave as expected.
- Prove that bug fixes work.
- Ensure we haven't broken existing functionality when refactoring.

## Testing in This Repository

In this repository, testing is structured across two complementary tiers:

1. **Declarative Sample Validation**: Each daily solution embeds sample inputs and expected answers directly in the module using [Template v3](/python/my-aoc-template3). The shared runner validates these before running against real data.
2. **Repository Test Suite**: Offline tests in `src/tests/` verify shared libraries, grid primitives, and CLI mechanics via `pytest`.

Rather than creating dozens of bespoke `test_dayXX.py` files for every puzzle day, Template v3's declarative approach provides instant test feedback with zero extra file clutter.

## Declarative Sample Validation in Template v3

In [Template v3](/python/my-aoc-template3), each solution defines sample inputs and expected answers using `ac.SampleInput` tuples:

```python
import aoc_common.aoc_commons as ac

locations = ac.get_aoc_locations(YEAR, DAY, __file__)

# Define (sample_source, expected_answer) pairs:
# sample_source can be a Path to an input file or an inline string.
PART1_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", 142),
    ("1abc2\npqr3stu8vwx\na1b2c3d4e5f\ntreb7uchet", 142),
]
PART2_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", 281),
]
```

When you run your puzzle:

```bash
# Validate sample assertions only (using DEBUG logging):
uv run aoc run 2025d01 -s

# Run against real input (automatically checks samples first):
uv run aoc run 2025 1
```

Under the hood, `ac.check_samples()` runs each sample through `parse_input(raw)` and passes the parsed data to `part1()` or `part2()`. If an assertion fails, the runner reports the difference immediately and halts execution before touching your real puzzle input. (You can bypass sample checking when desired with `--no-samples`.)

## The Repository Test Suite with pytest

The repository's shared utilities (`Point`, `Grid`, `to_base_n`, interval merging, locked `git-crypt` detection, and CLI argument parsing) live in `src/aoc_common/`. Their unit tests reside in `src/tests/` and are executed offline using `pytest`:

```bash
# Run the test suite:
uv run pytest src/tests

# Run the complete offline verification gate (linting + tests):
make check
```

Because `pytest` discovers and executes both standard Python test functions (`def test_*(): ...`) and `unittest.TestCase` classes, it integrates smoothly with existing test suites.

## The Python unittest Framework

Python includes a built-in `unittest` package in its standard library. Knowing how `unittest` works is a core Python skill.

### Overview

To create a `unittest` suite:

- `import unittest`
- Create a test case class that inherits from `unittest.TestCase`.
- Optionally implement a `setUp()` method in your class. If present, it executes before every single test method to initialise fresh test data and fixtures.
- Implement one or more `test_*()` methods containing assertions.
- Run the suite:

```python
if __name__ == "__main__":
    unittest.main()
```

### Assertion Methods

| Method | What it does | Example |
| :--- | :--- | :--- |
| `assertTrue(expr)` | Checks that the expression evaluates to `True` | `self.assertTrue(6 in self.items)` |
| `assertFalse(expr)` | Checks that the expression evaluates to `False` | `self.assertFalse(len(items) > 0)` |
| `assertEqual(a, b)` | Checks that `a == b` | `self.assertEqual(len(items), 0)` |
| `assertNotEqual(a, b)` | Checks that `a != b` | `self.assertNotEqual(len(items), 0)` |
| `assertRaises(exc)` | Checks that a code block raises an expected exception | `self.assertRaises(ValueError, lambda: int("abc"))` |

### Example: Testing with unittest.TestCase

Here is how a standalone `unittest` script might test a puzzle module against sample data:

```python
"""Test the Rope Bridge solution against example data."""
from pathlib import Path
import unittest
import rope_bridge  # Import the solution module to test

SAMPLE_INPUT_FILE = Path(__file__).parent / "input" / "sample_input.txt"


class TestRopeBridge(unittest.TestCase):
    """Set up data using sample input and assert correct results."""
    
    def setUp(self) -> None:
        """Load sample data before each test."""
        with open(SAMPLE_INPUT_FILE, mode="rt", encoding="utf-8") as f:
            self.data = [
                (direction, int(steps))
                for direction, steps in (line.split() for line in f.read().splitlines())
            ]
        
    def test_part_1(self) -> None:
        expected = 88
        self.assertEqual(len(rope_bridge.pull_rope(self.data, 2)), expected)
        
    def test_part_2(self) -> None:
        expected = 36
        self.assertEqual(len(rope_bridge.pull_rope(self.data, 10)), expected)


if __name__ == "__main__":
    unittest.main()
```

When you execute this script and all assertions pass:

```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.007s

OK
```

If code changes introduce a bug, `unittest` displays clear diagnostic diffs showing what was expected versus what was returned:

```text
FF
======================================================================
FAIL: test_part_1 (__main__.TestRopeBridge)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_rope_bridge.py", line 22, in test_part_1  
    self.assertEqual(len(rope_bridge.pull_rope(self.data, 2)), expected)
AssertionError: 0 != 88

======================================================================
FAIL: test_part_2 (__main__.TestRopeBridge)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test_rope_bridge.py", line 26, in test_part_2  
    self.assertEqual(len(rope_bridge.pull_rope(self.data, 10)), expected)
AssertionError: 0 != 36

----------------------------------------------------------------------
Ran 2 tests in 0.007s

FAILED (failures=2)
```
