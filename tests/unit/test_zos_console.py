"""Unit tests for the Zowe Python SDK z/OS Console package."""

import unittest
from zowe.zos_console_for_zowe_sdk import Console


class TestConsoleClass(unittest.TestCase):
    """Console class unit tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        self.session_details = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Console class."""
        console = Console(self.session_details)
        self.assertIsInstance(console, Console)