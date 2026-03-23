"""Tests for the offline local command database and keyword matching."""
import unittest
from red_ai.local_commands import LOCAL_COMMANDS, match_local_command


class TestLocalCommandsSchema(unittest.TestCase):
    """Validate every entry in LOCAL_COMMANDS has correct structure."""

    REQUIRED_FIELDS = {"keywords", "description", "category", "commands", "risk_level"}
    VALID_RISK_LEVELS = {"low", "medium", "high"}

    def test_all_entries_have_required_fields(self):
        for i, cmd in enumerate(LOCAL_COMMANDS):
            for field in self.REQUIRED_FIELDS:
                self.assertIn(
                    field, cmd,
                    "Entry %d ('%s') missing field '%s'" % (
                        i, cmd.get("description", "?"), field))

    def test_keywords_are_lowercase(self):
        for cmd in LOCAL_COMMANDS:
            for kw in cmd["keywords"]:
                self.assertEqual(
                    kw, kw.lower(),
                    "Keyword '%s' in '%s' should be lowercase" % (
                        kw, cmd["description"]))

    def test_keywords_are_strings(self):
        for cmd in LOCAL_COMMANDS:
            for kw in cmd["keywords"]:
                self.assertIsInstance(kw, str,
                    "Keyword in '%s' is not a string" % cmd["description"])

    def test_keywords_not_empty(self):
        for cmd in LOCAL_COMMANDS:
            self.assertTrue(
                len(cmd["keywords"]) > 0,
                "Empty keywords in '%s'" % cmd["description"])

    def test_risk_levels_are_valid(self):
        for cmd in LOCAL_COMMANDS:
            self.assertIn(
                cmd["risk_level"], self.VALID_RISK_LEVELS,
                "Invalid risk_level '%s' in '%s'" % (
                    cmd["risk_level"], cmd["description"]))

    def test_commands_not_empty(self):
        for cmd in LOCAL_COMMANDS:
            self.assertTrue(
                len(cmd["commands"]) > 0,
                "Empty commands in '%s'" % cmd["description"])

    def test_commands_are_strings(self):
        for cmd in LOCAL_COMMANDS:
            for c in cmd["commands"]:
                self.assertIsInstance(c, str,
                    "Command in '%s' is not a string" % cmd["description"])

    def test_no_duplicate_descriptions(self):
        descriptions = [c["description"] for c in LOCAL_COMMANDS]
        seen = set()
        dupes = []
        for d in descriptions:
            if d in seen:
                dupes.append(d)
            seen.add(d)
        self.assertEqual(len(dupes), 0,
            "Duplicate descriptions: %s" % dupes)

    def test_category_is_string(self):
        for cmd in LOCAL_COMMANDS:
            self.assertIsInstance(cmd["category"], str)
            self.assertTrue(len(cmd["category"]) > 0)

    def test_requires_reboot_is_bool(self):
        for cmd in LOCAL_COMMANDS:
            if "requires_reboot" in cmd:
                self.assertIsInstance(cmd["requires_reboot"], bool,
                    "'requires_reboot' in '%s' is not bool" % cmd["description"])

    def test_minimum_entry_count(self):
        """Ensure the database has a substantial number of patterns."""
        self.assertGreaterEqual(len(LOCAL_COMMANDS), 100,
            "Expected 100+ command patterns, got %d" % len(LOCAL_COMMANDS))


class TestKeywordMatching(unittest.TestCase):
    """Test the match_local_command() function."""

    def test_match_hugepages(self):
        result = match_local_command("disable transparent hugepages")
        self.assertIsNotNone(result)
        self.assertIn("commands", result)
        self.assertTrue(
            any("hugepage" in c for c in result["commands"]),
            "Expected hugepage-related commands")

    def test_match_selinux(self):
        result = match_local_command("disable selinux")
        self.assertIsNotNone(result)
        self.assertIn("commands", result)

    def test_match_user_creation(self):
        result = match_local_command("create a new user")
        self.assertIsNotNone(result)
        self.assertIn("commands", result)
        self.assertTrue(
            any("useradd" in c for c in result["commands"]),
            "Expected useradd command")

    def test_match_disk_space(self):
        result = match_local_command("check disk space")
        self.assertIsNotNone(result)

    def test_no_match_gibberish(self):
        result = match_local_command("xyzzy foobar baz quux")
        self.assertIsNone(result)

    def test_match_returns_required_fields(self):
        result = match_local_command("check kernel version")
        self.assertIsNotNone(result)
        for field in ["description", "commands", "risk_level"]:
            self.assertIn(field, result,
                "Match result missing '%s'" % field)

    def test_case_insensitive_matching(self):
        lower = match_local_command("disable selinux")
        upper = match_local_command("Disable SELinux")
        self.assertIsNotNone(lower)
        self.assertIsNotNone(upper)


if __name__ == "__main__":
    unittest.main()
