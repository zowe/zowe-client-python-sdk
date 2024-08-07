"""Unit tests for the Zowe Python SDK z/OS Files package."""

import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Datasets, Files, exceptions


class TestFilesClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    @mock.patch("requests.Session.send")
    def test_list_dsn(self, mock_send_request):
        """Test list DSN sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        test_values = [("MY.DSN", False), ("MY.DSN", True)]
        for test_case in test_values:
            Files(self.test_profile).list_dsn(*test_case)
            mock_send_request.assert_called()

    @mock.patch("requests.Session.send")
    def test_list_members(self, mock_send_request):
        """Test list members sends request"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {"items": [{}, {}]}

        test_cases = [
            ("MY.PDS", None, None, 1000, "member"),
            ("MY.PDS", "MEM*", None, 1000, "member"),
            ("MY.PDS", None, "MEMBER1", 1000, "member"),
            ("MY.PDS", "MEM*", "MEMBER1", 500, "extended"),
        ]

        for dataset_name, member_pattern, member_start, limit, attributes in test_cases:
            result = self.files_instance.list_dsn_members(dataset_name, member_pattern, member_start, limit, attributes)
            mock_send_request.assert_called()

            prepared_request = mock_send_request.call_args[0][0]
            self.assertEqual(prepared_request.method, "GET")
            self.assertIn(dataset_name, prepared_request.url)
            self.assertEqual(prepared_request.headers["X-IBM-Max-Items"], str(limit))
            self.assertEqual(prepared_request.headers["X-IBM-Attributes"], attributes)
