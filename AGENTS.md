# AGENTS.md

RED-AI agent roster and orchestration guide. Version 2.0.

## Available Agents

| Agent | Model | When to Use |
|-------|-------|-------------|
| **architect** | Opus | Planning new features, architectural decisions, system design |
| **planner** | Opus | Feature implementation plans, complex refactoring strategy |
| **tdd-guide** | Sonnet | Writing new features (enforces tests-first), bug fixes |
| **code-reviewer** | Sonnet | After any code change — reviews quality, maintainability |
| **python-reviewer** | Sonnet | Python-specific review: PEP 8, idioms, type hints, performance |
| **security-reviewer** | Sonnet | Code handling user input, commands, secrets, system calls |
| **build-error-resolver** | Sonnet | Build failures, import errors, packaging issues |
| **refactor-cleaner** | Sonnet | Dead code removal, consolidation, cleanup |

## Agent Details

### architect
System design and technical decision-making. Use when planning new command categories, modifying the execution pipeline, or restructuring modules.

### planner
Creates step-by-step implementation plans. Use before starting complex features that span multiple files (e.g., adding a new CLI flag or command category).

### tdd-guide
Enforces TDD workflow: RED (write failing test) → GREEN (minimal implementation) → REFACTOR. **Use proactively** for all new features. Targets 80%+ coverage.

### code-reviewer
General code quality review. Checks readability, error handling, naming, and maintainability. **Must be used** after writing or modifying code.

### python-reviewer
Python-specific reviewer. Checks PEP 8 compliance, Pythonic idioms, Python 3.6 compatibility (no walrus, no dataclasses), and performance. **Must be used** for all Python changes.

### security-reviewer
Scans for hardcoded secrets, command injection risks, unsafe subprocess usage, and OWASP Top 10 vulnerabilities. **Use proactively** after modifying executor.py, ai_engine.py, or cli.py.

### build-error-resolver
Fixes build and import errors with minimal changes. Use when `pip install -e .` fails, RPM build breaks, or imports are broken.

### refactor-cleaner
Identifies and removes dead code, duplicate logic, and unused imports. Use during cleanup phases.

## Orchestration Patterns

### New Feature
1. **planner** → create implementation plan
2. **tdd-guide** → write tests first, then implement
3. **python-reviewer** → review Python code quality
4. **security-reviewer** → scan for security issues

### Bug Fix
1. **tdd-guide** → write failing test reproducing the bug
2. **code-reviewer** → review the fix

### Refactoring
1. **architect** → design the new structure
2. **refactor-cleaner** → remove dead code
3. **code-reviewer** → review changes
4. **tdd-guide** → verify tests still pass

### Pre-Release
1. **security-reviewer** → full security scan
2. **python-reviewer** → PEP 8 and compatibility check
3. **build-error-resolver** → verify RPM build
