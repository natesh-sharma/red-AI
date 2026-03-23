# Code Review Patterns for RED-AI

## What to Check

### Safety Verification (Priority 1)
- Every command list must have a `risk_level` ("low", "medium", "high")
- Commands that modify system state must support `--dry-run`
- Root check (`os.geteuid() != 0`) must gate execution mode, never dry-run
- `subprocess.run()` calls must include `timeout` to prevent hangs
- No user input is passed unsanitized into shell commands

### Response Format Integrity
- All response dicts must include: `commands`, `description`, `category`, `risk_level`, `requires_reboot`, `notes`
- `commands` must be a list of strings, never a single string
- `source` field must be "local_commands" or "ollama"

### Python 3.6 Compatibility
- No f-strings with `=` (debug format) -- added in 3.8
- No walrus operator (`:=`) -- added in 3.8
- No `dict | dict` merge syntax -- added in 3.9
- Use `"{}".format(x)` in local_commands.py for consistency (f-strings OK in cli.py)

## Common Issues

### Shell Injection in executor.py
The executor uses `shell=True`. Verify that commands come only from trusted sources (local_commands.py or parsed Ollama JSON), never from raw user input.

```python
# BAD: user input flows into shell command
cmd = "echo {}".format(user_input)
subprocess.run(cmd, shell=True)

# OK: command comes from curated LOCAL_COMMANDS list
for cmd in response["commands"]:  # from local_commands.py
    subprocess.run(cmd, shell=True, timeout=120)
```

### Missing Timeout on subprocess
Every `subprocess.run()` call must have a `timeout` parameter:
```python
# BAD
result = subprocess.run(["systemctl", "status", "sshd"], stdout=subprocess.PIPE)

# GOOD
result = subprocess.run(
    ["systemctl", "status", "sshd"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    universal_newlines=True, timeout=5,
)
```

### Keyword Overlap in local_commands.py
When adding new entries to `LOCAL_COMMANDS`, check for keyword collisions with existing entries. The scoring system can return wrong matches when keywords overlap:
```python
# These would conflict -- "enable" + "firewall" appear in both
{"keywords": ["enable", "firewall", "logging"], ...}
{"keywords": ["enable", "firewall"], ...}
```
Add distinguishing keywords or increase specificity.

## Review Checklist
- [ ] No hardcoded paths except well-known system paths (`/etc/`, `/sys/`, `/proc/`)
- [ ] Error handling uses try/except, never bare `except:`
- [ ] Log file operations handle `PermissionError` and `IOError`
- [ ] New local_commands entries have accurate `risk_level` values
- [ ] All `subprocess.run()` calls capture both stdout and stderr
- [ ] Functions under 50 lines, files focused on single responsibility
