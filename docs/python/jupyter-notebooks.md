---
title: Jupyter Notebooks
description: How to use Jupyter Notebooks and JupyterLab for Advent of Code, running locally via uv or in the cloud with Google Colaboratory.
main_img:
  name: Jupyter Notebook
  link: /assets/images/aoc2017-jn.png
tags: 
  - name: Jupyter
    link: https://jupyter.org/
  - name: Jupyter Project Documentation
    link: https://docs.jupyter.org/en/latest/index.html
  - name: Jupyter Lab Documentation
    link: https://jupyterlab.readthedocs.io/en/stable/
  - name: Installing Jupyter
    link: https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html
  - name: Notebook Tips and Tricks
    link: https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/
  - name: uv Documentation
    link: https://docs.astral.sh/uv/
  - name: SciPy Docker Compose
    link: https://gist.github.com/derailed-dash/b1d9eb511e336ba837da234518c09842
  - name: Google Colab
    link: https://colab.research.google.com/
---
## Page Contents

- [What are Jupyter Notebooks?](#what-are-jupyter-notebooks)
- [A Few Benefits of Notebooks](#a-few-benefits-of-notebooks)
- [Ideal Scenarios for Using Notebooks](#ideal-scenarios-for-using-notebooks)
- [Jupyter Notebook vs Jupyter Lab](#jupyter-notebook-vs-jupyter-lab)
- [Options for Running Jupyter Notebooks and Jupyter Lab](#options-for-running-jupyter-notebooks-and-jupyter-lab)
  - [Local Installation with uv (Recommended)](#local-installation-with-uv-recommended)
  - [Run a Container!](#run-a-container)
  - [In the Cloud: Google Colaboratory](#in-the-cloud-google-colaboratory)
  - [Sharing with a Cloud Service](#sharing-with-a-cloud-service)
  - [Importing aoc_common: Local vs Google Colaboratory](#importing-aoc_common-local-vs-google-colaboratory)

## What are Jupyter Notebooks?

Integrated Development Environments (IDEs) have been the go-to choice for developers seeking a dedicated space to write, test, and debug their code. However, as data science and machine learning began gaining traction, there was increasing need for a more interactive and data-centric environment. Enter **Jupyter Notebooks**: a web-based application that has redefined the way we interact with code and data, the way we document our code, and the way we share it.

Unlike traditional IDEs, **Jupyter Notebooks allow for code, data, and multimedia to coexist in a shared space**. With its cell-based structure, users can write and execute code in small chunks, making it easier to test ideas and see results in real time. This attribute alone sets it apart from the linear approach of traditional coding environments, making Jupyter Notebooks a beloved tool among data scientists and analysts.

## A Few Benefits of Notebooks

- **Interactive computing:** Real-time feedback on code execution, facilitating a more iterative and exploratory approach to problem-solving. Code is organised into _cells_. Cells can be executed and re-executed. The output of those cells (such as the values assigned to variables) is available to all subsequent cells in the Notebook. This is useful, since we can run a cell, and then experiment with changes to the cells that come _after_ that cell.
- **Documentation and sharing:** You have the ability to intertwine code, text, and multimedia. You can place Markdown or HTML content alongside your code. This greatly improves your ability to document your solutions and share insights. And you can structure your Notebook using chapters.
- **Images and visualisation:** You can include images, visualisations, equations, animations, and video alongside your code.
- **Reproducibility:** Encourages reproducible research by packaging code, data, and narrative into a single document.
- **Extension ecosystem:** A vast array of extensions and libraries is available, enhancing functionality and integration with other tools.
- **Run shell commands:** You can run shell commands from within the Notebook! This is useful for running filesystem commands, or — for example — installing extra packages on the fly with `!pip install`.
- **Easy to share:** Since all the code, documentation, and output are in a single file, sharing (and collaborating) is wonderfully simple.
- **Portable:** Jupyter Notebooks are inherently portable, and can be run on a wide variety of platforms.

Here's an example of a Notebook, with chapter structure, and with an introduction written in Markdown:

![Notebook Example](/assets/images/notebook-md.png)

And here's an example where we're dynamically generating an image with code, and displaying it after the cell:

![Markdown, Cells, and Graphical Output](/assets/images/notebook-generating-image.png)

## Ideal Scenarios for Using Notebooks

- **Data Analysis and Visualisation:** Whether it's cleaning data, performing statistical analysis, or creating visualisations, Jupyter Notebooks provide an interactive environment that fosters insight discovery.
- **Machine Learning and Model Development:** Building and testing models becomes streamlined with the ability to execute code incrementally and visualise results on the fly.
- **Educational Purposes:** An excellent tool for teaching coding and problem-solving concepts, given its interactive nature and the ability to annotate code with rich text.
- **Collaborative Research:** Facilitates collaborative efforts by allowing multiple users to interact with the notebook and share their findings seamlessly.

## Jupyter Notebook vs Jupyter Lab

Whilst classic Jupyter Notebooks are great, they lack some of the features that developers have come to expect from an IDE like VS Code. This gap in capability led to the _next generation of the Jupyter environment_, called **JupyterLab**. It builds on the Jupyter notebook environment, adding a bunch of extra capabilities, like:

- The ability to run **multiple tabs** within the Lab environment.
- Integrated file explorer.
- The ability to run **terminals** alongside your code.
- The ability to **rearrange and snap** windows in your view.
- The ability to show **page navigation** in the same view.
- The ability to perform **visual debugging**, in the same way you would use a debugger within your favourite IDE.

For example, here's one of my AoC Jupyter Notebooks:

![Jupyter Notebook](/assets/images/aoc2017-jupyter-notebook.png)

Here's the same notebook, opened in the JupyterLab environment:

![Jupyter Lab](/assets/images/aoc2017-jupyter-lab.png)

## Options for Running Jupyter Notebooks and Jupyter Lab

There are a few ways to run a Jupyter Notebook. I'll go through the most practical options here.

### Local Installation with uv (Recommended)

In this repository, you don't need manual `pip install` commands or heavyweight multi-gigabyte Anaconda distributions. Everything required to run JupyterLab is pre-configured in `pyproject.toml`:

```bash
# Hydrate the virtual environment with dev and Jupyter dependencies:
make install              # or: uv sync --dev --extra jupyter --extra legacy

# Launch JupyterLab inside the managed .venv/:
uv run jupyter lab
```

If you prefer working inside **VS Code**, you can open any `.ipynb` notebook file directly. VS Code's Jupyter extension will detect `.venv/` automatically and allow you to select it as the active kernel with zero extra configuration.

### Run a Container!

**This is another great local approach.**

You can download a pre-configured container image, such as the [Jupyter Notebook Data Science Stack](https://hub.docker.com/r/jupyter/datascience-notebook){:target="_blank"}.

Advantages:

- You can pull an image that contains exactly what you need.
- The images are portable and run consistently on any machine.
- The container starts up really quickly.
- The container is _isolated_. There is no risk of conflicting with other Python-related software on your host machine.

There are a bunch of so-called _Jupyter stacks_ available as Docker images, and they are all documented [here](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html){:target="_blank"}.

For example:

| Stack | Includes (for example) | Approx Size |
| :--- | :--- | :--- |
| `jupyter/base-notebook` | Conda, mamba, notebook, jupyterlab | 1.0GB |
| `jupyter/minimal-notebook` | As with `base-notebook`, plus CLI tools (like `curl`, `git`, `nano`) | 1.6GB |
| `jupyter/scipy-notebook` | As with `minimal-notebook`, plus data science packages (like `matplotlib`, `pandas`, `scipy`, `seaborn`) | 4.1GB |
| `jupyter/datascience-notebook` | Combines everything from `scipy-notebook`, `r-notebook`, and `julia-notebook` | 4.2GB |

My favourite way to run a Jupyter container is using a `docker compose` file, such as my [docker-compose-scipy-lab.yml](https://gist.github.com/derailed-dash/b1d9eb511e336ba837da234518c09842){:target="_blank"}:

```yaml
version: '3.9'
services:
  jupyter:
    environment:
      JUPYTER_ENABLE_LAB: yes
      CHOWN_HOME: yes   # Env vars to handle permission issues on WSL
      CHOWN_HOME_OPTS: '-R'
      JUPYTER_ALLOW_INSECURE_WRITES: true
    image: jupyter/scipy-notebook
    container_name: scipy-lab
    volumes:
      - .:/home/jovyan
    ports:
      - 8888:8888
```

To run this file:

```bash
docker compose -f docker-compose-scipy-lab.yml up
```

And it looks like this:

![Running Docker Compose](/assets/images/docker-compose-as-gif.gif)

### In the Cloud: Google Colaboratory

You don't even need to run Jupyter Notebooks locally! You can make use of a cloud service like **[Google Colaboratory](https://colab.research.google.com/){:target="_blank"}**:

![Google Colab](/assets/images/collab.png)

- Advantages:
  - Free cloud-based Jupyter environment.
  - Seamless integration with the Google ecosystem (all you need is a Google account).
  - Integrates with Google Drive and GitHub — load notebooks directly without having to upload files manually.
  - Really easy to share your notebooks with others.
- Disadvantages:
  - Defaults to the classic notebook interface rather than full JupyterLab.
  - Ephemeral runtime — installed packages and local files reset after your session ends.

### Sharing with a Cloud Service

You can edit your notebooks locally, and then use a cloud-based service like Google Colab for sharing your work with others in an interactive, runnable format:

- To provide a Colab link that opens your notebook directly from Google Drive: \
  `https://colab.research.google.com/drive/some_unique_id`
- To provide a Colab link that opens your notebook directly from GitHub: \
  `https://colab.research.google.com/github/<username>/<repo>/blob/<branch>/path/to/notebook.ipynb` \
  For example: [Open Advent of Code 2017 Notebook in Google Colab](https://colab.research.google.com/github/derailed-dash/Advent-of-Code/blob/master/src/AoC_2017/Dazbo's_Advent_of_Code_2017.ipynb){:target="_blank"}

### Importing aoc_common: Local vs Google Colaboratory

Our shared helper module (`aoc_common`) provides common utilities (`Point`, `Grid`, `to_base_n`, etc.) used across many puzzle solutions. Depending on where you run your notebook, the import behaviour differs:

#### 1. Local Notebooks (JupyterLab or VS Code)

When running locally with `make install` (`uv sync --dev --extra jupyter`), the repository packages `src/aoc_common` **editably** into `.venv/`. You can import it directly without any path manipulation:

```python
import aoc_common.aoc_commons as ac

# Use spatial helpers, grids, and utilities directly:
p1 = ac.Point(0, 0)
p2 = ac.Point(3, 4)
print(p1.manhattan_distance_from(p2))  # 7
```

#### 2. Google Colaboratory

Google Colab runs on an isolated virtual machine in the cloud that does not have your local `.venv/` or cloned repository folders. To use `aoc_common` inside a Colab notebook, add an installation cell at the top of your notebook:

```python
# Install aoc_common directly from the GitHub repository into Colab:
!pip install -q "git+https://github.com/derailed-dash/Advent-of-Code.git"

import aoc_common.aoc_commons as ac
```

This installs the library directly into Colab's Python environment so your notebook runs smoothly from start to finish.
