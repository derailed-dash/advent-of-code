"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/7

We're stuck in a room with no doors, and a broken teleporter.
Our input is a diagram of the tachyon manifold, showing the path of the 
tachyon beam.

Rules:
- The beam starts at the S
- Beams move downwards
- Beams split when they hit a ^, with new beams appearing to each side.

Part 1:

How many times will the beam be split?

Solution:
- Fairly simple BFS, using deque for the queue and set for the explored set.
- Whenever we encounter a '^', we split and increment the split count.
- Otherwise, we move down.

Part 2:

Urgh, it's a quantum tachyon manifold.
Now we have a single particle, but for each path it takes, it creates a new timeline.

In total, how many different timelines would a single tachyon particle end up on?

Solution:

- We need to count the number of unique paths.
- We could do this by just NOT using a set for the explored set, 
  and instead using a dict to store the number of times we've seen each point.
  But this would get computationally expensive for big grids.
- A better approach is to use DFS with memoization.
  - We implement the DFS using recursion:
    - Base case: if we hit the bottom of the grid, we've found a path. Return 1.
    - If we hit a point in the cache, return the cached value.
    - Recurse: if we hit a '^', we split and sum the two paths. Otherwise, we move down.
  - We use a cache decorator to memoize the results of the recursive calls.
    That way, if we hit a point we've seen before, we can return the cached value
    instead of re-computing it.

"""
import logging
import sys
import textwrap
from collections import deque
from functools import cache
from typing import NamedTuple

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 7

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

class TachyonGrid:
    """ A grid representing the path of beams through the tachyon manifold. """

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
        points = [Point(x, y) for x in range(self._width) for y in range(self._height)]
        return points

    def start(self) -> Point:
        for point in self.all_points():
            if self.value_at_point(point) == 'S':
                return point
        raise ValueError("No start point 'S' found")

    def __repr__(self) -> str:
        return f"Grid(size={self._width}*{self._height})"
    
    def __str__(self) -> str:
        return "\n".join("".join(map(str, row)) for row in self.array)

def part1(data: list[str]):
    """ 
    Simulate the beam passing through the tachyon manifold.
    Count the number of splits. 
    """
    grid = TachyonGrid(data)
    start = grid.start()
    logger.debug(f"\n{grid}")
    logger.debug(f"start={start}")

    queue = deque()
    queue.append(start)
    explored = set()
    explored.add(start)

    splits = 0

    while queue:
        current = queue.popleft()

        if grid.value_at_point(current) == '^': # we need to split
            splits += 1

            # Split
            for dx in (-1, 1):
                adjacent = Point(current.x+dx, current.y)
                if grid.valid_location(adjacent) and adjacent not in explored:
                    queue.append(adjacent)
                    explored.add(adjacent)

        else: # we need to move down
            adjacent = Point(current.x, current.y+1)
            if grid.valid_location(adjacent) and adjacent not in explored:
                queue.append(adjacent)
                explored.add(adjacent)

    return splits

def part2(data: list[str]):
    """ 
    Simulate the beam passing through the tachyon manifold.
    Count the number of timelines created by each split.
    """
    grid = TachyonGrid(data)
    start = grid.start()

    @cache
    def count_timelines(point: Point) -> int:
        """ 
        Recursive DFS to count timelines. 
        Returns the number of timelines that result from a particle at `point`.
        """
        if not grid.valid_location(point):
            # The particle has exited the manifold. This counts as 1 valid timeline.
            return 1

        val = grid.value_at_point(point)

        if val == '^':
            # Split! Both new timelines continue downward.
            left = Point(point.x - 1, point.y + 1)
            right = Point(point.x + 1, point.y + 1)
            return count_timelines(left) + count_timelines(right)
        
        else: # Continue downward
            down = Point(point.x, point.y + 1)
            return count_timelines(down)

    return count_timelines(start)

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines() # Most puzzles are multiline strings
            logger.debug(dc.top_and_tail(input_data))
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        .......S.......
        ...............
        .......^.......
        ...............
        ......^.^......
        ...............
        .....^.^.^.....
        ...............
        ....^.^...^....
        ...............
        ...^.^...^.^...
        ...............
        ..^...^.....^..
        ...............
        .^.^.^.^.^...^.
        ..............."""))
    sample_answers = [21]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [40]
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
