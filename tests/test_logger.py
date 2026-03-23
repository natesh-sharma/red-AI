"""Tests for execution logging."""
import os
import tempfile
import unittest
from unittest.mock import patch
from red_ai import logger


class TestLogExecution(unittest.TestCase):
    """Test log writing with mocked paths."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.tmpdir, "executions.log")

    @patch.object(logger, "LOG_DIR")
    @patch.object(logger, "LOG_FILE")
    def test_writes_log_entry(self, mock_file, mock_dir):
        mock_dir.__str__ = lambda s: self.tmpdir
        mock_file.__str__ = lambda s: self.log_file
        # Patch at module level
        logger.LOG_DIR = self.tmpdir
        logger.LOG_FILE = self.log_file

        logger.log_execution(
            prompt="test prompt",
            commands=["echo hello"],
            results=[{"command": "echo hello", "status": "success", "output": "hello"}],
            dry_run=True,
            source="local_commands",
            risk_level="low",
            description="Test execution",
        )

        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file) as f:
            content = f.read()
        self.assertIn("test prompt", content)
        self.assertIn("DRY RUN", content)
        self.assertIn("echo hello", content)

    def tearDown(self):
        # Clean up
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.tmpdir):
            os.rmdir(self.tmpdir)
        # Restore defaults
        logger.LOG_DIR = "/var/log/red-ai"
        logger.LOG_FILE = os.path.join(logger.LOG_DIR, "executions.log")


class TestReadHistory(unittest.TestCase):
    """Test log reading."""

    @patch.object(logger, "LOG_FILE", "/nonexistent/path/log")
    def test_returns_empty_for_missing_log(self):
        entries = logger.read_history(10)
        self.assertEqual(entries, [])


class TestLogRotation(unittest.TestCase):
    """Test log rotation logic."""

    def test_rotate_skips_small_files(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("small content")
            tmpfile = f.name

        original_log = logger.LOG_FILE
        logger.LOG_FILE = tmpfile
        try:
            logger._rotate_logs()
            # File should still exist (not rotated)
            self.assertTrue(os.path.exists(tmpfile))
        finally:
            logger.LOG_FILE = original_log
            os.remove(tmpfile)

    def test_rotate_skips_missing_files(self):
        original_log = logger.LOG_FILE
        logger.LOG_FILE = "/nonexistent/file.log"
        try:
            # Should not raise
            logger._rotate_logs()
        finally:
            logger.LOG_FILE = original_log


if __name__ == "__main__":
    unittest.main()
