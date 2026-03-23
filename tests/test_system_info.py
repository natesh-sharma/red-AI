"""Tests for RHEL system detection."""
import unittest
from unittest.mock import patch, mock_open, MagicMock
from red_ai import system_info


class TestGetRhelVersion(unittest.TestCase):
    """Test RHEL version detection from /etc/redhat-release."""

    @patch("builtins.open", mock_open(
        read_data="Red Hat Enterprise Linux release 8.6 (Ootpa)\n"))
    def test_reads_rhel_release(self):
        # Clear cache
        system_info._cached_system_info = None
        result = system_info.get_rhel_version()
        self.assertIn("Red Hat", result)
        self.assertIn("8.6", result)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_returns_none_on_non_rhel(self, mock_file):
        result = system_info.get_rhel_version()
        self.assertIsNone(result)


class TestGetRhelMajorVersion(unittest.TestCase):
    """Test major version extraction."""

    @patch.object(system_info, "get_rhel_version",
                  return_value="Red Hat Enterprise Linux release 8.6 (Ootpa)")
    def test_extracts_major_8(self, mock_ver):
        result = system_info.get_rhel_major_version()
        self.assertEqual(result, 8)

    @patch.object(system_info, "get_rhel_version",
                  return_value="Red Hat Enterprise Linux release 9.2 (Plow)")
    def test_extracts_major_9(self, mock_ver):
        result = system_info.get_rhel_major_version()
        self.assertEqual(result, 9)

    @patch.object(system_info, "get_rhel_version", return_value=None)
    def test_returns_none_when_not_rhel(self, mock_ver):
        result = system_info.get_rhel_major_version()
        self.assertIsNone(result)

    @patch.object(system_info, "get_rhel_version",
                  return_value="Something without a version")
    def test_returns_none_for_bad_format(self, mock_ver):
        result = system_info.get_rhel_major_version()
        self.assertIsNone(result)


class TestFormatSystemContext(unittest.TestCase):
    """Test human-readable system info formatting."""

    def test_format_contains_all_fields(self):
        info = {
            "hostname": "test-host",
            "kernel": "4.18.0",
            "arch": "x86_64",
            "rhel_version": "Red Hat Enterprise Linux release 8.6",
            "is_root": False,
            "selinux": "Enforcing",
            "firewalld": "active",
        }
        result = system_info.format_system_context(info)
        self.assertIn("test-host", result)
        self.assertIn("4.18.0", result)
        self.assertIn("x86_64", result)
        self.assertIn("8.6", result)
        self.assertIn("Enforcing", result)

    def test_format_handles_none_rhel(self):
        info = {
            "hostname": "laptop",
            "kernel": "5.15.0",
            "arch": "x86_64",
            "rhel_version": None,
            "is_root": False,
            "selinux": "unknown",
            "firewalld": "unknown",
        }
        result = system_info.format_system_context(info)
        self.assertIn("Not RHEL", result)


class TestGetSystemInfo(unittest.TestCase):
    """Test full system info gathering (mocked)."""

    def setUp(self):
        # Clear cache before each test
        system_info._cached_system_info = None

    @patch("red_ai.system_info.subprocess.run")
    @patch("red_ai.system_info.get_rhel_version",
           return_value="Red Hat Enterprise Linux release 8.6")
    @patch("red_ai.system_info.os.geteuid", return_value=0)
    def test_returns_dict_with_expected_keys(self, mock_euid, mock_rhel, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Enforcing\n", stderr="")
        info = system_info.get_system_info()
        self.assertIn("hostname", info)
        self.assertIn("kernel", info)
        self.assertIn("arch", info)
        self.assertIn("is_root", info)
        self.assertIn("selinux", info)
        self.assertIn("firewalld", info)

    @patch("red_ai.system_info.subprocess.run",
           side_effect=FileNotFoundError)
    @patch("red_ai.system_info.get_rhel_version", return_value=None)
    @patch("red_ai.system_info.os.geteuid", return_value=1000)
    def test_handles_missing_commands(self, mock_euid, mock_rhel, mock_run):
        info = system_info.get_system_info()
        self.assertEqual(info["selinux"], "unknown")
        self.assertEqual(info["firewalld"], "unknown")

    def tearDown(self):
        system_info._cached_system_info = None


if __name__ == "__main__":
    unittest.main()
