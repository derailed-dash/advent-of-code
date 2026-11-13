# Project Plan: Dazbo's Advent of Code

Roadmap and backlog for modernising repository tooling, reusable Python utilities, agent customisations, and the [aoc.just2good.co.uk](https://aoc.just2good.co.uk/) documentation site.

## Completed

- [x] Modernise Python environment around `uv` (`>=3.13`), [`pyproject.toml`](pyproject.toml), and offline `make check` verification (`codespell`, `ruff`, `pyright`, `pytest`) (2026-11-13)
- [x] Decouple [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py) from `dazbo-commons`, enforce AoC `User-Agent` header, and add offline unit tests in [`src/tests/test_aoc_commons.py`](src/tests/test_aoc_commons.py) (2026-11-13)
- [x] Update [`scripts/create_year.sh`](scripts/create_year.sh) and [`src/template_folder/`](src/template_folder/template.py) for 12-day AoC events (2025+) and 2026 readiness (2026-11-13)
- [x] Replace legacy Jekyll container with [`docs/Dockerfile`](docs/Dockerfile) (`ruby:3.3-slim`, `github-pages ~> 233`), migrate MathJax to v3 (`mathjax: true`), add `2020`/`2026` landing pages, and fix broken links across [`docs/`](docs/index.md) (2026-11-13)
- [x] Add offline CI workflow ([`.github/workflows/pr-checks.yml`](.github/workflows/pr-checks.yml)), [`AGENTS.md`](AGENTS.md), and historical-code PR review exclusions ([`.github/workflows/gemini-review.yml`](.github/workflows/gemini-review.yml), [`.github/review-instruction-additions.md`](.github/review-instruction-additions.md)) (2026-11-13)

## Backlog

### 1. Assess `dazbo-commons` Utility & Usage

- [ ] Audit all remaining `dazbo_commons` imports and references across historical solutions (`src/AoC_2015/`, `src/AoC_2017/`, `src/AoC_2018/`, `src/AoC_2022/d01_calorie_counting/`, `src/AoC_2024/`, `src/AoC_2025/d01/d01-range.py`), [`src/template_folder/Dazbo's_Advent_of_Code_Template.ipynb`](src/template_folder/Dazbo's_Advent_of_Code_Template.ipynb), [`docs/2018/4.md`](docs/2018/4.md), and `.agents/skills/aoc-help/SKILL.md`.
- [ ] Compare features still used from `dazbo-commons` (coloured console logging, path locations) against native equivalents already in [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py) (`RichHandler`, `Locations`, `get_locations`, `setup_file_logging`).
- [ ] Decide whether to move `"dazbo-commons>=0.2.0"` in [`pyproject.toml`](pyproject.toml) into an optional `[project.optional-dependencies] legacy` group (preserving runnable legacy solutions while keeping the core install lean) and remove `dazbo-commons` from active notebook templates and skills.

### 2. General Repository Usage Documentation Updates

- [ ] Review [`README.md`](README.md), [`src/readme.md`](src/readme.md), [`docs/readme.md`](docs/readme.md), [`AGENTS.md`](AGENTS.md), and [`docs/index.md`](docs/index.md) end-to-end for accuracy, onboarding clarity, and cross-document consistency.
- [ ] Align the `Helper Libraries` section of [`README.md`](README.md) with actual symbols in [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py) (e.g. `setup_logging` with `RichHandler` rather than legacy `ColouredFormatter` / `retrieve_console_logger`).
- [ ] Add a concise "Daily AoC Workflow" guide covering year scaffolding (`make new-year YEAR=2026`), `AOC_SESSION_COOKIE` setup, running sample vs real inputs, authoring a walkthrough page, updating [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml), and previewing via `make docs`.
- [ ] Document new-machine `git-crypt` onboarding clearly (`git-crypt unlock ~/localdev/git-crypt-key`, `git-crypt-helper.sh sync-from-enc`, and how `input*.txt` vs `*.enc` filters interact).

### 3. Review Workspace Skills, Rules & Legacy Agent Customisations

- [ ] Audit all four encrypted skills in `.agents/skills/` (`aoc-help`, `aoc-doc-intro`, `aoc-create-doc`, `aoc-megathread-post`) and update them where needed for 12-day AoC events (2025+), `uv run`, current `aoc_common` helpers, MathJax v3 frontmatter (`mathjax: true`), and diagram guardrails (no Mermaid or ASCII trees).
- [ ] Review [`.agent/rules/aoc-retrieval.md`](.agent/rules/aoc-retrieval.md) and evaluate whether to relocate from legacy `.agent/rules/` or consolidate retrieval guardrails cleanly with [`AGENTS.md`](AGENTS.md) and `aoc-help`.
- [ ] Audit legacy Gemini CLI TOML slash commands in `.gemini/commands/aoc/` (`doc-intro.toml`, `doc.toml`, `help.toml`, `sample-input.toml`) — determine whether any unique logic (such as `sample-input.toml`) should be folded into `.agents/skills/` before retiring `.gemini/commands/aoc/`.

### 4. Review & Improve Reusable Code (`src/aoc_common/`)

- [ ] Add strict Python 3.13+ type annotations (`PEP 585` / `PEP 604`) and docstrings across [`src/aoc_common/aoc_commons.py`](src/aoc_common/aoc_commons.py), and avoid import-time side effects (`load_dotenv()` on module import).
- [ ] Fix edge cases and ergonomics in existing helpers (with TDD coverage in [`src/tests/test_aoc_commons.py`](src/tests/test_aoc_commons.py)):
  - `binary_search`: guard against `low = candidate` infinite loops when `high == low + 1`, and support lower-bound / upper-bound predicate bisection (`bisect` pattern) in addition to exact target matching.
  - `merge_intervals`: avoid mutating the caller's input list in-place, handle empty input safely, and support `tuple[int, int]` / `range` intervals cleanly.
  - `to_base_n`: support bases `> 10` (hex/alphanumeric digits) and negative integers, or validate `2 <= base <= 36`.
  - `Point` & `Grid`: replace `asdict(a_point)` in `Point.manhattan_distance` with direct coordinate arithmetic (`abs(a_point.x) + abs(a_point.y)`) for hot-loop performance; fix `Grid.transpose()` returning `list[tuple]` instead of `list[list]`; evaluate `Point3D`, sparse dict-backed grids, and top-left (`y`-down) vs Cartesian (`y`-up) coordinate helpers.

### 5. Standardise Repeated Solution Patterns & Refresh `docs/python/` Reference Pages

- [ ] Survey `src/AoC_2015/`–`src/AoC_2025/` to catalogue algorithms and data structures implemented repeatedly across days (e.g. BFS/DFS flood fill, Dijkstra / A* with `heapq`, Union-Find / connected components, 2D grid parsing and rotation/bounds checks, cycle detection for large-$N$ simulations, 1D/2D interval splitting).
- [ ] Decide which patterns merit promotion into [`src/aoc_common/`](src/aoc_common/aoc_commons.py) versus copy-ready canonical patterns in [`docs/python/`](docs/python/index.md) and [`src/template_folder/`](src/template_folder/template.py).
- [ ] Review and modernise existing [`docs/python/`](docs/python/index.md) reference pages — prioritising [`reusable_code.md`](docs/python/reusable_code.md), [`useful_algorithms.md`](docs/python/useful_algorithms.md), [`shortest_paths.md`](docs/python/shortest_paths.md), [`priority_queues.md`](docs/python/priority_queues.md), [`graph.md`](docs/python/graph.md), [`logging.md`](docs/python/logging.md), [`colours.md`](docs/python/colours.md), [`my-aoc-template.md`](docs/python/my-aoc-template.md), [`my-aoc-template2.md`](docs/python/my-aoc-template2.md), and excluded draft [`parsimonious.md`](docs/python/parsimonious.md) — for Python 3.13+, `uv`, `rich`, and updated `aoc_common` APIs.

### 6. Extract New Python Journey Pages from Solved Puzzles

- [ ] Mine past solutions and notebooks (`2015`–`2025`) for recurring puzzle-solving techniques not yet covered in [`docs/python/`](docs/python/index.md), and draft standalone reference pages (registered in [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml)):
  - **Caching & Dynamic Programming (`functools.cache`)**: top-down state-space DP, state tuple design, and pruning strategies.
  - **Interval & Range Algebra**: 1D and multi-dimensional range splitting, merging, and coordinate compression (e.g. mapping massive value ranges without brute force).
  - **Cycle Detection & Modular Arithmetic**: simulating $10^{12}+$ iterations via state hashing, `math.lcm`, modular inverses (`pow(a, -1, m)`), and the Chinese Remainder Theorem.
  - **Grid Geometry (Shoelace Formula & Pick's Theorem)**: computing polygon area and interior lattice points directly from boundary vertices/perimeter steps.
  - **Constraint Solving & Linear Systems**: expanding [`sympy.md`](docs/python/sympy.md) or adding dedicated coverage for simultaneous equations and integer optimisation puzzles.
  - **Modern Python Ergonomics for AoC**: structural pattern matching (`match`/`case`), `itertools` (`pairwise`, `batched`, `product`, `combinations`), and immutable `dataclass(frozen=True)` / `NamedTuple` state modelling.

### 7. Site Rebranding & Visual Reskinning (`docs/`)

- [ ] Define a cohesive visual identity (`docs/DESIGN.md`) aligned with Dazbo's personal brand ([darrenlester.net](https://darrenlester.net)) — covering colour palette (dark/terminal AoC aesthetic vs light/dark toggle), typography, code syntax highlighting, and responsive spacing tokens.
- [ ] Evaluate replacing or heavily customising the legacy `jekyll-theme-modernist` theme ([`docs/_config.yml`](docs/_config.yml), [`docs/_sass/jekyll-theme-modernist.scss`](docs/_sass/jekyll-theme-modernist.scss), [`docs/assets/css/style.scss`](docs/assets/css/style.scss)), deciding between GitHub Pages' managed Jekyll build and a custom GitHub Actions Pages workflow.
- [ ] Redesign [`docs/_layouts/default.html`](docs/_layouts/default.html), [`docs/_layouts/day-page.html`](docs/_layouts/day-page.html), and [`docs/_layouts/journey-page.html`](docs/_layouts/journey-page.html) with modern navigation (sticky/collapsible year & Python Journey menus, copy-code buttons, mobile drawer, and cleaner prev/next breadcrumbs).
- [ ] Refresh visual assets in `docs/assets/images/` — updated hero/banner artwork, favicon, social preview (`og:image`), and refreshed site screenshot in [`README.md`](README.md).
