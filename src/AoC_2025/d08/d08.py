"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/8

We have junction boxes in 3D space, connected by strings of lights.
Our input is the 3D coordinates of the junction boxes.
When junction boxes are connected, they form a circuit.
We need to connect the junction boxes with shortest strings, using straight line distance.

Part 1:

What is the product of the sizes of the three largest circuits?

Solution approach:
- Create a function that finds euclidean distance between two points
- Get the distances for all pairs using itertools.combinations.
- Sort the connections by distance and take the n shortest
- Build an adjacency dictionary from these shortest connections - these are our connected boxes
- Use BFS for all boxes, to build a list of circuits, leveraging our adjacency dictionary
- Sort the circuits by size; largest first
- Return the product of the sizes of the three largest circuits

Part 2:

We need to keep connecting circuits until we have a single circuit.
We must find identify the pair of boxes that results in a single circuit.
Then, return the product of the x coordinates of these two boxes, as required by the puzzle.

Solution approach:
- Connecting boxes using the adjacency dictionary is no longer a good idea.
- We need to connect boxes one pair at a time, and count how many circuits remain after each connection.
- Create a CircuitNetwork class to manage the set of separate circuits 
  using the Union-Find (Disjoint Set Union) algorithm. I.e.
  - Initially each box is its own circuit
  - Circuits are then merged, i.e. by connecting two circuits
  - The total number of disjoint sets (remaining circuits) is tracked

"""
import logging
import sys
import textwrap
from collections import deque
from itertools import combinations
from typing import NamedTuple

import dazbo_commons as dc  # For locations
from rich.logging import RichHandler

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 8

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

class Box(NamedTuple):
    """ The location of a Junction Box in 3D space """
    x: int
    y: int
    z: int

def get_distance(box1: Box, box2: Box) -> int:
    """ Returns the Euclidean distance between two boxes:
    the square root of the sum of the squares of the differences of their coordinates. 
    """
    return ((box1.x - box2.x)**2 + (box1.y - box2.y)**2 + (box1.z - box2.z)**2)**0.5

def part1(data: list[str], num_shortest_connections: int=10, num_largest_circuits: int=3):
    """
    Find the 3 largest circuits and return the product of their sizes, using BFS.
    """
    boxes = [Box(*map(int, point.split(","))) for point in data] # E.g. (162, 817, 812)
    connections = list(combinations(boxes, 2)) # E.g. ((162, 817, 812), (425, 690, 689))
    connections.sort(key=lambda x: get_distance(x[0], x[1])) # Sort by distance
    
    # build adjacency dict - represents connecting n boxes
    adj_dict = {box: [] for box in boxes}
    for box1, box2 in connections[:num_shortest_connections]:
        adj_dict[box1].append(box2)
        adj_dict[box2].append(box1)

    def find_circuits():
        """ 
        BFS to find all the circuits. 
        A circuit is defined as connected junction boxes 
        """
        visited = set()
        circuits = [] # our list of separate circuits
        
        for box in boxes:
            if box in visited:
                continue
                
            # Start a new circuit
            circuit = set() 
            queue = deque([box]) # For efficient queue operations
            visited.add(box)
            
            # Process all connected boxes in this circuit
            while queue:
                current = queue.popleft()
                circuit.add(current)
                
                for neighbor in adj_dict[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            circuits.append(circuit)

        return circuits
    
    circuits = find_circuits()
    circuits.sort(key=len, reverse=True) # Sort, largest first
    for circuit in circuits:
        logger.debug(f"circuit={circuit}")

    assert len(circuits) >= num_largest_circuits, f"Not enough circuits found: {len(circuits)} < {num_largest_circuits}"
    return len(circuits[0]) * len(circuits[1]) * len(circuits[2])

class CircuitNetwork:
    """
    Manages the set of separate circuits using the Union-Find (Disjoint Set Union) algorithm.
    
    Track connected components in the junction box network.
    - Initially each box is its own circuit
    - Circuits are then merged, i.e. by connecting two circuits
    - The total number of disjoint sets (remaining circuits) is tracked
    """

    def __init__(self, boxes):
        """ Initialise the network with each box in its own individual circuit. """
        # Dictionary mapping each box to its "leader" in the set.
        # When not connected to anything, a box is its own leader.
        self.circuit_leader = {box: box for box in boxes}
        
        # Track the number of disjoint sets remaining. Initially, all boxes are separate.
        self.circuit_count = len(boxes) 

    def find(self, box):
        """
        Finds the representative 'leader' of the circuit a box belongs to.
        
        Uses path compression: points the box directly to the root leader
        to speed up future queries.
        """
        if self.circuit_leader[box] != box: # If this box is not its own leader
            self.circuit_leader[box] = self.find(self.circuit_leader[box]) # Find the root leader
        return self.circuit_leader[box]

    def union(self, box1, box2):
        """
        Merges the circuits of two boxes.
            
        Returns:
            True if the boxes were in different circuits and a merge occurred.
            False if they were already in the same circuit.
        """
        leader1 = self.find(box1)
        leader2 = self.find(box2)

        if leader1 != leader2:
            # Arbitrarily make leader2 the parent of leader1
            self.circuit_leader[leader1] = leader2
            self.circuit_count -= 1
            return True # Merged
        return False # Already in same set

def part2(data: list[str]):
    boxes = [Box(*map(int, point.split(","))) for point in data] # E.g. (162, 817, 812)
    connections = list(combinations(boxes, 2)) # E.g. ((162, 817, 812), (425, 690, 689))
    connections.sort(key=lambda x: get_distance(x[0], x[1])) # Sort by distance
    
    uf = CircuitNetwork(boxes)
    
    # Iterate through shortest connections
    for box1, box2 in connections:
        if uf.union(box1, box2): # Connect them
            # If this connection reduced the number of circuits to 1, we are done
            if uf.circuit_count == 1:
                return box1.x * box2.x
                
    return None

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
        162,817,812
        57,618,57
        906,360,560
        592,479,940
        352,342,300
        466,668,158
        542,29,236
        431,825,988
        739,650,466
        52,470,668
        216,146,977
        819,987,18
        117,168,530
        805,96,715
        346,949,466
        970,615,88
        941,993,340
        862,61,35
        984,92,344
        425,690,689"""))
    sample_answers = [40]
    test_solution(part1, sample_inputs, sample_answers)

    # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data, num_shortest_connections=1000)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_answers = [25272]
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
