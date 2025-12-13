"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/2

Input is collection of comma-separated product ID ranges.
E.g. 11-22,95-115,998-1012,1188511880-1188511890,222220-222224

Certain product IDs are invalid and we need to find them.

Part 1:

Invalid prod IDs are those where the first half of the ID is the same 
as the second half.

Part 2:

Invalid prod IDs are those made up of repeated substrings.

"""
import logging
import sys
import textwrap
from functools import cache

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 2

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

def parse_input(input_data: str) -> list[tuple[int, int]]:
    """
    Returns a list ranges, expressed as (start, end) tuples.
    """
    ranges = []
    for range_str in input_data.split(","):
        start, end = map(int, range_str.split("-"))
        ranges.append((start, end))
    return ranges

def part1(data: str) -> int:
    ranges = parse_input(data)
    invalid_ids = []
    for prod_id_range in ranges:
        for prod_id in range(prod_id_range[0], prod_id_range[1] + 1):
            prod_id_str = str(prod_id)
            id_len = len(prod_id_str)
            if id_len % 2 != 0: # odd numbers of digits can't contain invalid IDs
                continue
            if prod_id_str[0:id_len//2] == prod_id_str[id_len//2:id_len]:
                invalid_ids.append(prod_id)

    return sum(invalid_ids)

@cache # We'll run this many times, so let's cache the results
def get_factor_pairs(n):
    """
    Returns a list of factor pairs of n. Always (smaller, larger).
    E.g. 8 -> [(1, 8), (2, 4)]
    """
    factors = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.append((i, n // i))
    
    return sorted(factors)

def part2(data: str) -> int:
    ranges = parse_input(data)
    invalid_ids = []
    for prod_id_range in ranges:
        for prod_id in range(prod_id_range[0], prod_id_range[1] + 1):
            prod_id_str = str(prod_id)
            id_len = len(prod_id_str)
            factor_pairs = get_factor_pairs(id_len)
            is_invalid = False
            for f1, f2 in factor_pairs:
                # Check using f1 as length (repeated f2 times)
                if f2 > 1 and f2 * prod_id_str[0:f1] == prod_id_str:
                    is_invalid = True
                # Check using f2 as length (repeated f1 times)
                elif f1 > 1 and f1 * prod_id_str[0:f2] == prod_id_str:
                    is_invalid = True
                
                if is_invalid:
                    invalid_ids.append(prod_id)
                    break

    return sum(invalid_ids)

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            #input_data = f.read().splitlines() # Most puzzles are multiline strings
            input_data = f.read().strip() # Raw string
            

    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        11-22,95-115,998-1012,1188511880-1188511890,222220-222224,\
        1698522-1698528,446443-446449,38593856-38593862,565653-565659,\
        824824821-824824827,2121212118-2121212124"""))
    sample_answers = [1227775554]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [4174379265]
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
