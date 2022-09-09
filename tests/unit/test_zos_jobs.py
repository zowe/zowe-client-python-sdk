"""Unit tests for the Zowe Python SDK z/OS Jobs package."""

from unittest import TestCase, mock
from zowe.zos_jobs_for_zowe_sdk import Jobs


class TestJobsClass(TestCase):
    """Jobs class unit tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        self.test_profile = {
            "host": "https://mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True
        }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Jobs class."""
        jobs = Jobs(self.test_profile)
        self.assertIsInstance(jobs, Jobs)

    @mock.patch("requests.Session.send")
    def test_delete_job(self, mock_send_request):
        """Test deleting a job sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Jobs(self.test_profile).delete_job("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    def test_delete_job_modify_version_parameterized(self):
        """Test deleting a job with different values sends the expected request"""
        test_values = [
            (("TESTJOB", "JOB00085", "1.0"), True),
            (("TESTJOBN", "JOB00083","2.0"), True),
            (("TESTJOBN", "JOB00111", "2"), False),
            (("TESTJOB", "JOB00011", "3.0"), False),
            (("TESTJOB", "JOB00010", "invalid"), False),
        ]

        jobs_test_object = Jobs(self.test_profile)

        for test_case in test_values:
            jobs_test_object.request_handler.perform_request = mock.Mock()

            if test_case[1]:
                jobs_test_object.delete_job(*test_case[0])
                custom_args = jobs_test_object._create_custom_request_arguments()

                custom_args["url"] = "https://https://mock-url.com:443/zosmf/restjobs/jobs/{}/{}".format(test_case[0][0], test_case[0][1])
                jobs_test_object.request_handler.perform_request.assert_called_once_with("DELETE", custom_args, expected_code=[202, 200])
            else:
                with self.assertRaises(ValueError) as e_info:
                    jobs_test_object.delete_job(*test_case[0])
                self.assertEqual(str(e_info.exception), 'Accepted values: "1.0" or "2.0".')
