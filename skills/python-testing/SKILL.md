---
name: python-testing
description: Testing strategies for RED-AI using pytest, unittest.mock, and Python 3.6+ compatible patterns. Covers CLI testing, subprocess mocking, and offline/online mode validation.
origin: red-ai
---

# Python Testing Patterns for RED-AI

Testing strategies tailored to RED-AI's architecture: CLI tool with subprocess execution, Ollama AI engine, offline fallback, and RHEL system operations.

## When to Activate

- Writing new RED-AI features (follow TDD: red, green, refactor)
- Adding new command patterns to local_commands.py
- Modifying executor.py safety checks
- Testing ai_engine.py Ollama integration
- Validating CLI argument parsing in cli.py

## Python 3.6+ Compatibility

RED-AI targets RHEL 7/8/9, so all test code must be Python 3.6 compatible:

- No walrus operator (`:=`)
- No `dataclasses`
- No f-string `=` debugging (`f"{var=}"`)
- Use `universal_newlines=True` instead of `text=True` in subprocess
- Use `unittest.mock` (stdlib), not `pytest-mock` (external dep)

## Core Testing Philosophy

### TDD Cycle

1. **RED**: Write a failing test for the desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code while keeping tests green

### Coverage Target: 80%+

```bash
# Run with coverage (stdlib only, no pytest-cov needed)
python3 -m pytest tests/ -v
# Or with coverage if available
python3 -m pytest tests/ --cov=red_ai --cov-report=term-missing
```

## Test Structure

```
tests/
    __init__.py
    conftest.py              # Shared fixtures
    test_cli.py              # CLI argument parsing, entry point
    test_ai_engine.py        # Ollama HTTP integration
    test_local_commands.py   # Keyword matching, command database
    test_executor.py         # Command execution, dry-run, risk levels
    test_logger.py           # Log file operations
    test_system_info.py      # RHEL detection
```

## Testing local_commands.py (Keyword Matching)

```python
import unittest
from red_ai.local_commands import LOCAL_COMMANDS

class TestLocalCommands(unittest.TestCase):
    """Test the offline command database."""

    def test_all_entries_have_required_fields(self):
        required = {"keywords", "description", "category", "commands", "risk_level"}
        for i, cmd in enumerate(LOCAL_COMMANDS):
            for field in required:
                self.assertIn(field, cmd,
                    "Entry %d missing field '%s'" % (i, field))

    def test_keywords_are_lowercase(self):
        for cmd in LOCAL_COMMANDS:
            for kw in cmd["keywords"]:
                self.assertEqual(kw, kw.lower(),
                    "Keyword '%s' should be lowercase" % kw)

    def test_risk_levels_are_valid(self):
        valid = {"low", "medium", "high"}
        for cmd in LOCAL_COMMANDS:
            self.assertIn(cmd["risk_level"], valid,
                "Invalid risk_level in: %s" % cmd["description"])

    def test_commands_not_empty(self):
        for cmd in LOCAL_COMMANDS:
            self.assertTrue(len(cmd["commands"]) > 0,
                "Empty commands in: %s" % cmd["description"])

    def test_no_duplicate_descriptions(self):
        descriptions = [c["description"] for c in LOCAL_COMMANDS]
        self.assertEqual(len(descriptions), len(set(descriptions)),
            "Duplicate descriptions found")
```

## Testing executor.py (Command Execution)

```python
import unittest
from unittest.mock import patch, MagicMock
from red_ai.executor import execute_commands

class TestExecutor(unittest.TestCase):
    """Test command execution with safety checks."""

    def test_dry_run_does_not_execute(self):
        """Verify dry-run mode never calls subprocess."""
        with patch("red_ai.executor.subprocess.run") as mock_run:
            results = execute_commands(
                ["echo hello"], dry_run=True,
                description="Test", risk_level="low"
            )
            mock_run.assert_not_called()
            self.assertEqual(results[0]["status"], "skipped")

    def test_dry_run_returns_all_commands(self):
        commands = ["cmd1", "cmd2", "cmd3"]
        results = execute_commands(
            commands, dry_run=True,
            description="Test", risk_level="low"
        )
        self.assertEqual(len(results), 3)

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=True)
    def test_successful_execution(self, mock_confirm, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ok", stderr=""
        )
        results = execute_commands(
            ["echo hello"], dry_run=False, skip_confirm=False,
            description="Test", risk_level="low"
        )
        self.assertEqual(results[0]["status"], "success")

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=False)
    def test_user_cancellation(self, mock_confirm, mock_run):
        results = execute_commands(
            ["echo hello"], dry_run=False,
            description="Test", risk_level="high"
        )
        self.assertIsNone(results)
        mock_run.assert_not_called()

    @patch("red_ai.executor.subprocess.run")
    def test_timeout_handling(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 120)
        results = execute_commands(
            ["sleep 999"], dry_run=False, skip_confirm=True,
            description="Test", risk_level="low"
        )
        self.assertEqual(results[0]["status"], "timeout")
```

