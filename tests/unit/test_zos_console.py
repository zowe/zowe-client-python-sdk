"""Unit tests for the Zowe Python SDK z/OS Console package."""

# Including necessary paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.zos_console.zowe.zos_console_for_zowe_sdk import Console


class TestConsoleClass(unittest.TestCase):
    """Console class unit tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        self.connection_dict = {"host_url": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password"}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Console class."""
        console = Console(self.connection_dict)
        self.assertIsInstance(console, Console)