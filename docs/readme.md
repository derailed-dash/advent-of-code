# Documentation (`docs/`)

Source files for the [aoc.just2good.co.uk](https://aoc.just2good.co.uk/) Jekyll site. If you're looking for Python puzzle source code, navigate to [`../src/`](../src/readme.md).

## Local Preview (Docker + Jekyll)

Run commands from the repository root (or use `docker compose` inside `docs/`):

- `make docs` — Build and serve the Jekyll site locally at `http://127.0.0.1:4000` (`cd docs && docker compose up`).
- `make docs-build` — Rebuild the local Docker image after modifying [`Dockerfile`](Dockerfile) or [`Gemfile`](Gemfile).
- `make docs-stop` — Stop and remove the local Jekyll container (`cd docs && docker compose down`).
- **Optional environment variables**: If you need `JEKYLL_GITHUB_TOKEN`, restore `docs/.env` via `git-crypt-helper.sh sync-from-enc` (for maintainers) or copy [`.env.template`](.env.template) to `docs/.env`.

## Site Structure & Authoring Notes

- **Navigation**: Top menus and prev/next breadcrumbs are driven by [`_data/navigation.yaml`](_data/navigation.yaml).
- **Layouts**: [`_config.yml`](_config.yml) defaults Markdown pages to the `day-page` layout. Year landing pages (e.g. `2026/index.md`) must explicitly set `layout: default` in frontmatter, while guides under [`python/`](python/index.md) use `layout: journey-page`.
- **LaTeX Maths**: Add `mathjax: true` to page frontmatter when rendering equations with MathJax v3 (loaded in `_includes/head-custom.html`). Avoid single-`$` inline delimiters and text-based `mermaid` or ASCII diagrams.
