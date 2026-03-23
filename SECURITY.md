# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | Yes       |
| 1.x     | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in RED-AI, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer with details
3. Include steps to reproduce the vulnerability
4. Allow reasonable time for a fix before disclosure

## Security Design

RED-AI executes system commands with root privileges. Security is enforced through:

- **Dry-run mode** — preview commands without execution (no root required)
- **Risk levels** — every command pattern is rated low/medium/high
- **Confirmation prompts** — user must confirm before execution (unless `--yes`)
- **Root checks** — execution mode requires UID 0
- **No external dependencies** — reduces supply chain attack surface
- **Local-first** — offline command database works without network access
- **Execution logging** — all executed commands logged to `/var/log/red-ai/`

## Secrets

- No API keys or credentials are stored in the repository
- Ollama runs locally — no data sent to external services
- Environment variables used for any configuration secrets
