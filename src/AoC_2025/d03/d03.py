"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/3

Batteries are arranged into banks - one bank per line of input.
The joltage that the bank produces is equal to the number formed by
concatenating the digits on the batteries you've turned on.

Part 1:

Find the largest possible joltage each bank can produce.
We must turn on exactly two batteries per bank.

Solution:
- Convert bank to list of joltages as ints
- Look for the max joltage in the list, with last index set 
  such that there is still a battery remaining to be enabled.
- Repeat looking for max joltage, but starting from the position after the battery we just enabled.

Sum the maximum joltages for all banks.

Part 2:

Now we must turn on 12 batteries per bank.
For this part, no changes are required to the solution!
"""
import logging
import sys

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 3

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)
    
def part1(data: list[str], num_batteries: int = 2):
    max_joltages = []
    for bank in data:
        logger.debug(f"bank={bank}")
        bank_len = len(bank)
        bank_joltages = [int(joltage) for joltage in bank]
        batteries_remaining = num_batteries
        batteries_enabled = []
        
        # Initialise where we start looking for the batteries in the bank.
        bank_index = -1 # We will always add 1 to this index to get the first position of the slice
        
        while batteries_remaining > 0:
            # Find the max digit in the remaining available slice.
            # The slice starts after the last selected index.
            # The slice ends early enough to leave room for the remaining required batteries.
            # E.g., if we need 2 more batteries, we can't pick the very last digit.
            search_slice = bank_joltages[bank_index+1 : bank_len - batteries_remaining + 1]
            battery_joltage = max(search_slice)
            
            # Find the position of this max digit in the bank (after the last selected index)
            bank_index = bank_joltages.index(battery_joltage, bank_index+1)
            
            batteries_enabled.append(battery_joltage)
            batteries_remaining -= 1

        # Concatenate the selected digits to form the final joltage number
        max_joltages.append(int("".join(str(battery) for battery in batteries_enabled)))

    logger.debug(f"max_joltages={max_joltages}")
    return sum(max_joltages)

def part2(data: list[str]):
    return part1(data, 12)

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
    sample_answers = [357]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [3121910778619]
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
