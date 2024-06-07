from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files
from unit.files.constants import profile


class TestCreateClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = profile
    
    @mock.patch("requests.Session.send")
    def test_recall_migrated_dataset(self, mock_send_request):
        """Test recalling migrated data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).recall_migrated_dataset("dataset_name")
        mock_send_request.assert_called_once()

    def test_recall_migrated_dataset_parameterized(self):
        """Testing recall migrated_dataset with different values"""

        test_values = [
            ("MY.OLD.DSN", False),
            ("MY.OLD.DSN", True),
            ("MY.NEW.DSN", False),
            ("MY.NEW.DSN", True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            data = {"request": "hrecall", "wait": test_case[1]}

            files_test_profile.recall_migrated_dataset(test_case[0], test_case[1])
            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                "PUT", custom_args, expected_code=[200]
            )
    
    @mock.patch("requests.Session.send")
    def test_delete_migrated_data_set(self, mock_send_request):
        """Test deleting a migrated data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).delete_migrated_data_set("dataset_name")
        mock_send_request.assert_called_once()

    def test_delete_migrated_data_set_parameterized(self):
        """Test deleting a migrated data set with different values"""

        test_values = [
            ("MY.OLD.DSN", False, False),
            ("MY.OLD.DSN", False, True),
            ("MY.OLD.DSN", True, True),
            ("MY.NEW.DSN", True, True),
            ("MY.NEW.DSN", False, True),
            ("MY.NEW.DSN", False, False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            data = {
                "request": "hdelete",
                "purge": test_case[1],
                "wait": test_case[2],
            }

            files_test_profile.delete_migrated_data_set(test_case[0], test_case[1], test_case[2])
            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                "PUT", custom_args, expected_code=[200]
            )

    @mock.patch("requests.Session.send")
    def test_migrate_data_set(self, mock_send_request):
        """Test migrating a data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).migrate_data_set("dataset_name")
        mock_send_request.assert_called_once()

    def test_migrate_data_set_parameterized(self):
        """Test migrating a data set with different values"""

        test_values = [
            ("MY.OLD.DSN", False),
            ("MY.OLD.DSN", True),
            ("MY.NEW.DSN", True),
            ("MY.NEW.DSN", False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            data = {
                "request": "hmigrate",
                "wait": test_case[1],
            }

            files_test_profile.migrate_data_set(test_case[0], test_case[1])

            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0])
            files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                "PUT", custom_args, expected_code=[200]
            )