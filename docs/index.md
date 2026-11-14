---
layout: default
title: Dazbo's Advent of Code Walkthroughs
description: Step-by-step Python walkthroughs, reusable algorithms, and practical guides across a decade of Advent of Code puzzles.
---

<section class="home-hero" aria-label="Introduction">
  <div class="home-hero__content">
    <p class="home-hero__kicker">★ Python Walkthroughs &amp; Tooling</p>
    <h1>Dazbo's Advent of Code</h1>
    <p class="home-hero__lead">
      Using <a href="https://adventofcode.com/" target="_blank" rel="noopener">Advent of Code</a> to sharpen idiomatic
      <a href="https://www.python.org/" target="_blank" rel="noopener">Python</a> — testing algorithms, exploring libraries, and sharing practical, step-by-step walkthroughs.
    </p>
    <div class="home-hero__actions">
      <a class="primary-cta-btn" href="{{ '/2025/' | relative_url }}">★ Explore 2025</a>
      <a class="secondary-cta-btn" href="{{ '/python/' | relative_url }}">Python Journey</a>
      <a class="secondary-cta-btn" href="{{ site.github.repository_url }}" target="_blank" rel="noopener">GitHub &amp; CLI ↗</a>
    </div>
  </div>
  <div class="home-hero__media">
    <img class="home-hero__art no-mat" src="{{ '/assets/images/aoc-hero-banner.png' | relative_url }}" alt="Midnight AoC glowing circuit constellation tree crowned with a gold Advent star" width="1280" height="714">
  </div>
</section>

## Browse Solutions by Year

From `2015`–`2024`, Advent of Code ran **25 days** (`50 ★`); from `2025` onwards, it runs a focused **12 days** (`24 ★`). Choose standalone Python scripts + walkthroughs or all-in-one Google Colab notebooks below.

<div class="year-grid">
  <a class="year-card" href="{{ '/2026/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2026</span>
      <span class="year-card__stars year-card__stars--muted">Upcoming</span>
    </div>
    <span class="year-card__format">12-Day Event · Template v3</span>
    <p class="year-card__note">Ready for December 2026 with Python 3.13+, <code>uv run aoc</code>, and streamlined daily walkthroughs.</p>
  </a>

  <a class="year-card" href="{{ '/2025/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2025</span>
      <span class="year-card__stars">★ 24 / 24</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Inaugural 12-day event solved end-to-end with <code>aoc_common</code>, intervals, geometry, and graph search.</p>
  </a>

  <a class="year-card" href="{{ '/2024/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2024</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format year-card__format--notebook">Jupyter + Colab</span>
    <p class="year-card__note">Full 25-day narrative and executable code combined into a single cloud-ready Jupyter Notebook.</p>
  </a>

  <a class="year-card" href="{{ '/2023/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2023</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format year-card__format--notebook">Jupyter + Colab</span>
    <p class="year-card__note">Complete 25-day notebook tackling Shoelace areas, Z3/SymPy linear algebra, and min-cut graphs.</p>
  </a>

  <a class="year-card" href="{{ '/2022/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2022</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Deep-dive walkthroughs covering BFS pathfinding, cube wrapping, 3D obsidian voxels, and state pruning.</p>
  </a>

  <a class="year-card" href="{{ '/2021/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2021</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Complete 25-day series rich in Matplotlib visualisations, Dijkstra shortest paths, and recursive packet parsing.</p>
  </a>

  <a class="year-card" href="{{ '/2020/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2020</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format">Scripts + Code Index</span>
    <p class="year-card__note">All 25 working Python solutions indexed by algorithm, PEG parsing grammar, and binary bitmasks.</p>
  </a>

  <a class="year-card" href="{{ '/2018/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2018</span>
      <span class="year-card__stars year-card__stars--muted">6 / 25 Days</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Selected walkthroughs featuring cyclic linked lists, coordinate sorting, and regex parsing.</p>
  </a>

  <a class="year-card" href="{{ '/2017/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2017</span>
      <span class="year-card__stars year-card__stars--muted">12 / 25 Days</span>
    </div>
    <span class="year-card__format year-card__format--notebook">Jupyter + Colab</span>
    <p class="year-card__note">First notebook experiment pairing puzzle explanations, inline outputs, and code in one place.</p>
  </a>

  <a class="year-card" href="{{ '/2016/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2016</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Full 25-day archive covering Assembunny VMs, MD5 hash mining, and multi-floor BFS mazes.</p>
  </a>

  <a class="year-card" href="{{ '/2015/' | relative_url }}">
    <div class="year-card__head">
      <span class="year-card__year">2015</span>
      <span class="year-card__stars">★ 50 / 50</span>
    </div>
    <span class="year-card__format">Scripts + Walkthroughs</span>
    <p class="year-card__note">Where Advent of Code began: all 25 inaugural puzzles, Conway grids, logic gates, and TSP loops.</p>
  </a>
