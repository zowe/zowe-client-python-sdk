"""Unit tests for the Zowe Python SDK z/OS Files package."""
import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Files, exceptions, Datasets


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
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        test_values = [("MY.DSN", False), ("MY.DSN", True)]
        for test_case in test_values:
            Files(self.test_profile).list_dsn(*test_case)
            mock_send_request.assert_called()