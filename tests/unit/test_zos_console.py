"""Unit tests for the Zowe Python SDK z/OS Console package."""

import unittest
from unittest import mock
from zowe.zos_console_for_zowe_sdk import Console


class TestConsoleClass(unittest.TestCase):
    """Console class unit tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        self.session_details = {"host": "mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Console class."""
        console = Console(self.session_details)
        self.assertIsInstance(console, Console)
    
    @mock.patch('requests.Session.send')
    def test_get_response_should_return_messages(self, mock_send_request):
       """Getting z/OS Console response messages on sending a response key"""
       mock_send_request.return_value = mock.Mock(headers={"Content-type": "application/json"}, status_codes=200)

       Console(self.session_details).get_response("console-key")
       mock_send_request.assert_called_once()
