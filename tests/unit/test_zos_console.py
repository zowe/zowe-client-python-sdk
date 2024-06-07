"""Unit tests for the Zowe Python SDK z/OS Console package."""

import unittest
from unittest import mock
from unit.files.constants import profile
from zowe.zos_console_for_zowe_sdk import Console


class TestConsoleClass(unittest.TestCase):
    """Console class unit tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        self.session_details = profile

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Console class."""
        console = Console(self.session_details)
        self.assertIsInstance(console, Console)

    @mock.patch("requests.Session.send")
    def test_issue_command_makes_request_to_the_default_console(self, mock_send):
        """Issued command should be sent to the correct default console name if no name is specified"""
        is_console_name_correct = False
        def send_request_side_effect(self, **other_args):
            assert "/defcn" in self.url
            return mock.Mock(headers={"Content-type": "application/json"}, status_code=200)
        mock_send.side_effect = send_request_side_effect
        Console(self.session_details).issue_command("TESTCMD")

    @mock.patch("requests.Session.send")
    def test_issue_command_makes_request_to_the_custom_console(self, mock_send):
        """Issued command should be sent to the correct custom console name if the console name is specified"""
        is_console_name_correct = False
        def send_request_side_effect(self, **other_args):
            assert "/TESTCNSL" in self.url
            return mock.Mock(headers={"Content-type": "application/json"}, status_code=200)
        mock_send.side_effect = send_request_side_effect
        Console(self.session_details).issue_command("TESTCMD", "TESTCNSL")

    @mock.patch("requests.Session.send")
    def test_get_response_should_return_messages(self, mock_send_request):
        """Getting z/OS Console response messages on sending a response key"""
        mock_send_request.return_value = mock.Mock(headers={"Content-type": "application/json"}, status_code=200)
        Console(self.session_details).get_response("console-key")
        mock_send_request.assert_called_once()
