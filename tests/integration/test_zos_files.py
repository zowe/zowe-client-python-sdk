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
        with open(FILES_FIXTURES_PATH, 'r') as fixtures_json:
            self.files_fixtures = json.load(fixtures_json)
        self.files = Files(test_profile)
        self.test_member_jcl = f'{self.files_fixtures["TEST_PDS"]}({self.files_fixtures["TEST_MEMBER"]})'
        self.test_member_generic = f'{self.files_fixtures["TEST_PDS"]}(TEST)'

    def test_list_dsn_should_return_a_list_of_datasets(self):
        """Executing list_dsn method should return a list of found datasets."""
        command_output = self.files.list_dsn(self.files_fixtures["TEST_HLQ"])
        self.assertIsInstance(command_output['items'], list)

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

    def test_create_zFS_file_system(self):
        """Executing create_zFS_file_system should be possible"""
        command_output = self.files.create_zFS_file_system(self.test_member_jcl)

    #TODO implement tests for download/upload datasets
