# Security Audit Checklist for RED-AI

## Secrets Scanning

RED-AI should never contain hardcoded credentials. Audit targets:
- `ai_engine.py` -- Ollama URL is `localhost:11434`; verify no API keys are embedded
- `logger.py` -- log entries must not record passwords or tokens from command output
- `Modelfile` -- training examples must use placeholder values, never real credentials

```python
# BAD: hardcoded token
headers = {"Authorization": "Bearer sk-abc123..."}

# GOOD: RED-AI uses no auth (local Ollama only)
headers = {"Content-Type": "application/json"}
```

## Command Injection Prevention

### The Critical Path
User input flows: `prompt` -> `match_local_command()` or `_call_ollama()` -> `execute_commands()` -> `subprocess.run(cmd, shell=True)`

Since `shell=True` is used, audit these injection surfaces:
1. **local_commands.py** -- commands are static strings in `LOCAL_COMMANDS`. Safe by design.
2. **Ollama responses** -- JSON-parsed commands from LLM output. The LLM could return malicious commands. Mitigation: user sees and confirms every command before execution.
3. **sysctl handler** -- user-supplied values flow into `sysctl -w param=value`. Validate format:

```python
# Validate sysctl parameter names (alphanumeric + dots only)
import re
if not re.match(r'^[\w.:-]+$', param):
    raise ValueError("Invalid sysctl parameter: {}".format(param))
```

## Input Validation

### Prompt Input
- `cli.py` joins `args.prompt` with spaces -- no shell expansion risk here
- Prompt is passed to keyword matching (string comparison only) and Ollama HTTP body (JSON-encoded)

### Choice/Confirmation Inputs
- `confirm()` only checks for "yes"/"y" -- safe, no injection vector
- `prompt_choice()` uses `int()` conversion with try/except -- safe

## Privilege Escalation Risks
- Root check in `cli.py` uses `os.geteuid()` -- correct for RHEL
- Dry-run mode must never call `subprocess.run()` with real commands
- Log directory `/var/log/red-ai/` must be root-owned (0700 or 0750)
- RPM spec creates log dir at install time -- verify permissions in `%files`

## Audit Procedure
1. Search for `subprocess.run` -- verify every call has `timeout`
2. Search for `shell=True` -- verify command source is trusted
3. Search for `open(` in write mode -- verify path is not user-controlled
4. Search for `input(` -- verify return value is validated
5. Grep for common secrets patterns: `password`, `token`, `secret`, `key`
6. Verify Ollama responses are JSON-parsed, not eval'd

## RHEL-Specific Security
- Commands writing to `/etc/sysctl.d/` must use safe filenames (no path traversal)
- SELinux context must be preserved when creating config files
- `grubby` commands modify boot config -- always `risk_level: "medium"` or higher
- Firewall changes must be flagged as `risk_level: "high"`
