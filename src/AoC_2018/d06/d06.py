"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2018/day/6

Our device has given us a list of coordinates in the format `x, y`. 
These coordinates might be dangerous! 
We need to work out which coordinate are closest to specified coordinates. 

Part 1:

What is the size of the largest area that isn't infinite? 
An area is defined as the count of all grid locations that are closest to a 
specific coordinate using Manhattan distance.

Strategy thoughts:
- Bounding Box Approach: 
  We only need to check all points within a bounding box defined by the 
  min/max x and y values of all provided danger coordinates.
- Manhattan Distance:
  For each point in the bounding box, use Manhattan distance to determine
  its closest danger coordinate.
- Area:
  An area is defined as the count of all grid locations that are closest to a 
  specific danger coordinate using Manhattan distance, including the danger 
  coordinate itself.
- Infinite Area Detection:
  A danger coordinate has an infinite area if ANY point in its area touches 
  the bounding box edge. We first build all areas, then identify which danger 
  coordinates have areas extending to the edge (infinite), and exclude those 
  when finding the largest area.
- Points equidistant from multiple danger coordinates don't belong to any danger coordinate

Part 2:

"""
from collections import defaultdict
from collections import Counter
import logging
import sys
import textwrap
from itertools import combinations

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2018
DAY = 6

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

def parse_input(data: list[str]):
    """Converts a list of coordinate strings into a list of Points."""
    return [ac.Point(*map(int, line.split(","))) for line in data]

def bounding_box(points: list[ac.Point]):
    """Returns the bounding box defined by the min/max x and y values of all points."""
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    logger.debug(f"min_x={min_x}, max_x={max_x}, min_y={min_y}, max_y={max_y}")

    return ac.Point(min_x, min_y), ac.Point(max_x, max_y)

def on_bounding_box_edge(point: ac.Point, tl: ac.Point, br: ac.Point):
    """Returns True if the point is on the bounding box edge."""
    return point.x in [tl.x, br.x] or point.y in [tl.y, br.y]
    
def part1(data: list[str]):
    danger_points = parse_input(data)
    logger.debug(danger_points)

    tl, br = bounding_box(danger_points)
    logger.debug(f"tl={tl}, br={br}")
    
    # Store the closest danger point and its distance for each point in the bounding box
    distances: dict[ac.Point, tuple[ac.Point, int]] = {}

    # Iterate over all points in the bounding box
    for y in range(tl.y, br.y + 1):
        for x in range(tl.x, br.x + 1):
            curr_point = ac.Point(x, y)

            # Determine the closest danger coordinate for this point
            for danger_point in danger_points:
                manhattan_distance = curr_point.manhattan_distance_from(danger_point)
                if curr_point not in distances:
                    distances[curr_point] = (danger_point, manhattan_distance)
                else:
                    if manhattan_distance < distances[curr_point][1]:
                        distances[curr_point] = (danger_point, manhattan_distance)
                    elif manhattan_distance == distances[curr_point][1]:
                        distances[curr_point] = (None, manhattan_distance)
    
    logger.debug(distances)

    # Filter out all points associated with multiple danger points (marked as None)
    # These don't belong to any danger point's area
    distances = {point: (danger_point, dist) for point, (danger_point, dist) in distances.items()
                    if danger_point is not None}
    logger.debug(distances)
    
    # Build areas: group all points by their closest danger point
    points_in_dp_area: defaultdict[ac.Point, set[ac.Point]] = defaultdict(set)
    for point, (danger_point, dist) in distances.items():
        points_in_dp_area[danger_point].add(point)
    logger.debug(points_in_dp_area)
    
    # Identify danger points with infinite areas
    # A danger point has an infinite area if ANY point in its area touches the bounding box edge
    infinite_danger_points = set()
    for danger_point, area_points in points_in_dp_area.items():
        for point in area_points:
            if on_bounding_box_edge(point, tl, br):
                infinite_danger_points.add(danger_point)
                break  # No need to check other points for this danger point
    logger.debug(f"infinite_danger_points={infinite_danger_points}")
    
    # Filter to only finite areas
    finite_areas = {dp: points for dp, points in points_in_dp_area.items() 
                    if dp not in infinite_danger_points}
    logger.debug(f"finite_areas={finite_areas}")
    
    # Return the size of the largest finite area
    biggest_area = max(finite_areas.items(), key=lambda item: len(item[1]))
    logger.debug(f"biggest_area={biggest_area}")
    return len(biggest_area[1])

def part2(data: list[str]):
    return "uvwxyz"

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
        1, 1
        1, 6
        8, 3
        3, 4
        5, 5
        8, 9"""))
    sample_answers = [17]
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
            ac.validate(soln_func(curr_input.splitlines()), curr_ans)
        except AssertionError as e:
            logger.error(f"{soln_func.__name__} test failed: {e}")
            sys.exit(1)
    logger.info(f"{soln_func.__name__} tests passed")
    
if __name__ == "__main__":
    main()
