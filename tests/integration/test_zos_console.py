"""Integration tests for the Zowe Python SDK z/OS Console package."""

from integration.conftest import TestIsolatedEnv
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_console_for_zowe_sdk import Console


class TestConsoleIntegration(TestIsolatedEnv):
    """Console class integration tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        self.console = Console(test_profile)
        self.addCleanup(lambda: self.console.__exit__(None, None, None))

    def test_console_command_time_should_return_time(self):
        """Test the execution of the time command should return the current time"""
        command_output = self.console.issue_command("D T")
        self.assertTrue(command_output["cmd-response"].strip().startswith("IEE136I"))

    def test_get_response_should_return_messages(self):
        """Test that response message can be received from the console"""
        command_output = self.console.issue_command("D T")
        response = self.console.get_response(command_output["cmd-response-key"])
        self.assertTrue(hasattr(response, "cmd_response"))
