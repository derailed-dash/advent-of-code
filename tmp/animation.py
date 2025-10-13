# animation.py
import imageio
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.AoC_2016.d8_display_numpy.display_pixels import process_instructions

def generate_animation(data):
    cols = 50
    rows = 6
    grid = np.zeros((rows, cols), dtype=np.int8)
    
    frames = []
    
    for line in data:
        # Create a copy of the grid to show the state *before* the instruction
        # frames.append(grid.copy())

        process_instructions([line], grid)
        
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.imshow(grid, cmap='gray_r', interpolation='nearest')
        ax.axis('off')
        
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_argb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        image = image[:, :, :3]  # Drop the alpha channel
        frames.append(image)
        plt.close(fig)

    imageio.mimsave('docs/assets/images/2016-08-animation.gif', frames, fps=10)

if __name__ == "__main__":
    with open("src/AoC_2016/d8_display_numpy/input/input.txt", mode="rt") as f:
        data = f.read().splitlines()
    generate_animation(data)
