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
from pathlib import Path
from typing import NamedTuple

import dazbo_commons as dc  # For locations
import matplotlib.animation as animation
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from rich.logging import RichHandler
from tqdm import tqdm

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 8

SHOULD_ANIMATE = True # Flag as requested
ANIMATION_INTERVAL_MS = 30
PAUSE_DURATION_SEC = 4.0

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
    
    # Build adjacency graph for the N shortest connections
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

    assert len(circuits) >= num_largest_circuits, f"Not enough circuits found: {len(circuits)}"
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
        
        # Track the size of each circuit (for visualization)
        # Leader -> Size
        self.circuit_sizes = dict.fromkeys(boxes, 1) 

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
            
            # Update size
            self.circuit_sizes[leader2] += self.circuit_sizes[leader1]
            del self.circuit_sizes[leader1] # Optional cleanup
            
            return True # Merged
        return False # Already in same set

class CircuitVisualiser:
    """ 
    Handles the 3D visualization of circuit merging 
    """
    def __init__(self, boxes, output_file: Path):
        self.output_file = output_file
        
        # Setup Plot
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(1, 1, 1, projection='3d')
        self.ax.set_axis_off() 
        self.ax.set_facecolor('black')
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # Remove all whitespace
        
        # Initial Data
        self.xs = [b.x for b in boxes]
        self.ys = [b.y for b in boxes]
        self.zs = [b.z for b in boxes]
        
        # Initialize colors
        self.box_colors = ['dodgerblue'] * len(boxes)
        
        # Plot initial points
        self.scatter = self.ax.scatter(self.xs, self.ys, self.zs, c=self.box_colors, s=15, alpha=0.8)
        
        self.title_text = self.ax.text2D(0.05, 0.95, f"Circuits: {len(boxes)}", 
                                        transform=self.ax.transAxes, color='white', fontsize=14)
        
        # Line Collection: Renders all established connections efficiently.
        # This is strictly for performance; plotting 1000+ individual Line3D objects kills FPS.
        self.line_segments = []
        self.line_collection = Line3DCollection([], colors='white', linewidths=1.5, alpha=0.5)
        self.ax.add_collection(self.line_collection)
        
        # Track the "current" (flashing) line separately
        self.current_line_artist = None
        self.current_line_segment = None
        
        self.frame_count = 0

    def update_with_state(self, connection, count, is_merge, sizes):
        frame_data = (connection, count, is_merge, sizes)
        return self.update(frame_data)

    def update(self, frame_data, uf=None, boxes=None):
        # Unpack frame data
        # frame_data is variable length: 
        # - 4 elements for standard simulation frames (connection, count, is_merge, sizes)
        # - 5 elements for end-sequence frames (..., effect_state)
        # We slice [:4] to safely unpack the core data common to both.
        connection, count, is_merge, sizes = frame_data[:4]
        
        # Rotation
        angle = (self.frame_count * 0.5) % 360
        self.ax.view_init(elev=20, azim=angle)
        self.frame_count += 1
        
        self.title_text.set_text(f"Circuits: {count}")
        
        # Handle "New" Line from previous frame becoming "Old"
        if self.current_line_segment:
             self.line_segments.append(self.current_line_segment)
             self.line_collection.set_segments(self.line_segments)
             self.current_line_segment = None
             
        # Remove the previous "flash" artist if it exists
        if self.current_line_artist:
             self.current_line_artist.remove()
             self.current_line_artist = None
        
        if is_merge and connection:
            b1, b2 = connection
            
            # Map sizes to colors
            # Rule:
            # - Size 1 (Unconnected): Blue
            # - Size > 1 (Connected): Gradient from Red -> Orange -> White based on simulation progress
            if sizes:
                # Calculate global progress (0.0 to 1.0)
                # count goes from len(boxes) down to 1
                total_boxes = len(self.xs)
                progress = 1.0 - ((count - 1) / (total_boxes - 1))
                
                # "hot" colormap: 0.0 is black, 0.35 is red, 1.0 is white
                # We want to map progress 0.0 -> 0.35 (Red) and 1.0 -> 1.0 (White)
                colormap_start = 0.35
                heat_val = colormap_start + (progress * (1.0 - colormap_start))
                connected_color = cm.hot(heat_val)
                
                # Assign colors
                # LOGIC CHANGE: Only update colors for boxes that are newly connected.
                # If a box is connected (s > 1) but currently blue, it becomes the current connected_color.
                # If a box is already connected (not blue), it KEEPS its color.
                new_colors = []
                for idx, size in enumerate(sizes):
                     current_c = self.box_colors[idx]
                     if size > 1 and current_c == 'dodgerblue':
                         new_colors.append(connected_color)
                     else:
                         new_colors.append(current_c)
                
                self.box_colors = new_colors
                self.scatter.set_color(self.box_colors)
            
            # Draw NEW line (Bright White, Thick)
            # We plot this individually so it pops
            line, = self.ax.plot([b1.x, b2.x], [b1.y, b2.y], [b1.z, b2.z], c='white', alpha=1.0, linewidth=4)
            self.current_line_artist = line
            
            # Store segment for next frame to move to collection
            self.current_line_segment = [(b1.x, b1.y, b1.z), (b2.x, b2.y, b2.z)]
            
        # Return all artists that need redrawing (for blitting, though we don't use blit here)
        artists = [self.title_text, self.scatter, self.line_collection]
        if self.current_line_artist:
             artists.append(self.current_line_artist)
             
             artists.append(self.current_line_artist)
             
        # Handle End-Sequence Effects
        if len(frame_data) > 4:
            effect_state = frame_data[4]
            if effect_state:
                # Zoom Effect: Interpolate dist from 7.0 (default) to 4.5
                progress = effect_state['progress']
                self.ax.dist = 7.0 - (2.5 * progress)
                
                # Pulse Effect: Modulate Scatter Size
                # Base size 15, pulse up to 50
                pulse = (np.sin(progress * np.pi * 4) + 1) / 2 # 0 to 1 oscillating
                pulse_factor = 1.0 + (pulse * 1.5) # 1.0 to 2.5x
                
                # Make sure we pass a numpy array to set_sizes for 3D scatter
                # and ensure it matches the number of points
                current_sizes = np.array([15.0] * len(sizes)) 
                self.scatter.set_sizes(current_sizes * pulse_factor)
        
        return artists

    def reset(self):
        """ Resets the visualization state for a new animation save. """
        self.line_segments = []
        self.line_collection.set_segments([])
        self.frame_count = 0
        
        # Clear "current" line state so it doesn't carry over
        self.current_line_segment = None
        if self.current_line_artist:
            self.current_line_artist.remove()
            self.current_line_artist = None
        
        
        # Reset colors and sizes to initial state
        self.box_colors = ['dodgerblue'] * len(self.xs)
        self.scatter.set_color(self.box_colors)
        initial_sizes = np.array([15.0] * len(self.xs))
        self.scatter.set_sizes(initial_sizes) 
        self.title_text.set_text(f"Circuits: {len(self.xs)}")
        self.ax.dist = 7.0 # Reset zoom level (closer startup)

    def generate_and_save(self, simulation_gen, output_files, total_steps_est=0):
        """
        Consumes the simulation generator, adds effects, and saves to files.
        """
        frames_list = []
        logger.info("Pre-calculating simulation states...")
        
        # 1. Pre-calculate frames
        for frame in tqdm(simulation_gen, total=total_steps_est, desc="Simulating"):
            frames_list.append(frame)
        
        # 2. Add End-Sequence Effects
        if frames_list:
            last_frame = frames_list[-1]
            last_connection, last_count, last_is_merge, last_sizes = last_frame
            
            fps = 30
            total_effect_frames = int(fps * PAUSE_DURATION_SEC)
            
            for i in range(total_effect_frames):
                progress = i / total_effect_frames
                # Create effect state
                effect = {'progress': progress, 'type': 'finish'}
                frames_list.append((last_connection, last_count, last_is_merge, last_sizes, effect))
        
        # 3. Create Animation Object
        def update_wrapper(frame):
             # Unpack frame. Might have 4 or 5 elements.
             return self.update(frame)
             
        ani = animation.FuncAnimation(
            self.fig,
            update_wrapper,
            frames=frames_list,
            interval=ANIMATION_INTERVAL_MS,
            blit=False,
            save_count=len(frames_list) + 10 
        )
        
        # 4. Save to files
        for out_file in output_files:
            output_file_path = Path(out_file)
            if output_file_path.exists():
                logger.info(f"File {output_file_path.name} already exists. Skipping.")
                continue

            # RESET STATE for each file (otherwise lines accumulate)
            self.reset()
            
            logger.info(f"Saving animation to {output_file_path}...")
            
            total_frames = len(frames_list)
            pbar = tqdm(total=total_frames, desc=f"Saving {output_file_path.suffix.upper()}", unit="frame")
            
            def progress_callback(current_frame, total_frames_, pbar=pbar):
                pbar.n = current_frame
                pbar.refresh()
            
            # Choose writer based on extension
            save_kwargs = {
                'writer': 'pillow',
                'fps': 30,
                'progress_callback': progress_callback
            }
            
            if output_file_path.suffix == '.mp4':
                save_kwargs['writer'] = 'ffmpeg'
                save_kwargs['extra_args'] = ['-vcodec', 'libx264']
            else:
                logger.info("Encoding GIF... this may take a moment after the bar fills.")

            ani.save(output_file_path, **save_kwargs)
            pbar.close()
            
        return frames_list[-1][0] if frames_list else None # Return last connection for answer extraction check if needed

