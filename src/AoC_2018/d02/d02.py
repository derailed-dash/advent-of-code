"""
Author: Darren
Date: 22/11/2025

Solving https://adventofcode.com/2018/day/2

Part 1:

Count the number of IDs that contain exactly two of any letter 
and the number of IDs that contain exactly three of any letter. 

The "checksum" is the product of these two counts. 

Part 2:

Find the two IDs that differ by exactly one character at the same position in both strings. 

"""
import logging
import sys
import textwrap
from collections import Counter
from itertools import combinations

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

YEAR = 2018
DAY = 2

locations = dc.get_locations(__file__)

# Configure root logger with Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(message)s",
    datefmt='%H:%M:%S',
    handlers=[RichHandler(
        rich_tracebacks=True, 
        show_path=True,
        markup=True,
        show_time=False  # Disable Rich's time since we're using our own
    )]
)
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

def part1(data):
    """ Count the number of IDs that contain exactly two of any letter 
    and the number of IDs that contain exactly three of any letter. 
    The "checksum" is the product of these two counts. """
    
    ids_with_2 = 0
    ids_with_3 = 0
    for id in data:
        counter = Counter(id)
        if 2 in counter.values():
            ids_with_2 += 1
        if 3 in counter.values():
            ids_with_3 += 1

    return ids_with_2 * ids_with_3

def part2(data):
    """ Find the two IDs that differ by exactly one character at the same position in both strings. """
    
    # Compare every pair of IDs
    for id1, id2 in combinations(data, 2):
        if sum(posn1 != posn2 for posn1, posn2 in zip(id1, id2)) == 1:
            # We've found two IDs that differ by exactly one character at the same position in both strings.
            # Return the common characters of the two IDs.
            return ''.join(posn1 for posn1, posn2 in zip(id1, id2) if posn1 == posn2)

    return "uvwxyz"

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines()
            logger.debug(dc.top_and_tail(input_data))
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        abcdef
        bababc
        abbcde
        abcccd
        aabcdd
        abcdee
        ababab"""))
    sample_answers = [12]
    test_solution(part1, sample_inputs, sample_answers)

    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
        
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        abcde
        fghij
        klmno
        pqrst
        fguij
        axcye
        wvxyz"""))
    sample_answers = ["fgij"]
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
        try:
            ac.validate(soln_func(curr_input.splitlines()), curr_ans)
        except AssertionError as e:
            logger.error(f"{soln_func.__name__} test failed: {e}")
            sys.exit(1)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
