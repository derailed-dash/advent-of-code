---
title: Logging in Python
description: How Python's standard logging module works — severity levels, formatters, file handlers with Path, lazy formatting — and how modern AoC solutions configure RichHandler via aoc_common.setup_logging.
---
## Why `logging` Beats `print()`

During early debugging it is tempting to scatter `print()` statements everywhere. Once a script grows — or when you need clean machine-readable CLI output (`--json`), selective verbosity (`--debug`), or persistent file output — `print()` quickly becomes painful to strip back out.

Python's built-in [`logging`](https://docs.python.org/3/library/logging.html) module separates **emitting messages** from **deciding how and where they appear**.

---

## Standard Log Levels

Each log record carries a severity level so callers can filter out noise at runtime without touching code:

| Level | Numeric Value | Typical Use in AoC |
| :--- | :---: | :--- |
| `DEBUG` | `10` | Detailed grid dumps, BFS frontier states, per-iteration trace (`-d` / `--debug`) |
| `INFO` | `20` | High-level progress, sample verification results, final answers |
| `WARNING` | `30` | Unexpected input quirks, locked `git-crypt` fallback hints, slow thresholds |
| `ERROR` | `40` | Missing input file, invalid CLI arguments, non-fatal failure |
| `CRITICAL` | `50` | Unrecoverable error terminating execution |

*(Note: legacy code occasionally uses `logging.WARN` as an alias for `logging.WARNING`, but `logging.WARNING` is the canonical name.)*

---

## Named Loggers & Formatters

Instead of mutating the root logger blindly from every module, create a module-scoped logger with `logging.getLogger(__name__)`. That externalises control to your script entrypoint or test runner, while still carrying the exact module hierarchy (`aoc_common.runner`, `__main__`, etc.) in every message.

Two modern best practices make standard logging clean and fast:

1. **Lazy `%`-formatting**: Pass arguments separately (`logger.debug("Visited %d states", len(seen))`) rather than eager f-strings. If `DEBUG` is disabled, Python skips formatting its value entirely!
2. **`pathlib.Path` with `encoding="utf-8"`**: Always specify `encoding="utf-8"` when writing log files so Unicode symbols or box characters never break across platforms.

```python
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def configure_basic_logging(log_file: Path | None = None, *, verbose: bool = False) -> None:
    """Configure standard console and optional file logging."""
    level = logging.DEBUG if verbose else logging.INFO
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers, force=True)
```

Notice `force=True` on `logging.basicConfig`: if a Jupyter notebook or another library already attached a handler, `force=True` cleanly replaces stale handlers instead of printing duplicate lines.

---

## Modern Logging in AoC with `Rich` and `aoc_common`

Rather than writing custom ANSI formatter subclasses (`ColouredFormatter`) by hand, modern scripts in this repository delegate terminal formatting to `Rich` via [`aoc_common`](/python/reusable_code):

```python
import logging
import aoc_common as ac

ac.setup_logging(logging.DEBUG)  # Attaches RichHandler with colourised levels & tracebacks
logger = logging.getLogger(__name__)
logger.info("Sample checks passed")
logger.debug("Grid dimensions: %dx%d", 140, 140)
```

### Automatic CLI & `--json` Support

When you run a puzzle through [Template v3](/python/my-aoc-template3) or `uv run aoc run`:

- Default runs call `ac.setup_logging(logging.INFO)`, keeping normal puzzle runs crisp and uncluttered.
- Passing `-d` or `--debug` switches `setup_logging` to `logging.DEBUG` automatically so you can inspect internal state without editing source code.
- Passing `--json` sets `stderr=True` (`ac.setup_logging(..., stderr=True)`), routing diagnostic logs to `stderr` so `stdout` emits pure, parseable JSON for automation and benchmarking scripts.
- Passing `ac.setup_file_logging(logger, folder)` adds a UTF-8 log file alongside terminal output whenever you want to inspect huge trace logs in an editor.

For full styling controls (`Console`, markup, `Table`), see [Terminal Colours & Rich](/python/colours).
