import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import DatasetOption, Files, exceptions


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
    def test_create_data_set_accept_valid_recfm(self, mock_send_request):
        """Test if create dataset does accept all accepted record formats"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)
        option = DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=5, recfm="XX", blksize=6160, lrecl=80)
        for recfm in ["F", "FB", "V", "VB", "U", "FBA", "FBM", "VBA", "VBM"]:
            option.recfm = recfm
            Files(self.test_profile).create_data_set("DSNAME123", options=option)
        mock_send_request.assert_called()

    def test_create_data_set_does_not_accept_invalid_recfm(self):
        """Test if create dataset raises an error for invalid record formats"""
        option = DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=5, recfm="XX", blksize=6160, lrecl=80)
        with self.assertRaises(KeyError):
            Files(self.test_profile).create_data_set("DSNAME123", options=option)

    def test_create_data_set_raises_error_without_required_arguments(self):
        """Test not providing required arguments raises an error"""
        option = DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=25, recfm="FB", blksize=6160)
        with self.assertRaises(ValueError) as e_info:
            obj = Files(self.test_profile).create_data_set("DSNAME123", options=option)
        self.assertEqual(str(e_info.exception), "If 'like' is not specified, you must specify 'primary' or 'lrecl'.")

    def test_create_data_set_raises_error_with_invalid_arguments_parameterized(self):
        """Test not providing valid arguments raises an error"""
        test_values = [
            DatasetOption(alcunit="invalid", dsorg="PO", primary=1, dirblk=5, recfm="FB", blksize=6160, lrecl=80),
            DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=25, recfm="invalid", blksize=32760, lrecl=260),
            DatasetOption(alcunit="CYL", dsorg="invalid", primary=1, dirblk=5, recfm="FB", blksize=6160, lrecl=80),
            DatasetOption(alcunit="CYL", dsorg="PO", primary=10, dirblk=0, recfm="U", blksize=27998, lrecl=27998),
            DatasetOption(alcunit="CYL", dsorg="PO", primary=99777215, dirblk=5, recfm="FB", blksize=6160, lrecl=80),
        ]

        for test_case in test_values:
            with self.assertRaises((KeyError, ValueError)):
                obj = Files(self.test_profile).create_data_set("MY.OLD.ds", options=test_case)

    def test_create_dataset_parameterized(self):
        """Test create dataset with different values"""
        test_values = [
            (DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=5, recfm="FB", blksize=6160, lrecl=80), True),
            (DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=25, recfm="FB", blksize=6160, lrecl=80), True),
            (
                DatasetOption(alcunit="CYL", dsorg="PO", primary=1, dirblk=25, recfm="VB", blksize=32760, lrecl=260),
                True,
            ),
            (DatasetOption(alcunit="CYL", dsorg="PS", primary=1, recfm="FB", blksize=6160, lrecl=80), True),
            (DatasetOption(alcunit="CYL", dsorg="PS", recfm="FB", blksize=6160), False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            if test_case[1]:
                files_test_profile.create_data_set("DSN", test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = test_case[0].to_dict()
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format("DSN")
                files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                    "POST", custom_args, expected_code=[201]
                )
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.create_data_set("DSN", test_case[0])
                self.assertEqual(
                    str(e_info.exception), "If 'like' is not specified, you must specify 'primary' or 'lrecl'."
                )

    @mock.patch("requests.Session.send")
    def test_create_default_dataset(self, mock_send_request):
        """Test creating a default data set sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_default_data_set("dataset_name", "partitioned")
        mock_send_request.assert_called_once()

    def test_create_default_dataset_parameterized(self):
        """Test create default dataset with different values"""
        test_values = [
            (("DSN", "partitioned"), True),
            (("DSN", "sequential"), True),
            (("DSN", "classic"), True),
            (("DSN", "c"), True),
            (("DSN", "binary"), True),
            (("DSN", "invalid"), False),
        ]

        files_test_profile = Files(self.test_profile)

        for test_case in test_values:
            files_test_profile.ds.request_handler.perform_request = mock.Mock()

            options = {
                "partitioned": {
                    "alcunit": "CYL",
                    "dsorg": "PO",
                    "primary": 1,
                    "dirblk": 5,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80,
                },
                "sequential": {
                    "alcunit": "CYL",
                    "dsorg": "PS",
                    "primary": 1,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80,
                },
                "classic": {
                    "alcunit": "CYL",
                    "dsorg": "PO",
                    "primary": 1,
                    "recfm": "FB",
                    "blksize": 6160,
                    "lrecl": 80,
                    "dirblk": 25,
                },
                "c": {
                    "dsorg": "PO",
                    "alcunit": "CYL",
                    "primary": 1,
                    "recfm": "VB",
                    "blksize": 32760,
                    "lrecl": 260,
                    "dirblk": 25,
                },
                "binary": {
                    "dsorg": "PO",
                    "alcunit": "CYL",
                    "primary": 10,
                    "recfm": "U",
                    "blksize": 27998,
                    "lrecl": 27998,
                    "dirblk": 25,
                },
            }

            if test_case[1]:
                files_test_profile.create_default_data_set(*test_case[0])
                custom_args = files_test_profile._create_custom_request_arguments()
                custom_args["json"] = options.get(test_case[0][1])
                custom_args["url"] = "https://mock-url.com:443/zosmf/restfiles/ds/{}".format(test_case[0][0])
                files_test_profile.ds.request_handler.perform_request.assert_called_once_with(
                    "POST", custom_args, expected_code=[201]
                )
            else:
                with self.assertRaises(ValueError) as e_info:
                    files_test_profile.create_default_data_set(*test_case[0])
                self.assertEqual(str(e_info.exception), "Invalid type for default data set.")
