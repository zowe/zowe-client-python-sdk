"""Unit tests for the Zowe Python SDK z/OS Files package."""
from unittest import TestCase, mock
import pytest
from zowe.zos_files_for_zowe_sdk import Files, exceptions


test_data = (
        "MY.DS.NAME", "MEMBEROLD", "MEMBERNEW", {
            "request": "rename",
            "from-dataset": {
                "dsn": "MY.DS.NAME",
                "member": "MEMBEROLD"
            }
        },
        "PUT",
        "https://https://mock-url.com:443/zosmf/restfiles/ds/MY.DS.NAME(MEMBERNEW)",
        200
    )

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
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()

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
    
    def test_invalid_permission(self):
        """Test that the correct exception is raised when an invalid permission option is provided"""
        with self.assertRaises(exceptions.InvalidPermsOption) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": -1, "cylsPri": 16777213, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Invalid zos-files create command 'perms' option: -1")

    def test_invalid_memory_allocation(self):
        """Test that the correct exception is raised when an invalid memory allocation option is provided"""
        with self.assertRaises(exceptions.MaxAllocationQuantityExceeded) as e_info:
            Files(self.test_profile).create_zFS_file_system("file_system_name", {"perms": 775, "cylsPri": 1677755513, "cylsSec": 16777215})
        self.assertEqual(str(e_info.exception), "Maximum allocation quantity of 16777215 exceeded")
    
    @mock.patch('requests.Session.send')
    def test_mount_zFS_file_system(self, mock_send_request):
        """Test mounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).mount_file_system("file_system_name", "mount_point")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_unmount_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).unmount_file_system("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_list_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).list_unix_file_systems("file_system_name")
        mock_send_request.assert_called_once()

    @mock.patch('requests.Session.send')
    def test_rename_dataset(self, mock_send_request):
        """Test renaming dataset sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset("MY.OLD.DSN", "MY.NEW.DSN")
        mock_send_request.assert_called_once()

    # @parametrize
    # def test_rename_dataset

    @mock.patch('requests.Session.send')
    def test_rename_dataset_member(self, mock_send_request):
        """Test renaming dataset member sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBEROLD", "MEMBERNEW")
        mock_send_request.assert_called_once()

    def test_rename_dataset_member_raises_exception(self):
        """Test renaming a dataset member raises error when assigning invalid values to enq parameter."""
        with self.assertRaises(exceptions.InvalidValuesForEnq) as e_info:
            Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBER1", "MEMBER1N", "RANDOM")

        self.assertEqual(str(e_info.exception), "Invalid value. Valid options are SHRW or EXCLU.")

    # @parametrize
    # def test_rename_dataset_member

    @pytest.mark.parametrize("ds_name,before_member,after_member,json_data,method,url,return_code", test_data)
    def test_rename_dataset_member_parametrized(self, ds_name, before_member, after_member, json_data, method, url, return_code):
        """Test renaming dataset member sends a request"""
        files_test_profile = Files(self.test_profile)
        files_test_profile.request_handler.perform_request = mock.Mock()
        files_test_profile.rename_dataset_member(ds_name, before_member, after_member)
        custom_args = files_test_profile._create_custom_request_arguments()
        custom_args["json"] = json_data
        custom_args["url"] = url

        files_test_profile.request_handler.perform_request.assert_called_once_with(method, custom_args, expected_code=[return_code])
