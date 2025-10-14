# Dazbo's Advent of Code

### See my walkthroughs [here](https://aoc.just2good.co.uk/).

## Overview

- My solutions to Advent of Code problems for multiple years, written in Python.
- All solutions are thoroughly documented.
- Some days have multiple solutions where I've experimented with different approaches or libraries.

[![Dazbo's AoC Walkthroughs](/docs/assets/images/AoC_site_screenshot.jpg)](https://aoc.just2good.co.uk/)

## Purpose of this Repo

I've been using [Advent of Code](https://adventofcode.com/) as a way to improve my **Python** skills. Here I document my solutions across the various AoC years. My hope is that this guide will help others to:

- Become more proficient with Python.
- Solve AoC problems they might be stuck with.
- Learn some new libraries and inventive ways of doing things.

## Use of my Code

This software is shared as open source. However, if you use it in your own solutions and/or incorporate into your own repos, please consider giving acknowledgement to me, and linking back to this repo and [walkthrough site](https://aoc.just2good.co.uk/). That would be really kind!

## What is Advent of Code?

An awesome [coding challenge](https://adventofcode.com/2021/about) created by Eric Wastl, released every December. A new problem is presented each day through the month. Typically the best way to solve any given problem is by writing a program. The program can be written in _any language and with any tools you like_. You don't need to be an expert coder to do AoC; in fact, AoC is a great way to learn a programming language.

Some problems are quite trivial and can be solved quickly; 
others can be a total PITA. Typically, the problems get harder as the month progresses.

You don't have to wait until December to try your hand at AoC though. 
All the previous events are available, and can be completed at _any_ time.

Each day is split into a Part 1 and a Part 2.  A star is awarded for each completed challenge.

**If you get 50 stars, you save Christmas!**

## Prerequisites & Setup

To run the solutions in this repository, you'll need the following:

- **Python >=3.13**
- **`uv`**: My preferred tool for managing Python packages and virtual environments.
- **Jupyter**: For running the notebook-based solutions (`.ipynb` files).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/derailed-dash/Advent-of-Code.git
    cd Advent-of-Code
    ```

2.  **Create a virtual environment and install dependencies:**
    I recommend using `uv` to create a virtual environment and install the required packages from `pyproject.toml`.

    ```bash
    # Install dependencies in a venv, including Jupyter
    make install # runs uv sync --dev --extra jupyter
    ```

    Alternatively, you can use `conda` as described in `src/readme.md`.

3.  **Run the solutions:**
    - For Python scripts, you can run them directly from your terminal.
    - For Jupyter Notebooks, run them directly in your IDE (e.g. VS Code), start a Jupyter Lab, 
      or run in a cloud service like [Google Colab](https://colab.research.google.com/).
      ```bash
      # Running a Jupyter lab locally
      jupyter lab
      ```
      Then navigate to the notebook file in the `src/AoC_YYYY` directory.

## Structure and Solution Approaches

This repository is organized by year and solution type. I've taken two main approaches for my solutions:

### 1. Python Scripts with Separate Walkthroughs

For some years (e.g., 2015-2022), the solutions are plain Python scripts. These are accompanied by detailed walkthroughs written in Markdown, which are published on the [website](https://aoc.just2good.co.uk/).

- **Code**: The Python solution files (`.py`) are located in the `src/AoC_YYYY/` directories.
- **Walkthroughs**: The corresponding Markdown files (`.md`) are in the `docs/YYYY/` directories. These are used by Jekyll to build the static website.

### 2. Jupyter Notebooks

For other years (e.g., 2023 onwards), I've used Jupyter Notebooks. This approach combines the Python code, the solution explanation, and the walkthrough into a single, self-contained file (`.ipynb`). These can be viewed directly on GitHub or run locally using Jupyter.

### Directory Structure

Here is a simplified overview of the repository's structure, showing examples of both solution types:

```
.
├───docs/                 # Source for the Jekyll-based walkthrough website
│   ├───2022/             # Walkthroughs for 2022 (Python script approach)
│   │   └───1.md          # Walkthrough Day 1
│   python/               # General Python guides
│   │   ├───assertion.md  # Walkthrough for a specific topic
|   |   └───...
|   ├───_config.yml        # Jekyll configuration for building docs
|   ├───_config.docker.yml # Jekyll configuration for Docker
|   ├───docker-compose.yml # Docker configuration
|   ├───index.md           # Index page for the website
│   └───...
├───src/                  # All Python source code and notebooks
│   ├───AoC_2022/         # Solutions for 2022
│   |   ├───d01/          # Day 1
|   |   |   ├───input/    # Input data
|   |   |   └───d01.py    # Solution for 2022, Day 1
|   |   ├───d02/          # Day 2
|   |   └───...
│   ├───AoC_2023/
│   │   ├───Dazbo's_Advent_of_Code_2023.ipynb  # Walkthroughs for 2023 (Jupyter Notebook approach)
│   |   ├───d01/         # Day 1
|   |   |   └───input/   # Input data
│   |   ├───d02/         # Day 2
|   |   |   └───input/   # Input data
|   |   └───...
│   ├───aoc_common/       # A shared library of common functions used across solutions
│   ├───template_folder/  # Template content
│   └───tests/            # Unit tests
├───scripts/              # Helper scripts for repository management
├───.env                  # Env vars, e.g. AoC session cookie
├───.gitignore
├───LICENSE
├───README.md             # This file
└───pyproject.toml        # Project metadata and dependencies for uv/pip
```

### Helper Libraries

This repository leverages two primary utility libraries to streamline solution development:

-   **`aoc_common` (local to this repository)**: Located in `src/aoc_common/`, this library provides Advent of Code-specific utilities such as:
    -   `Point`, `Vectors`, `VectorDicts`, and `Grid` classes for handling 2D grid-based problems.
    -   `binary_search`, `merge_intervals`, `get_factors`, and `to_base_n` for common algorithmic tasks.
    -   `timer` context manager for performance measurement.
    -   `setup_file_logging` for logging output to files.

-   **`dazbo-commons` (external PyPI package)**: This is a more generic utility library that provides foundational functionalities used across my Python projects. It is installed as a dependency and offers:
    -   **Coloured Logging**: Standardized console logging with color-coded output for different log levels.

By separating these concerns, `aoc_common` remains focused on AoC-specific helpers, while `dazbo-commons` handles more general-purpose tasks, promoting reusability and cleaner code.

Note that the `aoc_common` package is imported into standalone scripts, but it's code is replicated in the notebooks. 
This is so that the notebooks can be entirely portable.

### Assertions and Testing

Each solution typically includes assertions to verify correctness, especially against sample inputs provided by Advent of Code. The `aoc_common.validate` function is used for this purpose:

```python
ac.validate(test_result, expected_answer)
```

This function raises an `AssertionError` if the `test_result` does not match the `expected_answer`, providing immediate feedback during development and ensuring the solution works for known cases before attempting the full input.

## Helper Scripts

The `scripts/` directory contains helper scripts for managing this repository:

- **`create_year.ps1`**: A PowerShell script to scaffold the directory structure for a new Advent of Code year.

## Documentation Website

This repository includes a companion website that contains detailed walkthroughs and explanations for many of the solutions.

- **Website URL:** [https://aoc.just2good.co.uk/](https://aoc.just2good.co.uk/)
- **Technology:** The site is a static website generated using [Jekyll](https://jekyllrb.com/).
- **Source Code:** All source files for the website (Markdown content, layouts, etc.) are located in the `docs/` directory.

### Content Structure

- For solutions written as plain Python scripts, the corresponding walkthroughs are individual Markdown files found in `docs/YYYY/`, where `YYYY` is the year of the challenge.
- For solutions implemented in Jupyter Notebooks, the code and walkthrough are combined in the `.ipynb` file itself, located in the `src/AoC_YYYY/` directory.

### Working with the Documentation Locally

You can build and serve the documentation website on your local machine using Docker.

1.  Navigate to the `docs/` directory.
2.  Run the command `docker compose up`.
3.  The website will be available at `http://127.0.0.1:4000`.

If you need to specify a GitHub token for Jekyll, you can create a `.env` file in the `docs/` directory containing `JEKYLL_GITHUB_TOKEN=your_token_here`.
