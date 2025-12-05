"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/5

Our input contains two blocks:
- Fresh ingredient ID ranges (inclusive)
- Available ingedient IDs

Part 1:

How many of the available ingredient IDs are fresh?

Solution:

- Simply check if each available ID is within any of the fresh ingredient ID ranges.

Part 2:

How many ingredient IDs are considered to be fresh 
according to the fresh ingredient ID ranges?

The problem is that the ranges are overlapping.

Solution:

- If the ID ranges were smaller, we could use set intersection.
  Unfortunately, the ranges are far too large.
- So we need to merge intervals.

"""
import logging
import sys
import textwrap

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 5

locations = dc.get_locations(__file__)

# Configure root logger with Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(message)s",
    datefmt='%H:%M:%S',
    handlers=[RichHandler(
        rich_tracebacks=True, 
        show_path=False,
        markup=True,
        show_time=False  # Disable Rich's time since we're using our own
    )]
)
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

def parse_input(data: str):
    """Parse the input data into two blocks:
    - inclusive ranges (list of [start, end])
    - and available IDs (list of IDs)
    """
    inclusive_ranges, available_ids = data.split("\n\n")
    inclusive_ranges = [list(map(int, line.split("-"))) for line in inclusive_ranges.splitlines()]
    available_ids = list(map(int, available_ids.splitlines()))

    return inclusive_ranges, available_ids

def part1(data: str):
    """ How many of the available ingredient IDs are fresh? """
    inclusive_ranges, available_ids = parse_input(data)
    logger.debug(inclusive_ranges)
    logger.debug(available_ids)

    # Check if each available ID is within any of the fresh ingredient ID ranges
    fresh_ids = [id for id in available_ids 
                 if any(id >= start and id <= end for start, end in inclusive_ranges)]

    return len(fresh_ids)

def merge_intervals(intervals: list[list]) -> list[list]:
    """ 
    Takes intervals in the form [[a, b][c, d][d, e]...]
    Intervals can overlap. Compresses to minimum number of non-overlapping intervals. 
    """
    intervals.sort() # Sort intervals by start; if same start, sort by end
    stack = []
    stack.append(intervals[0])
    
    # First interval already added. Process the rest.
    for interval in intervals[1:]:
        # Check for overlapping interval
        if stack[-1][0] <= interval[0] <= stack[-1][-1]:
            stack[-1][-1] = max(stack[-1][-1], interval[-1])
        else:
            stack.append(interval)
      
    return stack

def part2(data: str):
    """ 
    How many ingredient IDs are considered to be fresh 
    according to the fresh ingredient ID ranges?

    The provided ranges are overlapping, so we can't simply count the size of each range.
    And we can't use set algebra because the input ranges are too large.
    E.g. ranges like this: 302553299774028-302939011277575
    
    So we need to merge these ranges, and then determine their sizes.
    """
    
    # For this part, we don't care about the available IDs
    inclusive_ranges, _ = parse_input(data)
    
    merged_ranges = merge_intervals(inclusive_ranges)
    logger.debug(merged_ranges)

    total_fresh_ids = sum(end - start + 1 for start, end in merged_ranges)
    return total_fresh_ids

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().strip() # Raw string
            logger.debug(dc.top_and_tail(input_data))
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        3-5
        10-14
        16-20
        12-18

        1
        5
        8
        11
        17
        32"""))
    sample_answers = [3]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [14]
    test_solution(part2, sample_inputs, sample_answers)
     
    # Part 2 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 2 soln={part2(input_data)}")

def test_solution(soln_func, sample_inputs: list, sample_answers: list):
    """
    Tests a solution function against multiple sample inputs and expected answers.

    Args:
        soln_func: The function to be tested (e.g., part1 or part2).
        sample_inputs: A list of sample input strings.
        sample_answers: A list of expected answers corresponding to the sample inputs.

    Raises:
        AssertionError: If any of the test cases fail validation.
    """
    for curr_input, curr_ans in zip(sample_inputs, sample_answers):
        try:
            ac.validate(soln_func(curr_input), curr_ans)
        except AssertionError as e:
            logger.error(f"{soln_func.__name__} test failed: {e}")
            sys.exit(1)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
