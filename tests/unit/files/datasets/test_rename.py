import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Files, exceptions, Datasets


class TestCreateClass(TestCase):
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
    def test_rename_dataset(self, mock_send_request):
        """Test renaming dataset sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset("MY.OLD.DSN", "MY.NEW.DSN")
        mock_send_request.assert_called_once()

    def test_rename_dataset_parameterized(self):
        """Test renaming a dataset with different values"""
        test_values = [
            (("DSN.OLD", "DSN.NEW"), True),
            (("DS.NAME.CURRENT", "DS.NAME.NEW"), True),
            (("MY.OLD.DSN", "MY.NEW.DSN"), True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                },
            }

            files_test_profile.rename_dataset(test_case[0][0], test_case[0][1])

            custom_args = files_test_profile._create_custom_request_arguments()
            custom_args["json"] = data
            custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][1])
            files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                "PUT", custom_args, expected_code=[200]
            )

    @mock.patch("requests.Session.send")
    def test_rename_dataset_member(self, mock_send_request):
        """Test renaming dataset member sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBEROLD", "MEMBERNEW")
        mock_send_request.assert_called_once()

    def test_rename_dataset_member_raises_exception(self):
        """Test renaming a dataset member raises error when assigning invalid values to enq parameter"""
        with self.assertRaises(ValueError) as e_info:
            Files(self.test_profile).rename_dataset_member("MY.DS.NAME", "MEMBER1", "MEMBER1N", "RANDOM")
        self.assertEqual(str(e_info.exception), "Invalid value for enq.")

    def test_rename_dataset_member_parameterized(self):
        """Test renaming a dataset member with different values"""
        test_values = [
            (("DSN", "MBROLD$", "MBRNEW$", "EXCLU"), True),
            (("DSN", "MBROLD#", "MBRNE#", "SHRW"), True),
            (("DSN", "MBROLD", "MBRNEW", "INVALID"), False),
            (("DATA.SET.@NAME", "MEMBEROLD", "MEMBERNEW"), True),
            (("DS.NAME", "MONAME", "MNNAME"), True),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            data = {
                "request": "rename",
                "from-dataset": {
                    "dsn": test_case[0][0].strip(),
                    "member": test_case[0][1].strip(),
                },
            }

            if len(test_case[0]) > 3:
                data["enq"] = test_case[0][3].strip()
            if test_case[1]:
                files_test_profile.rename_dataset_member(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = data
                ds_path = "{}({})".format(test_case[0][0], test_case[0][2])
                ds_path_adjusted = files_test_profile._encode_uri_component(ds_path)
                self.assertNotRegex(ds_path_adjusted, r"[\$\@\#]")
                self.assertRegex(ds_path_adjusted, r"[\(" + re.escape(test_case[0][2]) + r"\)]")
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(ds_path_adjusted)
                files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                    "PUT", custom_args, expected_code=[200]
                )
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.rename_dataset_member(*test_case[0])
                self.assertEqual(str(e_info.exception), "Invalid value for enq.")