def part2(data: list[str], visualize: bool = False, output_files: list[Path] | None = None):
    boxes = [Box(*map(int, point.split(","))) for point in data] 
    connections = list(combinations(boxes, 2)) 
    connections.sort(key=lambda x: get_distance(x[0], x[1])) 
    
    uf = CircuitNetwork(boxes)
    
    vis = None
    if visualize and output_files:
        vis = CircuitVisualiser(boxes, output_files[0]) # Path doesn't matter much to init
    
    # Generator for visualization
    def simulation_gen():
        # Initial frame
        yield (None, uf.circuit_count, False, [uf.circuit_sizes.get(uf.find(b), 1) for b in boxes])
        
        for box1, box2 in connections:
            is_merge = uf.union(box1, box2)
            if is_merge:
                # Calculate sizes for coloring
                # Optimization: Only calculate if visualizing
                sizes = [uf.circuit_sizes.get(uf.find(b), 1) for b in boxes]
                yield ((box1, box2), uf.circuit_count, True, sizes)
                
                if uf.circuit_count == 1:
                    break
    
    if visualize:
        # Generate animation and save
        # It takes N-1 merges to connect N items. So exactly len(boxes)-1 frames.
        total_merges = len(boxes) - 1
        return_connection = vis.generate_and_save(simulation_gen(), output_files, total_steps_est=total_merges)
        
        # Extract the answer from the last connection of the simulation
        if return_connection:
             box1, box2 = return_connection
             return box1.x * box2.x
        return None

    else:
        # Standard execution (No visualization)
        for box1, box2 in connections:
             if uf.union(box1, box2):
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
    
    # Animation specific behavior
    # User requested: "create the output if it doesn't already exist, AND if we've turned on an 'animate' flag"
    vis_file_gif = locations.output_dir / "2025_d08_vis.gif"
    vis_file_mp4 = locations.output_dir / "2025_d08_vis.mp4"
    
    # Check if needs generation
    visualize = SHOULD_ANIMATE and (not vis_file_gif.exists() or not vis_file_mp4.exists())
    
    with ac.timer():
        logger.info(f"Part 2 soln={part2(input_data, visualize=visualize, output_files=[vis_file_gif, vis_file_mp4])}")

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
