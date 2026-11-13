# Repository Instructions (`AGENTS.md`)

Guidance for local coding agents and automated CI reviewers working in **Dazbo's Advent of Code** repository.

## Project Overview

- **Author**: Darren "Dazbo" Lester (`derailed-dash`)
- **Documentation Site**: [aoc.just2good.co.uk](https://aoc.just2good.co.uk/)
- **Personal Website & Blog**: [darrenlester.net](https://darrenlester.net) · [Medium (`@dazbo`)](https://medium.com/@dazbo)
- **Repository README**: [`README.md`](README.md)

Advent of Code changed from a 25-day event (2015–2024) to a **12-day event from 2025 onwards**. Keep [`scripts/create_year.sh`](scripts/create_year.sh) defaulting to `12` days unless an explicit legacy count is passed.

## Repository Layout

| Path | Purpose | Notes |
| :--- | :--- | :--- |
| [`src/aoc_common/`](src/aoc_common/aoc_commons.py) | Shared utilities (`Locations`, `Point`, `Grid`, `write_puzzle_input_file`) | Zero dependency on `dazbo_commons`; enforces AoC `User-Agent` header |
| [`src/tests/`](src/tests/test_aoc_commons.py) | Offline unit tests (`pytest` / `unittest.mock`) | Must pass completely offline without a live `AOC_SESSION_COOKIE` |
| [`src/template_folder/`](src/template_folder/template.py) | Starter Python script and Jupyter notebook templates | Target for `scripts/create_year.sh` |
| `src/AoC_2015/` – `src/AoC_2025/` | Historical AoC puzzle solutions | Excluded from `ruff`, `codespell`, and `pyright` sweeps |
| [`scripts/create_year.sh`](scripts/create_year.sh) | Scaffolds `src/AoC_<year>/d01..d<days>` | Defaults to `12` days; does not create empty `input.txt` placeholders |
| [`docs/`](docs/index.md) | Jekyll GitHub Pages site (`https://aoc.just2good.co.uk/`) | Navigation defined in [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml) |
| [`.github/workflows/`](.github/workflows/pr-checks.yml) | CI checks (`pr-checks.yml`) and Gemini PR/issue workflows | Keep `gemini_model: 'gemini-3.8-flash'`; PR review guardrails in [`.github/review-instruction-additions.md`](.github/review-instruction-additions.md) |
| [`.agent/rules/`](.agent/rules/aoc-retrieval.md) | Workspace rule for Advent of Code retrieval | Governs `AOC_SESSION_COOKIE`, `User-Agent`, and `desc.html` cleanup |
| `.agents/skills/` | Workspace AoC skills (`SKILL.md.enc` encrypted in Git) | Plaintext `SKILL.md` files are gitignored via `git-crypt-helper.sh` |

## Environment, Dependencies & Static Checks

- Manage the virtual environment strictly with `uv` and [`pyproject.toml`](pyproject.toml) (`requires-python = ">=3.13"`):
  - Hydrate environment: `make install` (`uv sync --dev --extra jupyter`)
  - Run offline verification gate: `make check` (`codespell -s`, `ruff check --diff`, `pyright`, and `pytest src/tests`)
- **Historical Solutions Policy**: Do **NOT** run bulk `ruff --fix`, `ruff format`, or `codespell -w` across `src/AoC_2015`–`src/AoC_2025` or prose inside `docs/2015`–`docs/2025` unless explicitly requested. Lint/type gates intentionally cover [`src/aoc_common`](src/aoc_common/aoc_commons.py), [`src/tests`](src/tests/test_aoc_commons.py), [`src/template_folder`](src/template_folder/template.py), and 2026+ code.

## Secrets, Puzzle Inputs & `git-crypt` Guardrails

This is a **public** GitHub repository containing private files encrypted via `git-crypt`:

1. **AoC Input Files (`input*.txt`)**: Directly filtered by [`input*.txt filter=git-crypt`](.gitattributes) so puzzle inputs are never published in plaintext (per Advent of Code creator policy).
2. **Parallel `.enc` Pattern (`*.enc filter=git-crypt`)**: Files such as `.env`, `docs/.env`, and `.agents/skills/*/SKILL.md` are gitignored in plaintext and tracked in Git via their `.enc` twins (`.env.enc`, `docs/.env.enc`, `.agents/skills/*/SKILL.md.enc`).
   - Restore locally: `git-crypt-helper.sh sync-from-enc`
   - Update encrypted twin after local edit: `git-crypt-helper.sh sync-to-enc <file>`
   - Inspect [`.env.template`](.env.template) and [`docs/.env.template`](docs/.env.template) for required environment variable keys.
3. **AoC Retrieval Ethics**: Always follow [`.agent/rules/aoc-retrieval.md`](.agent/rules/aoc-retrieval.md) — identify automation with `User-Agent: github.com/derailed-dash/Advent-of-Code by derailed.dash@gmail.com`, never leak real puzzle outputs in docs, and delete temporary `desc.html` downloads immediately.

## GitHub Pages (`docs/`) Architecture

- **Layouts**: [`default.html`](docs/_layouts/default.html), [`day-page.html`](docs/_layouts/day-page.html), and [`journey-page.html`](docs/_layouts/journey-page.html). Year landing pages (`docs/2025/index.md`, etc.) **must** explicitly set `layout: default` because [`docs/_config.yml`](docs/_config.yml) defaults everything to `day-page`.
- **Navigation**: Menus and prev/next breadcrumbs read [`docs/_data/navigation.yaml`](docs/_data/navigation.yaml).
- **MathJax v3**: Enable LaTeX rendering by adding `mathjax: true` to page frontmatter (loaded cleanly from `cdn.jsdelivr.net` in [`head-custom.html`](docs/_includes/head-custom.html)). Never use single-`$` inline math delimiters or inline `cdn.mathjax.org` `<script>` tags.
- **Diagrams**: Never use `mermaid` code blocks or ASCII/Unicode box-drawing trees in Markdown; use Markdown tables or image assets in [`docs/assets/images/`](docs/assets/images/).
