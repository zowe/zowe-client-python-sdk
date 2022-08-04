"""Unit tests for the Zowe Python SDK z/OS Jobs package."""

import unittest
from zowe.zos_jobs_for_zowe_sdk import Jobs


class TestJobsClass(unittest.TestCase):
    """Jobs class unit tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        self.connection_dict = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Jobs class."""
        jobs = Jobs(self.connection_dict)
        self.assertIsInstance(jobs, Jobs)