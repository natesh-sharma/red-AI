# Refactoring Patterns for RED-AI

## Key Refactoring Target: local_commands.py

At ~2200 lines, `local_commands.py` is the largest file. It contains the `LOCAL_COMMANDS` list (230+ entries) plus matching logic. Refactoring strategies:

### Extract Matching Logic
Separate the data from the algorithm:
```
local_commands.py      -> command_database.py  (LOCAL_COMMANDS data only)
                       -> command_matcher.py   (match_local_command, _expand_prompt, _match_sysctl)
```

### Split Command Categories
Group LOCAL_COMMANDS entries by category into separate modules:
```
commands/
    __init__.py         # aggregates all commands
    kernel.py           # kernel, sysctl, modules
    network.py          # firewall, DNS, NIC
    storage.py          # LVM, filesystem, mount
    security.py         # SELinux, audit, crypto
    services.py         # systemd, cron, NTP
    packages.py         # yum, rpm, subscription
```

Each module exports a list; `__init__.py` merges them:
```python
# commands/__init__.py
from .kernel import KERNEL_COMMANDS
from .network import NETWORK_COMMANDS
# ...
ALL_COMMANDS = KERNEL_COMMANDS + NETWORK_COMMANDS + ...
```

## Extracting Functions

### Repeated Subprocess Patterns
`cli.py` and `system_info.py` repeat the same subprocess call pattern:
```python
# Extract this into a helper
def run_cmd(args, timeout=5):
    """Run a command and return (returncode, stdout). Never raises."""
    try:
        result = subprocess.run(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=timeout,
        )
        return result.returncode, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return -1, ""
```

### Response Dict Construction
Multiple places build response dicts with the same keys. Extract a factory:
```python
def make_response(description, commands, category="system",
                  risk_level="medium", requires_reboot=False, notes=""):
    return {
        "description": description,
        "category": category,
        "commands": commands,
        "risk_level": risk_level,
        "requires_reboot": requires_reboot,
        "notes": notes,
    }
```

## Simplifying Conditionals

### Nested if/else in cli.py main()
The sysctl action handler in `main()` has deep nesting. Extract to a function:
```python
# Before: 40+ lines of if/elif/else in main()
# After:
def _handle_sysctl_action(param):
    """Prompt user and return response dict for sysctl parameter."""
    action = prompt_choice(...)
    ...
    return response
```

### Keyword Matching Scoring
The scoring loop in `match_local_command` mixes matching, weighting, and boosting. Split into:
1. `_compute_keyword_score(keywords, prompt_words, expanded_words)`
2. `_apply_context_boosts(score, cmd, prompt_lower)`
3. `_select_best_match(candidates)`

## Safe Refactoring Process
1. Write tests for current behavior first (test_local_commands.py)
2. Extract function, keeping original as a thin wrapper
3. Run tests to verify identical behavior
4. Remove wrapper once tests pass
5. Keep Python 3.6 compatible -- no dataclasses, no typing.Protocol
