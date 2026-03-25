"""Tests for the AI engine (Ollama integration + local fallback)."""
import json
import unittest
from unittest.mock import patch, MagicMock
from red_ai.ai_engine import get_ai_response, _detect_sysctl_in_response, _detect_grubby_in_response


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

    @patch("red_ai.ai_engine._is_ollama_running", return_value=True)
    @patch("red_ai.ai_engine._call_ollama")
    @patch("red_ai.local_commands.match_local_command", return_value=None)
    def test_falls_back_to_ollama(self, mock_match, mock_ollama, mock_running):
        mock_ollama.return_value = {
            "description": "AI generated",
            "commands": ["systemctl restart httpd"],
            "risk_level": "medium",
        }
        result = get_ai_response("restart apache")
        self.assertEqual(result["source"], "ollama")

    @patch("red_ai.ai_engine._is_ollama_running", return_value=True)
    @patch("red_ai.ai_engine._call_ollama", side_effect=Exception("offline"))
    @patch("red_ai.local_commands.match_local_command", return_value=None)
    def test_returns_error_when_both_fail(self, mock_match, mock_ollama, mock_running):
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


class TestGrubbyDetection(unittest.TestCase):
    """Test grubby kernel modification detection in AI responses."""

    def test_detects_grubby_update_kernel(self):
        result = {
            "description": "Add kernel param",
            "commands": ["grubby --update-kernel=ALL --args='transparent_hugepage=never'"],
            "risk_level": "medium",
            "requires_reboot": False,
            "notes": "",
        }
        detected = _detect_grubby_in_response(result)
        self.assertTrue(detected["requires_reboot"])
        self.assertIn("reboot", detected["notes"].lower())

    def test_detects_grubby_set_default(self):
        result = {
            "description": "Set default kernel",
            "commands": ["grubby --set-default /boot/vmlinuz-5.14.0"],
            "risk_level": "high",
            "requires_reboot": False,
            "notes": "",
        }
        detected = _detect_grubby_in_response(result)
        self.assertTrue(detected["requires_reboot"])

    def test_detects_grubby_remove_args(self):
        result = {
            "description": "Remove kernel param",
            "commands": ["grubby --update-kernel=ALL --remove-args='hugepage'"],
            "risk_level": "medium",
            "requires_reboot": False,
            "notes": "",
        }
        detected = _detect_grubby_in_response(result)
        self.assertTrue(detected["requires_reboot"])

    def test_ignores_readonly_grubby(self):
        result = {
            "description": "Check boot entries",
            "commands": ["grubby --default-kernel", "grubby --info=ALL"],
            "risk_level": "low",
            "requires_reboot": False,
            "notes": "",
        }
        detected = _detect_grubby_in_response(result)
        self.assertFalse(detected["requires_reboot"])

    def test_ignores_non_grubby_commands(self):
        result = {
            "description": "Install package",
            "commands": ["yum install -y httpd"],
            "risk_level": "low",
            "requires_reboot": False,
            "notes": "",
        }
        detected = _detect_grubby_in_response(result)
        self.assertFalse(detected["requires_reboot"])

    def test_no_duplicate_reboot_note(self):
        result = {
            "description": "Add kernel param",
            "commands": ["grubby --update-kernel=ALL --args='crashkernel=auto'"],
            "risk_level": "high",
            "requires_reboot": True,
            "notes": "Reboot required for crashkernel.",
        }
        detected = _detect_grubby_in_response(result)
        self.assertTrue(detected["requires_reboot"])
        # Should not append duplicate reboot text
        self.assertEqual(detected["notes"].count("eboot"), 1)

    def test_handles_empty_commands(self):
        result = {"description": "Empty", "commands": []}
        detected = _detect_grubby_in_response(result)
        self.assertFalse(detected.get("requires_reboot", False))


if __name__ == "__main__":
    unittest.main()
