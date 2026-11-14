---
title: Packages and Environments
description: Modern Python dependency management, virtual environments, and package workflows using uv, pyproject.toml, and uv.lock.
tags: 
  - name: Python Package Index
    link: https://pypi.org/
  - name: uv Documentation
    link: https://docs.astral.sh/uv/
  - name: pyproject.toml Guide
    link: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
  - name: Python Packaging Authority
    link: https://www.pypa.io/en/latest/
  - name: Pip documentation
    link: https://pip.pypa.io/en/stable/
  - name: Python Environments in VS Code
    link: https://code.visualstudio.com/docs/python/environments
---
## The Need for Packages

Frequently we will need to import a package that is not part of the core Python standard library. For example, my Advent of Code solutions often make use of installable packages like:

- _Rich_ — for terminal formatting, styled progress tables, and logging (replacing `colorama`, which is now retired into `legacy` solely for historical 2015–2024 solutions)
- _parsimonious_ — for grammar parsing and token extraction in complex AoC puzzle inputs (see our [Parsimonious Guide](/python/parsimonious))
- _matplotlib_ — for plotting charts and creating visualisations
- _numpy_ — for data science, matrices, and multidimensional array manipulations
- _pandas_ — for working with tabular data and series
- _scipy_ — for applying mathematical, geometric, and graph algorithms
- _Pillow_ and _imageio_ — for creating and manipulating images and animations

## Package Managers

To install packages like these, we need to use a **Package Manager**. A package manager provides the ability to install and uninstall packages. In addition, a package manager resolves dependencies. This means that if you want to install package `x`, but package `x` depends on package `y`, the package manager will automatically install both `x` and `y` in the right order.

## uv and pyproject.toml (Recommended)

This repository manages dependencies and virtual environments exclusively using **[`uv`](https://docs.astral.sh/uv/){:target="_blank"}** paired with `pyproject.toml` and `uv.lock`:

```bash
# Install all project dependencies, dev tooling, Jupyter, and legacy extras into .venv/
uv sync --dev --extra jupyter --extra legacy   # or simply: make install

# Add a new runtime dependency to pyproject.toml
uv add some-package

# Run any script or test suite inside the managed environment
uv run python src/AoC_2025/d01/d01.py
uv run pytest src/tests
uv run aoc list
```

Compared to juggling manual virtual environments and `pip install`, `uv` offers dramatic advantages:

- **Speed:** Resolves and installs packages orders of magnitude faster than `pip`.
- **Single Source of Truth:** `pyproject.toml` specifies declared dependencies and extras (`jupyter` for notebooks, `legacy` for `dazbo-commons` and `colorama`).
- **Deterministic Locks:** `uv.lock` pins exact transitive package versions, hashes, and platforms, ensuring completely reproducible environments across all machines.
- **Zero-Activation Execution:** Prefixes like `uv run <command>` execute directly within `.venv/` without having to run shell activation scripts.

Because `uv` and `pyproject.toml` manage our dependencies deterministically, we do not use or maintain a `requirements.txt` file in this repository.

## Pip (Standard Reference)

Python comes pre-installed with its own package manager, called **pip**. To use pip, simply type `pip <command>` in your terminal:

```bash
# install matplotlib
pip install matplotlib

# uninstall matplotlib
pip uninstall matplotlib

# upgrade matplotlib
pip install --upgrade matplotlib

# upgrade pip itself
pip install --upgrade pip
```

Although you can just use `pip <command>` as shown above, it's generally recommended to instead use this syntax:

```bash
python -m pip <command>
```

This syntax ensures that pip installs the package into the currently active Python runtime or virtual environment.

## Virtual Environments

### What is a Virtual Environment?

Virtual environments are isolated Python contexts in which we can install Python packages. In short, virtual environments isolate the dependencies of individual Python projects.

Say what?

Well, you might be working on project `a` that requires package `x` version 1, while project `b` needs package `x` version 2. If you install packages globally on your operating system, the two projects will conflict with one another.

The answer? Virtual environments! You simply create a dedicated virtual environment for each project.

Here are some reasons why virtual environments are essential:

- Multiple projects may have conflicting dependencies.
- Projects may conflict with operating system dependencies. Particularly on Linux systems, installing packages globally outside of a virtual environment can disrupt system packages.
- There may be a need to test code against different Python and library versions.
- There may be a need to distribute your project along with specific, pinned environment dependencies.

### Creating a Virtual Environment (Manual venv)

If you are working outside this repository without `uv`, you can create a virtual environment using Python's built-in `venv` module:

1. Create your project folder.
2. Within your project folder, create a virtual environment called `.venv`:
   ```bash
   python -m venv .venv
   ```
3. Add `.venv/` to your project's `.gitignore`, since virtual environments must never be committed to version control.

In case it's useful, here is the `.gitignore` pattern I use on Python projects:

```text
# Env & local virtual environments
.venv/
.env
.*-env/

# Build / distribution / packaging
build/
dist/
*.egg-info/

# Byte-compiled / caches
__pycache__/
.ruff_cache/
.pytest_cache/
.mypy_cache/

# Jupyter
.ipynb_checkpoints/

# Secrets & local outputs
*.key
output/
```

### Using Your Virtual Environment

When using `uv`, you don't even have to activate the virtual environment manually — prefix commands with `uv run` (e.g. `uv run python script.py`). If you created a manual `venv` instead, activate it before running commands:

```bash
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\Activate.ps1       # Windows PowerShell
```

Fortunately, if you're using VS Code, then VS Code will automatically detect `.venv/` the next time you open your project folder and select it as the active interpreter.

### Tips for Working with Virtual Environments

Here are my general thoughts on how to work with virtual environments:

- They are **not portable**. They are **machine-specific** and should be recreated on any given machine.
- Never commit `.venv/` to version control — always exclude it in `.gitignore`.
- Don't keep your virtual environment folder inside a cloud-synchronised folder (such as Google Drive or OneDrive).
- Track your dependencies in `pyproject.toml` and `uv.lock` under version control so that any machine can recreate the exact environment with `uv sync`.
