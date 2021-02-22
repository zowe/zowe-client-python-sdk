"""Integration tests for the Zowe Python SDK z/OS Console package."""
from decouple import config
import unittest
from zowe.zos_console_for_zowe_sdk import Console


class TestConsoleIntegration(unittest.TestCase):
    """Console class integration tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        test_profile = config('ZOWE_TEST_PROFILE')
        self.connection_dict = {"plugin_profile": test_profile}
        self.console = Console(self.connection_dict)
    
    def test_console_command_time_should_return_time(self):
        """Test the execution of the time command should return the current time"""
        command_output = self.console.issue_command("D T")
        self.assertTrue(command_output['cmd-response'].strip().startswith("IEE136I"))


