"""
Author: Darren
Date: 01/12/2023

Solving https://adventofcode.com/2025/day/9

We're in a movie theater with a big tile floor. 
Puzzle input is the location of red tiles on the floor. It looks like:

```
7,1
11,1
11,7
9,7
```

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
import os
import sys
from itertools import combinations
from typing import NamedTuple

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

import aoc_common.aoc_commons as ac  # General AoC utils

# Set these to the current puzzle
YEAR = 2025
DAY = 9

locations = ac.get_locations(__file__)

# Configure root logger with Rich logging
# Configure root logger with Rich logging
ac.setup_logging()
logger = logging.getLogger(locations.script_name)
logger.setLevel(logging.DEBUG)

class Point(NamedTuple):
    x: int
    y: int

def part1(data: list[str]) -> int:
    """
    Using two red tiles as opposite corners, what is the largest area of any rectangle you can make?
    """
    red_tiles = set()
    for line in data:
        x, y = map(int, line.split(",")) # Input data is location of red tiles
        red_tiles.add(Point(x, y))

    biggest_area = 0
    for point1, point2 in combinations(red_tiles, 2): # Get all pairs of points
        # We need inclusive area
        rectangle_area = (abs(point2.x - point1.x) + 1) * (abs(point2.y - point1.y) + 1)
        biggest_area = max(biggest_area, rectangle_area)
            
    return biggest_area

class PolygonSolver:
    """ Solves the problem using Ray Casting and edge intersection checks. """
    
    def __init__(self, corners: list[Point]):
        """ 
        corners: list of points that represented adjacent red tiles
        """
        self.corners = corners
        self.num_corners = len(corners)
        
        # Pre-calculate edges for intersection checks
        # Store as (x1, y1, x2, y2) tuples
        self.vertical_edges = [] # e.g. (x, y1, y2)
        self.horizontal_edges = [] # e.g. (x1, x2, y)
        
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
            
            # Edge must be strictly to the right of the point
            if vx > px:
                # Ray's Y must be within the edge's Y range
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

def generate_visualization(corners: list[Point], output_file: str):  # noqa: C901
    """
    Generates a GIF visualization of the Ray Casting algorithm.
    Only generates if the file does not already exist.
    """
    vis_path = locations.output_dir / output_file
    if os.path.exists(vis_path):
        logger.info(f"Visualization already exists at {vis_path}. Skipping.")
        return

    logger.info(f"Generating visualization: {vis_path}...")
    
    points = [(p.x, p.y) for p in corners]
    edges = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        edges.append((p1, p2))

    # --- STYLE CONFIGURATION ---
    plt.style.use('dark_background')
    
    # Colors (Neon Cyberpunk Palette)
    BG_COLOR = '#0e1117' # Very dark blue/black
    GRID_COLOR = '#4a4d54' # Brightened from #2a2d34
    POLY_FILL = '#00f0ff' # Cyan
    POLY_EDGE = '#00f0ff'
    RAY_COLOR = '#ff00ff' # Magenta/Pink
    INSIDE_COLOR = '#39ff14' # Neon Green
    OUTSIDE_COLOR = '#ff073a' # Neon Red
    INTERSECT_COLOR = '#ffd700' # Gold
    TEXT_COLOR = '#ff88ff'
    
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    
    margin_x = (x_max - x_min) * 0.1
    margin_y = (y_max - y_min) * 0.1
    
    ax.set_xlim(x_min - margin_x, x_max + margin_x)
    ax.set_ylim(y_min - margin_y, y_max + margin_y)
    
    # Remove standard axes for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.tick_params(axis='x', colors=GRID_COLOR)
    ax.tick_params(axis='y', colors=GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, linestyle='--', linewidth=0.5, alpha=0.3)
    
    ax.set_title("RAY CASTING ALGORITHM // PART 2", color=TEXT_COLOR, fontsize=16, pad=20, fontname='monospace', loc='left')
    
    # Polygon with Glow Effect (simulated by multiple lines)
    poly_patch = patches.Polygon(points, closed=True, fill=True, facecolor=POLY_FILL, 
                                 edgecolor=None, alpha=0.15, zorder=1)
    ax.add_patch(poly_patch)
    
    # Glowing edge
    glow_patch = patches.Polygon(points, closed=True, fill=False, edgecolor=POLY_EDGE, 
                                linewidth=2, alpha=0.8, zorder=2)
    # Simulating outer glow
    glow_patch_outer = patches.Polygon(points, closed=True, fill=False, edgecolor=POLY_EDGE, 
                                linewidth=6, alpha=0.2, zorder=1.5)
    
    ax.add_patch(poly_patch)
    ax.add_patch(glow_patch)
    ax.add_patch(glow_patch_outer)
    
    # --- LASER BEAM & TRAIL SETUP ---
    trail_length = 20
    trail_lines = []
    for i in range(trail_length):
        alpha = 0.4 * (1 - i/trail_length) # Fade out
        # Glow trail
        t_line, = ax.plot([], [], color=RAY_COLOR, linewidth=1.5, alpha=alpha, zorder=9)
        trail_lines.append(t_line)

    # Main Laser Beam
    # 1. Glow (Thick, colored, semi-transparent)
    ray_glow, = ax.plot([], [], color=RAY_COLOR, linewidth=5, alpha=0.5, label='Scanner Ray', zorder=10)
    # 2. Core (cihin, white, solid)
    ray_core, = ax.plot([], [], color='white', linewidth=1.5, alpha=1.0, zorder=11)
    
    # Animated Point
    test_point, = ax.plot([], [], 'o', markersize=8, markeredgecolor='white', markeredgewidth=1.5, zorder=20)
    
    # Intersections
    intersection_points, = ax.plot([], [], 'x', color=INTERSECT_COLOR, markersize=10, markeredgewidth=2, label='Intersections', zorder=15)
    
    # HUD Status Text
    status_text = ax.text(
        0.02, 0.95, '', 
        transform=ax.transAxes, 
        verticalalignment='top', 
        fontsize=12, 
        fontname='monospace',
        color=TEXT_COLOR,
        bbox={'boxstyle': 'round,pad=0.5', 'facecolor': '#000000', 'edgecolor': GRID_COLOR, 'alpha': 0.8}
    )
    
    scan_y = 49500 # Fixed Y for demo
    
    # Find static intersections on this line to know where to pause
    line_intersections = []
    for p1, p2 in edges:
        x1, y1 = p1
        x2, y2 = p2
        if y1 == y2:
            continue
        y_min_edge, y_max_edge = min(y1, y2), max(y1, y2)
        if y_min_edge <= scan_y < y_max_edge:
             if x1 == x2:
                ix = x1
             else:
                ix = x1 + (scan_y - y1) * (x2 - x1) / (y2 - y1)
             line_intersections.append(ix)
    
    line_intersections.sort()
    
    steps = 150
    base_scan_xs = np.linspace(x_min - margin_x/2, x_max + margin_x/2, steps)
    
    final_frames = []
    fps = 20 # Smoother
    pause_duration = 0.8 
    pause_frames = int(fps * pause_duration)
    
    next_ix_idx = 0
    
    for x in base_scan_xs:
        final_frames.append(x)
        if next_ix_idx < len(line_intersections):
            ix = line_intersections[next_ix_idx]
            if x >= ix:
                final_frames.extend([x] * pause_frames)
                next_ix_idx += 1
                while next_ix_idx < len(line_intersections) and (
                    x >= line_intersections[next_ix_idx]
                ):
                    next_ix_idx += 1
                    
    def solve_ray_intersections_left(px, py, edges):
        intersections = []
        for p1, p2 in edges:
            x1, y1 = p1
            x2, y2 = p2
            if y1 == y2:
                continue
            y_min_edge, y_max_edge = min(y1, y2), max(y1, y2)
            if y_min_edge <= py < y_max_edge:
                if x1 == x2:
                    ix = x1
                else:
                    ix = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                
                if ix < px:
                    intersections.append((ix, py))
        return sorted(intersections, key=lambda p: p[0])

    def init():
        ray_glow.set_data([], [])
        ray_core.set_data([], [])
        for line in trail_lines:
            line.set_data([], [])
        test_point.set_data([], [])
        intersection_points.set_data([], [])
        status_text.set_text('')
        return [ray_glow, ray_core, test_point, intersection_points, status_text, *trail_lines]
        
    def animate(i):
        px = final_frames[i]
        py = scan_y
        
        intersections = solve_ray_intersections_left(px, py, edges)
        count = len(intersections)
        is_inside = count % 2 == 1
        
        test_point.set_data([px], [py])
        if is_inside:
            test_point.set_color(INSIDE_COLOR)
            # Add a "halo" effect for the point if inside
            test_point.set_markersize(10)
        else:
            test_point.set_color(OUTSIDE_COLOR)
            test_point.set_markersize(8)
            
        ray_start_x = x_min - margin_x
        
        # Update Main Laser
        # Projectile Effect: Glow travels with the head, trailing behind slightly
        glow_len = 6000 
        glow_start_x = max(ray_start_x, px - glow_len)
        ray_glow.set_data([glow_start_x, px], [py, py])
        
        # Core: Short "Pulse" at the tip
        core_start_x = max(ray_start_x, px - 2000) # Short bright tip
        ray_core.set_data([core_start_x, px], [py, py])
        
        # Update Trail
        for idx, line in enumerate(trail_lines):
            prev_frame_idx = i - (idx + 1) * 3 # Skip frames for distinct trail segments
            if prev_frame_idx >= 0:
                prev_x = final_frames[prev_frame_idx]
                # Trail should be a "Ghost Core" -> Short segment at the previous position
                ghost_len = 3000
                ghost_start = max(ray_start_x, prev_x - ghost_len)
                line.set_data([ghost_start, prev_x], [py, py])
            else:
                 line.set_data([], [])

        if count > 0:
            ixs = [p[0] for p in intersections]
            iys = [p[1] for p in intersections]
            intersection_points.set_data(ixs, iys)
        else:
            intersection_points.set_data([], [])
        
        status_text.set_text(
            f"SCAN_POS : [{int(px):>5}, {int(py):>5}]\n"
            f"INTERSECT: {count:>3}\n"
            f"STATUS   : {'[ INSIDE ]' if is_inside else '[ OUTSIDE ]'}"
        )
        # Dynamic text color (White for Outside, Green for Inside)
        status_text.set_color(INSIDE_COLOR if is_inside else TEXT_COLOR)
        
        # --- DYNAMIC CAMERA ZOOM ---
        # Strategy:
        # 0% - 40%: Full View (1.0x)
        # 40% - 55%: Fast Transition to Close Up (2.5x X, 1.5x Y)
        # 55% - 100%: Close Up
        
        total_frames = len(final_frames)
        progress = i / total_frames if total_frames > 0 else 0
        
        start_zoom_x, end_zoom_x = 1.0, 2.5
        start_zoom_y, end_zoom_y = 1.0, 1.8
        
        t_start = 0.4
        t_end = 0.6 # Fast transition
        
        if progress < t_start:
            current_zoom_x = start_zoom_x
            current_zoom_y = start_zoom_y
        elif progress > t_end:
            current_zoom_x = end_zoom_x
            current_zoom_y = end_zoom_y
        else:
            # Linear Interpolation
            t = (progress - t_start) / (t_end - t_start)
            current_zoom_x = start_zoom_x + (end_zoom_x - start_zoom_x) * t
            current_zoom_y = start_zoom_y + (end_zoom_y - start_zoom_y) * t
            
        # X-Axis Zoom (Follows Ray)
        world_width = (x_max + margin_x) - (x_min - margin_x)
        view_width = world_width / current_zoom_x
        
        view_min_x = px - (view_width / 2.0)
        view_max_x = px + (view_width / 2.0)
        
        # Clamp X
        global_min_x = x_min - margin_x
        global_max_x = x_max + margin_x
        
        if view_min_x < global_min_x:
            view_min_x = global_min_x
            view_max_x = global_min_x + view_width
        elif view_max_x > global_max_x:
            view_max_x = global_max_x
            view_min_x = global_max_x - view_width
            
        ax.set_xlim(view_min_x, view_max_x)
        
        # Y-Axis Zoom (Center of World)
        world_height = (y_max + margin_y) - (y_min - margin_y)
        view_height = world_height / current_zoom_y
        world_center_y = (y_min + y_max) / 2.0
        
        view_min_y = world_center_y - (view_height / 2.0)
        view_max_y = world_center_y + (view_height / 2.0)
        
        ax.set_ylim(view_min_y, view_max_y)

        return [ray_glow, ray_core, test_point, intersection_points, status_text, *trail_lines]

    ani = animation.FuncAnimation(
        fig, animate, init_func=init, 
        frames=len(final_frames), interval=1000/fps, blit=False
    ) # blit=False needed for set_xlim changes
    
    os.makedirs(os.path.dirname(vis_path), exist_ok=True)
    ani.save(vis_path, writer='pillow', fps=fps)
    logger.info(f"Visualisation saved to {vis_path}")
    plt.close(fig) # Cleanup

def part2(data: list[str], vis_filename: str | None = None):
    """
    In our *input list*, every red tile is connected to the red tile before and after it
    by a straight line of green tiles. And the list wraps so the first and last red tiles are connected.
    Adjacent red tiles in the list will always be in the same row or same column.
    Thus, red tiles are corners of the irregular polygon.
    When we form closed loops, internal tiles are also green.

    Now we must choose rectangles that have red in opposite corners, 
    but otherwise ONLY contain green or red tiles.
    What is the largest area of any rectangle you can make?
    """
    red_tiles = [] # Order matters for polygon checks
    for line in data:
        x, y = map(int, line.split(","))
        red_tiles.append(Point(x, y))

    if vis_filename:
        generate_visualization(red_tiles, vis_filename)

    # Initialize Polygon Solver
    solver = PolygonSolver(red_tiles)
    
    biggest_area = 0
    
    for p1, p2 in combinations(red_tiles, 2): # Compare all pairs of points
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
        # If this point is inside the polygon AND no polygon edges intersect the rectangle's interior,
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
            

    except (ValueError, FileNotFoundError) as e:
        logger.error("Could not read input file: %s", e)
        return 1

    # Part 1 tests
    logger.setLevel(logging.DEBUG)
    sample_inputs = []
    with open(locations.input_dir / "sample_input_part_1.txt", encoding="utf-8") as f:
        sample_inputs.append(f.read())
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
        logger.info(f"Part 2 soln={part2(input_data, vis_filename='2025_d09_vis.gif')}")

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
