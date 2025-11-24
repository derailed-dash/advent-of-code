"""
Author: Darren
Date: 24/11/2025

Solving https://adventofcode.com/2018/day/3

The Elves have found some prototype fabric for Santa's suit, but they can't agree on how to cut it. 
The fabric is a large square, at least 1000 inches on each side. Each Elf makes a claim for a rectangular area of the fabric.

Each claim describes a rectangle with an ID, the offset from the left and top edges, and the dimensions (width and height).

The input looks like this:

```
#1 @ 1,3: 4x4
#2 @ 3,1: 4x4
#3 @ 5,5: 2x2
```

In this example:
   - Claim #1 specifies a 4x4 rectangle, starting 1 inch from the left and 3 inches from the top.
   - Claim #2 specifies a 4x4 rectangle, starting 3 inches from the left and 1 inch from the top.
   - Claim #3 specifies a 2x2 rectangle, starting 5 inches from the left and 5 inches from the top.

The problem is that these claims can overlap. In the example above, claims #1 and #2 share an overlapping area, 
while claim #3 is separate.

# Part 1

How many square inches of fabric are within two or more claims?

# Part 2

Which claim does not overlap?

"""
import logging
import re
import sys
import textwrap
from dataclasses import dataclass

import dazbo_commons as dc  # For locations
import numpy as np
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

YEAR = 2018
DAY = 3

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
logger.setLevel(logging.DEBUG)

matcher = re.compile(r"#(\d+) @ (\d+),(\d+): (\d+)x(\d+)") # e.g. #1 @ 1,3: 4x4

@dataclass
class Claim:
    claim_id: int
    x: int
    y: int
    width: int
    height: int

def process_data(data):
    """ 
    Process the data into a list of claims
    Input is a list of claim strings. Each string is in the format #1 @ 1,3: 4x4, which represents a rectangle on a fabric.
    Output is a list of claims.
    """
    claims = []
    for claim in data:
        claims.append(Claim(*map(int, matcher.match(claim).groups())))
    return claims

def part1(data):
    """
    Return sum of squares where array > 1 (claimed by 2+ Elves)
    """
    array = np.zeros((1000, 1000), dtype=int)
    claims = process_data(data)
    for claim in claims:
        array[claim.x:claim.x+claim.width, claim.y:claim.y+claim.height] += 1
    
    return (array > 1).sum()  # Count squares where array > 1 (claimed by 2+ Elves)

def part2(data):
    """
    Return ID of claim that does not overlap
    """
    array = np.zeros((1000, 1000), dtype=int)
    claims = process_data(data)

    # First increment array for each claim
    for claim in claims:
        array[claim.x:claim.x+claim.width, claim.y:claim.y+claim.height] += 1
    
    # Then go through the claims again and check if all squares in the claim are claimed by only one Elf
    for claim in claims:
        if (array[claim.x:claim.x+claim.width, claim.y:claim.y+claim.height] == 1).all():
            return claim.claim_id

    raise AssertionError("No non-overlapping claim found")

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
        #1 @ 1,3: 4x4
        #2 @ 3,1: 4x4
        #3 @ 5,5: 2x2"""))
    sample_answers = [4]
    test_solution(part1, sample_inputs, sample_answers)

    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
        
    sample_answers = [3]
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
