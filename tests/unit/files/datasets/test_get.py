import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Files, exceptions, Datasets


class TestGetClass(TestCase):
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
    def test_get(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).get_dsn_content(dataset_name="ds_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")

    @mock.patch("requests.Session.send")
    def test_binary_get(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).get_dsn_binary_content(dataset_name="ds_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")
