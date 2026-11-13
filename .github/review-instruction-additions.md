# Repository Review Instructions (Advent of Code)

Apply these repository-specific rules during pull request reviews:

1. **Historical Solution Code (`src/AoC_2015/` – `src/AoC_2025/`)**:
   - **Never** review, critique, or suggest linting, formatting, typing, or algorithmic changes to historical Advent of Code solutions in `src/AoC_2015/` through `src/AoC_2025/`. These directories are intentionally frozen and excluded from `ruff`, `codespell`, and `pyright`.

2. **Historical Walkthrough Pages (`docs/2015/` – `docs/2025/`)**:
   - When a PR modifies existing walkthrough pages under `docs/2015/` through `docs/2025/` (for example, fixing broken links or adding `mathjax: true` frontmatter), review **only** the changed lines in the diff. Do not flag untouched legacy prose, spelling, or embedded code snippets on those pages.

3. **Active Code & Tooling (`src/aoc_common/`, `src/tests/`, `src/template_folder/`, `src/AoC_2026+`)**:
   - Enforce Python 3.13+ conventions (`uv`, PEP 585/604 type annotations, offline unit tests in `src/tests/`) and UK English spelling.
   - Flag any unencrypted puzzle input files (`input*.txt`), real puzzle answers leaked in documentation, or plaintext secrets/tokens.
   - Never suggest downgrading configured Gemini models (such as `gemini-3.8-flash`).
