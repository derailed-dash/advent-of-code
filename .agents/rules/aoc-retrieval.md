---
trigger: model_decision
description: Apply whenever fetching Advent of Code puzzle descriptions, sample inputs, or user-specific puzzle inputs from adventofcode.com, or when updating, refreshing, or troubleshooting AOC_SESSION_COOKIE (including HTTP 400/401/403/500 errors).
---

# AoC Puzzle Description, Sample & Input Retrieval

When Dazbo asks to fetch a puzzle, description, sample input, or puzzle input (e.g. *"fetch the sample for day 7"*), or to refresh his AoC session cookie, follow this workflow using [`aoc fetch`](../../src/aoc_common/cli.py) cleanly rather than ad-hoc HTML downloads.

## 1. Resolve Year & Day

- **Check active file first**: If year is omitted (e.g. *"day 7"*), inspect any currently open file path under `src/AoC_<year>/` or `docs/<year>/` and pass an explicit target such as `<year> <day>` (`2018 7`) or compact shorthand (`2018d07`, `201807`) so historical years resolve unambiguously.
- **CLI fallback**: Otherwise pass `<day>` shorthand (resolves `AOC_YEAR` -> current year if `src/AoC_<year>` exists -> latest `src/AoC_<year>` on disk).
- Default to Part 1 unless Part 2 is requested (Part 2 unlocks on AoC only after Part 1 is solved and requires a valid `AOC_SESSION_COOKIE`).

## 2. Single-Call Fetch (Never Blindly Pass `--write-sample` from an Agent)

```bash
uv run --no-sync aoc fetch <target> --desc-only --json    # Description + ranked <pre><code> sample candidates (works anonymously for Part 1)
uv run --no-sync aoc fetch <target> --json                # Same, plus caches input/input.txt (requires valid AOC_SESSION_COOKIE)
uv run --no-sync aoc fetch <target> --input-only --json   # Caches input/input.txt only (0 HTTP calls if already cached; use when description/samples are already in context)
```

- **Sandbox & network**: Live `aoc fetch` HTTP requests to `adventofcode.com` require `BypassSandbox: true` (standard sandbox blocks outbound HTTPS), whereas local `write_file`, `aoc list`, `aoc run -s`, and `git-crypt-helper.sh` run sandboxed (`BypassSandbox: false`).
- **Check `"authenticated"` when Part 2 is `null`**: Unlike `/<year>/day/<day>/input` (which fails with HTTP `400`/`500` on an invalid cookie), `GET /<year>/day/<day>` returns HTTP `200` even with a missing or expired cookie — silently omitting Part 2 (`"authenticated": false`, `"part2_markdown": null`). Whenever Part 2 is requested and `part2_markdown` is `null`, check `authenticated`: `false` means `AOC_SESSION_COOKIE` is missing or expired; `true` means Part 1 is not yet solved on AoC.
- **No `desc.html` temp files**: `aoc fetch` (`fetch_puzzle_page` / `parse_puzzle_html`) converts AoC HTML to clean Markdown and numbered `<pre><code>` blocks in memory. Never persist raw `desc.html` downloads on disk.
- **No secret input leakage**: `--json` reports metadata only (`path`, `action`, `exists`) for `input/input.txt` and never prints raw input data.
- *(Note: `make fetch <target> [ARGS="--write-sample --desc-only"]` exists for human terminal convenience, but agents should never pass `--write-sample` blindly.)*

## 3. Semantic Sample & Expected-Answer Verification

- Read `part1_markdown` (or `part2_markdown`) alongside `samples[]` (`score` is only a heuristic hint).
- Distinguish the **actual puzzle sample input** from rule-illustration diagrams, step-by-step simulation traces, or example output blocks.
- **Inline examples (no `<pre>` block)**: If a puzzle lists short one-line examples inline inside `<code>` tags instead of a `<pre>` block, extract those sample strings and their expected answers directly from the Markdown prose (suited to `PART1_SAMPLES = [("inline", expected), ...]` in Template v3).
- Identify the **expected sample answer(s)** stated in the prose.

## 4. Write Sample Locally (`write_file` — Zero Extra HTTP Calls)

- **Do NOT run `aoc fetch --write-sample` a second time** just to write text you already hold in memory.
- **Part 2 sample reuse**: Most AoC Part 2 descriptions reuse Part 1's sample input with a new expected answer (matching [`src/template_folder/template.py`](../../src/template_folder/template.py), where `PART2_SAMPLES` defaults to `sample_input_part_1.txt`). Only create `sample_input_part_2.txt` (and update `PART2_SAMPLES`) when Part 2 introduces a genuinely distinct sample input.
- **Preserve significant whitespace**: Keep **exact leading and trailing spaces** on every line (critical for column-aligned puzzles such as crate stacks or ASCII maps) and end the file with a single `\n`.
- Write the verified sample input directly via `write_file` to `src/AoC_{year}/d{nn}/input/sample_input_part_{part}.txt` (matching any existing `d{nn}_<slug>` folder on disk):
  - **Missing or `0`-byte placeholder** (created by `aoc new-year`): write immediately without asking.
  - **Non-empty with different content**: show the extracted sample and ask Dazbo before overwriting.
- Report the saved file path and the expected sample answer(s) found in the prose. If `d{nn}.py` is a Template v3 script with `None` in `PART1_SAMPLES` / `PART2_SAMPLES`, offer to wire the expected answer — **do not implement solver logic unless asked**.

## Session Cookie (`AOC_SESSION_COOKIE`) & Guardrails

- **User-Agent**: `github.com/derailed-dash/Advent-of-Code by derailed.dash@gmail.com` (`ac.AOC_USER_AGENT`, enforced automatically).
- **Cookie lookup**: `ac.get_aoc_session_cookie` reads `AOC_SESSION_COOKIE` lazily from the environment or `.env`, stripping whitespace and surrounding quotes.
- **Refreshing an expired cookie (~30-day lifetime)**:
  - **Automated via `browser` subagent (preferred in Antigravity)**: Although AoC's `session` cookie is `HttpOnly` (hidden from `document.cookie`), delegate to the `browser` subagent to open or reload `https://adventofcode.com` (if `[Log In]` is visible, navigate to `https://adventofcode.com/auth/login` and pause for Dazbo to sign in), extract `session=<hex>` from the outgoing `cookie:` request header via `list_network_requests` -> `get_network_request`, update `AOC_SESSION_COOKIE` in `.env` **without echoing the raw token in chat**, and sync `.env.enc`:
    ```bash
    git-crypt-helper.sh sync-to-enc .env
    ```
  - **Manual fallback**: Log in at `https://adventofcode.com`, copy the `session` cookie value from **Chrome DevTools -> Application -> Cookies**, update `.env`, and run `git-crypt-helper.sh sync-to-enc .env`.
- **Never submit answers**: Never automate answer submissions to `adventofcode.com`.
- **No real data in docs**: Never include real `input.txt` contents or real puzzle answers in walkthroughs or docs.
