# Error Handling Patterns in RED-AI

## Graceful Degradation

RED-AI is designed to degrade gracefully at every layer:

### AI Engine Fallback Chain
```
1. match_local_command(prompt)   -> instant offline match
2. _call_ollama(prompt)          -> local LLM (may be unavailable)
3. return {"error": "..."}       -> helpful error message with guidance
```
Never crash on Ollama failure. The bare `except Exception: pass` in `get_ai_response()` is intentional -- the user gets the error dict with installation instructions.

### System Info Collection
```python
# Each probe fails independently -- partial info is still useful
try:
    info["selinux"] = ...
except (FileNotFoundError, subprocess.TimeoutExpired):
    info["selinux"] = "unknown"  # safe default, not a crash
```

### Logging Failures
```python
# Log write failures must never interrupt the user's workflow
try:
    with open(LOG_FILE, "a") as f:
        f.write(entry)
except PermissionError:
    pass  # intentional: non-root dry-run can't write to /var/log
```

## User-Friendly Error Messages

### Do
```python
print(color("Error: RED-AI must be run as root for execution mode.", "red"))
print("Use --dry-run to preview commands without root, or run as root.")
```

### Do Not
```python
# Never expose tracebacks or internal details to users
print("OSError: [Errno 13] Permission denied: '/var/log/red-ai/executions.log'")
```

### Pattern for External Failures
```python
return {
    "error": "No matching command found. Install Ollama "
             "(https://ollama.ai) for full AI mode, or try "
             "rephrasing your request."
}
```
Always tell the user (1) what went wrong, (2) what they can do about it.

## Logging Best Practices

### What to Log
- Timestamp, user, hostname, mode (dry-run vs executed)
- Full command list with per-command status (success/failed/timeout)
- Risk level and source (local_commands vs ollama)

### What Not to Log
- Passwords or tokens from command output
- Full tracebacks (use structured error messages instead)
- Redundant entries (check for duplicates on rapid re-execution)

### Log Rotation
`logger.py` implements simple rotation: when `executions.log` exceeds 5MB, it shifts to `.1`, `.2`, `.3` and deletes the oldest. No external dependency on logrotate.

## Recovery Strategies

### Subprocess Timeout Recovery
```python
try:
    result = subprocess.run(cmd, shell=True, timeout=120, ...)
except subprocess.TimeoutExpired:
    results.append({"command": cmd, "status": "timeout", "output": ""})
    # Continue with remaining commands, don't abort the batch
```

### Partial Execution Tracking
When multiple commands are executed sequentially, each result is recorded independently. If command 2 of 5 fails, commands 3-5 still execute and all results are logged.

### Handling Corrupt Log Files
`read_history()` splits on separator lines. If the file is corrupted:
```python
parts = content.split("=" * 70)
# Malformed entries are silently skipped -- no crash on corrupt logs
```

## Anti-Patterns to Avoid

```python
# BAD: bare except hides bugs during development
try:
    complex_operation()
except:
    pass

# GOOD: catch specific exceptions
try:
    complex_operation()
except (ValueError, KeyError) as e:
    logger.warning("Operation failed: %s", e)

# EXCEPTION: get_ai_response() uses bare except intentionally
# for the Ollama fallback -- this is documented and deliberate
```

```python
# BAD: sys.exit() deep in a function
def helper():
    if error:
        sys.exit(1)  # makes testing impossible

# GOOD: return error state, let main() handle exit
def helper():
    if error:
        return None  # caller decides what to do
```
