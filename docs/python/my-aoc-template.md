---
title: My AoC Template
description: "Dazbo's original Advent of Code template (Version 1, 2021) — foundational script structure with stdlib logging, manual input paths, and perf_counter timing."
tags:
  - name: My AoC Template, Version 3
    link: /python/my-aoc-template3
  - name: Logging
    link: /python/logging
  - name: Opening and Reading Files
    link: /python/reading_files
---

> **Historical Reference (Template v1, 2021):** This page preserves my original starter script from 2021, which introduced top-of-module docstrings, stdlib `logging`, `pathlib.Path`, and timing around `main()`. For the current production starter with decoupled sample assertions, automatic `DEBUG` switching, `aoc_common`, and the Rich `aoc` CLI runner, see **[My AoC Template, Version 3](/python/my-aoc-template3)**.

I used to start every AoC challenge with this minimal standalone template. It brings together the early foundations from the [Python Journey](/python/) — `pathlib.Path`, structured `logging`, docstrings, and basic wall-clock timing:

```python
"""
Author: Darren
Date: 01/12/2021

Solving https://adventofcode.com/2021/day/1

Solution overview:

"""
import logging
import time
from pathlib import Path

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:\t%(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "input" / "sample_input.txt"
# INPUT_FILE = SCRIPT_DIR / "input" / "input.txt"


def main() -> None:
    """Read input lines and log them for inspection."""
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = f.read().splitlines()

    logger.debug(data)


if __name__ == "__main__":
    t1 = time.perf_counter()
    main()
    t2 = time.perf_counter()
    logger.info("Execution time: %0.4f seconds", t2 - t1)
```

Key Python fundamentals introduced here:

- **Module docstring**: Placed at the very top of the file inside triple quotes so tools and readers immediately understand the script's purpose and puzzle URL.
- **`main()` entry point**: Keeps logic organised inside a function rather than loose top-level statements.
- **`if __name__ == "__main__":` guard**: Distinguishes running the file directly as a standalone script from importing its functions into tests or another module.
- **Timing with `time.perf_counter()`**: Wraps `main()` with a high-resolution monotonic timer to measure total runtime.

When you're ready for the modern architecture — and why each piece of this boilerplate evolved — head over to **[My AoC Template, Version 3](/python/my-aoc-template3)**.
