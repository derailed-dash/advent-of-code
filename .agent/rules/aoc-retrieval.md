---
trigger: always_on
---

# AoC Puzzle Description and Input Data

When asked to retrieve any information from the Advent of Code (AoC) website, make use of my AOC_SESSION_COOKIE and use this when making API calls to https://adventofcode.com.

## Retrieving Puzzle Description

- Puzzle description is available at https://adventofcode.com/{year}/day/{day}, e.g. https://adventofcode.com/2018/day/2
- Note that the puzzle description usually has two parts: part 1 and part 2. Part 2 is only available after Part 1 has been solved.

## Retrieving Sample Puzzle Input

- The "sample input" is usually described within the puzzle description.
- The "sample input" for Part 1 may be different to the sample input for Part 2.
- Remember that Part 2 puzzle description will not be available until Part 1 has been solved.
- Retrieved puzzle input should be saved as /src/AoC_{year}/d{nn}/input/sample_input_part_n.txt.

## Retrieving (User-Specific) Puzzle Input Data

- The user-specific puzzle input data is available at https://adventofcode.com/{year}/day/{day}/input, e.g. https://adventofcode.com/2018/day/2/input
- Retrieved puzzle input should be saved as /src/AoC_{year}/d{nn}/input/input.txt.

## Other Rules

- Do NOT perform any additional steps without first being asked to. For example, do not try and solve the puzzle.
- Do NOT persist any downloaded `desc.html` file.
- Once you have completed the task asked of you, if you have downloaded or created `desc.html`, delete it.