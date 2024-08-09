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
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).get_file_content("uss_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")

    @mock.patch("requests.Session.send")
    def test_get_streamed(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).get_file_content_streamed("uss_name", binary=True)
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")

    @mock.patch("requests.Session.send")
    def test_write(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).write_to_uss(filepath_name="test", data="test")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")

    @mock.patch("requests.Session.send")
    def test_list_uss(self, mock_send_request):
        """Test list DSN sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(self.test_profile).list_files("")
        mock_send_request.assert_called()
