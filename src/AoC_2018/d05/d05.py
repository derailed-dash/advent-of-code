"""
Author: Darren
Date: 22/11/2025

Solving https://adventofcode.com/2018/day/5

A polymer is formed by smaller units which react with each other. 
Two adjacent units of the same type and opposite polarity are destroyed. #
Units' types are represented by letters; units' polarity is represented by capitalization. 
For instance, `r` and `R` are units with the same type but opposite polarity, 
whereas `r` and `s` are entirely different types and do not react.

Part 1:

How many units remain after fully reacting the polymer you scanned?

Part 2:

The goal is to remove **all** units of exactly one type (both lowercase and uppercase) 
from the original polymer, and then fully react the remaining polymer.

How many units remain after fully reacting the polymer you scanned?

"""
import logging
import sys
import textwrap

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

YEAR = 2018
DAY = 5

locations = dc.get_locations(__file__)

# Configure Rich logging
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
    
def part1(polymer: str):
    """
    Fully react the polymer using a stack-based approach.
    Iterates through the polymer, removing adjacent units of the same type but opposite polarity.
    Returns the length of the remaining polymer.
    """
    logger.debug("Polymer: %s", polymer)
    stack = []
    
    for char in polymer:
        if stack and char != stack[-1] and char.lower() == stack[-1].lower():
            # Same letter, different case (e.g. 'a' and 'A') -> React!
            stack.pop()
        else:
            # No reaction, add to stack
            stack.append(char)

        logger.debug("Stack: %s", stack)
            
    return len(stack)


def part2(polymer: str):
    return "uvwxyz"

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().strip()
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        dabAcCaCBAcCcaDA"""))
    sample_answers = [10]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
        
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        abcdef"""))
    sample_answers = ["uvwxyz"]
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
