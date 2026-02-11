from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Datasets, Files, exceptions
from zowe.zos_files_for_zowe_sdk.constants import ContentType


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
        """Test get content sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).ds.get_content(dataset_name="ds_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")

    @mock.patch("requests.Session.send")
    def test_retrieve_content(self, mock_send_request):
        """Test retrieve content sends a correct request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).ds.retrieve_content(dataset_name="ds_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")

    @mock.patch("requests.Session.send")
    def test_binary_get(self, mock_send_request):
        """Test get binary content sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).ds.get_binary_content(dataset_name="ds_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")

    @mock.patch("requests.Session.send")
    def test_retrieve_binary_content(self, mock_send_request):
        """Test retrieve binary content sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).ds.retrieve_content(dataset_name="ds_name", content_type=ContentType.BINARY)
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")
