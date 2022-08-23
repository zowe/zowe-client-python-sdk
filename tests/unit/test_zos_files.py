"""Unit tests for the Zowe Python SDK z/OS Files package."""

from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files, exceptions


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

    def test_create_data_set_raises_error_without_required_arguments(self):
        """Not providing required arguments should raise error."""
        with self.assertRaises(KeyError):
            obj = Files(self.connection_dict).create_data_set("DSNAME123", options={
                "alcunit": "CYL",
                "dsorg": "PO",
                "recfm": "FB",
                "blksize": 6160,
                "dirblk": 25
            })

    def test_create_default_data_set_raises_error_for_unsupported_types(self):
        """Attempting to create a data set that is not part of the suggested list should raise error."""
        with self.assertRaises(exceptions.UnsupportedDefaultDataSetRequested) as e_info:
            obj = Files(self.connection_dict).create_default_data_set("DSNAME123", "unsuporrted_type")
        
        expected = "Invalid request. The following default options are available: partitioned, sequential, classic, c, binary, vsam."
        self.assertEqual(str(e_info.exception), expected)

    @mock.patch('requests.Session.send')
    def test_create_default_dataset_with_partitioned_type(self, mock_send_request):
        """Test creating a partitioned data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.connection_dict).create_default_data_set("dataset_name", "partitioned")
        mock_send_request.assert_called_once()
