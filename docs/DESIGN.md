---
version: "1.0"
name: "Dazbo's Advent of Code — Midnight AoC"
description: "Dark-first 'Midnight AoC' visual design system with persisted Daylight Light toggle, aligned with darrenlester.net and Advent of Code."
colors:
  background: "#07080D"
  surface: "#0F131D"
  surface-elevated: "#161C2B"
  primary: "#7C4DFF"
  brand-accent: "#BB86FC"
  secondary: "#03DAC6"
  aoc-gold: "#FFD166"
  on-background: "#E8ECF4"
  on-surface: "#E8ECF4"
  on-surface-muted: "#7E8CA6"
  code-background: "#131722"
  error: "#FF6B6B"
  success: "#34D399"
light_mode:
  background: "#F4F6FA"
  surface: "#FFFFFF"
  surface-elevated: "#EEF2F8"
  primary: "#6200EE"
  brand-accent: "#6200EE"
  secondary: "#00796B"
  aoc-gold: "#92400E"
  on-background: "#141B29"
  on-surface: "#141B29"
  on-surface-muted: "#5B6B82"
  code-background: "#131722"
typography:
  display-lg:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: "44px"
    letterSpacing: "-0.5px"
  heading-md:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: "32px"
    letterSpacing: "-0.25px"
  body-md:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "26px"
    letterSpacing: "0px"
  code-md:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "22px"
rounded:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
components:
  header-glass:
    height: "56px"
    backdropFilter: "blur(12px)"
  reading-card:
    borderRadius: "12px"
    padding: "32px"
  code-block:
    background: "#131722"
    borderRadius: "8px"
  concept-pill:
    borderRadius: "9999px"
---

# Visual Design and UX Specification — Midnight AoC

