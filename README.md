# Dazbo's Advent of Code

### See my walkthroughs [here](https://aoc.just2good.co.uk/).

## Overview

- My solutions to Advent of Code problems for multiple years, written in Python.
- I've taken two main approaches for my solutions:
  - **Python Scripts:** For some years (e.g., 2015-2022), solutions are plain Python scripts. These are accompanied by detailed walkthroughs written in Markdown.
  - **Jupyter Notebooks:** For other years (e.g., 2023 onwards), I've used Jupyter Notebooks, which combine the Python code, the solution explanation, and the walkthrough into a single file.
- All solutions are thoroughly documented.
- Some days have multiple solutions where I've experimented with different approaches or libraries.
- The walkthroughs are published on my [AoC website](https://aoc.just2good.co.uk/).

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

## Structure of this Repo

This repository is organized as follows:
- **`src/`**: This directory contains all the source code for the solutions.
  - Solutions are organized by year in `src/AoC_YYYY/` folders.
  - Inside each year's folder, you will find either:
    - Individual Python scripts (`.py`) for each day's solution.
    - Jupyter Notebooks (`.ipynb`) that contain both the code and the walkthrough.
- **`docs/`**: This directory contains the source for my [AoC walkthrough website](https://aoc.just2good.co.uk/).
  - For solutions that use Python scripts, the corresponding Markdown walkthroughs are in `docs/YYYY/`.
  - The entire folder is a Jekyll project that builds the static site.
- **Templates**: If you want to follow my structure, I've included templates:
  - `src/template_folder/`: A template for creating a new day's solution with a Python script.
  - `docs/2022/day_template.md`: A template for the Markdown walkthrough page.

```
.
├───docs/
│   ├───2015/
│   │   └───...
│   ├───2022/
│   │   └───...
│   └───python/
│       └───...
├───scripts/
│   ├───build_aoc_commons.ps1
│   ├───create_year.ps1
│   └───upload_to_pypi.py
├───src/
│   ├───AoC_2015/
│   │   └───...
│   ├───AoC_2022/
│   │   └───...
│   ├───aoc_common/
│   │   └───...
│   └───template_folder/
│       └───...
├───.gitignore
├───LICENSE
├───README.md
└───requirements.txt
```

## Helper Scripts

The `scripts/` directory contains helper scripts for managing this repository:

- **`create_year.ps1`**: A PowerShell script to scaffold the directory structure for a new Advent of Code year.
- **`build_aoc_commons.ps1`**: A PowerShell script to build the `aoc_common` package.
- **`upload_to_pypi.py`**: A Python script to upload the `aoc_common` package to PyPI.

## Documentation Website

This repository includes a companion website that contains detailed walkthroughs and explanations for many of the solutions.

- **Website URL:** [https://aoc.just2good.co.uk/](https://aoc.just2good.co.uk/)
- **Technology:** The site is a static website generated using [Jekyll](https://jekyllrb.com/).
- **Source Code:** All source files for the website (Markdown content, layouts, etc.) are located in the `docs/` directory.

### Content Structure

- For solutions written as plain Python scripts, the corresponding walkthroughs are individual Markdown files found in `docs/YYYY/`, where `YYYY` is the year of the challenge.
- For solutions implemented in Jupyter Notebooks, the code and walkthrough are combined in the `.ipynb` file itself, located in the `src/AoC_YYYY/` directory.

### Running Locally

You can build and serve the documentation website on your local machine using Docker.

1.  Navigate to the `docs/` directory.
2.  Run the command `docker compose up`.
3.  The website will be available at `http://127.0.0.1:4000`.

If you need to specify a GitHub token for Jekyll, you can create a `.env` file in the `docs/` directory containing `JEKYLL_GITHUB_TOKEN=your_token_here`.
