"""Unit tests for the Zowe Python SDK z/OS Jobs package."""

from unittest import TestCase, mock
from zowe.zos_jobs_for_zowe_sdk import Jobs


class TestJobsClass(TestCase):
    """Jobs class unit tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        self.test_profile = {"host": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password",
                                "port": 443,
                                "rejectUnauthorized": True
                                }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Jobs class."""
        jobs = Jobs(self.test_profile)
        self.assertIsInstance(jobs, Jobs)
    
    @mock.patch('requests.Session.send')
    def test_cancel_job(self, mock_send_request):
        """Test cancelling a job sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Jobs(self.test_profile).cancel_job("TESTJOB2","JOB00084")
        mock_send_request.assert_called_once()
