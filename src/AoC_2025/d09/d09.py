"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/9

We're in a movie theater with a big tile floor. 
Puzzle input is the location of red tiles on the floor.

Part 1:

Using two red tiles as opposite corners, what is the largest area of any rectangle you can make?
This is just about creating areas from all pairs of points.
The gotcha is that we need to add one to the width and height, because the points are inclusive.

Part 2:

In our *input list*, every red tile is connected to the red tile before and after it
by a straight line of green tiles. And the list wraps so the first and last red tiles are connected.
Adjacent tiles in the list will always be in the same row or same column.
When we form closed loops, internal tiles are also green.

Now we must choose rectangles that have red in opposite corners, 
but otherwise ONLY contain green or red tiles.
What is the largest area of any rectangle you can make?

The tricky part here is that the edges described by the input create a polygon, 
but the polygon may contain non-green tiles:

    RgggR..RggR
    gRggR..gggg
    gg..RggRggg
    gg..ggRgggR
    gRggRgg....   
    ggggggRgggR
    ggggggggggg
    ggggggggggg
    RgggggggggR

I opted to use ray casting to determine if a point is in the "enclosed" polygon, 
and therefore green or red.

I've used ray casting before (see 2023 day 10), so I wasn't starting from scratch.
"""
import logging
import sys
import textwrap
from itertools import combinations
from typing import NamedTuple

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 9

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

def part1(data: list[str]):
    red_tiles = set()
    for line in data:
        x, y = map(int, line.split(","))
        red_tiles.add(Point(x, y))

    biggest_area = 0
    for point1, point2 in combinations(red_tiles, 2):
        # We need inclusive area
        rectangle_area = (abs(point2.x - point1.x) + 1) * (abs(point2.y - point1.y) + 1)
        biggest_area = max(biggest_area, rectangle_area)
            
    return biggest_area

class PolygonSolver:
    """ Solves the problem using Ray Casting and edge intersection checks. """
    def __init__(self, corners: list[Point]):
        self.corners = corners
        self.num_corners = len(corners)
        
        # Pre-calculate edges for intersection checks
        # Store as (x1, y1, x2, y2) tuples
        self.vertical_edges = []
        self.horizontal_edges = []
        
        for i in range(self.num_corners):
            p1 = corners[i]
            p2 = corners[(i + 1) % self.num_corners]
            
            if p1.x == p2.x: # Vertical
                # Store with y1 < y2 for simplified checking
                y_min, y_max = min(p1.y, p2.y), max(p1.y, p2.y)
                self.vertical_edges.append((p1.x, y_min, y_max))
            else: # Horizontal
                x_min, x_max = min(p1.x, p2.x), max(p1.x, p2.x)
                self.horizontal_edges.append((x_min, x_max, p1.y))
                
    def is_point_inside(self, px: float, py: float) -> bool:
        """ 
        Determines if a point is inside the polygon using Ray Casting. 
        Casts a horizontal ray to the right from (px, py).
        Odd intersections = Inside.
        """
        intersections = 0
        
        for vx, vy_min, vy_max in self.vertical_edges:
            # Check if ray crosses this vertical edge
            # Ray is y = py, x > px
            # Edge is x = vx, y in [vy_min, vy_max]
            
            # 1. Edge must be strictly to the right of the point
            if vx > px:
                # 2. Ray's Y must be within the edge's Y range
                # We use vy_min <= py < vy_max to avoid double counting vertices
                if vy_min <= py < vy_max:
                    intersections += 1
                    
        return intersections % 2 == 1

    def intersects_rect(self, r_min_x, r_min_y, r_max_x, r_max_y) -> bool:
        """ 
        Checks if any polygon edge strictly intersects the INTERIOR of the rectangle. 
        Touching the boundary is allowed.
        """
        # Check Vertical Edges
        for vx, vy_min, vy_max in self.vertical_edges:
            # Does vertical edge X fall strictly inside rect X range?
            if r_min_x < vx < r_max_x:
                # Does vertical edge Y range overlap strictly with rect Y range?
                # Overlap: max(A_min, B_min) < min(A_max, B_max)
                overlap_min = max(vy_min, r_min_y)
                overlap_max = min(vy_max, r_max_y)
                if overlap_min < overlap_max:
                    return True # Intersects
        
        # Check Horizontal Edges
        for hx_min, hx_max, hy in self.horizontal_edges:
            # Does horizontal edge Y fall strictly inside rect Y range?
            if r_min_y < hy < r_max_y:
                # Does horizontal edge X range overlap strictly with rect X range?
                overlap_min = max(hx_min, r_min_x)
                overlap_max = min(hx_max, r_max_x)
                if overlap_min < overlap_max:
                    return True
                    
        return False

def part2(data: list[str]):
    red_tiles = [] # Order matters for polygon checks
    for line in data:
        x, y = map(int, line.split(","))
        red_tiles.append(Point(x, y))

    # Initialize Polygon Solver
    solver = PolygonSolver(red_tiles)
    
    biggest_area = 0
    
    for p1, p2 in combinations(red_tiles, 2):
        # Determine the rectangle area in real coordinates
        width = abs(p1.x - p2.x) + 1
        height = abs(p1.y - p2.y) + 1
        area = width * height
        
        # Optimization: Don't check validity if area is smaller than current max
        if area <= biggest_area:
            continue
            
        r_min_x, r_max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        r_min_y, r_max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        
        # To check if the rectangle is valid (part of the polygon's interior),
        # we test a point slightly offset from the top-left corner into the rectangle's body.
        # This (min_x + 0.5, min_y + 0.5) approach avoids ambiguity with boundary lines.
        # If this point is inside the polygon AND no edges intersect the rectangle's interior,
        # then the entire rectangle is valid.
        
        if solver.is_point_inside(r_min_x + 0.5, r_min_y + 0.5):
             if not solver.intersects_rect(r_min_x, r_min_y, r_max_x, r_max_y):
                 biggest_area = area

    logger.debug(f"Max Area: {biggest_area}")
    return biggest_area

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
        7,1
        11,1
        11,7
        9,7
        9,5
        2,5
        2,3
        7,3"""))
    sample_answers = [50]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [24]
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
