"""Unit tests for the Zowe Python SDK z/OS Files package."""

from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files


class TestFilesClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.connection_dict = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Files class."""
        files = Files(self.connection_dict)
        self.assertIsInstance(files, Files)

    @mock.patch('requests.Session.send')
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.connection_dict).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()
