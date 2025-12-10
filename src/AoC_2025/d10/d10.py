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

Solution assertions:
- We can press any combination of buttons.
- But each button need only be pressed once, because pressing it again simply reverts the state.
- Input has a max of around 13 buttons, and therefore max of 2**13 (8192) button combinations per machine.
- This is small so we can brute force all combinations.

Solution:

- Simply test all combinations of of single button presses, starting with one button, 
  all the way to k buttons, where k is the max number of buttons.
- For each combination, calculate the result of pressing those buttons, using XOR.
- If the result matches the target state, return the number of button presses, i.e. k.

Part 2:

Each machine needs to be configured to exactly the specified joltage levels.
E.g. {3,5,4,7} means we need to configure the joltage levels to 3, 5, 4, and 7.

Joltage levels are initially set to 0 per joltage requirement.
Buttons now increase joltage levels; indicator lights are irrelevant for this part.
The button "tuple" now indicates which joltage counters are incremented.
E.g. button (1,3) increases the joltage counters at index 1 and 3 by 1.

What is the fewest button presses required to correctly configure the joltage level counters
on all of the machines?

Solution:

I think this might be a linear algebra problem. I've used SymPy for solving linear equations before.
But simple linear equations don't work here, because we have so many variables.
We need an optimal solution, and one that is constrained to only integer values.
(As the problem states: we can't do half a button press!)

We can use Integer Linear Programming (ILP) to solve this.

"""
import itertools
import logging
import sys
import textwrap
from dataclasses import dataclass

import dazbo_commons as dc
import numpy as np
from rich.logging import RichHandler
from scipy.optimize import Bounds, LinearConstraint, milp

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
    num_lights: int 
    target_lights: int 
    button_indices: list[list[int]] 
    target_joltages: list[int]
    
    def __post_init__(self):
        """ Create button masks from button indices """
        self.button_masks = [sum(1 << i for i in indices) for indices in self.button_indices]

    def get_presses_for_lights(self) -> int:
        """ Part 1: Minimum button presses to match target light state, 
        using brute force of all possible button combinations. """
        num_buttons = len(self.button_masks)
        
        # Try k presses, from 0 to num_buttons
        for k in range(num_buttons + 1): # E.g. [0, 1, 2, 3]
            # We can brute force all combinations of k buttons
            for combo in itertools.combinations(self.button_masks, k):
                # Calculate the result of pressing these k buttons
                current_state = 0
                for mask in combo: # Apply each button in the combo
                    current_state ^= mask # XOR to combine button effects
                if current_state == self.target_lights:
                    return k  
        raise ValueError("No solution found for machine")

    def get_presses_for_joltages(self) -> int:
        """ 
        Part 2: Minimum button presses to match target joltages.
        
        This problem is an optimization problem where we need to find non-negative integers.
        We model this as an Integer Linear Programming (ILP) problem:
        
        Variables: x[0], x[1], ... x[num_buttons-1] = number of times to press each button.
        Objective: Minimize sum(x) (total button presses).
        Constraints: The sum of button effects must exactly equal the target joltage for each light.
        
        We use `scipy.optimize.milp` to solve this efficiently.
        """
        num_buttons = len(self.button_indices)
        
        # Build the Coefficient Matrix 'A' (num_lights rows x num_buttons cols)
        # Each row 'i' represents a light (equation).
        # Each col 'j' represents a button (variable).
        # A[i][j] = 1 means "Button j adds 1 to Light i".
        A = np.zeros((self.num_lights, num_buttons))
        for j, indices in enumerate(self.button_indices):
            for i in indices:
                A[i, j] = 1
                
        # Build the Target Vector 'b'
        # These are the RHS values for our equations: "Light i needs 5 jolts".
        # Equation i: Sum(Buttons affecting Light i) = b[i]
        b = np.array(self.target_joltages)
        
        # Define the Cost Vector 'c'
        # The solver minimizes the dot product of c and x (c · x).
        # This means it minimizes: (c[0]*x[0] + c[1]*x[1] + ... + c[n]*x[n])
        # Since we want to minimize the *total count* of presses, every button costs 1.
        # If we wanted to minimize just Button 0 presses, c would be [1, 0, 0...].
        c = np.ones(num_buttons)
        
        # Define Linear Constraints
        # A @ x == b  (The button effects sum to exactly the target)
        constraints = LinearConstraint(A, b, b)
        
        # Define Integrality Constraint
        # We need whole number button presses. 0.5 presses doesn't exist.
        # 1 = Integer, 0 = Continuous. We set all to 1.
        integrality = np.ones(num_buttons)
        
        # Define Bounds
        # We can't have negative button presses (lb=0).
        # upper bound is infinity.
        bounds = Bounds(lb=0, ub=np.inf)
        
        # Run the Mixed-Integer Linear Programming Solver
        res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)
        
        if not res.success:
            logger.warning(f"MILP failed for joltages {self.target_joltages}: {res.message}")
            return 0
            
        # Result x is returned as floats, even with integer constraints.
        # Due to floating point precision, 5 might be 4.99999999.
        # Casting directly to int() would floor it to 4 (wrong).
        solution = np.round(res.x).astype(int)
        
        # Verify we have a solution
        # (A @ solution) means Matrix A multipled by Vector solution.
        # This calculates the actual produced joltages for each light.
        if not np.all(A @ solution == b):
             logger.error("MILP solution verification failed")
             return 0
             
        return int(np.sum(solution))

    def __str__(self):
        return f"Target: {bin(self.target_lights)[2:]}, " \
             + f"Buttons: [{', '.join([bin(b)[2:] for b in self.button_masks])}], " \
             + f"Joltages: {self.target_joltages}"

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
        # The buttons are between ] and {
        # Note: We need a slight correction here from original logic to use start of {
        buttons_str = line[diagram_end+1:line.find('{')].strip()
        parts = buttons_str.split(' ')
        button_indices = []
        for part in parts:
            # bit of a hacky parse: remove ( and ) and split by comma
            nums = [int(x) for x in part[1:-1].split(',')]
            
            # Create mask
            mask = 0
            for light_idx in nums:
                mask |= (1 << light_idx)
                
            button_indices.append(nums)
        
        # 3. Extract Joltages, e.g. {3,5,4,7}
        joltages_str = line[line.find('{') + 1:line.find('}')].strip()
        joltages = [int(x) for x in joltages_str.split(',')]
        
        machines.append(Machine(num_lights, target_state, button_indices, joltages))

    return machines

def part1(data: list[str]):
    machines = parse_input(data)
    total_presses = 0
    
    for i, machine in enumerate(machines):
        logger.debug(f"Machine {i}: {machine}")
        presses = machine.get_presses_for_lights()
        logger.debug(f"Presses: {presses}")
        total_presses += presses
        
    return total_presses

def part2(data: list[str]):
    """ Part 2: Minimum button presses to match target joltages. """
    machines = parse_input(data)
    total_presses = 0
    for _, machine in enumerate(machines):
        presses = machine.get_presses_for_joltages()
        total_presses += presses
    return total_presses

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
    sample_answers = [33]
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
