# Repository Instructions (`AGENTS.md`)

Guidance for local coding agents and automated CI reviewers working in **Dazbo's Advent of Code** repository.

## Project Overview

Advent of Code changed from a 25-day event (2015–2024) to a **12-day event from 2025 onwards**. Keep `uv run aoc new-year` (`make new-year`) and [`scripts/create_year.sh`](scripts/create_year.sh) defaulting to `12` days unless an explicit legacy count is passed.

## Repository Layout

| Path | Purpose | Notes |
| :--- | :--- | :--- |
| [`src/aoc_common/`](src/aoc_common/aoc_commons.py) | Shared utilities (`aoc_commons.py`, `runner.py`, `cli.py` -> `uv run aoc` including `clean-inputs`) | Packaged editably in `.venv`; zero dependency on `dazbo_commons`; enforces AoC `User-Agent` header; `is_git_crypt_locked` locked-blob detection; in-memory `aoc fetch` parser; notebook-safe `get_aoc_locations` |
| [`src/tests/`](src/tests/test_aoc_commons.py) | Offline unit tests ([`test_aoc_commons.py`](src/tests/test_aoc_commons.py), [`test_runner_and_cli.py`](src/tests/test_runner_and_cli.py)) | Must pass completely offline without a live `AOC_SESSION_COOKIE` |
| [`src/template_folder/`](src/template_folder/template.py) | Template v3 script (`-p`, `-s`, `--no-samples`, `-d`, `--json`) and Jupyter notebook template | Target for `uv run aoc new-year` (`make new-year`) and [`scripts/create_year.sh`](scripts/create_year.sh) |
| `src/AoC_2015/` – `src/AoC_2025/` | Historical AoC puzzle solutions | Excluded from `ruff`, `codespell`, and `pyright` sweeps |
| [`scripts/create_year.sh`](scripts/create_year.sh) | Standalone Bash fallback to scaffold `src/AoC_<year>/d01..d<days>` | Defaults to `12` days; does not create empty `input.txt` placeholders |
| [`docs/`](docs/index.md) | Jekyll GitHub Pages site (`https://aoc.just2good.co.uk/`) | Custom Midnight AoC theme ([`docs/DESIGN.md`](docs/DESIGN.md)), navigation defined in [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml) |
| [`.github/workflows/`](.github/workflows/pr-checks.yml) | CI checks (`pr-checks.yml`) and Gemini PR/issue workflows | Keep `gemini_model: 'gemini-3.8-flash'`; PR review guardrails in [`.github/review-instruction-additions.md`](.github/review-instruction-additions.md) |
| [`.agents/rules/`](.agents/rules/aoc-retrieval.md) | Model-triggered workspace rule for AoC retrieval | Governs `uv run aoc fetch`, `AOC_SESSION_COOKIE`, `User-Agent`, and zero-temp-file policy |
| `.agents/skills/` | Workspace AoC skills (`aoc-problem-summary`, `aoc-solution-support`, `aoc-create-doc`, `aoc-megathread-post`; `SKILL.md.enc` encrypted in Git) | Plaintext `SKILL.md` files are gitignored via `git-crypt-helper.sh` |
| [`TODO.md`](TODO.md) | Project roadmap and backlog | Tracks planned code, docs, and skill improvements |

## Environment, Dependencies & Static Checks

- Manage the virtual environment strictly with `uv` and [`pyproject.toml`](pyproject.toml) (`requires-python = ">=3.13"`):
  - Hydrate environment: `make install` (`uv sync --dev --extra jupyter --extra legacy` — includes `legacy` extras `dazbo-commons` and `colorama` so untouched `2015`–`2024` solutions remain runnable locally; CI runs without `legacy`)
  - Run offline verification gate: `make check` (`codespell -s`, `ruff check`, `pyright`, and `pytest src/tests`)
