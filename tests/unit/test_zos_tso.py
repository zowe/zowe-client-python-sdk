"""Unit tests for the Zowe Python SDK z/OS TSO package."""

# Including necessary paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.zos_tso.zowe.zos_tso_for_zowe_sdk import Tso


class TestTsoClass(unittest.TestCase):
    """Tso class unit tests."""

    def setUp(self):
        """Setup fixtures for Tso class."""
        self.connection_dict = {"host_url": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password"}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Tso class."""
        tso = Tso(self.connection_dict)
        self.assertIsInstance(tso, Tso)