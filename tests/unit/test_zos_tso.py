"""Unit tests for the Zowe Python SDK z/OS TSO package."""

from unittest import TestCase, mock

from zowe.zos_tso_for_zowe_sdk import Tso


class TestTsoClass(TestCase):
    """Tso class unit tests."""

    def setUp(self):
        """Setup fixtures for Tso class."""
        self.test_profile = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Tso class."""
        tso = Tso(self.test_profile)
        self.assertIsInstance(tso, Tso)

    @mock.patch("requests.Session.send")
    def test_issue_command(self, mock_send_request):
        """Test issuing a command sends a request"""
        expected = ["READY", "GO"]
        message = {"TSO MESSAGE": {"DATA": expected[0]}}
        message2 = {"TSO MESSAGE": {"DATA": expected[1]}}
        fake_responses = [
            mock.Mock(
                headers={"Content-Type": "application/json"},
                status_code=200,
                json=lambda: {"servletKey": None, "tsoData": [message]},
            ),
            mock.Mock(
                headers={"Content-Type": "application/json"},
                status_code=200,
                json=lambda: {"servletKey": None, "tsoData": [message]},
            ),
            mock.Mock(
                headers={"Content-Type": "application/json"},
                status_code=200,
                json=lambda: {"servletKey": None, "tsoData": [message2]},
            ),
            mock.Mock(
                headers={"Content-Type": "application/json"},
                status_code=200,
                json=lambda: {"servletKey": None, "tsoData": ["TSO PROMPT"]},
            ),
            mock.Mock(
                headers={"Content-Type": "application/json"},
                status_code=200,
                json=lambda: {"servletKey": None},
            ),
        ]

        mock_send_request.side_effect = fake_responses

        result = Tso(self.test_profile).issue_command("TIME").tso_messages
        self.assertEqual(result, expected)
        self.assertEqual(mock_send_request.call_count, 5)
