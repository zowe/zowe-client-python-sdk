"""Unit tests for the Zowe Python SDK z/OS Files package."""

import re
from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Datasets, Files, exceptions


class TestFilesClass(TestCase):
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
    def test_create_zfs_file_system(self, mock_send_request):
        """Test creating a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).create_zfs_file_system(
            "file_system_name", {"perms": 100, "cylsPri": 16777213, "cylsSec": 16777215}
        )
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_delete_zfs_file_system(self, mock_send_request):
        """Test deleting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_zfs_file_system("file_system_name")
        mock_send_request.assert_called_once()

    def test_invalid_permission(self):
        """Test that the correct exception is raised when an invalid permission option is provided"""
        with self.assertRaises(exceptions.InvalidPermsOption) as e_info:
            Files(self.test_profile).create_zfs_file_system(
                "file_system_name", {"perms": -1, "cylsPri": 16777213, "cylsSec": 16777215}
            )
        self.assertEqual(str(e_info.exception), "Invalid zos-files create command 'perms' option: -1")

    def test_invalid_memory_allocation(self):
        """Test that the correct exception is raised when an invalid memory allocation option is provided"""
        with self.assertRaises(exceptions.MaxAllocationQuantityExceeded) as e_info:
            Files(self.test_profile).create_zfs_file_system(
                "file_system_name", {"perms": 775, "cylsPri": 1677755513, "cylsSec": 16777215}
            )
        self.assertEqual(str(e_info.exception), "Maximum allocation quantity of 16777215 exceeded")

    @mock.patch("requests.Session.send")
    def test_mount_zFS_file_system(self, mock_send_request):
        """Test mounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).mount_file_system("file_system_name", "mount_point")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_unmount_zFS_file_system(self, mock_send_request):
        """Test unmounting a zfs sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        try:
            Files(self.test_profile).unmount_file_system("file_system_name")
        except TypeError:
            mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_list_fs(self, mock_send_request):
        """Test list DSN sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(self.test_profile).list_unix_file_systems()
        mock_send_request.assert_called()

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_added_in_range(self, mock_send_request):
        """responseTimeout in profile should set X-IBM-Response-Timeout header (5-600)."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = 120  # valid range per IBM docs
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertEqual(prepared.headers.get("X-IBM-Response-Timeout"), "120")  # seconds [web:102]

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_clamped_low(self, mock_send_request):
        """responseTimeout below 5 should be clamped to 5."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = 1  # below lower bound 5 [web:102]
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertEqual(prepared.headers.get("X-IBM-Response-Timeout"), "5")  # clamped [web:102]

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_clamped_high(self, mock_send_request):
        """responseTimeout above 600 should be clamped to 600."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = 1000  # above upper bound 600 [web:102]
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertEqual(prepared.headers.get("X-IBM-Response-Timeout"), "600")  # clamped [web:102]

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_ignored_when_async_threshold_present(self, mock_send_request):
        """If async threshold is provided, omit X-IBM-Response-Timeout since z/OSMF ignores it."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = 120
        profile["X-IBM-Async-Threshold"] = 3  # any 0–60 value per docs [web:102]
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertIsNone(prepared.headers.get("X-IBM-Response-Timeout"))  # ignored when async header present [web:102]

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_string_value_is_accepted(self, mock_send_request):
        """responseTimeout provided as string should be coerced to int and applied."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = "45"
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertEqual(prepared.headers.get("X-IBM-Response-Timeout"), "45")  # seconds [web:102]

    @mock.patch("requests.Session.send")
    def test_files_response_timeout_header_invalid_value_is_skipped(self, mock_send_request):
        """Non-integer responseTimeout should not set the header."""
        profile = dict(self.test_profile)
        profile["responseTimeout"] = "abc"  # invalid
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(profile).list_unix_file_systems()

        prepared = mock_send_request.call_args[0][0]
        self.assertIsNone(prepared.headers.get("X-IBM-Response-Timeout"))  # not set on invalid value [web:102]

