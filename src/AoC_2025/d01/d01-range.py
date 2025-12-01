"""
Author: Darren
Date: 01/12/2025

Solving https://adventofcode.com/2025/day/1

Secret Entrance - Safe Dial Puzzle

The dial has positions 0-99 and starts at 50.
Rotations are specified as L (left/lower) or R (right/higher) followed by steps.

Solution 1 - Simple Simulation
This works fine because the input is small and we're only rotating in the order of hundreds.

Part 1:
    Count how many times the dial ends at position 0 after each rotation.

Part 2:
    Count how many times the dial passes through position 0 during rotations,
    including both intermediate crossings and final positions.
    This requires counting every click that lands on 0, not just the final position.
"""
import logging
import sys
import textwrap

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 1

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

def part1(data: list[str], start: int = 50, dial_nums: int = 100) -> int:
    """
    Count how many times the dial ends at position 0 after each rotation.
    
    Args:
        data: List of rotation instructions (e.g., ['L68', 'R48', ...])
        start: Starting position of the dial (default: 50)
        dial_nums: Number of positions on the dial (default: 100)
    
    Returns:
        Number of times the dial ends at position 0
    """
    zero_counter = 0
    curr_pos = start

    for instruction in data:
        logger.debug(f"instruction={instruction}")
        direction = instruction[0]
        clicks = int(instruction[1:])
        
        if direction == "L":
            clicks = dial_nums - clicks # equivalent to going right this many steps
        
        curr_pos = (curr_pos + clicks) % dial_nums
        logger.debug(f"curr_pos={curr_pos}")

        if curr_pos == 0: # if we end on 0, count it
            zero_counter += 1
    
    return zero_counter

def part2(data: list[str], start: int = 50, dial_nums: int = 100) -> int:
    """
    Count how many times the dial passes through position 0 during rotations.
   
    Args:
        data: List of rotation instructions (e.g., ['L68', 'R48', ...])
        start: Starting position of the dial (default: 50)
        dial_nums: Number of positions on the dial (default: 100)
    
    Returns:
        Total number of times the dial points at 0 during all rotations
    """
    zero_counter = 0
    curr_pos = start

    for instruction in data:
        logger.debug(f"instruction={instruction}")
        direction = instruction[0]
        clicks = int(instruction[1:])
        
        for _ in range(clicks): # simulate EVERY click
            if direction == "R":
                curr_pos = (curr_pos + 1) % dial_nums
            else:  # direction == "L"
                curr_pos = (curr_pos - 1) % dial_nums
            
            if curr_pos == 0:
                zero_counter += 1
        
        logger.debug(f"curr_pos={curr_pos}")

    return zero_counter

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines() # Most puzzles are multiline strings
            # input_data = f.read().strip() # Raw string
            
            logger.debug(dc.top_and_tail(input_data))
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        L68
        L30
        R48
        L5
        R60
        L55
        L1
        L99
        R14
        L82"""))
    sample_answers = [3]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [6]
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
            ac.validate(soln_func(curr_input.splitlines()), curr_ans)
        except AssertionError as e:
            logger.error(f"{soln_func.__name__} test failed: {e}")
            sys.exit(1)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
