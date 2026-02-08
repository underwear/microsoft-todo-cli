#!/usr/bin/env python3
"""Unit tests for attachment wrapper functions"""

import unittest
from unittest.mock import patch, MagicMock
import json
import base64
import os
import tempfile

from todocli.graphapi.wrapper import (
    AttachmentTooLarge,
    AttachmentNotFoundByIndex,
    ATTACHMENT_DIRECT_UPLOAD_LIMIT,
    ATTACHMENT_MAX_SIZE,
    BASE_URL,
    get_attachments,
    get_attachment,
    create_attachment,
    delete_attachment,
)


class TestAttachmentExceptions(unittest.TestCase):
    """Test custom attachment exception classes"""

    def test_attachment_too_large_exception(self):
        exc = AttachmentTooLarge(30 * 1024 * 1024)
        self.assertIn("30.0 MB", exc.message)
        self.assertIn("25 MB", exc.message)

    def test_attachment_not_found_by_index_exception(self):
        exc = AttachmentNotFoundByIndex(5, "My Task")
        self.assertIn("5", exc.message)
        self.assertIn("My Task", exc.message)
        self.assertIn("could not be found", exc.message)


class TestAttachmentConstants(unittest.TestCase):
    """Test attachment size limit constants"""

    def test_direct_upload_limit(self):
        self.assertEqual(ATTACHMENT_DIRECT_UPLOAD_LIMIT, 3 * 1024 * 1024)

    def test_max_size(self):
        self.assertEqual(ATTACHMENT_MAX_SIZE, 25 * 1024 * 1024)


