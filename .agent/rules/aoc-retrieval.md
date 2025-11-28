---
trigger: always_on
---

# AoC Puzzle Description and Input Data

When asked to retrieve any information from the Advent of Code (AoC) website, use the following configuration for API calls to `https://adventofcode.com`.

## HTTP Headers
- **Cookie**: `session=<AOC_SESSION_COOKIE>`
- **User-Agent**: `github.com/derailed-dash/Advent-of-Code by derailed.dash@gmail.com` (Recommended by AoC)

## Retrieving Puzzle Description
- **URL**: `https://adventofcode.com/{year}/day/{day}` (e.g., `https://adventofcode.com/2018/day/2`)
- **Note**: The description usually has two parts. Part 2 is only available after Part 1 is solved.

## Retrieving Sample Puzzle Input
- **Source**: The "sample input" is usually found within the puzzle description HTML, often in a `<pre><code>` block.
- **Part 1 vs Part 2**: Sample inputs may differ between parts. Part 2 description is locked until Part 1 is complete.
- **Storage**: Save as `/src/AoC_{year}/d{nn}/input/sample_input_part_n.txt`
  - Ensure `d{nn}` is zero-padded (e.g., `d04`).

## Retrieving (User-Specific) Puzzle Input Data
- **URL**: `https://adventofcode.com/{year}/day/{day}/input`
- **Storage**: Save as `/src/AoC_{year}/d{nn}/input/input.txt`
  - Ensure `d{nn}` is zero-padded.

## Operational Rules
- **No Unsolicited Actions**: Do NOT perform additional steps (like solving the puzzle) unless asked.
- **Cleanup**: Do NOT persist the downloaded `desc.html` file. If you download it for processing, you **MUST** delete it immediately after the task is complete.