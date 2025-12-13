"""
Author: Darren
Date: 01/12/2025

Solving https://adventofcode.com/2025/day/1

Secret Entrance - Safe Dial Puzzle

The dial has positions 0-99 and starts at 50.
Rotations are specified as L (left/lower) or R (right/higher) followed by steps.

Solution 2 - Efficient for large inputs
Much faster than solution 1, but harder to follow.

Part 1:
    Count how many times the dial ends at position 0 after each rotation.

Part 2:
    Count how many times the dial passes through position 0 during rotations,
    including both intermediate crossings and final positions.
    This requires counting every click that lands on 0, not just the final position.
"""
import logging
import sys

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 1

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
ac.setup_logging()
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
            clicks = dial_nums - clicks
        
        curr_pos = (curr_pos + clicks) % dial_nums
        logger.debug(f"curr_pos={curr_pos}")

        if curr_pos == 0:
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
        
        if direction == "R":
            zero_counter += (curr_pos + clicks) // dial_nums
            curr_pos = (curr_pos + clicks) % dial_nums
        else:  # direction == "L"
            new_pos = (curr_pos - clicks) % dial_nums
            
            if curr_pos == 0:
                # Starting at 0: only count complete loops (not the starting position)
                zero_counter += clicks // dial_nums
            elif clicks > curr_pos:
                # We cross 0 at least once during the CCW rotation
                zero_counter += ((clicks - curr_pos - 1) // dial_nums) + 1
                # If we also END on 0, count that final landing
                if new_pos == 0:
                    zero_counter += 1
            elif clicks == curr_pos:
                # We land exactly on 0
                zero_counter += 1
            # else: clicks < curr_pos, we don't reach 0
            
            curr_pos = new_pos
        
        logger.debug(f"curr_pos={curr_pos}")

    return zero_counter

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines() # Most puzzles are multiline strings
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    with open(locations.input_dir / "sample_input_part_1.txt", encoding="utf-8") as f:
        sample_inputs.append(f.read())
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
