"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/6

We're in a magnetically sealed garbage smasher. (There's something strangely familiar about this.)
The cephalapods will open it! But one of them needs help with her homework.
It's cephalopod math!

The math is a set of problems, given as blocks of numbers horizontally.

Part 1:

What is the grand total found by adding together all of the answers to the individual problems?

Solution:
The tricky part is separating the input into blocks of numbers.
Fortunately, looking at sample input and real input, the operators are always
left aligned to the start of that puzzle block. So we can use this to delineate the blocks.

Part 2:

"""
import logging
import math
import sys
import textwrap

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 6

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

class Puzzle:
    def __init__(self, operator: str):
        self.numbers = []
        self.operator = operator

    def add_number(self, number: int):
        self.numbers.append(number)

    def calculate(self):
        match self.operator:
            case "+":
                return sum(self.numbers)
            case "*":
                return math.prod(self.numbers)
            case _:
                raise ValueError(f"Invalid operator: {self.operator}")
    
    def __str__(self):
        return self.operator + ": " + ",".join(map(str, self.numbers))

def part1(data: list[str]):
    puzzles = []
    operator_indices = {}
    for idx, operator in enumerate(data[-1]):
        if operator in "*/+-":
            operator_indices[idx] = operator
            puzzles.append(Puzzle(operator))

    logger.debug(operator_indices)
    for line in data[:-1]:
        indices_list = list(operator_indices.keys())
        start = end = None
        for puzzle_num, puzzle in enumerate(puzzles):
            if puzzle_num == len(puzzles) - 1: # If last puzzle
                end = len(line)
            else:
                end = indices_list[puzzle_num + 1]
            start = indices_list[puzzle_num]
            logger.debug(line[start:end])
            puzzle.add_number(int(line[start:end]))

    return sum(puzzle.calculate() for puzzle in puzzles)

def part2(data: list[str]):
    puzzles = []
    operator_indices = {}
    for idx, operator in enumerate(data[-1]):
        if operator in "*/+-":
            operator_indices[idx] = operator
            puzzles.append(Puzzle(operator))

    logger.debug(operator_indices)

    # First we want the blocks. We need to preserve character spacing, so store as strings.
    # We want to get to [['123', ' 45', '  6'], ['328', '64 ', '98 '], ...]
    blocks = [] 
    for _ in puzzles:
        blocks.append([]) # Create an empty block for each puzzle

    for line in data[:-1]: # Process each row (ignoring operators)
        indices_list = list(operator_indices.keys())
        start = end = None
        for puzzle_num in range(len(puzzles)):
            if puzzle_num == len(puzzles) - 1: # If last puzzle
                end = len(line) + 1
            else:
                end = indices_list[puzzle_num + 1]
            start = indices_list[puzzle_num]
            blocks[puzzle_num].append(line[start:end-1])
    
    logger.debug(f"blocks={blocks}")
    
    # Now we want to transpose the cols and rows of each block
    for puzzle_num, block in enumerate(blocks):
        transposed_block = list(zip(*block)) # E.g. [('1', ' ', ' '), ('2', '4', ' '), ('3', '5', '6')]
        for num_chars in transposed_block:
            num = int("".join(num_chars))
            puzzles[puzzle_num].add_number(num)
    
    return sum(puzzle.calculate() for puzzle in puzzles)

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
    sample_inputs.append(textwrap.dedent("""\
        123 328  51 64 
         45 64  387 23 
          6 98  215 314
        *   +   *   +  """))
    sample_answers = [4277556]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [3263827]
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
