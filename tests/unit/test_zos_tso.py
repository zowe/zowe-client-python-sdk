"""Unit tests for the Zowe Python SDK z/OS TSO package."""

from unittest import TestCase, mock
from unit.files.constants import profile
from zowe.zos_tso_for_zowe_sdk import Tso


class TestTsoClass(TestCase):
    """Tso class unit tests."""

    def setUp(self):
        """Setup fixtures for Tso class."""
        self.test_profile = profile

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Tso class."""
        tso = Tso(self.test_profile)
        self.assertIsInstance(tso, Tso)

    @mock.patch("requests.Session.send")
    def test_issue_command(self, mock_send_request):
        """Test issuing a command sends a request"""
        fake_response = {"servletKey": None, "tsoData": "READY"}
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/json"}, status_code=200, json=lambda: fake_response
        )

        Tso(self.test_profile).issue_command("TIME")
        self.assertEqual(mock_send_request.call_count, 3)
