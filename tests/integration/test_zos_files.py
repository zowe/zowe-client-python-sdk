"""Integration tests for the Zowe Python SDK z/OS Files package."""

import json
import os
import unittest

import urllib3
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_files_for_zowe_sdk import Files
from zowe.zos_files_for_zowe_sdk.response.datasets import (
    DatasetListResponse,
    MemberListResponse,
)

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
FILES_FIXTURES_PATH = os.path.join(FIXTURES_PATH, "files.json")
SAMPLE_JCL_FIXTURE_PATH = os.path.join(FIXTURES_PATH, "sample.jcl")


class TestFilesIntegration(unittest.TestCase):
    """Files class integration tests."""

    def setUp(self):
        """Setup fixtures for Files class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        self.user_name = test_profile["user"]
        with open(FILES_FIXTURES_PATH, "r") as fixtures_json:
            self.files_fixtures = json.load(fixtures_json)
        self.files = Files(test_profile)
        self.addCleanup(lambda: self.files.__exit__(None, None, None))
        self.test_member_jcl = f'{self.files_fixtures["TEST_PDS"]}({self.files_fixtures["TEST_MEMBER"]})'
        self.test_member_generic = f'{self.files_fixtures["TEST_PDS"]}(TEST)'
        self.test_ds_upload = f'{self.files_fixtures["TEST_PDS"]}({self.files_fixtures["TEST_MEMBER_NEW"]})'
        self.test_uss_upload = self.files_fixtures["TEST_USS_NEW"]
        self.test1_zfs_file_system = f'{self.user_name}.{self.files_fixtures["TEST1_ZFS"]}'
        self.test2_zfs_file_system = f'{self.user_name}.{self.files_fixtures["TEST2_ZFS"]}'
        self.create_zfs_options = {"perms": 755, "cylsPri": 10, "cylsSec": 2, "timeout": 20}
        self.mount_zfs_file_system_options = {"fs-type": "ZFS", "mode": "rdonly"}

    def test_list_dsn_should_return_a_list_of_datasets(self):
        """Executing list_dsn method should return a list of found datasets."""

        scenarios = [
            {"attributes": False, "expected_attributes": ["dsname"]},
            {"attributes": True, "expected_attributes": ["dsname", "migr", "vol"]},
        ]

        for scenario in scenarios:
            # Get the command output
            command_output = self.files.ds.list(self.files_fixtures["TEST_HLQ"], scenario["attributes"])

            # Assert that command_output['items'] is a list
            self.assertIsInstance(command_output, DatasetListResponse)

            # Assert that command_output['items'] contains at least one item
            self.assertGreater(len(command_output["items"]), 0)

            # Assert that the first item in the list has 'dsname' defined
            first_item = command_output["items"][0]
            self.assertTrue(hasattr(first_item, "dsname"))

            # Assert that the first item in the list has the expected attributes defined
            attributes = dir(first_item)
            for expected_attr in scenario["expected_attributes"]:
                self.assertIn(expected_attr, attributes)

    def test_list_members_should_return_a_list_of_members(self):
        """Executing list_members should return a list of members."""
        command_output = self.files.ds.list_members(self.files_fixtures["TEST_PDS"])
        self.assertIsInstance(command_output, MemberListResponse)

    def test_get_content_should_return_content_from_dataset(self):
        """Executing gget_content should return content from dataset."""
        command_output = self.files.ds.get_content(self.test_member_jcl)
        self.assertIsInstance(command_output, str)

    def test_get_content_should_return_response_content(self):
        """Executing get_content should return response object from the server."""
        command_output = self.files.ds.get_content(self.test_member_jcl)
        self.assertIsInstance(command_output, str)

    def test_get_binary_content_should_return_response_content(self):
        """Executing get_binary_content should return response object from the server."""
        command_output = self.files.ds.get_binary_content(self.test_member_jcl)
        self.assertIsInstance(command_output, bytes)

    def test_get_file_content_streamed_should_return_response_content(self):
        """Executing get_binary_content should return response object from the server."""
        command_output = self.files.uss.get_content_streamed(self.files_fixtures["TEST_USS"])
        self.assertIsInstance(command_output.raw, urllib3.response.HTTPResponse)

    def test_write_should_be_possible(self):
        """Executing write should be possible."""
        command_output = self.files.ds.write(self.test_member_generic, "HELLO WORLD")
        self.assertTrue(command_output == None)

    def test_copy_uss_to_data_set_should_be_possible(self):
        """Executing copy_uss_to_data_set should be possible."""
        command_output = self.files.ds.copy_uss_to_data_set(
            self.files_fixtures["TEST_USS"], self.files_fixtures["TEST_PDS"] + "(TEST2)", replace=True
        )
        self.assertTrue(command_output == None)

    def test_copy_data_set_or_member_should_be_possible(self):
        """Executing copy_data_set_or_member should be possible."""
        test_case = {
            "from_dataset_name": self.files_fixtures["TEST_PDS"],
            "to_dataset_name": self.files_fixtures["TEST_PDS"],
            "from_member_name": self.files_fixtures["TEST_MEMBER"],
            "to_member_name": "TEST",
            "replace": True,
        }
        command_output = self.files.ds.copy_data_set_or_member(**test_case)
        self.assertTrue(command_output == None)

    def test_mount_unmount_zfs_file_system(self):
        """Mounting a zfs filesystem should be possible"""
        username = self.user_name.lower()
        mount_point = self.files_fixtures["TEST_USS_MOUNT"]

        # Create a zfs file system
        zfs_file_system = self.files.fs.create(self.test2_zfs_file_system, self.create_zfs_options)

        # Mount file system
        command_output = self.files.fs.mount(
            self.test2_zfs_file_system, mount_point, self.mount_zfs_file_system_options
        )
        self.assertTrue(command_output == None)

        # List a zfs file system
        command_output = self.files.fs.list(file_system_name=self.test2_zfs_file_system.upper())
        self.assertTrue(len(command_output["items"]) > 0)

        # Unmount file system
        command_output = self.files.fs.unmount(self.test2_zfs_file_system)
        self.assertTrue(command_output == None)

        # Delete file system
        command_output = self.files.fs.delete(self.test2_zfs_file_system)
        self.assertTrue(command_output == None)

    def test_upload_download_delete_dataset(self):
        self.files.ds.upload_file(SAMPLE_JCL_FIXTURE_PATH, self.test_ds_upload)
        self.files.ds.download(self.test_ds_upload, SAMPLE_JCL_FIXTURE_PATH + ".tmp")

        with open(SAMPLE_JCL_FIXTURE_PATH, "r") as in_file:
            old_file_content = in_file.read()
        with open(SAMPLE_JCL_FIXTURE_PATH + ".tmp", "r") as in_file:
            new_file_content = in_file.read().rstrip()
        self.assertEqual(old_file_content, new_file_content)

        self.files.ds.delete(self.files_fixtures["TEST_PDS"], member_name=self.files_fixtures["TEST_MEMBER_NEW"])
        os.unlink(SAMPLE_JCL_FIXTURE_PATH + ".tmp")

    def test_upload_download_delete_uss(self):
        self.files.uss.upload(SAMPLE_JCL_FIXTURE_PATH, self.test_uss_upload)
        self.files.uss.download(self.test_uss_upload, SAMPLE_JCL_FIXTURE_PATH + ".tmp")
        with open(SAMPLE_JCL_FIXTURE_PATH, "r") as in_file:
            old_file_content = in_file.read()
        with open(SAMPLE_JCL_FIXTURE_PATH + ".tmp", "r") as in_file:
            new_file_content = in_file.read()
        self.assertEqual(old_file_content, new_file_content)

        self.files.uss.delete(self.test_uss_upload)
        os.unlink(SAMPLE_JCL_FIXTURE_PATH + ".tmp")
