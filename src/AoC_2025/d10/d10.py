"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/10

We need to initialise the factory machines.
Our input is the remains of the manual:

```
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}
```

- The first part are the required indicator lights that must be on.
- The "tuples" represent buttons. 
  Pressing any of these buttons toggles the state of the respective lights.
- The "set" at the end are the required joltages.

Part 1:

What is the fewest button presses required to correctly configure 
the indicator lights on all of the machines?

Here, joltages are irrelevant.

Part 2:

"""
import itertools
import logging
import sys
import textwrap
from dataclasses import dataclass

import dazbo_commons as dc
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac

# Set these to the current puzzle
YEAR = 2025
DAY = 10

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
        show_time=False 
    )]
)
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

@dataclass
class Machine:
    """ Represents a factory machine based on the schematic input """

    # We need this because the leading zero bits are lost when converting to int
    # So we need to know how many bits we started with
    num_lights: int 
    target_state: int # E.g. ".##." -> 0b110 = 6
    button_masks: list[int] # E.g. [3] [1,3] ... -> [0b1000, 0b1010, ...] = [8, 10, ...]
    joltages: list[int]
    
    def get_presses(self) -> int:
        """
        Determine fewest button presses to reach target state (all lights matching target).
        Start with all lights OFF (0). 
        Target state represents specific configuration of ON lights we need.
        Buttons toggle lights (XOR).
        So we need: (Button_A ^ Button_B ^ ...) == target_state.

        Return k, the fewest number of button presses required.
        """
        num_buttons = len(self.button_masks)
        
        # Try k presses, from 0 to num_buttons
        for k in range(num_buttons + 1): # E.g. [0, 1, 2, 3]
            # We can brute force all combinations of k buttons
            for combo in itertools.combinations(self.button_masks, k):
                # Calculate the result of pressing these k buttons
                current_state = 0
                for mask in combo: # Apply each button in the combo
                    current_state ^= mask
                
                if current_state == self.target_state:
                    return k
                    
        raise ValueError("No solution found for machine")

    def __str__(self):
        return f"Target: {bin(self.target_state)[2:]}, " \
             + f"Buttons: [{', '.join([bin(b)[2:] for b in self.button_masks])}], " \
             + f"Joltages: {self.joltages}"

def parse_input(data: list[str]) -> list[Machine]:
    """
    Parse input data into list of Machine objects.
    Format: [.##.] (3) (1,3) ... {3,5,4,7}
    """
    machines = []
    
    for line in data:
        # 1. Extract Indicator Light Diagram (Target State)
        # E.g. [.##.]
        diagram_start = line.find('[')
        diagram_end = line.find(']')
        diagram_str = line[diagram_start+1:diagram_end]
        
        num_lights = len(diagram_str)
        target_state = 0
        for i, char in enumerate(diagram_str):
            if char == '#': # Light at index i is ON.
                # We can map index 0 to bit 0, index 1 to bit 1, etc.
                target_state |= (1 << i) # E.g. .##. -> 0110 = 6
                
        # 2. Extract Buttons, e.g. (3) (1,3) (2) ...
        buttons_str = line[diagram_end+1:line.find('{')].strip()
        button_masks = []
        parts = buttons_str.split(' ') # get individual buttons: ['(1,3)', '(2)', '(2,3)']
        
        for part in parts:
            nums = [int(x) for x in part[1:-1].split(',')] # Get to "1,3" from "(1,3)"
            
            mask = 0
            for light_idx in nums:
                # Convert to a mask where button positions are set to 1
                mask |= (1 << light_idx) # E.g. 1, 3 -> 0b1010
            button_masks.append(mask)
        
        # 3. Extract Joltages, e.g. {3,5,4,7}
        joltages_str = line[line.find('{') + 1:line.find('}')].strip()
        joltages = [int(x) for x in joltages_str.split(',')]
        
        machines.append(Machine(num_lights, target_state, button_masks, joltages))

    return machines

def part1(data: list[str]):
    machines = parse_input(data)
    total_presses = 0
    
    for i, machine in enumerate(machines):
        logger.debug(f"Machine {i}: {machine}")
        presses = machine.get_presses()
        logger.debug(f"Presses: {presses}")
        total_presses += presses
        
    return total_presses

def part2(data: list[str]):
    return "To Be Implemented"

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines()
    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        [.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
        [...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
        [.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}"""))
    sample_answers = [7]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = ["uvwxyz"]
    test_solution(part2, sample_inputs, sample_answers)
     
    # Part 2 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 2 soln={part2(input_data)}")

def test_solution(soln_func, sample_inputs: list, sample_answers: list):
    """
    Tests a solution function against multiple sample inputs and expected answers.
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
