"""Unit tests for the Zowe Python SDK z/OSMF package."""

import unittest
from zowe.zosmf_for_zowe_sdk import Zosmf


class TestZosmfClass(unittest.TestCase):
    """Zosmf class unit tests."""

    def setUp(self):
        """Setup fixtures for Zosmf class."""
        self.connection_dict = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Zosmf class."""
        zosmf = Zosmf(self.connection_dict)
        self.assertIsInstance(zosmf, Zosmf)
