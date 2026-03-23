# Working with Ollama API in RED-AI

## Architecture
RED-AI uses Ollama as an optional local LLM backend. The flow:
1. `ai_engine.py` tries `match_local_command()` first (instant, offline)
2. If no match, calls `_call_ollama()` via HTTP to `localhost:11434`
3. If Ollama fails, returns an error message

## API Configuration
```python
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "red-ai-model"  # Custom model defined in Modelfile
```

The custom model is created from the project's `Modelfile` which includes 230+ RHEL training examples baked into the system prompt.

## Model Management
```bash
# Create/update the custom model from Modelfile
ollama create red-ai-model -f Modelfile

# List available models
ollama list

# Test the model directly
ollama run red-ai-model "disable SELinux"

# Remove and recreate (after Modelfile changes)
ollama rm red-ai-model
ollama create red-ai-model -f Modelfile
```

## Prompt Engineering
The `Modelfile` contains the system prompt with structured output instructions. User prompts are augmented with live system context:
```python
full_prompt = "Current system information:\n{}\nUser request: {}".format(
    system_context, prompt)
```

Key LLM parameters in `_call_ollama()`:
- `temperature: 0.1` -- low creativity, deterministic output for system commands
- `num_predict: 256` -- cap response length to avoid runaway generation
- `stream: False` -- wait for complete response (simpler parsing)

## Response Parsing
Ollama returns JSON with a `response` field containing the model's text output. RED-AI expects that text to be valid JSON:
```python
# Primary: direct JSON parse
result = json.loads(response_text)

# Fallback: extract JSON object from mixed text
start = response_text.find("{")
end = response_text.rfind("}") + 1
result = json.loads(response_text[start:end])
```

Expected response structure:
```json
{
    "commands": ["systemctl restart sshd"],
    "description": "Restart the SSH daemon",
    "category": "services",
    "risk_level": "medium",
    "requires_reboot": false,
    "notes": ""
}
```

## Error Handling
`_call_ollama()` can raise several exceptions, all caught by `get_ai_response()`:
- `urllib.error.URLError` -- Ollama not running or unreachable
- `socket.timeout` / `urllib.error.URLError(timeout)` -- 30-second timeout exceeded
- `json.JSONDecodeError` -- model returned non-JSON response
- `ValueError` -- JSON extracted but missing required fields
- `KeyError` -- response dict missing expected keys

The bare `except Exception: pass` in `get_ai_response()` ensures the CLI always falls back gracefully. For debugging, temporarily add logging:
```python
except Exception as e:
    import sys
    print("Ollama error: {}".format(e), file=sys.stderr)
```

## Sysctl Detection
After Ollama returns a response, `_detect_sysctl_in_response()` checks if any command is a `sysctl -w` call and adds `persist_mode: "ask"` so the CLI can prompt the user about persistence. This ensures Ollama-generated sysctl changes get the same persistence workflow as local commands.
