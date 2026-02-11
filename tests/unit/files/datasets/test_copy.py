from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Files


class TestCopyClass(TestCase):
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
    def test_copy_uss_to_data_set(self, mock_send_request):
        """Test copy_uss_to_data_set sends a request"""

        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).copy_uss_to_data_set(
            "from_filename", "to_dataset_name", "to_member_name", replace=True
        )

        mock_send_request.assert_called_once()

    def test_copy_data_set_or_member_raises_exception(self):
        """Test copying a data set or member raises error when assigning invalid values to enq parameter"""

        test_case = {
            "from_dataset_name": "MY.OLD.DSN",
            "to_dataset_name": "MY.NEW.DSN",
            "from_member_name": "MYMEM1",
            "to_member_name": "MYMEM2",
            "enq": "RANDOM",
            "replace": True,
        }
        with self.assertRaises(ValueError) as e_info:
            Files(self.test_profile).copy_data_set_or_member(**test_case)
        self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    @mock.patch("requests.Session.send")
    def test_copy_data_set_or_member(self, mock_send_request):
        """Test copying a data set or member sends a request"""

        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        test_values = [
            {
                "from_dataset_name": "MY.OLD.DSN",
                "to_dataset_name": "MY.NEW.DSN",
                "from_member_name": "MYMEM1",
                "to_member_name": "MYMEM2",
                "volser": "ABC",
                "alias": False,
                "enq": "SHRW",
                "replace": False,
            },
            {
                "from_dataset_name": "MY.OLD.DSN",
                "to_dataset_name": "MY.NEW.DSN",
                "from_member_name": "MYMEM1",
                "to_member_name": "MYMEM2",
                "volser": "ABC",
                "alias": True,
                "enq": "SHRW",
                "replace": True,
            },
        ]
        for test_case in test_values:
            Files(self.test_profile).copy_data_set_or_member(**test_case)
            mock_send_request.assert_called()
