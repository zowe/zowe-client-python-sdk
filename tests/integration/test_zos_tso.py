"""Integration tests for the Zowe Python SDK z/OS Tso package."""

from integration.conftest import TestIsolatedEnv
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_tso_for_zowe_sdk import Tso
from zowe.zos_tso_for_zowe_sdk.response import IssueResponse


class TestTsoIntegration(TestIsolatedEnv):
    """Tso class integration tests."""

    def setUp(self):
        """Setup fixtures for Tso class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        self.tso = Tso(test_profile, {"account": "IZUACCT"})
        self.addCleanup(lambda: self.tso.__exit__(None, None, None))

    def test_issue_command_should_return_valid_response(self):
        """Executing the issue_command method should return a valid response from TSO"""
        command_output = self.tso.issue_command("TIME")
        self.assertIsInstance(command_output, IssueResponse)
        self.assertIn("TIME", command_output.tso_messages[0])

    def test_start_tso_session_should_return_a_session_key(self):
        """Executing the start_tso_session method should return a valid TSO session key"""
        command_output = self.tso.start_tso_session()
        self.assertIsNotNone(command_output)
        self.assertIsInstance(command_output, str)
        self.tso.end_tso_session(command_output)

    def test_ping_tso_session_should_return_success_for_valid_session(self):
        """Executing the ping_tso_session method shold return success for active session."""
        valid_session = self.tso.start_tso_session()
        command_output = self.tso.ping_tso_session(valid_session)
        self.assertEqual(command_output, "Ping successful")
        self.tso.end_tso_session(valid_session)

    def test_ping_tso_session_should_return_failure_for_invalid_session(self):
        """Executing the ping_tso_session method should return a failure message for invalid TSO session."""
        command_output = self.tso.ping_tso_session("INVALID")
        self.assertEqual(command_output, "Ping failed")
