# Documentation (`docs/`)

Source files for the [aoc.just2good.co.uk](https://aoc.just2good.co.uk/) Jekyll site, styled with the custom **Midnight AoC** dark-first design system and persisted Daylight Light toggle. If you're looking for Python puzzle source code, navigate to [`../src/`](../src/readme.md).

## Visual Design & Architecture

- **Design Specification**: See [`DESIGN.md`](DESIGN.md) for the complete Midnight AoC token palette (`#07080D` canvas, `#BB86FC` / `#6200EE` purple, `#03DAC6` teal, `#FFD166` star gold, constant `#131722` code blocks), typography (`Inter` and `JetBrains Mono`), responsive grid, and legacy guardrails.
- **Custom Theme Implementation**: Replaced `jekyll-theme-modernist` with custom templates and stylesheets under [`_layouts/`](_layouts/default.html), [`_includes/`](_includes/header.html), [`_sass/`](_sass/_tokens.scss), and [`assets/js/site.js`](assets/js/site.js) (zero-FOUC `aoc-theme` bootstrap, collapsible sidebar drawer, desktop `"On this page"` TOC scroll-spy, and code-block copy buttons).
- **Ruby Sass `3.7.4` Guardrails**: GitHub Pages (`github-pages ~> 233`) compiles CSS using Ruby Sass `3.7.4`. Always use `@import` partials in [`assets/css/style.scss`](assets/css/style.scss) and comma-separated `rgba(r, g, b, a)` values; never use `@use`/`@forward`, CSS Color 4 slash syntax, or mixed-unit `min()`/`max()`/`clamp()`.
- **Social Preview & Favicons**: Default OpenGraph and Twitter cards (`summary_large_image`) point to [`assets/images/aoc-social-card.png`](assets/images/aoc-social-card.png) via [`_config.yml`](_config.yml), paired with Midnight AoC favicons and [`site.webmanifest`](site.webmanifest).
- **Dark-Mode Image Matting**: Standard `.png` diagrams inside `.prose` automatically receive a light `#F8FAFC` mat in Dark mode so historical black-on-transparent figures remain legible. Add `class="no-mat"` to any dark-background PNG banner embedded inside `.prose`.

## Local Preview (Docker + Jekyll)

Run commands from the repository root (or use `docker compose` inside `docs/`):

- `make docs` — Build and serve the Jekyll site locally at `http://127.0.0.1:4000` (`cd docs && docker compose up`).
- `make docs-build` — Rebuild the local Docker image after modifying [`Dockerfile`](Dockerfile) or [`Gemfile`](Gemfile).
- `make docs-stop` — Stop and remove the local Jekyll container (`cd docs && docker compose down`).
- **CI Build Verification**: [`.github/workflows/pr-checks.yml`](../.github/workflows/pr-checks.yml) runs `bundle exec jekyll build --trace` in `docs/` alongside Python checks.
- **Optional environment variables**: If you need `JEKYLL_GITHUB_TOKEN`, restore `docs/.env` via `git-crypt-helper.sh sync-from-enc` (for maintainers) or copy [`.env.template`](.env.template) to `docs/.env`.

## Site Structure & Authoring Notes

- **Navigation**: Top menus, year dropdowns, and prev/next breadcrumbs are driven by [`_data/navigation.yaml`](_data/navigation.yaml).
- **Layouts**: [`_config.yml`](_config.yml) defaults Markdown pages to the `day-page` layout. Year landing pages (e.g. `2026/index.md`) must explicitly set `layout: default` in frontmatter, while guides under [`python/`](python/index.md) use `layout: journey-page`.
- **LaTeX Maths**: Add `mathjax: true` to page frontmatter when rendering equations with MathJax v3 (loaded in [`_includes/head-custom.html`](_includes/head-custom.html)). Avoid single-`$` inline delimiters and text-based `mermaid` or ASCII diagrams.
