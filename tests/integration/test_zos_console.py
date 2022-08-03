"""Integration tests for the Zowe Python SDK z/OS Console package."""
import unittest
from zowe.zos_console_for_zowe_sdk import Console
from zowe.core_for_zowe_sdk import ProfileManager


class TestConsoleIntegration(unittest.TestCase):
    """Console class integration tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        test_profile = ProfileManager().load(profile_type="zosmf")
        self.console = Console(test_profile)
    
    def test_console_command_time_should_return_time(self):
        """Test the execution of the time command should return the current time"""
        command_output = self.console.issue_command("D T")
        self.assertTrue(command_output['cmd-response'].strip().startswith("IEE136I"))


