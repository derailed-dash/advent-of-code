"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/4

We have a grid showing where rolls of paper (@) are located.

Part 1:

Which rolls of paper can forklifts access?
These are locations with fewer than four rolls of paper in the 
8 adjacent locations.

Solution:
- Check each location in the grid.
- If it is a roll of paper (@), check the 8 adjacent locations.
- If it has fewer than 4 rolls of paper, it is accessible.

Part 2:

How many rolls of paper can be removed by iteratively removing accessible rolls?

Solution:
- Iteratively repeat Part 1.
- With each iteration, remove the accessible roll of paper.
- Count the number of rolls removed in total.
"""
from typing import NamedTuple
import logging
import sys
import textwrap

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 4

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

class Point(NamedTuple):
    x: int
    y: int

    def yield_neighbors(self):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                yield Point(self.x + dx, self.y + dy)

class ForkliftGrid():
    def __init__(self, grid_array: list) -> None:
        self.array = [list(row) for row in grid_array]
        self._width = len(self.array[0])
        self._height = len(self.array)
        
    def value_at_point(self, point: Point):
        """ The value at this point """
        return self.array[point.y][point.x]

    def set_value_at_point(self, point: Point, value):
        self.array[point.y][point.x] = value
        
    def valid_location(self, point: Point) -> bool:
        """ Check if a location is within the grid """
        if (0 <= point.x < self._width and 0 <= point.y < self._height):
            return True
        
        return False

    @property
    def width(self):
        """ Array width (cols) """
        return self._width
    
    @property
    def height(self):
        """ Array height (rows) """
        return self._height
    
    def all_points(self) -> list[Point]:
        points = [Point(x, y) for x in range(self.width) for y in range(self.height)]
        return points

    def __repr__(self) -> str:
        return f"Grid(size={self.width}*{self.height})"
    
    def __str__(self) -> str:
        return "\n".join("".join(map(str, row)) for row in self.array)

def get_accessible_locations(grid: ForkliftGrid):
    accessible_locations = []
    for point in grid.all_points():
        if grid.value_at_point(point) == "@":
            roll_count = 0
            for neighbor in point.yield_neighbors():
                if grid.valid_location(neighbor):
                    if grid.value_at_point(neighbor) == "@":
                        roll_count += 1
            if roll_count < 4:
                accessible_locations.append(point)
    
    return accessible_locations

def part1(data: list[str]):
    """ 
    Count accessible locations: 
    locations with fewer than 4 rolls of paper in the 8 adjacent locations 
    """
    grid = ForkliftGrid(data)
    logger.debug(grid)

    accessible_locations = get_accessible_locations(grid)
    logger.debug(f"Accessible locations: {accessible_locations}")
    return len(accessible_locations)

def part2(data: list[str]):
    """ Count how many rolls can be removed by iteratively removing accessible rolls """
    grid = ForkliftGrid(data)
    logger.debug(grid)

    rolls_removed = 0
    while True:
        accessible_locations = get_accessible_locations(grid)
        if not accessible_locations:
            break
        for loc in accessible_locations:
            grid.set_value_at_point(loc, "X")
            rolls_removed += 1

    return rolls_removed

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
        ..@@.@@@@.
        @@@.@.@.@@
        @@@@@.@.@@
        @.@@@@..@.
        @@.@@@@.@@
        .@@@@@@@.@
        .@.@.@.@@@
        @.@@@.@@@@
        .@@@@@@@@.
        @.@.@@@.@."""))
    sample_answers = [13]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [43]
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
