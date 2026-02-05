#!/usr/bin/env python3
"""Unit tests for note CLI commands (argument parsing)"""

import unittest
from todocli.cli import setup_parser


class TestNoteCLIArgParsing(unittest.TestCase):
    """Test that CLI parsers correctly parse note command arguments"""

    def setUp(self):
        self.parser = setup_parser()

    # note command

    def test_note_basic(self):
        """Test note command with task name and content"""
        args = self.parser.parse_args(["note", "Buy groceries", "Remember to check prices"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.note_content, "Remember to check prices")

    def test_note_with_list_flag(self):
        """Test note command with --list flag"""
        args = self.parser.parse_args(
            ["note", "Buy groceries", "Remember to check prices", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.note_content, "Remember to check prices")
        self.assertEqual(args.list, "Shopping")

    def test_note_with_id_flag(self):
        """Test note command with --id flag"""
        args = self.parser.parse_args(
            ["note", "--id", "task123", "This is a note"]
        )
        self.assertEqual(args.task_id, "task123")
        self.assertEqual(args.note_content, "This is a note")

    def test_note_with_json_flag(self):
        """Test note command with --json flag"""
        args = self.parser.parse_args(
            ["note", "Buy groceries", "Note content", "--json"]
        )
        self.assertTrue(args.json)

    # show-note command

    def test_show_note_basic(self):
        """Test show-note command with task name"""
        args = self.parser.parse_args(["show-note", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")

    def test_show_note_with_list_flag(self):
        """Test show-note command with --list flag"""
        args = self.parser.parse_args(["show-note", "Buy groceries", "-l", "Shopping"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    def test_show_note_with_id_flag(self):
        """Test show-note command with --id flag"""
        args = self.parser.parse_args(["show-note", "--id", "task123"])
        self.assertEqual(args.task_id, "task123")

    def test_show_note_with_json_flag(self):
        """Test show-note command with --json flag"""
        args = self.parser.parse_args(["show-note", "Buy groceries", "--json"])
        self.assertTrue(args.json)

    def test_show_note_alias_sn(self):
        """Test sn alias for show-note command"""
        args = self.parser.parse_args(["sn", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")

    # clear-note command

    def test_clear_note_basic(self):
        """Test clear-note command with task name"""
        args = self.parser.parse_args(["clear-note", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")

    def test_clear_note_with_list_flag(self):
        """Test clear-note command with --list flag"""
        args = self.parser.parse_args(["clear-note", "Buy groceries", "-l", "Shopping"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    def test_clear_note_with_id_flag(self):
        """Test clear-note command with --id flag"""
        args = self.parser.parse_args(["clear-note", "--id", "task123"])
        self.assertEqual(args.task_id, "task123")

    def test_clear_note_with_json_flag(self):
        """Test clear-note command with --json flag"""
        args = self.parser.parse_args(["clear-note", "Buy groceries", "--json"])
        self.assertTrue(args.json)

    def test_clear_note_alias_cn(self):
        """Test cn alias for clear-note command"""
        args = self.parser.parse_args(["cn", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")


if __name__ == "__main__":
    unittest.main()
