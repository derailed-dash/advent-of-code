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
import os

# For visualisation
import numpy as np
import imageio.v3 as iio
from PIL import Image, ImageDraw
import matplotlib.cm as cm
import matplotlib.colors as mcolors

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
    """ A grid representing a warehouse with rolls of paper """

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

    def __repr__(self) -> str:
        return f"Grid(size={self._width}*{self._height})"
    
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

class Visualiser:
    def __init__(self, grid: ForkliftGrid, scale=10):
        self.grid = grid
        self.scale = scale
        self.frames = []
        
        # Heatmap state: Point -> intensity (0.0 to 1.0)
        self.heat_map: dict[Point, float] = {}
        self.decay_rate = 0.15  # How fast the heat fades
        
        # Colormap for the heat
        self.cmap = cm.get_cmap('plasma') 

        self.colors = {
            "@": (100, 149, 237),  # Paper rolls (Cornflower Blue) - Cool color
            ".": (15, 15, 35),     # Empty floor (Very Dark Blue) - Background
        }

    def update(self, new_points: list[Point]):
        """ Update the heatmap with newly removed points """
        # Decay existing heat
        for p in list(self.heat_map.keys()):
            self.heat_map[p] -= self.decay_rate
            if self.heat_map[p] <= 0:
                del self.heat_map[p]
        
        # Add new points with max heat
        for p in new_points:
            self.heat_map[p] = 1.0

    def render_frame(self):
        """ Render the current grid state to an image frame """
        # Create base image
        img = Image.new("RGB", (self.grid.width * self.scale, self.grid.height * self.scale), self.colors["."])
        draw = ImageDraw.Draw(img)
        
        # Draw static grid elements
        for y, row in enumerate(self.grid.array):
            for x, cell in enumerate(row):
                if cell == "@":
                    color = self.colors["@"]
                    draw.rectangle(
                        [x * self.scale, y * self.scale, (x + 1) * self.scale - 1, (y + 1) * self.scale - 1],
                        fill=color
                    )

        # Draw heatmap overlay
        for point, intensity in self.heat_map.items():
            # Get color from colormap (returns RGBA float tuple)
            rgba = self.cmap(intensity)
            # Convert to RGB int tuple
            color = tuple(int(c * 255) for c in rgba[:3])
            
            draw.rectangle(
                [point.x * self.scale, point.y * self.scale, (point.x + 1) * self.scale - 1, (point.y + 1) * self.scale - 1],
                fill=color
            )
            
        self.frames.append(img)

    def save_gif(self, filename="vis.gif", fps=15):
        """ Save collected frames as a GIF """
        if not self.frames:
            return
        # Convert PIL images to numpy arrays for imageio
        frames_np = [np.array(f) for f in self.frames]
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        iio.imwrite(filename, frames_np, loop=0, duration=1000/fps)
        logger.info(f"Saved GIF to {filename}")

def part2(data: list[str], vis_filename: str = None):
    """ Count how many rolls can be removed by iteratively removing accessible rolls """
    grid = ForkliftGrid(data)
    logger.debug(grid)
    
    vis = None
    vis_path = None

    # Only run visualisation if the output file doesn't already exist    
    if vis_filename:
        vis_path = locations.output_dir / vis_filename
        if not os.path.exists(vis_path):
            vis = Visualiser(grid, scale=5)
            vis.render_frame() # Initial state

    rolls_removed = 0
    
    while True:
        accessible_locations = get_accessible_locations(grid)
        if not accessible_locations:
            break
        for loc in accessible_locations:
            grid.set_value_at_point(loc, "X")
            rolls_removed += 1
        
        if vis:
            vis.update(accessible_locations)
            vis.render_frame()

            # Clean up 'X's for next iteration (optional, or keep them to show history)
            # If we want them to disappear, set them to '.' here.
            for loc in accessible_locations:
                grid.set_value_at_point(loc, ".")

    if vis and vis_path:
        vis.save_gif(vis_path, fps=10)
    return rolls_removed

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
    
    def part2_with_sample_vis(data):
        return part2(data, vis_filename="2025_d04_sample_vis.gif")
        
    test_solution(part2_with_sample_vis, sample_inputs, sample_answers)
     
    # Part 2 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 2 soln={part2(input_data, vis_filename='2025_d04_vis.gif')}")

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
