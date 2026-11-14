---
title: Opening and Reading Files
description: Modern file I/O in Python 3.13+, path handling with pathlib, block parsing, and the automated Advent of Code input retrieval workflow.
tags: 
  - name: Context Manager
    link: https://www.geeksforgeeks.org/context-manager-in-python/
  - name: pathlib Documentation
    link: https://docs.python.org/3/library/pathlib.html
---
Almost every challenge in Advent of Code requires you to read and parse some input data. Perhaps the easiest approach to get this data into your Python program is to save the supplied input data as a file. You can then read that file in your program.

## Organising Your Input Files

Generally, each AoC day works with two types of data:

1. **Sample data**: Most AoC problems provide one or more small example inputs in the puzzle description, which are much simpler and smaller than the real data. It is always best practice to build and test your solution against this sample data first.
2. **Actual puzzle data**: The actual input data is unique to your Advent of Code user account. Consequently, different AoC participants will solve the problem using different inputs and answers.

In older AoC years, participants had to manually create empty text files and copy-paste values from the browser. In our modern repository workflow, this is automated:

- `uv run aoc fetch <target> --write-sample` fetches the problem description in memory, saves the top-ranked example into `input/sample_input_part_1.txt`, and caches `input/input.txt` lazily.
- We deliberately avoid committing empty `input.txt` placeholder files to version control.

## Reading The Data

Reading a text file in Python involves three steps:

1. Open the file.
2. Read the contents.
3. Close the file.

### Opening the File

Python provides a built-in `open()` function for opening files. When you open a file, you should tell Python:

- What mode to use: reading (`r`), writing (`w`), or appending (`a`), combined with text (`t`) or binary (`b`). For AoC text inputs, use mode `"rt"`.
- The text encoding: always specify `encoding="utf-8"` explicitly to prevent platform-dependent encoding bugs (such as Windows default CP-1252 decoding errors).

```python
f = open(input_file, mode="rt", encoding="utf-8")
```

### Reading the File

The object returned by `open()` is a file-like stream object. There are a few different ways we can read and transform the data:

```python
# 1. Read all the data in one go as a single str
raw_data = f.read()
```

```python
# 2. Split the data at each newline to obtain a list of strings
data_lines = f.read().splitlines()

# Process line by line:
for line in data_lines:
    # do something with line
    pass
```

### Reading Blocks and Paragraphs

Many AoC puzzles present input grouped into distinct "blocks" or paragraphs separated by double newlines (`\n\n`), such as bingo cards, navigation maps, or batches of rules.

To parse block-structured input cleanly, strip trailing whitespace and split on `"\n\n"`:

```python
blocks = raw_data.strip().split("\n\n")
```

Here is an example inspired by 2023 Day 5 where the input has a header followed by multiple mapping tables:

```text
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15
```

We can unpack the first block into the seeds list, and collect the remaining blocks with `*blocks`:

```python
def parse_data(data: str) -> tuple[list[int], list[GardinerMap]]:
    """Parse input data into seeds and GardinerMap instances."""
    seeds_line, *blocks = data.strip().split("\n\n")
    assert seeds_line.startswith("seeds"), "First line must contain seeds values"
    
    _, seeds_part = seeds_line.split(":")
    seeds = [int(x) for x in seeds_part.split()]
    
    maps: list[GardinerMap] = []
    for block in blocks:
        block_header, *block_records = block.splitlines()
        map_src_type, _, map_dest_type = block_header.split()[0].split("-")
        gardiner_map = GardinerMap(map_src_type, map_dest_type)
        
        for line in block_records:
            assert line[0].isdigit(), "Line must start with numbers"
            dest_start, src_start, interval_len = [int(x) for x in line.split()]
            gardiner_map.add_range(src_start=src_start, dest_start=dest_start, range_length=interval_len)
        
        gardiner_map.finalise()
        maps.append(gardiner_map)
            
    return seeds, maps
```

Extended iterable unpacking (`seeds_line, *blocks = ...`) is an expressive Python idiom: one variable captures the leading block, and `*blocks` captures the remainder as a list.

### Closing the File

Having read all the data, you should always close the file:

```python
f.close()
```

### Exception Handling

During file operations, errors can easily happen — the file might not exist, permissions might be restricted, or the disk might be unreadable. Your program should handle these situations gracefully. Fortunately, Python makes this effortless with context managers!

## The Better Way: Context Managers

Python provides the `with` statement (a context manager) for file operations:

```python
with open(input_file, mode="rt", encoding="utf-8") as f:
    data = f.read().splitlines()
```

When the `with` block exits, Python guarantees that the file stream is closed immediately — even if an unhandled exception is raised inside the block.

Alternatively, for simple whole-file reads where you don't need a stream handle, Python's `pathlib.Path` offers a concise one-liner:

```python
from pathlib import Path

raw_data = Path(input_file).read_text(encoding="utf-8")
```

## File Locations and Paths with pathlib

Always keep file paths relative to your script rather than assuming the current working directory of your terminal shell:

```python
from pathlib import Path

# Build paths using pathlib's / operator
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "input" / "input.txt"

with open(INPUT_FILE, mode="rt", encoding="utf-8") as f:
    data = f.read().splitlines()
```

Using `pathlib.Path` with the `/` operator is cross-platform, handling Windows and POSIX path separators transparently without brittle string concatenation.

## The Modern AoC Workflow (Template v3)

In our repository's [Template v3](/python/my-aoc-template3), path resolution and file handling are integrated into the execution lifecycle via `aoc_common`:

```python
import aoc_common.aoc_commons as ac

YEAR: int = 2026
DAY: int = 1

# Automatically resolves script_dir, input_dir, and input_file
locations = ac.get_aoc_locations(YEAR, DAY, __file__)

# Define declarative sample assertions (file paths or inline strings)
PART1_SAMPLES: list[ac.SampleInput] = [
    (locations.input_dir / "sample_input_part_1.txt", 142),
    ("1abc2\npqr3stu8vwx\na1b2c3d4e5f\ntreb7uchet", 142),
]
```

Key advantages of this architecture:

1. **Sample validation first**: Run `uv run aoc run <target> -s` to test your parser and logic against sample inputs before touching real data.
2. **Lazy retrieval**: You never need empty `input.txt` placeholders. When you run against real input (`uv run aoc run <target>`), the runner checks if `input/input.txt` exists. If not (and if `AOC_SESSION_COOKIE` is configured in `.env`), it downloads and caches your puzzle input automatically.
3. **Fresh parsing per part**: The runner passes fresh `raw` text to `parse_input(raw)` before each sample and each puzzle part, ensuring in-place mutations in Part 1 can never contaminate Part 2.