</div>

## The Python Journey

Whenever a puzzle relies on a technique worth keeping in your toolkit — Dijkstra's algorithm, `itertools` combinatorics, regex extraction, or 2D grid coordinates — my day walkthroughs link straight into a standalone chapter of **[The Python Journey](/python/)**. You can work through them as a curriculum or jump directly to the topic you need:

<div class="feature-grid">
  <a class="feature-card" href="{{ '/python/getting-started' | relative_url }}">
    <span class="feature-card__title">Getting Started with Python</span>
    <p class="feature-card__desc">Set up Python, Visual Studio Code, virtual environments, and clean development habits from scratch.</p>
  </a>

  <a class="feature-card" href="{{ '/python/reusable_code' | relative_url }}">
    <span class="feature-card__title">Reusable Code (<code>aoc_common</code>)</span>
    <p class="feature-card__desc">Shared <code>Point</code>, <code>Grid</code>, and <code>Vectors</code> abstractions, binary search, interval merging, and puzzle validation.</p>
  </a>

  <a class="feature-card" href="{{ '/python/shortest_paths' | relative_url }}">
    <span class="feature-card__title">Shortest Paths — BFS, Dijkstra &amp; A*</span>
    <p class="feature-card__desc">Navigate unweighted mazes, weighted cost maps, and heuristic search spaces without reinventing the queue.</p>
  </a>

  <a class="feature-card" href="{{ '/python/graph' | relative_url }}">
    <span class="feature-card__title">Graphs &amp; NetworkX</span>
    <p class="feature-card__desc">Model dependency trees, connected components, cycles, and visual network diagrams cleanly.</p>
  </a>

  <a class="feature-card" href="{{ '/python/perms_combos' | relative_url }}">
    <span class="feature-card__title">Permutations, Sets &amp; Comprehensions</span>
    <p class="feature-card__desc">Expressive <code>itertools</code> pipelines, set algebra, and generator expressions built for puzzle speed.</p>
  </a>

  <a class="feature-card" href="{{ '/python/sympy' | relative_url }}">
    <span class="feature-card__title">Symbolic Maths (SymPy) &amp; Plots</span>
    <p class="feature-card__desc">Solve linear equations and trajectory intersections algebraically, and debug spatial grids with Matplotlib.</p>
  </a>

  <a class="feature-card" href="{{ '/python/jupyter-notebooks' | relative_url }}">
    <span class="feature-card__title">Jupyter Notebooks &amp; Colab</span>
    <p class="feature-card__desc">Combine executable Python cells, rich telemetry, and narrative notes interactively in the browser.</p>
  </a>

  <a class="feature-card" href="{{ '/python/encrypting' | relative_url }}">
    <span class="feature-card__title">Encrypting Inputs (<code>git-crypt</code>)</span>
    <p class="feature-card__desc">Respect AoC's input-sharing rules in a public repository using transparent <code>git-crypt</code> encryption.</p>
  </a>
</div>

Browse all **39 reference guides** on the **[Python Journey index](/python/)**.

