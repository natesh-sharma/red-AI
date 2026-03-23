# Contributing to RED-AI

## Getting Started

1. Clone the repository
2. Install in dev mode: `pip3 install -e .`
3. Run tests: `python3 -m unittest discover -s tests -v`

## Development Workflow

1. Create a feature branch from `main`
2. Write tests first (TDD)
3. Implement the feature
4. Run the full validation: `./scripts/validate.sh`
5. Commit with conventional format
6. Open a pull request

## Commit Messages

Use conventional commits:

```
feat: add chrony NTP configuration pattern
fix: correct selinux keyword matching
docs: update usage examples
test: add executor timeout tests
refactor: simplify risk level validation
chore: update build script
```

## Adding Command Patterns

1. Edit `red_ai/local_commands.py`
2. Add entry to `LOCAL_COMMANDS` with required fields:
   - `keywords` — list of lowercase matching terms
   - `description` — what the commands do
   - `category` — one of: kernel, security, storage, network, services, users, packages, performance, logging, boot
   - `commands` — list of shell commands
   - `risk_level` — low, medium, or high
   - `requires_reboot` — boolean
   - `notes` — additional context
3. Add matching training example to `Modelfile`
4. Run tests to validate: `python3 -m unittest tests/test_local_commands.py -v`

## Code Standards

- Python 3.6+ compatible (no walrus operator, no dataclasses)
- Zero external dependencies — stdlib only
- Use `logging` module, not `print()`
- snake_case for all Python identifiers
- Functions under 50 lines
- Files under 800 lines

## Testing

- All new features require tests
- Use `unittest` with `unittest.mock` (stdlib only)
- Target 80%+ coverage
- Test both success and failure paths
- Mock external calls (subprocess, HTTP, filesystem)

## Security

- Never hardcode credentials or secrets
- Always validate user input at boundaries
- All new command categories must support dry-run mode
- Risk levels must be accurately assigned