## Testing ai_engine.py (Ollama Integration)

```python
import unittest
from unittest.mock import patch, MagicMock
import json

class TestAIEngine(unittest.TestCase):
    """Test Ollama HTTP integration with mocked responses."""

    @patch("red_ai.ai_engine.urllib.request.urlopen")
    def test_successful_ollama_response(self, mock_urlopen):
        response_data = json.dumps({
            "response": "sudo systemctl disable firewalld"
        }).encode()
        mock_response = MagicMock()
        mock_response.read.return_value = response_data
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        # Test your AI engine function here
        # result = query_ollama("disable firewall")
        # self.assertIn("firewalld", result)

    @patch("red_ai.ai_engine.urllib.request.urlopen")
    def test_ollama_connection_failure(self, mock_urlopen):
        """Verify graceful fallback when Ollama is unreachable."""
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError("Connection refused")

        # Should fall back to local_commands, not crash
        # result = query_ollama("disable firewall")
        # self.assertIsNone(result)  # or whatever fallback behavior

    def test_ollama_timeout(self):
        """Verify timeout handling for slow Ollama responses."""
        pass  # Mock with socket.timeout
```

## Testing CLI (cli.py)

```python
import unittest
from unittest.mock import patch
import sys

class TestCLI(unittest.TestCase):
    """Test CLI argument parsing and routing."""

    @patch("sys.argv", ["red-ai", "--dry-run", "disable selinux"])
    def test_dry_run_flag(self):
        # Test that --dry-run is parsed correctly
        pass

    @patch("sys.argv", ["red-ai", "--info"])
    def test_info_flag(self):
        # Test that --info shows system information
        pass

    @patch("sys.argv", ["red-ai", "--version"])
    def test_version_flag(self):
        # Test that --version prints version
        pass

    def test_no_args_shows_help(self):
        """Running with no arguments should show usage."""
        pass
```

## Fixture Patterns for RED-AI

```python
# tests/conftest.py
import pytest
import tempfile
import os

@pytest.fixture
def mock_rhel_system():
    """Simulate RHEL system info for testing."""
    return {
        "os": "Red Hat Enterprise Linux",
        "version": "8.6",
        "kernel": "4.18.0-372.el8.x86_64",
        "arch": "x86_64",
        "python": "3.6.8"
    }

@pytest.fixture
def temp_log_dir():
    """Provide a temporary log directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_commands():
    """Common test commands for executor tests."""
    return {
        "safe": ["echo hello", "date", "whoami"],
        "risky": ["systemctl restart sshd"],
        "dangerous": ["rm -rf /tmp/test"],
    }
```

## Best Practices for RED-AI Tests

### DO
- Test dry-run mode for every new command category
- Mock subprocess.run for all execution tests
- Test both online (Ollama) and offline (local_commands) paths
- Validate risk_level is set correctly for dangerous operations
- Test Python 3.6 compatibility (no newer syntax)
- Use `unittest.mock` from stdlib (zero external deps)

### DON'T
- Don't execute real system commands in tests
- Don't require root access for unit tests
- Don't depend on Ollama being available
- Don't use pytest plugins (keep stdlib-only philosophy)
- Don't use f-string `=` syntax (Python 3.8+)
- Don't import `dataclasses` (Python 3.7+)

## Running Tests

```bash
# All tests
python3 -m pytest tests/ -v

# Specific module
python3 -m pytest tests/test_executor.py -v

# Pattern match
python3 -m pytest tests/ -k "dry_run" -v

# Stop on first failure
python3 -m pytest tests/ -x

# With coverage
python3 -m pytest tests/ --cov=red_ai --cov-report=term-missing
```
