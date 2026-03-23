"""Tests for the AI engine (Ollama integration + local fallback)."""
import json
import unittest
from unittest.mock import patch, MagicMock
from red_ai.ai_engine import get_ai_response, _detect_sysctl_in_response


class TestGetAIResponse(unittest.TestCase):
    """Test the main response routing (local -> Ollama -> error)."""

    @patch("red_ai.local_commands.match_local_command")
    def test_local_match_preferred_over_ollama(self, mock_match):
        mock_match.return_value = {
            "description": "Test command",
            "commands": ["echo test"],
            "risk_level": "low",
        }
        result = get_ai_response("test prompt")
        self.assertEqual(result["source"], "local_commands")
        self.assertIn("commands", result)

    @patch("red_ai.ai_engine._call_ollama")
    @patch("red_ai.local_commands.match_local_command", return_value=None)
    def test_falls_back_to_ollama(self, mock_match, mock_ollama):
        mock_ollama.return_value = {
            "description": "AI generated",
            "commands": ["systemctl restart httpd"],
            "risk_level": "medium",
        }
        result = get_ai_response("restart apache")
        self.assertEqual(result["source"], "ollama")

    @patch("red_ai.ai_engine._call_ollama", side_effect=Exception("offline"))
    @patch("red_ai.local_commands.match_local_command", return_value=None)
    def test_returns_error_when_both_fail(self, mock_match, mock_ollama):
        result = get_ai_response("something unknown")
        self.assertIn("error", result)


class TestSysctlDetection(unittest.TestCase):
    """Test sysctl parameter detection in AI responses."""

    def test_detects_sysctl_write(self):
        result = {
            "description": "Set swappiness",
            "commands": ["sysctl -w vm.swappiness=10"],
            "risk_level": "medium",
        }
        detected = _detect_sysctl_in_response(result)
        self.assertEqual(detected["persist_mode"], "ask")
        self.assertEqual(detected["sysctl_param"], "vm.swappiness")
        self.assertEqual(detected["sysctl_value"], "10")
        self.assertIn("sysctl.d", detected["sysctl_conf"])

    def test_ignores_non_sysctl_commands(self):
        result = {
            "description": "Install package",
            "commands": ["yum install -y httpd"],
            "risk_level": "low",
        }
        detected = _detect_sysctl_in_response(result)
        self.assertNotIn("persist_mode", detected)

    def test_handles_empty_commands(self):
        result = {"description": "Empty", "commands": []}
        detected = _detect_sysctl_in_response(result)
        self.assertNotIn("persist_mode", detected)

    def test_handles_no_commands_key(self):
        result = {"description": "No commands"}
        detected = _detect_sysctl_in_response(result)
        self.assertNotIn("persist_mode", detected)


if __name__ == "__main__":
    unittest.main()