This specification is the single source of truth for the visual identity, layout architecture, legacy content compatibility, and staged delivery plan for [aoc.just2good.co.uk](https://aoc.just2good.co.uk/).

## Overview

The **Midnight AoC** design system replaces the legacy `jekyll-theme-modernist` theme with a custom, responsive Jekyll layout aligned with Dazbo's personal brand on [darrenlester.net](https://darrenlester.net) — glassmorphic dark surfaces, purple brand accents (`#BB86FC` / `#6200EE`), teal interactive highlights (`#03DAC6`), and crisp `Inter` typography — fused with Advent of Code's terminal heritage and gold-star (`#FFD166`) accents.

Unlike the short-form portfolio cards on `darrenlester.net`, `aoc.just2good.co.uk` serves long-form Python tutorials, mathematical derivations, and multi-part puzzle walkthroughs. To balance brand cohesion with extended reading comfort, the default palette uses a deep midnight slate (`#07080D` canvas, `#0F131D` surface) rather than harsh `#000000`, paired with a persisted **Daylight Light** toggle for daytime reading and seamless rendering of legacy visual assets.

## Colours & Theme Modes

Theme state is controlled via a `data-theme="dark"` (default) or `data-theme="light"` attribute on `<html>`, persisted in `localStorage` under the `aoc-theme` key. A small inline script inside `<head>` applies the stored preference before first paint so visitors never experience a flash of the wrong theme.

All foreground/background pairings target **WCAG 2.1 AA** contrast ratios (`>= 4.5:1` for normal body text and links; `>= 3.0:1` for large headings and UI boundaries). In Daylight Light mode, interactive teal (`#03DAC6`) and AoC gold (`#FFD166`) deepen to `#00796B` and `#92400E` respectively so text labels remain sharp on white surfaces.

| Semantic CSS Variable | Dark (`[data-theme="dark"]`, Default) | Light (`[data-theme="light"]`) | Purpose & Usage |
| :--- | :--- | :--- | :--- |
| `--aoc-bg-canvas` | `#07080D` | `#F4F6FA` | Outer page backdrop behind sidebars and reading cards |
| `--aoc-bg-surface` | `#0F131D` | `#FFFFFF` | Main reading surface, sidebar panels, and cards |
| `--aoc-bg-elevated` | `#161C2B` | `#EEF2F8` | Hover states, table headers, callout backgrounds, and secondary controls |
| `--aoc-bg-glass` | `rgba(15, 19, 29, 0.86)` | `rgba(255, 255, 255, 0.90)` | Sticky top header and slide-over mobile drawer with `backdrop-filter: blur(12px)` |
| `--aoc-border-subtle` | `#1F2536` | `#DBE2EE` | Hairline dividers, card outlines, and sidebar separators |
| `--aoc-border-strong` | `#2E3750` | `#CBD5E1` | Interactive button borders, active card outlines, and focus rings |
| `--aoc-text-primary` | `#E8ECF4` | `#141B29` | Headings (`h1`–`h4`), body copy, and strong emphasis |
| `--aoc-text-secondary` | `#B8C1D4` | `#334155` | Navigation links, TOC labels, and metadata subtitles |
| `--aoc-text-muted` | `#7E8CA6` | `#5B6B82` | Breadcrumbs, timestamps, captions, and inactive controls |
| `--aoc-brand-purple` | `#BB86FC` | `#6200EE` | *"Dazbo's"* wordmark accent, internal `/python/` concept pills, and active sidebar indicators |
| `--aoc-primary-action` | `#7C4DFF` | `#6200EE` | Primary CTA buttons, active tab borders, and keyboard focus outlines |
| `--aoc-accent-teal` | `#03DAC6` | `#00796B` | Standard prose hyperlinks, active TOC markers, and external link pills |
| `--aoc-accent-gold` | `#FFD166` | `#92400E` | Advent of Code stars (`★`), problem link badges, and solution milestone highlights |
| `--aoc-code-bg` | `#131722` | `#131722` | Constant dark terminal background for `<pre>` and Rouge syntax blocks |
| `--aoc-code-border` | `#283046` | `#263044` | Code block frame border and header divider |

## Typography

The site loads `Inter` (`400`, `500`, `600`, `700`) and `JetBrains Mono` (`400`, `500`, `600`) from Google Fonts with `display=swap` and clean system fallbacks so pages remain readable immediately on slow connections or offline builds.

| Role | Font Family | Size | Weight / Line Height | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Display / Hero (`h1`)** | `Inter`, system sans-serif | `2.25rem` (`36px`) desktop / `1.75rem` (`28px`) mobile | `700` / `1.22` (`-0.5px` tracking) | Page title on home, year landing, and walkthrough headers |
| **Section Heading (`h2`)** | `Inter`, system sans-serif | `1.5rem` (`24px`) | `600` / `1.33` (`-0.25px` tracking) | Top-bordered or subtle-underlined section breaks (`Part 1`, `Part 2`) |
| **Subsection (`h3`, `h4`)** | `Inter`, system sans-serif | `1.1875rem` (`19px`) / `1.0625rem` (`17px`) | `600` / `1.4` | Coloured in `--aoc-brand-purple` (`h3`) or `--aoc-text-primary` (`h4`) |
| **Body Prose** | `Inter`, system sans-serif | `1rem` (`16px`) | `400` / `1.625` | Constrained to `72ch`–`78ch` optimal reading measure inside the central column |
| **Code & Terminal** | `JetBrains Mono`, system monospace | `0.875rem` (`14px`) | `400` / `1.55` | Tabular alignment (`font-variant-numeric: tabular-nums`) for AoC grids and timings |
| **UI Labels & Badges** | `Inter`, system sans-serif | `0.75rem`–`0.8125rem` (`12px`–`13px`) | `500`–`600` / `1.4` | Minimum `12px` across all navigation items, pills, and captions |

## Code Syntax Highlighting & Terminal Tags

Code blocks (`pre`, `div.highlight`, `figure.highlight`) always render on a dark `#131722` terminal surface across **both** Dark and Light modes. Keeping terminal blocks dark preserves high contrast for Python syntax tokens and maintains visual parity with historical console output snippets.

Each fenced block is enhanced by `site.js` with a compact header/toolbar featuring a **Copy** button (`Copy` -> `Copied!` feedback with `aria-live="polite"` status).

### Rouge Syntax Palette (`_sass/_syntax.scss`)

| Rouge Token Class | Purpose | Hex Colour | Style |
| :--- | :--- | :--- | :--- |
| `.hll`, `.c`, `.cm`, `.c1`, `.cs` | Comments & docstrings | `#7E8CA6` | Italic |
| `.k`, `.kd`, `.kn`, `.kp`, `.kr`, `.kt`, `.kv` | Python keywords (`def`, `class`, `return`, `match`) | `#C792EA` | Medium (`500`) |
| `.nf`, `.nc`, `.nn`, `.nb`, `.bp` | Function names, classes, and built-ins | `#82AAFF` | Regular |
| `.s`, `.s1`, `.s2`, `.sb`, `.sc`, `.sd`, `.sh`, `.sx` | String literals & f-strings | `#A5D6A7` | Regular |
| `.m`, `.mi`, `.mf`, `.mh`, `.mo`, `.il`, `.kc` | Numbers, booleans (`True`/`False`), `None` | `#FFD166` | Regular |
| `.o`, `.ow`, `.p`, `.si`, `.se` | Operators, punctuation, escape sequences | `#4FD1C5` | Regular |
| `.err` | Syntax errors | `#FF6B6B` on `rgba(255, 107, 107, 0.14)` | Bold |

### Preserved Legacy Terminal Colour Tags

Historical walkthroughs (e.g. [`2015/20.md`](2015/20.md) and [`2021/24.md`](2021/24.md)) embed custom inline HTML tags (`<grn>`, `<ylw>`, `<red>`, `<mag>`, `<cyn>`) directly inside `<pre>` blocks to highlight terminal output. These tags are preserved cleanly against the `#131722` terminal surface:

| Custom Tag | Hex Colour | Intended Meaning |
| :--- | :--- | :--- |
| `<grn>` | `#66FF00` | Verified matches, start states, positive highlights |
| `<ylw>` | `#FFE066` | Running totals, intermediate pointers, warnings |
| `<red>` | `#FF6B6B` | Mismatches, errors, critical branch paths |
| `<mag>` | `#F472B6` | Special instructions or highlighted registers |
| `<cyn>` | `#22D3EE` | Coordinates, structural markers, secondary values |

## Layout, Spacing & Responsive Breakpoints

The overall shell uses a centred fluid container (`max-width: 1380px`) anchored by a sticky `56px` top header and a three-column reading grid on wide desktop viewports.

### Breakpoint Behaviour

| Breakpoint | Width | Top Header | Left Sidebar (Year / Python Journey) | Centre Column | Right `"On this page"` TOC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mobile** | `< 768px` | Hamburger `☰`, brand wordmark, theme toggle | Hidden; opens as slide-over drawer with backdrop and top links | Full width (`16px` gutter); inline `## Page Navigation` remains visible | Hidden |
| **Tablet** | `768px–1023px` | Hamburger `☰`, compact nav links, theme toggle | Hidden; opens as slide-over drawer | Full width (`24px` gutter); `max-width: 820px` centred | Hidden |
| **Desktop** | `1024px–1199px` | Full horizontal nav (`Home`, `Python Journey`, `Years ▾`, external links, theme toggle) | Visible `256px` sticky column; active group expanded automatically | Fluid column (`1fr`) inside reading card (`32px` padding) | Hidden; inline `## Page Navigation` remains visible |
| **Wide Desktop** | `>= 1200px` | Full horizontal nav + theme toggle | Visible `256px` sticky column | Fluid column (`72ch`–`78ch` inner measure) | Visible `220px` sticky column with scroll-spy; redundant inline `## Page Navigation` hidden via CSS |

## Elevation, Depth & Shapes

Rather than heavy drop shadows that muddy dark surfaces, depth is communicated through surface step-ups, subtle `1px` borders, and selective glassmorphism:

- **Elevation Levels**:
  - **Level 0 (Canvas)**: `#07080D` (Dark) / `#F4F6FA` (Light).
  - **Level 1 (Base Surface)**: `#0F131D` / `#FFFFFF` with `1px solid var(--aoc-border-subtle)` and no heavy shadow.
  - **Level 2 (Interactive Cards / Hover)**: `#161C2B` / `#EEF2F8` with `1px solid var(--aoc-border-strong)`, subtle `translateY(-2px)` lift, and a faint `0 8px 24px rgba(0, 0, 0, 0.25)` shadow.
  - **Level 3 (Sticky Header, Dropdowns & Mobile Drawer)**: `var(--aoc-bg-glass)` with `backdrop-filter: blur(12px)` and `z-index` layering.
- **Corner Radii**:
  - Inline code & `<kbd>`: `4px` (`xs`)
  - Buttons & sidebar items: `6px`–`8px` (`sm`–`md`)
  - Reading cards, code blocks, & hero thumbnails: `12px` (`lg`)
  - Year cards & storefront hero panels: `16px` (`xl`)
  - Concept pills, star badges, & theme toggle pill: `9999px` (`full`)

## Components & Legacy Content Compatibility

### 1. Sticky Top Header & Theme Toggle

- Left: Mobile drawer toggle (`☰`, hidden `>= 1024px`), gold star mark (`★`), and `<span class="brand-accent">Dazbo's</span> Advent of Code` link to `/`.
- Centre: Top-level navigation driven by [`_data/navigation.yaml`](_data/navigation.yaml) (`Home`, `Python Journey`, quick **Years** dropdown covering `2026` back to `2015`) plus external links (`darrenlester.net ↗`, `GitHub ↗`).
- Right: Accessible `<button>` theme toggle (`🌙 Dark` / `☀️ Light`, updating `aria-pressed` and `aria-label`).

### 2. Contextual Left Sidebar & Mobile Drawer

- Driven entirely by [`_data/navigation.yaml`](_data/navigation.yaml) so `25`-day legacy years (`2015`–`2024`) and `12`-day modern years (`2025`+) render automatically with zero hardcoded day lists.
- Uses native HTML `<details>` / `<summary>` groups (accessible and functional even without JavaScript) for **Python Journey** and each **AoC Year**.
- Liquid automatically adds `open` to whichever group matches `page.year` or `page.layout == 'journey-page'`, highlighting the active day or chapter with `--aoc-brand-purple` accent styling.
- On mobile (`< 1024px`), clicking `☰` reveals the sidebar as an off-canvas drawer with Escape-key dismissal, focus management, and backdrop click-to-close.

### 3. Day & Journey Page Headers (`day-page.html` & `journey-page.html`)

- **Metadata Header**: Replaces legacy inline `<img style="float: right; width:330px" />` tags with a responsive flex/grid header slot:
  - Left: Breadcrumb (`Home / 2025 / Day 1`), `<h1>` puzzle/chapter title, AoC external problem badge (`★ Day 1: Secret Entrance ↗`), and GitHub source link (`View solution code ↗`).
  - Right: `page.main_img` rendered inside a framed `16:10` / square card thumbnail (`.page-hero-thumb`, scaling cleanly down to full-width or hidden gracefully when absent).
- **Concept Tags (`page.tags`)**: Preserves full compatibility with all three `aoc-create-doc` frontmatter modes:
  1. **Internal `/python/` link**: Purple-tinted interactive pill (`--aoc-brand-purple`).
  2. **External authoritative link** (`https://...`): Teal-tinted interactive pill (`--aoc-accent-teal`) with external arrow indicator.
  3. **Standalone concept pill** (no `link:` property): Neutral elevated badge (`--aoc-bg-elevated`).

### 4. Prev / Next Navigation Controls

- Top of page: Compact icon/label prev/next bar for rapid sequential browsing.
- Bottom of page: Rich two-column Prev / Next cards displaying the adjacent day number + problem title (or adjacent Python Journey chapter title).

### 5. Landing Page ([`index.md`](index.md)) Storefront Components

- **Hero Banner**: Compact Midnight AoC banner introducing the repo's mission, `uv run aoc` CLI quick-link, and primary actions (`Start Python Journey`, `Browse 2025 Solutions`, `View on GitHub`).
- **Years Showcase Grid**: Responsive card grid driven by [`_data/navigation.yaml`](_data/navigation.yaml) displaying every AoC year, event format (`25 Days / 50 ★` vs `12 Days / 24 ★` from `2025+`), solution format (`Python Scripts` vs `Jupyter Notebooks`), and direct entry links.
- **Python Journey Highlights**: Curated entry cards (`Getting Started`, `Template v3 & CLI`, `Reusable Code`, `Shortest Paths & Graphs`, `Encrypting Inputs`) linking directly into [`python/index.md`](python/index.md).
- **Author & Writing Strip**: Clean cross-links to [darrenlester.net](https://darrenlester.net), [Dev.to](https://dev.to/dazbo), and selected Medium guides without overwhelming the homepage scroll height.

### 6. Historical Content Guardrails (`docs/2015`–`docs/2025` & `docs/python/`)

Historical pages will **not** be bulk-rewritten; instead, CSS rules guarantee clean rendering out of the box:

- **Inline-Styled Pastel Tables**: Legacy tables using inline light backgrounds (e.g. `tr[style*="background"]` with `#ddffdd` or `#dddddd` in `python/perms_combos.md`, or `table[style*="background: white"]` in `python/sets.md` and `2021/8.md`) explicitly force dark ink (`color: #141B29`) inside those cells in Dark mode so contrast never collapses.
- **Wide Table Responsiveness**: Markdown and `.dazbo-table` tables wrap or scroll cleanly (`display: block; overflow-x: auto; max-width: 100%` on mobile, overriding legacy fixed pixel widths like `style="width: 800px"` with `max-width: 100%`).
- **Transparent & Dark-Line Diagrams**: `.png` images inside `.prose` automatically receive a subtle protective mat (`background: #F8FAFC; padding: 6px; border-radius: 8px;`) in Dark mode so legacy transparent-background Matplotlib charts, Graphviz exports, and black mathematical diagrams remain crisp. Hero thumbnails (`.page-hero-thumb`), photos (`.jpg`), and any explicit `.no-mat` asset bypass this mat.
- **Legacy Class Aliases**: `.dazbo-link-button`, `.dazbo-nolink-button`, `.nav-button`, and `.dazbo-table` remain styled to match the Midnight AoC system in case any legacy markdown page references them directly.
- **Right TOC Deduplication**: On wide viewports (`>= 1200px`) where the sticky right `"On this page"` TOC is visible, `site.js` detects the top `## Page Navigation` section + its immediate `<ul>` list and marks it compactly hidden on wide desktop (while keeping it visible below `1200px` and when JS is disabled).

## Jekyll & GitHub Pages Build Architecture

- **Hosting & Build Engine**: Retain **GitHub Pages' managed Jekyll build** (`github-pages ~> 233`, Jekyll `3.10.0`) with `theme:` removed (`null`) in [`_config.yml`](_config.yml) and `jekyll-theme-modernist` replaced by custom templates under `_layouts/`, `_includes/`, and `_sass/`.
- **Offline CI Build Gate**: The `docs-build` job in [`../.github/workflows/pr-checks.yml`](../.github/workflows/pr-checks.yml) runs `bundle exec jekyll build --trace` against `docs/`, catching broken Liquid tags, invalid YAML frontmatter, and SCSS compilation errors before merge.
- **Ruby Sass `3.7.4` (`jekyll-sass-converter 1.5.2`) Compatibility Guardrails**:
  - `github-pages ~> 233` compiles stylesheets with legacy **Ruby Sass `3.7.4`**, not Dart Sass.
  - Always use `@import` partials inside [`assets/css/style.scss`](assets/css/style.scss); **never** use `@use` or `@forward`.
  - Always use comma-separated `rgba(r, g, b, a)` syntax; **never** use CSS Color 4 space/slash syntax (`rgb(15 19 29 / 85%)`), which causes Sass parse failures.
  - Avoid SCSS-evaluated CSS math functions mixing units (`min(100%, 1380px)` or `clamp()` with CSS variables where Sass 3.7 tries to evaluate units); prefer standard `width: 100%; max-width: 1380px;` or `unquote(...)` when needed.

## Commands & Project Structure

### Executable Commands

```bash
# Start live local Jekyll preview (http://127.0.0.1:4000)
make docs

# Rebuild Jekyll Docker image after editing docs/Dockerfile or docs/Gemfile
make docs-build

# Stop local Jekyll container
make docs-stop

# Run offline Jekyll build verification inside the docs container
docker compose -f docs/docker-compose.yml run --rm --no-deps jekyll-aoc bundle exec jekyll build --trace

# Run Python lint, spellcheck, typecheck, and unit tests
make check
```

### Implemented `docs/` Structure

| Path | Role | Status |
| :--- | :--- | :--- |
| [`_config.yml`](_config.yml) | Site metadata, excluded docs (`DESIGN.md`, `readme.md`), default `image:` (`aoc-social-card.png`), Twitter `summary_large_image`, and layout defaults (`theme:` removed) | Implemented (Slice 1A/1E) |
| `DESIGN.md` | Visual design system specification and staged plan (this file) | Implemented (Slice 1A) |
| [`_sass/_tokens.scss`](_sass/_tokens.scss) | Midnight Dark & Daylight Light CSS custom properties | Implemented (Slice 1B) |
| [`_sass/_base.scss`](_sass/_base.scss) | Typography, reset, scrollbars, and accessible focus rings | Implemented (Slice 1B) |
| [`_sass/_layout.scss`](_sass/_layout.scss) | Sticky header, 3-column desktop grid, collapsible sidebar, mobile drawer, and right TOC | Implemented (Slice 1B) |
| [`_sass/_components.scss`](_sass/_components.scss) | Concept pills, prev/next cards, legacy table/image mats, and homepage storefront cards | Implemented (Slice 1B/1D) |
| [`_sass/_syntax.scss`](_sass/_syntax.scss) | Always-dark `#131722` Rouge syntax theme, copy toolbar, and `<grn>`/`<ylw>`/`<red>`/`<mag>`/`<cyn>` tags | Implemented (Slice 1B) |
| [`assets/css/style.scss`](assets/css/style.scss) | Sass entrypoint importing partials via `@import` | Implemented (Slice 1B) |
| [`_includes/head-custom.html`](_includes/head-custom.html) | Zero-FOUC theme bootstrap script, Google Fonts (`Inter` + `JetBrains Mono`), MathJax v3, favicons, and `theme-color` | Implemented (Slice 1C/1E) |
| [`_includes/header.html`](_includes/header.html) | Sticky top bar, Year switcher dropdown, external links, and Dark/Light toggle | Implemented (Slice 1C) |
| [`_includes/sidebar.html`](_includes/sidebar.html) | Collapsible `<details>` navigation built from [`_data/navigation.yaml`](_data/navigation.yaml) | Implemented (Slice 1C) |
| [`_includes/toc.html`](_includes/toc.html) | Desktop sticky `"On this page"` container populated cleanly by `site.js` | Implemented (Slice 1C) |
| [`_includes/footer.html`](_includes/footer.html) | Branded footer linking to GitHub, [darrenlester.net](https://darrenlester.net), Medium, and Dev.to | Implemented (Slice 1C) |
| [`assets/js/site.js`](assets/js/site.js) | Vanilla JS (~3 KB) for theme persistence, mobile drawer, right TOC scroll-spy, and copy-code buttons | Implemented (Slice 1C) |
| [`_layouts/default.html`](_layouts/default.html), [`_layouts/day-page.html`](_layouts/day-page.html), [`_layouts/journey-page.html`](_layouts/journey-page.html), [`404.html`](404.html) | Redesigned core Jekyll layouts preserving all existing YAML frontmatter contracts | Implemented (Slice 1C) |
| [`assets/images/aoc-hero-banner.png`](assets/images/aoc-hero-banner.png), [`assets/images/aoc-social-card.png`](assets/images/aoc-social-card.png), & [`site.webmanifest`](site.webmanifest) | Hero circuit-tree artwork, `1200x630` OpenGraph card, updated PWA manifest, and full favicon icon suite (`favicon.ico`, `16x16`, `32x32`, `apple-touch-icon.png`, `192x192`, `512x512`) | Implemented (Slice 1E) |
| [`index.md`](index.md) & [`../README.md`](../README.md) | Overhauled Jekyll homepage storefront and refreshed root repository README + live screenshot ([`AoC_site_screenshot.jpg`](assets/images/AoC_site_screenshot.jpg)) | Implemented (Slice 1D/1E) |

## Operational Boundaries

- **Always Do**: Keep YAML frontmatter contracts backwards-compatible with [`aoc-create-doc`](../.agents/skills/aoc-create-doc/SKILL.md) and historical pages (`main_img`, all 3 `tags:` modes, `mathjax: true`); run `make check` and Jekyll build verification after edits; preserve WCAG AA contrast across Dark and Light modes.
- **Ask First**: Adding any new Ruby gems to [`Gemfile`](Gemfile) or Jekyll plugins to [`_config.yml`](_config.yml); changing deployment from GitHub Pages' managed build to GitHub Actions Pages; deleting existing image assets; or running `git commit` / `git push`.
- **Never Do**: Bulk-rewrite prose across historical `docs/2015/`–`docs/2025/` pages; introduce single-`$` MathJax delimiters, `mermaid` blocks, or ASCII diagrams; use Dart Sass `@use` or CSS Color 4 slash syntax unsupported by Ruby Sass `3.7.4`; or embed absolute local file URIs in documentation.

## Do's and Don'ts

| Do | Don't |
| :--- | :--- |
| Use semantic `--aoc-*` CSS variables everywhere so Dark/Light switching stays consistent | Hardcode hex backgrounds or text colours directly on component elements (except the constant dark code theme and explicit legacy table overrides) |
| Use `width: 100%; max-width: ...` and `overflow-x: auto` on wide tables and code blocks | Leave fixed `800px` table widths or negative `-60px` code margins that cause horizontal scroll on mobile |
| Keep code blocks dark (`#131722`) across both themes so `<grn>`/`<ylw>` tags remain readable | Switch code blocks to white backgrounds where neon terminal tags lose contrast |
| Use subtle `1px` borders and surface contrast to separate panels | Overuse heavy drop shadows, neon glows, or rounded-full pills on multi-line prose containers |

## Development CLI UX

Visual consistency extends to the companion Python CLI (`uv run aoc`), which uses `Rich` panels, OSC 8 clickable terminal hyperlinks, and `stdout` JSON isolation (`--json` mode routes Rich logs to `stderr`) — matching the site's dark-first terminal aesthetic and structured tabular presentation.

## Staged Implementation Plan & Acceptance Criteria

### Delivery Slices

| Slice | Scope | Status | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **1A** | Design Specification & Jekyll Exclusion | Complete | [`docs/DESIGN.md`](DESIGN.md) approved; `DESIGN.md` excluded in [`_config.yml`](_config.yml) |
| **1B** | Design System SCSS & CI Build Gate | Complete | `_sass/` partials (`_tokens`, `_base`, `_layout`, `_components`, `_syntax`), refactored [`assets/css/style.scss`](assets/css/style.scss), legacy theme removal, and `jekyll build` check in [`../.github/workflows/pr-checks.yml`](../.github/workflows/pr-checks.yml) |
| **1C** | Layouts, Navigation, Theme Toggle & Copy-Code | Complete | Redesigned [`_layouts/default.html`](_layouts/default.html), [`_layouts/day-page.html`](_layouts/day-page.html), [`_layouts/journey-page.html`](_layouts/journey-page.html), `_includes/`, `404.html`, and `assets/js/site.js`; local verification via `make docs` + browser inspection across Dark/Light & Mobile/Desktop |
| **1D** | Storefront & Core Docs Overhaul | Complete | Overhauled [`index.md`](index.md), refreshed [`../README.md`](../README.md), and synchronised [`readme.md`](readme.md) / [`../AGENTS.md`](../AGENTS.md) / [`../TODO.md`](../TODO.md) |
| **1E** | Brand Artwork & Screenshot Refresh | Complete | Updated banner artwork, favicon set, `og:image` social preview, and fresh site screenshot in `docs/assets/images/` linked from [`../README.md`](../README.md) |

### Acceptance Criteria (`B1`–`B8`)

| ID | Criterion | Verification Method |
| :--- | :--- | :--- |
| `B1` | Jekyll builds cleanly with zero Ruby Sass `3.7.4` or Liquid warnings | `bundle exec jekyll build --trace` exits `0` |
| `B2` | Zero FOUC and persisted Dark/Light toggle (`localStorage` key `aoc-theme`) | Browser test across reload and navigation between pages |
| `B3` | All 3 `day-page.html` `tags:` modes, `main_img`, and `mathjax: true` render accurately | Inspect `/2025/1`, `/2022/1`, and `/python/perms_combos` |
| `B4` | Legacy `<grn>`/`<ylw>`/`<red>` tags, `#ddffdd` pastel table rows, and transparent PNG plots remain high-contrast in both modes | Visual inspection of `/2015/20`, `/2021/24`, `/python/perms_combos`, and `/python/visualisation` |
| `B5` | Mobile (`375px`) layout has zero horizontal page overflow and working slide-over drawer | Browser DevTools responsive audit at `375px`, `768px`, `1024px`, `1440px` |
| `B6` | Code blocks include accessible Copy buttons with live confirmation | Interactive test on code block in browser |
| `B7` | Right `"On this page"` TOC tracks headings cleanly and hides duplicate inline `## Page Navigation` on `>= 1200px` | Browser inspection at `1280px+` and `768px` |
| `B8` | Offline Python gates remain green | `make check` (`codespell -s`, `ruff check`, `pyright`, `pytest src/tests`) passes |
