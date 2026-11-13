---
title: Packages and Environments
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

Frequently we will need to import a package that is not part of the core Python installation. For example, my Advent of Code solutions often make use of installable packages like:

- _imageio_ - for reading and writing image files
- _matplotlib_ - for plotting charts and graphical data; for creating visualisations
- _numpy_ - for data science and manipulating multidimensional array data
- _pandas_ - for working with tabular data
- _scipy_ - for applying mathematical algorithms
- _Pillow_ - for manipulating images
- _parsimonious_ - for parsing grammars, extracting tokens

## Package Managers

To install packages like these, we need to use a **Package Manager**. A package manager provides the ability to install and uninstall packages.  But in addition, a package manager resolves dependencies.  This means that if you want to install package `x`, but package `x` depends on package `y`, then the package manager will automatically install both `x` and `y`, in the right order.

## uv and `pyproject.toml` (Recommended)

This repository manages dependencies and virtual environments using **[`uv`](https://docs.astral.sh/uv/){:target="_blank"}** with `pyproject.toml` and `uv.lock`:

```bash
# Install all project, dev tooling, and Jupyter dependencies into .venv/
uv sync --dev --extra jupyter   # or: make install

# Add a new runtime dependency to pyproject.toml
uv add some-package

# Run any script or test suite inside the managed environment
uv run python src/AoC_2025/d01/d01.py
uv run pytest src/tests
```

Compared to juggling `venv`, `pip install`, and `pip freeze > requirements.txt`, `uv` resolves dependencies orders of magnitude faster, pins exact transitive versions in `uv.lock`, and handles virtual environment creation automatically.

## Pip (Standard Reference)

Python comes pre-installed with its own package manager, called **pip**. To use pip, simply type `pip <command>`, e.g.

```python
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

```python
py -m pip <command>
```

This syntax ensures that pip installs the package to the currently active Python runtime or environment.

## Virtual Environments

### What is a Virtual Environment?

Virtual environments are isolated Python contexts in which we can install Python packages. In short, virtual environments isolate dependencies of Python projects. 

Say what?

Well, you might be working on project `a` that requires packages `x`, and package `x` depends on package `y`. And then you might start working on project `b`, which needs package `z`. But package `z` won't work if you have package `y` installed. So your two projects have incompatible package requirements.

The answer? Virtual environments!  You simply create a dedicated virtual environment for each project.

Here are some reasons why virtual environments are a good thing:

- Multiple projects may have conflicting dependencies.
- Projects may conflict with operating system dependencies. Particularly on Linux systems, installing packages outside of a virtual environment could break the OS, given that the OS may have specific version dependencies.
- There may be a need to test code against different Python and library versions.
- There may be a need to distribute your project, along with specific environment dependencies.  E.g. for standalone applications.

### Creating a Virtual Environment (Manual `venv`)

1. Create your project folder, as usual.
1. Within your project folder, create a virtual environment. You do this using the `venv` command (or let `uv sync` create `.venv/` automatically).  For example, to create a virtual environment called `.venv`: \
`python -m venv .venv`
1. Add `.venv/` to your project's `.gitignore`, since we don't want it included in version control.

In case it's useful, here's the `.gitignore` pattern I tend to use on modern Python projects:

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

When using `uv`, you don't even have to activate the virtual environment manually — prefix commands with `uv run` (e.g. `uv run python script.py`). If you created a manual `venv` instead, activate it so `pip install` installs into it rather than globally.

Fortunately, if you're using VS Code, then VS Code will automatically detect `.venv/` the next time you open your project folder.

### Tips for Working with Virtual Environments

Here are my general thoughts on how to work with virtual environments:

- They are **not portable**. They are **machine specific** and should be recreated on any given machine.
- So don't put `.venv/` under version control — exclude it in `.gitignore`.
- Don't keep your virtual environment folder in a synchronised folder (such as Google Drive or OneDrive).
- Track your dependencies in `pyproject.toml` and `uv.lock` (or `requirements.txt` for simple pip workflows) under version control so another machine can recreate the exact environment with `uv sync`.
