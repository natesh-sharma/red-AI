# Ollama Setup for RED-AI

## Prerequisites

- RHEL 7/8/9 or compatible Linux
- 4GB+ RAM (for Mistral model)
- Internet access (for initial download only)

## Step 1: Install Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Verify:
```bash
ollama --version
```

## Step 2: Build the RED-AI Model

From the project root:
```bash
ollama create red-ai-model -f Modelfile
```

This creates a custom Mistral-based model with 230+ RHEL-specific training examples.

## Step 3: Verify

```bash
# Test the model directly
ollama run red-ai-model "check kernel version"

# Test through RED-AI
red-ai --dry-run "check kernel version"
```

## Step 4: Run RED-AI

```bash
# Dry-run (no root needed)
red-ai --dry-run "disable transparent hugepages"

# Live execution (requires root)
sudo red-ai "disable transparent hugepages"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `connection refused` | Start Ollama: `systemctl start ollama` |
| `model not found` | Rebuild: `ollama create red-ai-model -f Modelfile` |
| Slow responses | Normal on first run (model loading). Subsequent calls are faster |
| Out of memory | Mistral needs ~4GB RAM. Close other applications |

## Notes

- RED-AI uses **only** the custom `red-ai-model`. No other models (GPT, Claude, etc.) are needed.
- Ollama runs 100% locally. No data is sent to external services.
- If Ollama is unavailable, RED-AI falls back to its built-in local command database (230+ patterns).
