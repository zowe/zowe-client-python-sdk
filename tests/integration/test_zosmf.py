"""Integration tests for the Zowe Python SDK z/OSMF package."""

from integration.conftest import TestIsolatedEnv
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zosmf_for_zowe_sdk import Zosmf
from zowe.zosmf_for_zowe_sdk.response import ZosmfResponse


class TestZosmfIntegration(TestIsolatedEnv):
    """Zosmf class integration tests."""

    def setUp(self):
        """Setup fixtures for Zosmf class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        self.zosmf = Zosmf(test_profile)
        self.addCleanup(lambda: self.zosmf.__exit__(None, None, None))

    def test_get_info_should_return_valid_response(self):
        """Executing the get_info method should return a valid response."""
        command_output = self.zosmf.get_info()
        self.assertIsInstance(command_output, ZosmfResponse)

    def test_list_systems_should_return_valid_response(self):
        """Executing the list_systems method should return a valid response."""
        command_output = self.zosmf.list_systems()
        self.assertIsInstance(command_output, ZosmfResponse)
