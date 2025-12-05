"""
AoC 2025 Day 5 Visualization

This script creates a console-based animation of intervals falling and merging.
It handles the massive scale of the input numbers by implementing a dynamic
"Zoom Out" mechanic.

Concepts:
- **Orbital View:** We start at scale 1:1. As numbers get bigger, we zoom out (scale x5).
- **The Rain:** New intervals fall from the sky.
- **The Ground:** Merged intervals accumulate at the bottom.
- **Heat Map:** Colors shift (Green->Cyan->Blue->Yellow->Orange->Red->Magenta) as we zoom out to indicate magnitude.
"""

import time
from math import log10
from pathlib import Path

import d05  # type: ignore
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class ConsoleVisualizer:
    """
    Manages the state and rendering of the interval visualization.
    """
    def __init__(self, input_file: Path):
        self.console = Console()
        self.input_file = input_file
        
        # Load and sort data
        with open(input_file) as f:
            data = f.read().strip()
        self.raw_ranges, _ = d05.parse_input(data)
        self.raw_ranges.sort()
        
        # Normalize to 0 to enable zoom effect even if numbers start high
        if self.raw_ranges:
            min_offset = self.raw_ranges[0][0]
            for r in self.raw_ranges:
                r[0] -= min_offset
                r[1] -= min_offset
        
        # Demo Limit (optional, full set is huge)
        # self.raw_ranges = self.raw_ranges[:100]

        # Visualization State
        self.current_scale = 1.0 
        self.view_width = 100 # Characters wide
        self.stack: list[list[int]] = [] # Merged intervals [start, end] stored here
        
    @property
    def scale(self):
        return self.current_scale

    def to_screen_x(self, val: int) -> int:
        """Projects a value to screen X coordinate based on current scale."""
        return int(val / self.scale)

    def get_max_screen_x(self):
        """Returns the screen X coordinate of the largest value in current state."""
        if not self.stack:
            return 0
        return self.to_screen_x(self.stack[-1][1])

    def check_zoom(self, next_interval_end: int):
        """Checks if we need to zoom out to fit the next interval."""
        screen_end = self.to_screen_x(next_interval_end)
        
        # If the new interval would fall off the screen
        if screen_end >= self.view_width:
            # ONE STEP ZOOM ONLY - Allows animation of the zoom process
            self.current_scale *= 5.0
            return True # Zoom happened
        return False

    def render_row(self, interval: list[int] | None, color: str = "red") -> str:
        """Renders a single row string with the interval placed correctly."""
        if interval is None:
            return " " * self.view_width
            
        start_x = self.to_screen_x(interval[0])
        end_x = self.to_screen_x(interval[1])
        
        # Clamp width to at least 1 char
        width = max(1, end_x - start_x + 1)
        
        # Construct line
        line = list(" " * self.view_width)
        
        # Draw bars
        for i in range(width):
            if start_x + i < self.view_width:
                line[start_x + i] = "█"
        
        return f"[{color}]{''.join(line)}[/{color}]"

    def render_stack(self, color: str = "green") -> Text:
        """Renders the accumulated stack at the bottom."""
        line = list(" " * self.view_width)
        
        for start, end in self.stack:
            start_x = self.to_screen_x(start)
            end_x = self.to_screen_x(end)
            width = max(1, end_x - start_x + 1)
            
            for i in range(width):
                if start_x + i < self.view_width:
                    line[start_x + i] = "█"
                    
        return Text("".join(line), style=color)

    def get_color_theme(self):
        """Returns (falling_color, stack_color) based on scale."""
        # Scale: 1 -> ~10^14.
        # Break down into granular steps to keep the lights show interesting.
        
        # Format: (Falling Color, Stack Color)
        # Steps 0-7: Green (Preamble)
        # Steps 8-11: Cyan (4 Steps)
        # Steps 12-15: Blue (4 Steps)
        # Step 16: Yellow (1 Step)
        # Step 17: Orange (1 Step)
        # Step 18: Red (1 Step)
        # Step 19: Magenta (1 Step)
        # Finale: White/Cyan
        
        # Adjusted to ensure distinct visual phases.
        # Format: (Falling, Stack)
        
        # Use float for precision to catch the 0.7 order increments of x5 zoom
        order = log10(self.current_scale)
        
        # 1. Start (Small numbers): Organic/Earth (Steps 0-7)
        if order < 4.9:
            return "bright_green", "green"
            
        # 2. Mechanization: Cyan (Steps 8-11 -> 4 Steps)
        if order < 7.7:
            return "cyan", "blue"
            
        # 3. Data Flow: Blue (Steps 12-15 -> 4 Steps)
        if order < 10.5:
            return "dodger_blue1", "blue"

        # 4. Energy Build: Yellow (Step 16 -> 1 Step)
        if order < 11.2:
            return "bright_yellow", "yellow"
            
        # 5. Reaction: Orange (Step 17 -> 1 Step)
        if order < 11.9:
            return "orange1", "dark_orange"
            
        # 6. Critical Mass: Red (Step 18 -> 1 Step)
        if order < 12.6:
            return "bright_red", "red"
            
        # 7. Singularity: Magenta (Step 19 -> 1 Step)
        if order < 13.3:
            return "bright_magenta", "magenta"

        # 8. Finale
        return "bright_white", "bright_cyan"

    def run(self):
        # Initial zoom setup - REMOVED fast forward so we see the initial zoom sequence
        # self.check_zoom(self.raw_ranges[0][1]) (This is handled in the loop now)
        
        falling_interval = None
        falling_y = 0
        processing_idx = 0
        
        zoom_message = None
        zoom_timer = 0
        
        # Prepare layout
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="sky", size=10),
            Layout(name="ground", size=3)
        )
        
        with Live(layout, refresh_per_second=30, console=self.console):
            while processing_idx < len(self.raw_ranges) or falling_interval is not None:
                
                # Logic: Spawn new interval if none falling
                if falling_interval is None and processing_idx < len(self.raw_ranges):
                    next_interval = self.raw_ranges[processing_idx]
                    
                    # Check Zoom BEFORE spawning
                    if self.check_zoom(next_interval[1]):
                        # Zoom triggered (one step)
                        zoom_message = "ZOOMING OUT! scale x5"
                        zoom_timer = 20 # frames
                        # Do NOT spawn yet. Loop back to render zoom effect.
                    else:
                        # Fits! Spawn it.
                        falling_interval = next_interval
                        falling_y = 0
                        processing_idx += 1
                
                # Logic: Move Falling
                if falling_interval:
                    falling_y += 1
                    
                    # Hit ground?
                    if falling_y >= 9: # Sky height (10) - 1 roughly
                        # --- Merge Logic ---
                        # This replicates the core logic of d05.py but step-by-step
                        # 1. If stack empty, just add
                        # 2. If overlap with top of stack, merge (extend end)
                        # 3. If no overlap, push new interval to stack
                        if not self.stack:
                            self.stack.append(falling_interval)
                        else:
                            top = self.stack[-1]
                            if falling_interval[0] <= top[1]:
                                # Merge
                                top[1] = max(top[1], falling_interval[1])
                            else:
                                # Stack
                                self.stack.append(falling_interval)
                        
                        falling_interval = None
                        falling_y = 0

                # Render
                falling_color, stack_color = self.get_color_theme()
                
                # 1. Header
                scale_str = f"{self.scale:,.0f}" if self.scale >= 10 else f"{self.scale:.0f}"
                max_val = self.stack[-1][1] if self.stack else 0
                header_content = (
                    f"Range: {processing_idx}/{len(self.raw_ranges)} | "
                    f"Scale: 1:{scale_str} | "
                    f"Max Value: {max_val:,}"
                )
                header_text = Text(header_content, style="bold white")
                layout["header"].update(Panel(header_text))
                
                # 2. Sky
                if zoom_timer > 0:
                    zoom_timer -= 1
                    layout["sky"].update(Panel(
                        Align.center(f"[bold yellow blink]{zoom_message}[/]", vertical="middle"), 
                        title="Incoming Ranges"
                    ))
                else:
                    sky_rows = []
                    for y in range(10):
                        if falling_interval and y == falling_y:
                            sky_rows.append(self.render_row(falling_interval, falling_color))
                        else:
                            sky_rows.append("")
                    layout["sky"].update(Panel("\n".join(sky_rows), title="Incoming Ranges"))
                
                # 3. Ground
                layout["ground"].update(Panel(self.render_stack(stack_color), title="Merged Intervals", style=stack_color))

                # Dynamic sleep logic:
                # User wants "slower start, faster zoom".
                # 0.25s (start) -> 0.005s (max speed)
                # Acceleration increases exponentially (Power 1.5)
                
                if zoom_timer > 0:
                    sleep_time = 0.05 # Fixed readable speed for messages
                else:
                    current_order = log10(self.current_scale)
                    max_order = 13.5 # Matches max data ~13.3
                    
                    # Interpolation t (0.0 to 1.0)
                    t = min(1.0, max(0.0, current_order / max_order))
                    
                    # Exponential acceleration:
                    # Sleep time drops proportional to distance_to_end^1.5
                    # This creates a massive speed up in the final 20%
                    start_speed = 0.25
                    min_speed = 0.005
                    
                    sleep_time = start_speed * ((1.0 - t) ** 1.5)
                    sleep_time = max(min_speed, sleep_time)
                    
                time.sleep(sleep_time)
        
        self.console.print("[bold green]Visualization Complete![/]")

if __name__ == "__main__":
    locations = d05.locations
    viz = ConsoleVisualizer(Path(locations.input_file))
    viz.run()