- **Historical Solutions Policy**: Do **NOT** run bulk `ruff --fix`, `ruff format`, or `codespell -w` across `src/AoC_2015`–`src/AoC_2025` or prose inside `docs/2015`–`docs/2025` unless explicitly requested. Lint/type gates intentionally cover [`src/aoc_common`](src/aoc_common/aoc_commons.py), [`src/tests`](src/tests/test_aoc_commons.py), [`src/template_folder`](src/template_folder/template.py), and 2026+ code.
- **Context-Lean Reads & Searches**: Prefer `uv run --no-sync aoc ... --json` for structured metadata. Never `read_file` a whole yearly `.ipynb` notebook (`400 KB`–`1.1 MB`); locate `## Day <N>` line offsets via `grep -n` first and read bounded slices. Pass `--exclude-dir=_site` whenever running `grep` across `docs/` so local Jekyll HTML builds do not pollute results.

## Secrets, Puzzle Inputs & `git-crypt` Guardrails

This is a **public** GitHub repository containing private files encrypted via `git-crypt`:

1. **AoC Input Files (`input*.txt`)**: Directly filtered by [`input*.txt filter=git-crypt`](.gitattributes) so puzzle inputs are never published in plaintext (per Advent of Code creator policy).
2. **Parallel `.enc` Pattern (`*.enc filter=git-crypt`)**: Files such as `.env`, `docs/.env`, and `.agents/skills/*/SKILL.md` are gitignored in plaintext and tracked in Git via their `.enc` twins (`.env.enc`, `docs/.env.enc`, `.agents/skills/*/SKILL.md.enc`).
   - Restore locally: `git-crypt-helper.sh sync-from-enc`
   - Update encrypted twin after local edit: `git-crypt-helper.sh sync-to-enc <file>`
   - Inspect [`.env.template`](.env.template) and [`docs/.env.template`](docs/.env.template) for required environment variable keys.
3. **AoC Retrieval Ethics**: Always follow [`.agents/rules/aoc-retrieval.md`](.agents/rules/aoc-retrieval.md) — use `uv run aoc fetch` (enforcing `User-Agent: github.com/derailed-dash/Advent-of-Code by derailed.dash@gmail.com`), never leak real puzzle outputs in docs, and never leave temporary `desc.html` downloads on disk.

## GitHub Pages (`docs/`) Architecture

- **Visual Design System**: Styled with the custom **Midnight AoC** dark-first theme and persisted Daylight Light toggle specified in [`docs/DESIGN.md`](docs/DESIGN.md). Partials in [`docs/_sass/`](docs/_sass/_tokens.scss) compile on GitHub Pages (`github-pages ~> 233`) with **Ruby Sass `3.7.4`** — always use `@import` and comma-separated `rgba(r, g, b, a)`, never `@use`/`@forward`, CSS Color 4 slash syntax, or mixed-unit `min()`/`max()`/`clamp()`. [`.github/workflows/pr-checks.yml`](.github/workflows/pr-checks.yml) verifies builds via the `docs-build` job (`bundle exec jekyll build --trace`).
- **Dark-Mode Image Matting**: `.png` diagrams inside `.prose` automatically receive a light `#F8FAFC` mat in Dark mode so historical black-on-transparent figures remain readable; add `.no-mat` to intentionally dark-background PNG banners (such as `aoc-hero-banner.png`).
- **Layouts**: [`default.html`](docs/_layouts/default.html), [`day-page.html`](docs/_layouts/day-page.html), and [`journey-page.html`](docs/_layouts/journey-page.html). Year landing pages (`docs/2025/index.md`, etc.) **must** explicitly set `layout: default` because [`docs/_config.yml`](docs/_config.yml) defaults everything to `day-page` (paired with default OpenGraph `image: /assets/images/aoc-social-card.png`).
- **Navigation**: Menus and prev/next breadcrumbs read [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml).
- **MathJax v3**: Enable LaTeX rendering by adding `mathjax: true` to page frontmatter (loaded cleanly from `cdn.jsdelivr.net` in [`head-custom.html`](docs/_includes/head-custom.html)). Never use single-`$` inline math delimiters or inline `cdn.mathjax.org` `<script>` tags.
- **Diagrams**: Never use `mermaid` code blocks or ASCII/Unicode box-drawing trees in Markdown; use Markdown tables or image assets in [`docs/assets/images/`](docs/assets/images/).
