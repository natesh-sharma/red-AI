# Debugging RED-AI

## Common Issues

### "No matching command found" When Command Exists
The keyword matcher in `local_commands.py` requires sufficient keyword overlap. Debug steps:
1. Check what `_expand_prompt()` produces for the user's input
2. Verify the LOCAL_COMMANDS entry has matching keywords
3. Check if another entry scores higher due to keyword overlap
```python
# Quick debug: add to match_local_command temporarily
import sys
print("Prompt words:", prompt_words, file=sys.stderr)
print("Expanded:", expanded_words, file=sys.stderr)
print("Best score:", best_score, "hits:", best_hits, file=sys.stderr)
```

### Ollama Connection Failures
`ai_engine.py` calls `urllib.request.urlopen` with a 30-second timeout. Common failures:
- **ConnectionRefusedError**: Ollama not running. Check `systemctl status ollama`.
- **URLError**: Network issue or wrong port. Verify `OLLAMA_URL` is `http://localhost:11434/api/generate`.
- **TimeoutError**: Model loading. First request after restart can take 30+ seconds.
- **JSON decode error**: Model returned non-JSON. Check `response_text` in `_call_ollama`.

### Permission Denied on Log File
`logger.py` silently catches `PermissionError`. To debug:
```python
# Temporarily remove the bare except in log_execution
try:
    with open(LOG_FILE, "a") as f:
        f.write(...)
except PermissionError as e:
    print("Log write failed: {}".format(e), file=sys.stderr)
```
Fix: ensure `/var/log/red-ai/` is owned by root with correct permissions.

## Mock Patterns for Testing

### Mocking subprocess.run
```python
from unittest.mock import patch, MagicMock

@patch("red_ai.executor.subprocess.run")
def test_execute_success(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="OK\n",
        stderr="",
    )
    results = execute_commands(["echo test"], dry_run=False, skip_confirm=True)
    assert results[0]["status"] == "success"
```

### Mocking Ollama HTTP Calls
```python
@patch("red_ai.ai_engine.urllib.request.urlopen")
def test_ollama_response(mock_urlopen):
    response_json = json.dumps({
        "response": json.dumps({
            "commands": ["systemctl restart sshd"],
            "description": "Restart SSH",
            "risk_level": "medium",
        })
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__ = lambda s: MagicMock(
        read=lambda: response_json
    )
    result = get_ai_response("restart ssh")
    assert result["source"] == "ollama"
```

### Mocking System Info
```python
@patch("red_ai.system_info.get_rhel_version", return_value="Red Hat Enterprise Linux release 8.9 (Ootpa)")
@patch("red_ai.system_info.os.geteuid", return_value=0)
def test_system_context(mock_euid, mock_version):
    info = get_system_info()
    assert "8.9" in info["rhel_version"]
```

## Testing Ollama Connectivity
```bash
# Check Ollama is running
curl -s http://localhost:11434/api/tags | python3 -m json.tool

# Test the red-ai-model specifically
curl -s http://localhost:11434/api/generate \
  -d '{"model":"red-ai-model","prompt":"disable firewall","stream":false}' \
  | python3 -m json.tool

# Check model is loaded
curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
tags = json.load(sys.stdin)
for m in tags.get('models', []):
    print(m['name'])
"
```

## Debugging the Keyword Scorer
When matches seem wrong, test scoring in isolation:
```python
from red_ai.local_commands import match_local_command
result = match_local_command("configure network bonding")
print(result)  # Check which entry matched and why
```
