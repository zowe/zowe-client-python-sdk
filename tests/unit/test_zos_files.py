"""Unit tests for the Zowe Python SDK z/OS Files package."""
from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files


class TestFilesClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Files class."""
        files = Files(self.test_profile)
        self.assertIsInstance(files, Files)

    @mock.patch('requests.Session.send')
    def test_create_zFS_file_system(self, mock_send_request):
        """Test creating a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms":100, "cylsPri": 16777213, "cylsSec": 16777215})
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_delete_zFS_file_system(self, mock_send_request):
        """Test deleting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_zFS_file_system("file_system_name")
        mock_send_request.assert_called_once()
