"""Unit tests for the Zowe Python SDK z/OS TSO package."""

import unittest
from zowe.zos_tso_for_zowe_sdk import Tso


class TestTsoClass(unittest.TestCase):
    """Tso class unit tests."""

    def setUp(self):
        """Setup fixtures for Tso class."""
        self.connection_dict = {"host": "mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Tso class."""
        tso = Tso(self.connection_dict)
        self.assertIsInstance(tso, Tso)