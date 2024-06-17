import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Datasets, Files, exceptions


class TestDeleteClass(TestCase):
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
    def test_delete(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_data_set(dataset_name="ds_name", member_name="member_name")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_delete_param(self, mock_send_request):
        """Test list members sends request"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {}

        test_cases = [("MY.PDS", 1000, "m1"), ("MY.C", 100, "m2"), ("MY.D", 1000, "member"), ("MY.E", 500, "extended")]

        for dataset_name, volume, member_name in test_cases:
            result = self.files_instance.delete_data_set(dataset_name, volume, member_name)
            self.assertEqual(result, {})
            mock_send_request.assert_called()
            prepared_request = mock_send_request.call_args[0][0]
            self.assertEqual(prepared_request.method, "DELETE")
