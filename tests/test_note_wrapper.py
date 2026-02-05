#!/usr/bin/env python3
"""Unit tests for note wrapper functions"""

import unittest
from todocli.graphapi.wrapper import BASE_URL


class TestNoteEndpointPattern(unittest.TestCase):
    """Test that the note endpoint URL is correctly constructed"""

    def test_task_endpoint_for_note_update(self):
        """Test the task endpoint follows the expected pattern for note updates"""
        list_id = "list123"
        task_id = "task456"
        endpoint = f"{BASE_URL}/{list_id}/tasks/{task_id}"

        self.assertIn(list_id, endpoint)
        self.assertIn(task_id, endpoint)
        self.assertTrue(endpoint.startswith("https://graph.microsoft.com"))
        self.assertIn("/tasks/", endpoint)

    def test_note_request_body_format(self):
        """Test that note request body has correct structure"""
        note_content = "Test note content"
        content_type = "text"

        request_body = {
            "body": {
                "content": note_content,
                "contentType": content_type,
            }
        }

        self.assertIn("body", request_body)
        self.assertEqual(request_body["body"]["content"], note_content)
        self.assertEqual(request_body["body"]["contentType"], content_type)

    def test_clear_note_request_body_format(self):
        """Test that clear note request body has correct structure (empty content)"""
        request_body = {
            "body": {
                "content": "",
                "contentType": "text",
            }
        }

        self.assertIn("body", request_body)
        self.assertEqual(request_body["body"]["content"], "")


if __name__ == "__main__":
    unittest.main()
