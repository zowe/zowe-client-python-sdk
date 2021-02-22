"""Unit tests for the Zowe Python SDK z/OS z/OS Jobs package."""

# Including necessary paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.zos_jobs.zowe.zos_jobs_for_zowe_sdk import Jobs


class TestJobsClass(unittest.TestCase):
    """Jobs class unit tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        self.connection_dict = {"host_url": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password"}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Jobs class."""
        jobs = Jobs(self.connection_dict)
        self.assertIsInstance(jobs, Jobs)