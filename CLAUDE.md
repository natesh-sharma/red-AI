# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**RED-AI** is an AI-powered RHEL system configuration CLI tool. Users describe what they want in natural language, and RED-AI generates and optionally executes the appropriate Linux commands.

- **Author:** Natesh Sharma
- **License:** GPL-3.0
- **Python:** 3.6+
- **Target OS:** RHEL 7, 8, 9

## Architecture

```
red_ai/
  cli.py            # Main CLI, argument parsing, response handling
  ai_engine.py      # Ollama/Mistral LLM integration via HTTP
  local_commands.py  # Offline command database (230+ RHEL patterns)
  executor.py        # Command execution with safety checks
  logger.py          # Execution logging to /var/log/red-ai/
  system_info.py     # RHEL system detection and context
```

**Flow:** User prompt → ai_engine (Ollama) or local_commands (fallback) → executor → logger

## Core Principles

1. **Safety first** — never execute without explicit confirmation; dry-run is the default mindset
2. **Zero dependencies** — stdlib only; no pip install surprises on production RHEL systems
3. **Offline capable** — local_commands.py works without network; Ollama is a bonus, not a requirement
4. **RHEL native** — RPM packaged, tested on RHEL 7/8/9, respects system conventions
5. **Auditable** — every execution logged, every command previewed, every risk level visible

## Key Design Decisions

- **Zero external Python dependencies** — uses only stdlib + HTTP to Ollama
- **Offline fallback** — local_commands.py handles requests when Ollama is unavailable
- **Safety first** — dry-run mode, risk levels (low/medium/high), confirmation prompts, root checks
- **RPM packaging** — build_rpm.sh for native RHEL distribution

## Running & Testing

```bash
# Install in dev mode
pip3 install -e .

# Dry run (no root needed)
red-ai --dry-run "disable transparent hugepages"

# Show system info
red-ai --info

# Build RPM
./build_rpm.sh
```

## Development Notes

- Entry point: `red_ai.cli:entry_point`
- The Modelfile contains the custom Ollama model with 230+ RHEL training examples
- All commands require root (UID 0) for execution mode; dry-run works without root
- Use `logging` module, not `print()` for debug output
- Keep local_commands.py patterns comprehensive — it's the offline safety net
- Test on RHEL 7/8/9 compatibility (Python 3.6 minimum)

## Testing Requirements

- **Minimum coverage:** 80%
- **Framework:** unittest + unittest.mock (stdlib only)
- **TDD workflow:** write test → verify it fails → implement → verify it passes
- **Run tests:** `python3 -m unittest discover -s tests -v`
- **Full validation:** `./scripts/validate.sh` (syntax + imports + tests + secrets scan)
- **CI:** GitHub Actions runs tests on Python 3.6, 3.8, 3.9, 3.11

## Security Guidelines

- No hardcoded secrets — use environment variables or config files
- Validate all user input before processing
- Sanitize prompts sent to Ollama to prevent command injection
- All new command patterns must include accurate `risk_level`
- Execution requires root (UID 0); dry-run works unprivileged
- Run `./scripts/validate.sh` to scan for accidental secret commits

## Performance Notes

- `local_commands.py` keyword matching must remain O(n) or better
- Ollama HTTP timeout: 30s default, configurable
- Keep `LOCAL_COMMANDS` list load time under 50ms
- Prefer local match over Ollama when confidence is high (reduces latency)

## Success Metrics

- All tests pass on Python 3.6+
- Zero hardcoded secrets in codebase
- Every command category has dry-run support
- Local command match rate > 90% for common RHEL tasks
- Response time < 1s for local matches, < 10s for Ollama

## Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- File naming: snake_case for Python modules
- No hardcoded credentials or secrets
- Always provide dry-run support for new command categories
