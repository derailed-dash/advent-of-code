"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/11

We need to connect a new server rack to the reactor!
The input is a list of devices and their outputs. E.g.

```
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
```

Part 1:

How many different paths lead from you to out?

Let's build a graph with NetworkX and use its built-in function to find all paths.

Part 2:

Find all of the paths that lead from svr to out.
How many of those paths visit both dac and fft?

Solution Approach:

My first thought was simply to do the same as Part1, but with a different source and target.
(I guessed there would be a gotcha with this approach!)
It turns out that there's just far too many paths and this doesn't complete.
So we need a smarter way to find the valid paths.

There are two valid sequences to visit both devices `dac` and `fft`:

1. svr -> dac -> fft -> out
2. svr -> fft -> dac -> out

For sequence 1, we can:

1. Count paths from svr -> dac
2. Count paths from dac -> fft
3. Count paths from fft -> out

Multiply the counts together to get the total number of paths.
Then repeat for sequence 2.

Because there are so many paths to check, we need to optimise.
I've used a memoized recursive function to count paths between nodes.
"""
import logging
import sys
import textwrap
from collections.abc import Sequence
from functools import cache
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 11

VIS_ENABLED = False

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

def parse_input(data: list[str]) -> list[tuple[str, str]]:
    """ Parse the input into a list of edges. I.e. (device, output) """
    edges = []
    for line in data:
        device, outputs = line.split(":")
        for output in outputs.split():
            edges.append((device.strip(), output.strip()))

    return edges

def part1(data: list[str]):
    """ Find all paths from `you` to `out` """
    edges = parse_input(data)
    graph = nx.DiGraph(edges)
    logger.debug(graph)
    
    paths = list(nx.all_simple_paths(graph, source="you", target="out"))
    logger.debug("Paths:")
    for path in paths:
        logger.debug(path)
    return len(paths)

def count_paths_between(graph: nx.DiGraph, start_node: str, end_node: str) -> int:
    """ 
    Count unique paths from start_node to end_node using recursion and memoization.
    """

    @cache
    def _count(current: str) -> int:
        """ Inner function used between the graph itself is unhashable. """
        if current == end_node: # A valid path was found
            return 1
        
        count = 0
        # Outgoing paths must either lead to the end node, 
        # or lead to a node that has no outgoing neighbours.
        for neighbor in graph.neighbors(current):
            count += _count(neighbor)

        return count

    return _count(start_node)

def count_paths_for_sequence(graph, sequence: Sequence[str]):
    """ 
    Count unique paths for a given sequence of nodes, 
    i.e. a list of nodes where there must be paths between each pair. 
    """
    total = 1 # accumulator
    for i in range(len(sequence) - 1): # Count paths between each pair in the sequence
        c = count_paths_between(graph, sequence[i], sequence[i + 1])
        total *= c
        if total == 0: # Pointless continuing
            break
    logger.debug(f"Routes for {sequence}: {total}")
    return total

def render_graph(graph: nx.DiGraph, file: Path):
    """ Render the graph using a layered layout to show flow. """
    plt.figure(figsize=(20, 10)) # Wider figure for the flow
    
    # Calculate generations for layered layout
    # This groups nodes by their distance from the start (topological sort)
    try:
        for i, layer in enumerate(nx.topological_generations(graph)):
            for node in layer:
                graph.nodes[node]["subset"] = i
        pos = nx.multipartite_layout(graph, subset_key="subset", align="horizontal")
    except (nx.NetworkXError, nx.NetworkXUnfeasible):
        logger.warning("Graph is not a DAG, falling back to spring layout")
        pos = nx.spring_layout(graph)

    # Node styling
    node_colors = []
    node_sizes = []
    labels = {} # Only label key nodes
    
    for node in graph.nodes:
        if node == "svr":
            node_colors.append("green")
            node_sizes.append(300)
            labels[node] = node
        elif node == "out":
            node_colors.append("red")
            node_sizes.append(300)
            labels[node] = node
        elif node in ["dac", "fft"]:
            node_colors.append("gold")
            node_sizes.append(300)
            labels[node] = node
        else:
            node_colors.append("dodgerblue")
            node_sizes.append(20)
            # No label for standard nodes

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
    
    # Draw edges with transparency to avoid clutter
    nx.draw_networkx_edges(graph, pos, alpha=0.2, arrowsize=10, edge_color="gray")
    
    # Draw labels only for key nodes
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=12, font_weight="bold")
    
    plt.axis("off") # Hide axis
    
    dir_path = file.parent
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    plt.savefig(file, bbox_inches="tight") # Tight layout
    plt.close() # Free memory
    logger.info(f"Graph rendered to {file}")
    
def part2(data: list[str]):
    """ 
    Find all paths from `svr` to `out` that visit both `dac` and `fft` 
    Valid routes:
    1. svr -> dac -> fft -> out
    2. svr -> fft -> dac -> out
    """
    edges = parse_input(data)
    graph = nx.DiGraph(edges)
    logger.debug(graph)
    if VIS_ENABLED:
        render_graph(graph, locations.output_dir / "graph.png")

    sequences = [
        ("svr", "dac", "fft", "out"),
        ("svr", "fft", "dac", "out")
    ]

    total = 0
    for seq in sequences:
        total += count_paths_for_sequence(graph, seq)

    return total

def main():
    try:
        ac.write_puzzle_input_file(YEAR, DAY, locations)
        with open(locations.input_file, encoding="utf-8") as f:
            input_data = f.read().splitlines() # Most puzzles are multiline strings
            # input_data = f.read().strip() # Raw string
            

    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    with open(locations.input_dir / "sample_input_part_1.txt", encoding="utf-8") as f:
        sample_inputs.append(f.read())
    sample_answers = [5]
    test_solution(part1, sample_inputs, sample_answers)

    # # Part 1 solution
    logger.setLevel(logging.INFO)
    with ac.timer():
        logger.info(f"Part 1 soln={part1(input_data)}")
    
    # Part 2 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    sample_inputs.append(textwrap.dedent("""\
        svr: aaa bbb
        aaa: fft
        fft: ccc
        bbb: tty
        tty: ccc
        ccc: ddd eee
        ddd: hub
        hub: fff
        eee: dac
        dac: fff
        fff: ggg hhh
        ggg: out
        hhh: out"""))
    sample_answers = [2]
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
