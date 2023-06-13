"""Integration tests for the Zowe Python SDK z/OS Files package."""
import unittest
import json
import os
from zowe.zos_files_for_zowe_sdk import Files
import urllib3
from zowe.core_for_zowe_sdk import ProfileManager

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'fixtures')
FILES_FIXTURES_PATH = os.path.join(FIXTURES_PATH, 'files.json')


class TestFilesIntegration(unittest.TestCase):
    """Files class integration tests."""

    def setUp(self):
        """Setup fixtures for Files class."""
        test_profile = ProfileManager().load(profile_type="zosmf")
        self.user_name = test_profile["user"]
        with open(FILES_FIXTURES_PATH, 'r') as fixtures_json:
            self.files_fixtures = json.load(fixtures_json)
        self.files = Files(test_profile)
        self.test_member_jcl = f'{self.files_fixtures["TEST_PDS"]}({self.files_fixtures["TEST_MEMBER"]})'
        self.test_member_generic = f'{self.files_fixtures["TEST_PDS"]}(TEST)'
        self.test1_zfs_file_system = f'{self.user_name}.{self.files_fixtures["TEST1_ZFS"]}'
        self.test2_zfs_file_system = f'{self.user_name}.{self.files_fixtures["TEST2_ZFS"]}'
        self.create_zfs_options = {"perms": 755,"cylsPri": 10,"cylsSec": 2,"timeout": 20, "volumes": ["VPMVSC"]}
        self.mount_zfs_file_system_options = {"fs-type": "ZFS", "mode": "rdonly"}

    def test_list_dsn_should_return_a_list_of_datasets(self):
        """Executing list_dsn method should return a list of found datasets."""
        
        scenarios = [
            {"attributes": False, "expected_attributes": ["dsname"]},
            {"attributes": True, "expected_attributes": ["dsname", "dsorg"]}
        ]
        
        for scenario in scenarios:

            # Get the command output
            command_output = self.files.list_dsn(self.files_fixtures["TEST_HLQ"], scenario["attributes"])
            
            # Assert that command_output['items'] is a list
            self.assertIsInstance(command_output['items'], list)
            
            # Assert that command_output['items'] contains at least one item
            self.assertGreater(len(command_output['items']), 0)
            
            # Assert that the first item in the list has 'dsname' defined
            first_item = command_output['items'][0]
            self.assertIn('dsname', first_item)
            
            # Assert that the first item in the list has the expected attributes defined
            attributes = first_item.keys()
            for expected_attr in scenario["expected_attributes"]:
                self.assertIn(expected_attr, attributes)
        
    def test_list_members_should_return_a_list_of_members(self):
        """Executing list_dsn_members should return a list of members."""
        command_output = self.files.list_dsn_members(self.files_fixtures["TEST_PDS"])
        self.assertIsInstance(command_output, list)

    def test_get_dsn_content_should_return_content_from_dataset(self):
        """Executing get_dsn_content should return content from dataset."""
        command_output = self.files.get_dsn_content(self.test_member_jcl)
        self.assertIsInstance(command_output['response'], str)

    def test_get_dsn_content_streamed_should_return_a_raw_response_content(self):
        """Executing get_dsn_content_streamed should return raw socket response from the server."""
        command_output = self.files.get_dsn_content_streamed(self.test_member_jcl)
        self.assertIsInstance(command_output, urllib3.response.HTTPResponse)

    def test_get_dsn_binary_content_streamed_should_return_a_raw_response_content(self):
        """Executing get_dsn_binary_content_streamed should return raw socket response from the server."""
        command_output = self.files.get_dsn_binary_content_streamed(self.test_member_jcl)
        self.assertIsInstance(command_output, urllib3.response.HTTPResponse)

    def test_write_to_dsn_should_be_possible(self):
        """Executing write_to_dsn should be possible."""
        command_output = self.files.write_to_dsn(self.test_member_generic, "HELLO WORLD")
        self.assertTrue(command_output['response'] == '')
    
    def test_mount_unmount_zfs_file_system(self):
        """Mounting a zfs filesystem should be possible"""
        username = self.user_name.lower()
        mount_point = f"/u/{username}/mount" # Assuming a dir called mount exist in zOS USS

        # Create a zfs file system
        zfs_file_system = self.files.create_zFS_file_system(self.test2_zfs_file_system, self.create_zfs_options)


        # Mount file system
        command_output = self.files.mount_file_system(self.test2_zfs_file_system, mount_point, self.mount_zfs_file_system_options)
        self.assertTrue(command_output['response'] == '')

        # List a zfs file system
        command_output = self.files.list_unix_file_systems(file_system_name=self.test2_zfs_file_system)
        self.assertTrue(len(command_output['items']) > 0)

        # Unmount file system
        command_output = self.files.unmount_file_system(self.test2_zfs_file_system)
        self.assertTrue(command_output['response'] == '')

        # Delete file system
        command_output = self.files.delete_zFS_file_system(self.test2_zfs_file_system)
        self.assertTrue(command_output['response'] == '')

    #TODO implement tests for download/upload datasets