class TestGetAttachments(unittest.TestCase):
    """Test get_attachments wrapper function"""

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_task_id_by_name")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_get_attachments_by_name(
        self, mock_get_list_id, mock_get_task_id, mock_session
    ):
        mock_get_list_id.return_value = "list-id-123"
        mock_get_task_id.return_value = "task-id-456"

        response_data = {
            "value": [
                {
                    "id": "att-1",
                    "name": "report.pdf",
                    "contentType": "application/pdf",
                    "size": 12345,
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.content = json.dumps(response_data).encode()
        mock_session.return_value.get.return_value = mock_resp

        result = get_attachments(list_name="Tasks", task_name="My Task")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "report.pdf")

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    def test_get_attachments_by_id(self, mock_session):
        response_data = {"value": []}
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.content = json.dumps(response_data).encode()
        mock_session.return_value.get.return_value = mock_resp

        result = get_attachments(list_id="list-id", task_id="task-id")
        self.assertEqual(result, [])


class TestCreateAttachment(unittest.TestCase):
    """Test create_attachment wrapper function"""

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_task")
    @patch("todocli.graphapi.wrapper.get_task_id_by_name")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    def test_create_attachment_direct_upload(
        self, mock_get_list_id, mock_get_task_id, mock_get_task, mock_session
    ):
        mock_get_list_id.return_value = "list-id-123"
        mock_get_task_id.return_value = "task-id-456"
        mock_task = MagicMock()
        mock_task.title = "My Task"
        mock_get_task.return_value = mock_task

        post_response = MagicMock()
        post_response.ok = True
        post_response.content = json.dumps({"id": "att-new-1"}).encode()
        mock_session.return_value.post.return_value = post_response

        # Create a small temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("Hello, world!")
            temp_path = f.name

        try:
            att_id, file_name, task_id, title = create_attachment(
                file_path=temp_path,
                list_name="Tasks",
                task_name="My Task",
            )
            self.assertEqual(att_id, "att-new-1")
            self.assertTrue(file_name.endswith(".txt"))
            self.assertEqual(task_id, "task-id-456")
            self.assertEqual(title, "My Task")

            # Verify the POST request body
            call_args = mock_session.return_value.post.call_args
            req_body = call_args.kwargs["json"]
            self.assertEqual(
                req_body["@odata.type"], "#microsoft.graph.taskFileAttachment"
            )
            self.assertIn("contentBytes", req_body)
            self.assertIn("name", req_body)
            self.assertEqual(req_body["size"], os.path.getsize(temp_path))
        finally:
            os.unlink(temp_path)

    def test_create_attachment_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            create_attachment(
                file_path="/nonexistent/file.txt",
                list_id="lid",
                task_id="tid",
            )

    def test_create_attachment_file_too_large(self):
        """Test that files over 25MB raise AttachmentTooLarge"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            # Mock os.path.getsize to return > 25MB
            with patch("todocli.graphapi.wrapper.os.path.getsize") as mock_size:
                mock_size.return_value = 30 * 1024 * 1024
                with patch(
                    "todocli.graphapi.wrapper.os.path.isfile", return_value=True
                ):
                    with self.assertRaises(AttachmentTooLarge):
                        create_attachment(
                            file_path=temp_path,
                            list_id="lid",
                            task_id="tid",
                        )
        finally:
            os.unlink(temp_path)

    def test_create_attachment_empty_file(self):
        """Test that empty files raise ValueError"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            # File is empty (0 bytes)

        try:
            with self.assertRaises(ValueError) as ctx:
                create_attachment(
                    file_path=temp_path,
                    list_id="lid",
                    task_id="tid",
                )
            self.assertIn("empty file", str(ctx.exception))
        finally:
            os.unlink(temp_path)


class TestDeleteAttachment(unittest.TestCase):
    """Test delete_attachment wrapper function"""

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_attachments")
    @patch("todocli.graphapi.wrapper.get_task")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    @patch("todocli.graphapi.wrapper.get_task_id_by_name")
    def test_delete_all_attachments(
        self,
        mock_get_task_id,
        mock_get_list_id,
        mock_get_task,
        mock_get_attachments,
        mock_session,
    ):
        mock_get_list_id.return_value = "list-id"
        mock_get_task_id.return_value = "task-id"
        mock_task = MagicMock()
        mock_task.title = "My Task"
        mock_get_task.return_value = mock_task
        mock_get_attachments.return_value = [
            {"id": "att-1", "name": "file1.txt"},
            {"id": "att-2", "name": "file2.txt"},
        ]

        del_resp = MagicMock()
        del_resp.ok = True
        mock_session.return_value.delete.return_value = del_resp

        task_id, title, count = delete_attachment(
            list_name="Tasks", task_name="My Task"
        )
        self.assertEqual(count, 2)
        self.assertEqual(title, "My Task")
        self.assertEqual(mock_session.return_value.delete.call_count, 2)

    @patch("todocli.graphapi.wrapper.get_oauth_session")
    @patch("todocli.graphapi.wrapper.get_attachments")
    @patch("todocli.graphapi.wrapper.get_task")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    @patch("todocli.graphapi.wrapper.get_task_id_by_name")
    def test_delete_attachment_by_index(
        self,
        mock_get_task_id,
        mock_get_list_id,
        mock_get_task,
        mock_get_attachments,
        mock_session,
    ):
        mock_get_list_id.return_value = "list-id"
        mock_get_task_id.return_value = "task-id"
        mock_task = MagicMock()
        mock_task.title = "My Task"
        mock_get_task.return_value = mock_task
        mock_get_attachments.return_value = [
            {"id": "att-1", "name": "file1.txt"},
            {"id": "att-2", "name": "file2.txt"},
        ]

        del_resp = MagicMock()
        del_resp.ok = True
        mock_session.return_value.delete.return_value = del_resp

        task_id, title, count = delete_attachment(
            list_name="Tasks", task_name="My Task", attachment_index=1
        )
        self.assertEqual(count, 1)
        # Should have deleted only att-2
        call_args = mock_session.return_value.delete.call_args
        self.assertIn("att-2", call_args.args[0])

    @patch("todocli.graphapi.wrapper.get_attachments")
    @patch("todocli.graphapi.wrapper.get_task")
    @patch("todocli.graphapi.wrapper.get_list_id_by_name")
    @patch("todocli.graphapi.wrapper.get_task_id_by_name")
    def test_delete_attachment_invalid_index(
        self,
        mock_get_task_id,
        mock_get_list_id,
        mock_get_task,
        mock_get_attachments,
    ):
        mock_get_list_id.return_value = "list-id"
        mock_get_task_id.return_value = "task-id"
        mock_task = MagicMock()
        mock_task.title = "My Task"
        mock_get_task.return_value = mock_task
        mock_get_attachments.return_value = [
            {"id": "att-1", "name": "file1.txt"},
        ]

        with self.assertRaises(AttachmentNotFoundByIndex):
            delete_attachment(
                list_name="Tasks", task_name="My Task", attachment_index=5
            )


class TestAttachmentEndpointPattern(unittest.TestCase):
    """Test that attachment endpoint URLs are correctly constructed"""

    def test_attachments_endpoint_format(self):
        """Verify the endpoint pattern for listing attachments"""
        list_id = "list-123"
        task_id = "task-456"
        expected = f"{BASE_URL}/{list_id}/tasks/{task_id}/attachments"
        self.assertIn("/me/todo/lists/", expected)
        self.assertIn("/attachments", expected)

    def test_single_attachment_endpoint_format(self):
        """Verify the endpoint pattern for getting a single attachment"""
        list_id = "list-123"
        task_id = "task-456"
        att_id = "att-789"
        expected = f"{BASE_URL}/{list_id}/tasks/{task_id}/attachments/{att_id}"
        self.assertIn(att_id, expected)


if __name__ == "__main__":
    unittest.main()