## What is Advent of Code?

Created by Eric Wastl every December since 2015, **[Advent of Code](https://adventofcode.com/about){:target="_blank"}** releases a fresh two-part programming puzzle each day. Part 1 introduces the scenario cleanly; Part 2 usually turns up the scale — forcing you to replace brute-force nested loops with sets, caching, modular arithmetic, or graph search. You can write solutions in any language, run them in any environment, and revisit every past event at any time of year.

If you'd like to run my solutions locally against their built-in sample inputs right away (without needing an AoC cookie or decryption key), clone [derailed-dash/Advent-of-Code]({{ site.github.repository_url }}){:target="_blank"}, install the environment with `uv`, and use the bundled `aoc` CLI:

```bash
git clone https://github.com/derailed-dash/Advent-of-Code.git
cd Advent-of-Code
make install           # hydrates Python 3.13+ virtualenv via uv sync
uv run aoc list        # inspect solved years, progress, and script/notebook formats
uv run aoc run 2025 1 -s
```

Every walkthrough page here maps directly back to the runnable files under [`src/`]({{ site.github.repository_url }}/tree/master/src/){:target="_blank"}.

## More From Dazbo

Away from December puzzles, I write about Python tooling, AI engineering, cloud architecture, and pragmatism in delivery across my personal site and developer blogs:

<div class="social-strip">
  <a class="secondary-cta-btn" href="https://darrenlester.net" target="_blank" rel="noopener">darrenlester.net ↗</a>
  <a class="secondary-cta-btn" href="https://dev.to/dazbo" target="_blank" rel="noopener">Dev.to (dazbo) ↗</a>
  <a class="secondary-cta-btn" href="https://medium.com/@dazbo" target="_blank" rel="noopener">Medium (@dazbo) ↗</a>
  <a class="secondary-cta-btn" href="https://github.com/derailed-dash" target="_blank" rel="noopener">GitHub Profile ↗</a>
  <a class="aoc-problem-pill" href="https://github.com/derailed-dash/Advent-of-Code" target="_blank" rel="noopener">★ Star this Repo ↗</a>
</div>

If you'd like to dive straight into some of my longer-form Medium writing:

<details class="article-accordion" open>
  <summary class="article-accordion__summary">
    <span>Coding, Python &amp; Generative AI</span>
    <span class="article-accordion__count">8 articles</span>
  </summary>
  <ul>
    <li><a href="https://medium.com/python-in-plain-english/advent-of-code-the-best-way-to-learn-to-code-d86c6478d484" target="_blank" rel="noopener">Advent of Code: the Best Way to Learn to Code!</a></li>
    <li><a href="https://python.plainenglish.io/solving-mathematical-problems-in-python-with-sympy-5f138c0deaef" target="_blank" rel="noopener">Solving Mathematical Problems in Python with SymPy</a></li>
    <li><a href="https://python.plainenglish.io/finding-the-coefficients-of-a-quadratic-with-sympy-777cd9479ea1" target="_blank" rel="noopener">Finding the Coefficients of a Quadratic with SymPy</a></li>
    <li><a href="https://medium.com/python-in-plain-english/noobs-guide-to-creating-a-pip-installable-distributable-python-package-ed52e03cd4e8" target="_blank" rel="noopener">Noob's Guide to Creating a Pip-Installable Distributable Python Package</a></li>
    <li><a href="https://medium.com/python-in-plain-english/five-ways-to-run-jupyter-labs-and-notebooks-23209f71e5c0" target="_blank" rel="noopener">Six Ways to Run Jupyter Labs and Notebooks</a></li>
    <li><a href="https://medium.com/python-in-plain-english/youtube-video-downloader-with-generative-ai-and-python-run-anywhere-transcribe-and-translate-dec2e593dd58" target="_blank" rel="noopener">YouTube Video Downloader with Generative AI and Python: Run Anywhere, Transcribe and Translate</a></li>
    <li><a href="https://python.plainenglish.io/downloading-youtube-videos-extracting-audio-and-generating-transcripts-with-python-and-jupyter-c3068f82bbe0" target="_blank" rel="noopener">Downloading YouTube Videos, Extracting Audio, and Generating Transcripts with Python and Jupyter Notebooks</a></li>
    <li><a href="https://medium.com/google-cloud/building-a-serverless-image-text-extractor-and-translator-using-google-cloud-pre-trained-ai-adfdccdb18d9" target="_blank" rel="noopener">Building a Serverless Image Text Extractor and Translator Using Google Cloud Pre-Trained AI</a></li>
  </ul>
</details>

<details class="article-accordion">
  <summary class="article-accordion__summary">
    <span>Google Cloud, Terraform &amp; Enterprise Architecture</span>
    <span class="article-accordion__count">12 articles</span>
  </summary>
  <ul>
    <li><a href="https://medium.com/@dazbo/architecture-documentation-where-to-draw-the-line-df73fb5ca85c" target="_blank" rel="noopener">Architecture Documentation: Where to Draw the Line</a></li>
    <li><a href="https://medium.com/@dazbo/compelling-pitches-and-arguments-for-any-scenario-top-down-thinking-108c9edda6ec" target="_blank" rel="noopener">Compelling Pitches and Arguments for any Scenario: Top Down Thinking (TDT)</a></li>
    <li><a href="https://medium.com/google-cloud/how-to-accelerate-cloud-migrations-at-scale-ecee08a09089" target="_blank" rel="noopener">How to Accelerate Cloud Migrations at Scale</a></li>
    <li><a href="https://medium.com/google-cloud/tips-for-passing-the-google-professional-developer-pcd-exam-c2b6d2253d17" target="_blank" rel="noopener">Tips for Passing the Google Professional Developer (PCD) Exam</a></li>
    <li><a href="https://medium.com/google-cloud/create-a-ci-cd-pipeline-using-github-actions-and-google-cloud-9be20ff50e97" target="_blank" rel="noopener">Create a CI/CD Pipeline using GitHub Actions and Google Cloud</a></li>
    <li><a href="https://medium.com/google-cloud/google-cloud-adoption-for-the-enterprise-from-strategy-to-operation-part-0-overview-9091f5a1ddfc" target="_blank" rel="noopener">My Series on Google Cloud Adoption: from Strategy to Operation</a></li>
    <li><a href="https://medium.com/google-cloud/google-cloud-landing-zone-with-terraform-and-cloud-foundation-fabric-fast-part-1-2c7634ac31fd" target="_blank" rel="noopener">Google Cloud Landing Zones with Google Cloud Foundation Fabric FAST</a></li>
    <li><a href="https://medium.com/google-cloud/design-your-landing-zone-design-considerations-part-1-google-cloud-adoption-series-74978d968fed" target="_blank" rel="noopener">Design your Google Cloud Landing Zone</a></li>
    <li><a href="https://medium.com/google-cloud/develop-serverless-applications-on-cloud-run-google-cloud-challenge-lab-walkthrough-a62da1c33989" target="_blank" rel="noopener">Develop Serverless Applications on Cloud Run: Google Cloud Challenge Lab Walkthrough</a></li>
    <li><a href="https://medium.com/google-cloud/optimise-costs-for-google-kubernetes-engine-google-cloud-challenge-lab-walkthrough-739abfb58ea0" target="_blank" rel="noopener">Optimise Costs for Google Kubernetes Engine: Google Cloud Challenge Lab Walkthrough</a></li>
    <li><a href="https://medium.com/google-cloud/a-sample-application-using-terraform-on-google-cloud-2405c598a60a" target="_blank" rel="noopener">Terraforming an Application on Google Cloud</a></li>
    <li><a href="https://medium.com/google-cloud/google-next-2023-experience-and-favourite-sessions-fb00add5f59e" target="_blank" rel="noopener">Google Cloud Next Summaries, and Announcements</a></li>
  </ul>
</details>
