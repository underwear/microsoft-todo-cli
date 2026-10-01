#!/usr/bin/env python3
"""Unit tests for lst command output (due date, importance, steps display)"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime

from todocli.cli import lst


def _make_task(title, importance="normal", due_datetime=None, task_id="tid-0"):
    task = MagicMock()
    task.title = title
    task.importance = importance
    task.due_datetime = due_datetime
    task.id = task_id
    return task


def _make_args(
    list_name="Tasks",
    no_steps=False,
    json=False,
    due_today=False,
    overdue=False,
    important=False,
    top=None,
    skip=None,
):
    args = MagicMock()
    args.list_name = list_name
    args.no_steps = no_steps
    args.date_format = "eu"
    args.json = json
    args.due_today = due_today
    args.overdue = overdue
    args.important = important
    args.top = top
    args.skip = skip
    return args


class TestLstOutput(unittest.TestCase):

    @patch("todocli.cli.wrapper")
    def test_lst_shows_due_date(self, mock_wrapper):
        dt = datetime(2026, 2, 15, 7, 0, 0)
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [_make_task("Buy milk", due_datetime=dt)]
        mock_wrapper.get_checklist_items_batch.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args())
            output = mock_stdout.getvalue()

        self.assertIn("(due: 15.02.2026)", output)
        self.assertIn("Buy milk", output)

    @patch("todocli.cli.wrapper")
    def test_lst_no_due_date(self, mock_wrapper):
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [_make_task("Buy milk")]
        mock_wrapper.get_checklist_items_batch.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args())
            output = mock_stdout.getvalue()

        self.assertNotIn("(due:", output)
        self.assertIn("Buy milk", output)

    @patch("todocli.cli.wrapper")
    def test_lst_shows_importance(self, mock_wrapper):
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [
            _make_task("Important task", importance="high")
        ]
        mock_wrapper.get_checklist_items_batch.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args())
            output = mock_stdout.getvalue()

        self.assertIn("Important task !", output)

    @patch("todocli.cli.wrapper")
    def test_lst_normal_importance_no_marker(self, mock_wrapper):
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [
            _make_task("Normal task", importance="normal")
        ]
        mock_wrapper.get_checklist_items_batch.return_value = {}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args())
            output = mock_stdout.getvalue()

        self.assertNotIn("!", output)

    @patch("todocli.cli.wrapper")
    def test_lst_shows_steps_by_default(self, mock_wrapper):
        dt = datetime(2026, 3, 1, 7, 0, 0)
        task = _make_task(
            "Task with steps", importance="high", due_datetime=dt, task_id="t1"
        )
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [task]

        step = MagicMock()
        step.is_checked = False
        step.display_name = "Step 1"
        mock_wrapper.get_checklist_items_batch.return_value = {"t1": [step]}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args())
            output = mock_stdout.getvalue()

        self.assertIn("Task with steps !", output)
        self.assertIn("(due: 01.03.2026)", output)
        self.assertIn("[ ] Step 1", output)

    @patch("todocli.cli.wrapper")
    def test_lst_no_steps_flag_hides_steps(self, mock_wrapper):
        task = _make_task("My task", task_id="t1")
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [task]

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(_make_args(no_steps=True))
            output = mock_stdout.getvalue()

        self.assertIn("My task", output)
        # Batch should not have been called
        mock_wrapper.get_checklist_items_batch.assert_not_called()

    @patch("todocli.cli.wrapper")
    def test_lst_passes_top_and_skip(self, mock_wrapper):
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = []

        with patch("sys.stdout", new_callable=StringIO):
            lst(_make_args(top=5, skip=10))

        _, kwargs = mock_wrapper.get_tasks.call_args
        self.assertEqual(kwargs["top"], 5)
        self.assertEqual(kwargs["skip"], 10)

    @patch("todocli.cli.wrapper")
    def test_lst_skip_offsets_indices(self, mock_wrapper):
        mock_wrapper.get_list_id_by_name.return_value = "lid"
        mock_wrapper.get_tasks.return_value = [
            _make_task("Sixth", task_id="t5"),
            _make_task("Seventh", task_id="t6"),
        ]

        args = _make_args(no_steps=True, top=2, skip=5)
        args.show_id = False
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            lst(args)
            output = mock_stdout.getvalue()

        self.assertIn("[5]\tSixth", output)
        self.assertIn("[6]\tSeventh", output)


if __name__ == "__main__":
    unittest.main()
