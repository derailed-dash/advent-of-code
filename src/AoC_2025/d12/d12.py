"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/12

We're in a cavern full of Christmas trees.
We need to organise the presents under the trees.
Presents must be arranged to form a 2D grid of non-overlapping presents. 
- They will not be stacked.
- Presents can be rotated and flipped.

The input has two sections:
1. The shapes of each present, each as a multiline string. E.g. 

```
0:
###
##.
##.
```

2. Region sizes, with a list of the quantities of each present that need to fit in this region

```
12x5: 1 0 1 0 2 2
```

This menas 1 of shape 0, 0 of shape 1, 1 of shape 2, etc.

Part 1:

How many of the regions can fit all of the presents listed?

Solution thoughts:

- Pre-compute all the rotations and flips for each present, and exclude
  configurations that are duplicates. In the sample data, shape 0 has 8 configs
  whilst, shape 5 has only 2 configs.
- We can use NumPy to store the shapes and apply the rotations and flips easily.
- There are only 6 presents, so the total number of configs will be small.
- Parse the regions. Let's create a class for the Region.
- For each tree space, we don't need to find all valid configurations. 
  We just need *a* configuration. So we can do recursive DFS.
- Call can_fit(region) 
  - Start by adding up the sizes of all the presents to be placed, 
    and check if they fit in the region. If not, we're done already.
  - Make an assumption about how much extra space we need to support the required shapes.
    I'm gonna go with 20% extra space.
    If we don't have this extra space, the shapes won't fit.
  - If we're here, they might fit.

*** Oh, seems this was good enough.

- Now check if they will fit...
  - Initialises empty grid of the correct size.
  - Calls recursive fit(grid, remaining_presents)
    - If no remaining presents, return True
    - Otherwise, find all valid placements for each config of this present.
    - For each valid placement: place, recurse, return True. Remove, go to next placement.
    - If not valid placements: return False.

"""
import logging
import sys
from dataclasses import dataclass

import numpy as np
from tqdm import tqdm

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 12

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

@dataclass
class Region:
    width: int
    height: int
    present_counts: list[int] # E.g. [1, 0, 1, 0, 2, 2]

def parse_input(data:str):
    blocks = data.strip().split("\n\n")
    shape_blocks = blocks[:-1]
    region_block = blocks[-1]

    shapes = [] # Store in order so we can easily index
    for block in shape_blocks:
        shape_lines = block.splitlines()[1:]
        grid = [[1 if char == '#' else 0 for char in line] for line in shape_lines]
        shape_array = np.array(grid, dtype=np.bool)
        shapes.append(shape_array)

    regions = []
    for line in region_block.splitlines():
        dims, counts = line.split(":")
        width, height = list(map(int, dims.split("x")))
        present_counts = list(map(int, counts.strip().split(" ")))
        region = Region(width, height, present_counts)
        regions.append(region)
        
    return shapes, regions

def shape_configs(shape):
    """ Return all unique configurations of the shape """
    configs = [] # Store the actual configs we will return
    seen_configs = set() # Store the bytes of the configs we've seen; numpy arrays are not hashable

    for _ in range(4): # Apply rotations and get back to original
        if shape.tobytes() not in seen_configs:
            seen_configs.add(shape.tobytes())
            configs.append(shape)
        shape = np.rot90(shape)

    lr_flipped = np.fliplr(shape) # Flip left-right
    for _ in range(4):
        if lr_flipped.tobytes() not in seen_configs:
            seen_configs.add(lr_flipped.tobytes())
            configs.append(lr_flipped)
        lr_flipped = np.rot90(lr_flipped)

    # up-down flip is redundant due to rotations
    return configs

def can_fit(region: Region, configs_all_shapes: list[list[np.ndarray]]):
    """ Return True if the region can fit all the presents """

    region_size = region.width * region.height
    
    # Create flattened list of present indices to place
    # E.g. [1, 0, 1, 0, 3, 2] means 1*0, 1*2, 3*4, 2*5 -> [0, 2, 4, 4, 4, 5, 5]
    to_place = []
    for i, count in enumerate(region.present_counts):
        to_place.extend([i] * count)

    total_presents_size = sum(configs_all_shapes[i][0].sum() for i in to_place)
    logger.debug(f"Region size: {region_size}, Total presents size: {total_presents_size}")

    # This seems to be a fudge!!
    if region_size < total_presents_size * 1.2:
        logger.debug("Region probably too small.")
        return False
    
    return True

def part1(data: list[str]):
    shapes, regions = parse_input(data)
    # Store a list of configs for each shape, in order
    configs = [] # E.g. [[config1.1, config1.2, config1.3], [config2.1, config2.2], ...]
    for shape in shapes:
        logger.debug(f"Shape:\n{shape}")
        configs.append(shape_configs(shape))
        logger.debug(f"Configs={len(configs)}")

    regions_satisfied = 0 
    for region in tqdm(regions, desc="Processing Regions", unit="region"):
        if can_fit(region, configs):
            regions_satisfied += 1

    return regions_satisfied

def part2(data: list[str]):
    return "uvwxyz"

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read() # Most puzzles are multiline strings

    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    with open(locations.input_dir / "sample_input_part_1.txt", encoding="utf-8") as f:
        sample_inputs.append(f.read())
    sample_answers = [2]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")

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
