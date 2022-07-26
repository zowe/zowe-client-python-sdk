"""Unit tests for the Zowe Python SDK z/OS Files package."""

import unittest
from zowe.zos_files_for_zowe_sdk import Files


class TestFilesClass(unittest.TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.connection_dict = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorised": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Files class."""
        files = Files(self.connection_dict)
        self.assertIsInstance(files, Files)
