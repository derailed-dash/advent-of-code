---
title: Terminal Colours & Rich Styling
description: How ANSI escape sequences work in Python terminals using StrEnum, why colorama was retired to legacy extras, and how modern AoC solutions render styled output, tables, and logs with Rich.
---
## Why Style Terminal Output?

Good terminal output makes debugging faster: errors stand out immediately, sample pass/fail badges pop at a glance, and dense grid traces stay readable. Understanding both the low-level **ANSI escape codes** and modern high-level libraries like **[`Rich`](https://rich.readthedocs.io/)** explains how Python formats colour cleanly across operating systems.

![ANSI Console Output](/assets/images/ansi-console-output.png)

---

## ANSI Escape Codes & `StrEnum`

Terminals interpret special character sequences beginning with the ESC byte (`\x1b`, octal `\033`) as formatting instructions rather than literal text — known as **ANSI escape codes**.

For example:

```text
\x1b[31mRed Text\x1b[0m
```

- `\x1b[` introduces a Control Sequence Introducer (CSI).
- `31m` sets foreground colour to red.
- `\x1b[0m` resets all attributes back to terminal defaults so colour does not bleed onto subsequent lines.

![Terminal Colour Table](/assets/images/term_colors.png)

Since Python 3.11, [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum) lets you model raw ANSI sequences cleanly as strings with zero third-party dependencies:

```python
from enum import StrEnum


class Ansi(StrEnum):
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    CYAN = "\x1b[36m"


def paint(text: str, *styles: Ansi) -> str:
    """Wrap text with one or more ANSI sequences and reset afterward."""
    prefix = "".join(styles)
    return f"{prefix}{text}{Ansi.RESET}"


if __name__ == "__main__":
    print(paint("Part 1 solved!", Ansi.BOLD, Ansi.GREEN))
    print(paint("Check bounds carefully", Ansi.YELLOW))
```

### What Happened to `colorama`?

Historically, Windows `cmd.exe` did not interpret ANSI escape codes natively, so older Python code (and earlier AoC chapters in this repository) relied on `colorama.init(autoreset=True)` plus hand-rolled `ColouredFormatter` classes.

Modern Windows Terminal, PowerShell, Linux, and macOS consoles support ANSI natively, and `Rich` handles terminal capability detection automatically (stripping colour cleanly when output is piped to a file or `--json` is used). Consequently, `colorama` is no longer part of core AoC dependencies — it remains strictly inside the optional `legacy` extra in [`pyproject.toml`](https://github.com/derailed-dash/Advent-of-Code/blob/master/pyproject.toml) so untouched 2015–2024 scripts stay runnable.

---

## Modern Terminal Styling with `Rich`

For anything beyond tiny scripts, **Rich** is the standard toolkit across this repository (managed with `uv add rich`). It provides intuitive markup, layout tables, live progress bars, pretty tracebacks, and log formatting out of the box.

![Coloured Console Output](/assets/images/coloured_console_ouput.png)

### 1. Styled Console Output & Markup

`rich.console.Console` accepts lightweight BBCode-style tags such as `[bold green]...[/]` and automatically adapts to terminal width and colour depth:

```python
from rich.console import Console

console = Console()
console.print("[bold cyan]Advent of Code 2025[/] — [green]All samples passed![/]")
console.print("Elapsed:", "[yellow]14.2 ms[/]", highlight=False)
```

### 2. Structured Summary Tables (`rich.table.Table`)

When comparing Part 1 vs Part 2 answers and timings — just like `uv run aoc run` and [Template v3](/python/my-aoc-template3) — `Table` renders crisp aligned columns without brittle manual whitespace padding:

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Day 7 Results")
table.add_column("Part", style="cyan", no_wrap=True)
table.add_column("Answer", justify="right", style="bold green")
table.add_column("Duration", justify="right", style="magenta")

table.add_row("Part 1", "1689", "3.4 ms")
table.add_row("Part 2", "729376744", "18.1 ms")

console.print(table)
```

### 3. Coloured Logs (`RichHandler`)

In [Logging in Python](/python/logging) and [`aoc_common`](/python/reusable_code), `ac.setup_logging()` wires `rich.logging.RichHandler` directly into Python's standard `logging` module — giving you colourised severity badges, clean timestamps, clickable source locations, and readable exception tracebacks without maintaining custom formatter classes.
