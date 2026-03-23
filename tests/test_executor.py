"""Tests for the command executor with safety checks."""
import subprocess
import unittest
from unittest.mock import patch, MagicMock
from red_ai.executor import execute_commands, color


class TestDryRunMode(unittest.TestCase):
    """Verify dry-run mode never executes commands."""

    @patch("red_ai.executor.subprocess.run")
    def test_dry_run_does_not_call_subprocess(self, mock_run):
        execute_commands(
            ["echo hello", "echo world"],
            dry_run=True, description="Test", risk_level="low")
        mock_run.assert_not_called()

    def test_dry_run_returns_skipped_status(self):
        results = execute_commands(
            ["cmd1", "cmd2", "cmd3"],
            dry_run=True, description="Test", risk_level="low")
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["status"], "skipped")

    def test_dry_run_preserves_command_text(self):
        cmds = ["echo hello", "systemctl restart sshd"]
        results = execute_commands(
            cmds, dry_run=True, description="Test", risk_level="low")
        for i, r in enumerate(results):
            self.assertEqual(r["command"], cmds[i])


class TestExecution(unittest.TestCase):
    """Test actual command execution (mocked)."""

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=True)
    def test_successful_execution(self, mock_confirm, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ok\n", stderr="")
        results = execute_commands(
            ["echo hello"], dry_run=False, skip_confirm=False,
            description="Test", risk_level="low")
        self.assertIsNotNone(results)
        self.assertEqual(results[0]["status"], "success")
        mock_run.assert_called_once()

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=True)
    def test_failed_command(self, mock_confirm, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="error\n")
        results = execute_commands(
            ["false"], dry_run=False, skip_confirm=False,
            description="Test", risk_level="low")
        self.assertEqual(results[0]["status"], "failed")

    @patch("red_ai.executor.subprocess.run")
    def test_timeout_handling(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 120)
        results = execute_commands(
            ["sleep 999"], dry_run=False, skip_confirm=True,
            description="Test", risk_level="low")
        self.assertEqual(results[0]["status"], "timeout")

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=False)
    def test_user_cancellation(self, mock_confirm, mock_run):
        results = execute_commands(
            ["echo hello"], dry_run=False, skip_confirm=False,
            description="Test", risk_level="high")
        self.assertIsNone(results)
        mock_run.assert_not_called()

    @patch("red_ai.executor.subprocess.run")
    def test_skip_confirm_bypasses_prompt(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="", stderr="")
        results = execute_commands(
            ["echo hello"], dry_run=False, skip_confirm=True,
            description="Test", risk_level="low")
        self.assertIsNotNone(results)
        self.assertEqual(results[0]["status"], "success")

    @patch("red_ai.executor.subprocess.run")
    @patch("red_ai.executor.confirm", return_value=True)
    def test_multiple_commands_all_run(self, mock_confirm, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="", stderr="")
        results = execute_commands(
            ["cmd1", "cmd2", "cmd3"], dry_run=False, skip_confirm=False,
            description="Test", risk_level="low")
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_run.call_count, 3)


class TestColorFunction(unittest.TestCase):
    """Test the ANSI color helper."""

    def test_color_wraps_text(self):
        result = color("hello", "red")
        self.assertIn("hello", result)
        self.assertIn("\033[", result)

    def test_color_unknown_returns_text(self):
        result = color("hello", "nonexistent")
        self.assertIn("hello", result)

    def test_color_reset_appended(self):
        result = color("test", "green")
        self.assertTrue(result.endswith("\033[0m"))


if __name__ == "__main__":
    unittest.main()
