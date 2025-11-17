"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2018/day/1

Part 1:

Part 2:

"""
import logging
import textwrap

import dazbo_commons as dc  # For logging

import aoc_common.aoc_commons as ac  # General AoC utils

YEAR = 2018
DAY = 1

locations = dc.get_locations(__file__)
logger = dc.retrieve_console_logger(locations.script_name)
logger.setLevel(logging.DEBUG)
# td.setup_file_logging(logger, locations.output_dir)
    
def part1(data):
    return "uvwxyz"

def part2(data):
    return "uvwxyz"

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines()
            logger.debug(input_data)
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        abcdef"""))
    sample_answers = ["uvwxyxz"]
    test_solution(part1, sample_inputs, sample_answers)

    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
        
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        abcdef"""))
    sample_answers = ["uvwxyz"]
    test_solution(part2, sample_inputs, sample_answers)
     
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
        ac.validate(soln_func(curr_input.splitlines()), curr_ans)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
