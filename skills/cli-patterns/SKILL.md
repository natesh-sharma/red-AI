# CLI Design Patterns in RED-AI

## Argparse Usage
RED-AI uses `argparse` in `cli.py` with positional + optional arguments:
```python
parser = argparse.ArgumentParser(prog="red-ai")
parser.add_argument("prompt", nargs="*", help="Request in plain English")
parser.add_argument("-d", "--dry-run", action="store_true")
parser.add_argument("-y", "--yes", action="store_true")
parser.add_argument("-v", "--version", action="store_true")
parser.add_argument("-i", "--info", action="store_true")
parser.add_argument("--history", nargs="?", const=10, type=int, metavar="N")
```

Key patterns:
- `nargs="*"` lets users type prompts without quotes: `red-ai disable transparent hugepages`
- `nargs="?"` with `const=10` makes `--history` optional with a default count
- Boolean flags use `action="store_true"` (no arguments needed)

## Exit Codes
```python
def main():
    # Success
    return 0

    # User error (no prompt, invalid input)
    return 1

    # Applies throughout:
    # 0 = success or dry-run completed
    # 1 = error, cancelled, or missing input
```

Always `return` from `main()`, never `sys.exit()` mid-function. The `entry_point()` wrapper handles the exit:
```python
def entry_point():
    sys.exit(main())
```

## Colored Output
`executor.py` defines ANSI color helpers used throughout the CLI:
```python
COLORS = {
    "red": "\033[1;31m",    # Errors, failures, high-risk warnings
    "green": "\033[1;32m",  # Success, PASS indicators
    "yellow": "\033[1;33m", # Warnings, dry-run messages, prompts
    "blue": "\033[1;34m",   # Info headers, processing messages
    "cyan": "\033[1;36m",   # Decorative separators, choice numbers
}

def color(text, c):
    return "{}{}{}".format(COLORS.get(c, ""), text, COLORS["reset"])
```

Convention: use `color()` for all terminal output, never raw ANSI codes inline.

## Interactive Prompts

### Confirmation (yes/no)
```python
def confirm(message):
    response = input(color("{} (yes/no): ".format(message), "yellow"))
    return response.strip().lower() in ("yes", "y")
```

### Numbered Choice Menu
```python
def prompt_choice(message, options):
    # Displays numbered list, returns selected option's "value"
    # Default is first option if user presses Enter
```

Both handle `EOFError` and `KeyboardInterrupt` for piped input and Ctrl+C.

## Signal Handling
Currently, RED-AI relies on Python's default signal handling:
- `KeyboardInterrupt` (Ctrl+C) is caught in `confirm()` and `prompt_choice()`
- `subprocess.run()` with `timeout` prevents hung child processes

When adding new interactive features, always wrap `input()` calls:
```python
try:
    value = input(color("Enter value: ", "yellow")).strip()
except (EOFError, KeyboardInterrupt):
    print()
    return 1  # or a sensible default
```

## Output Formatting
Execution results use a consistent layout:
```
============================================================    # cyan
  Description of operation                                      # cyan
============================================================    # cyan
Risk Level: medium                                              # blue
Commands to execute:                                            # blue
  1. command-one
  2. command-two
[DRY RUN MODE - Commands will not be executed]                  # yellow
```

Use `sys.stdout.flush()` after printing status lines to ensure immediate display during command execution.
