#!/usr/bin/env python3
"""Unit tests for attachment CLI commands (argument parsing)"""

import unittest
from todocli.cli import setup_parser


class TestAttachmentCLIArgParsing(unittest.TestCase):
    """Test that CLI parsers correctly parse attachment command arguments"""

    def setUp(self):
        self.parser = setup_parser()

    # attach command

    def test_attach_basic(self):
        """Test attach command with task name and file path"""
        args = self.parser.parse_args(["attach", "Buy groceries", "/tmp/list.txt"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.file_path, "/tmp/list.txt")

    def test_attach_with_list_flag(self):
        """Test attach command with --list flag"""
        args = self.parser.parse_args(
            ["attach", "Buy groceries", "/tmp/list.txt", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.file_path, "/tmp/list.txt")
        self.assertEqual(args.list, "Shopping")

    def test_attach_with_id_flag(self):
        """Test attach command with --id flag"""
        args = self.parser.parse_args(
            ["attach", "--id", "task123", "/tmp/list.txt"]
        )
        self.assertEqual(args.task_id, "task123")
        self.assertEqual(args.file_path, "/tmp/list.txt")

    def test_attach_with_json_flag(self):
        """Test attach command with --json flag"""
        args = self.parser.parse_args(
            ["attach", "Buy groceries", "/tmp/list.txt", "--json"]
        )
        self.assertTrue(args.json)

    # attachments command

    def test_attachments_basic(self):
        """Test attachments command with task name"""
        args = self.parser.parse_args(["attachments", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")

    def test_attachments_with_list_flag(self):
        """Test attachments command with --list flag"""
        args = self.parser.parse_args(
            ["attachments", "Buy groceries", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    def test_attachments_with_id_flag(self):
        """Test attachments command with --id flag"""
        args = self.parser.parse_args(["attachments", "--id", "task123"])
        self.assertEqual(args.task_id, "task123")

    def test_attachments_with_json_flag(self):
        """Test attachments command with --json flag"""
        args = self.parser.parse_args(
            ["attachments", "Buy groceries", "--json"]
        )
        self.assertTrue(args.json)

    # detach command

    def test_detach_basic(self):
        """Test detach command with task name"""
        args = self.parser.parse_args(["detach", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertIsNone(args.att_index)

    def test_detach_with_index(self):
        """Test detach command with --index flag"""
        args = self.parser.parse_args(
            ["detach", "Buy groceries", "--index", "0"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.att_index, 0)

    def test_detach_with_list_flag(self):
        """Test detach command with --list flag"""
        args = self.parser.parse_args(
            ["detach", "Buy groceries", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    def test_detach_with_id_flag(self):
        """Test detach command with --id flag"""
        args = self.parser.parse_args(["detach", "--id", "task123"])
        self.assertEqual(args.task_id, "task123")

    def test_detach_with_json_flag(self):
        """Test detach command with --json flag"""
        args = self.parser.parse_args(
            ["detach", "Buy groceries", "--json"]
        )
        self.assertTrue(args.json)

    # download command

    def test_download_basic(self):
        """Test download command with task name"""
        args = self.parser.parse_args(["download", "Buy groceries"])
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertIsNone(args.att_index)

    def test_download_with_index(self):
        """Test download command with --index flag"""
        args = self.parser.parse_args(
            ["download", "Buy groceries", "--index", "1"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.att_index, 1)

    def test_download_with_output_dir(self):
        """Test download command with --output flag"""
        args = self.parser.parse_args(
            ["download", "Buy groceries", "-o", "/tmp/downloads"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.output, "/tmp/downloads")

    def test_download_with_id_flag(self):
        """Test download command with --id flag"""
        args = self.parser.parse_args(["download", "--id", "task123"])
        self.assertEqual(args.task_id, "task123")

    def test_download_with_list_flag(self):
        """Test download command with --list flag"""
        args = self.parser.parse_args(
            ["download", "Buy groceries", "-l", "Shopping"]
        )
        self.assertEqual(args.task_name, "Buy groceries")
        self.assertEqual(args.list, "Shopping")

    # new command --attach flag

    def test_new_with_attach_flag(self):
        """Test new command with --attach flag"""
        args = self.parser.parse_args(
            ["new", "-A", "/tmp/report.pdf", "Review report"]
        )
        self.assertEqual(args.task_name, "Review report")
        self.assertEqual(args.attach, "/tmp/report.pdf")

    def test_new_with_attach_long_flag(self):
        """Test new command with --attach flag (long form)"""
        args = self.parser.parse_args(
            ["new", "--attach", "/tmp/report.pdf", "Review report"]
        )
        self.assertEqual(args.task_name, "Review report")
        self.assertEqual(args.attach, "/tmp/report.pdf")

    def test_new_without_attach(self):
        """Test new command defaults attach to None"""
        args = self.parser.parse_args(["new", "buy milk"])
        self.assertIsNone(args.attach)


if __name__ == "__main__":
    unittest.main()
