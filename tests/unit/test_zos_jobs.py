"""Unit tests for the Zowe Python SDK z/OS Jobs package."""

from datetime import datetime
from unittest import TestCase, mock

from zowe.zos_jobs_for_zowe_sdk import Jobs
from zowe.zos_jobs_for_zowe_sdk.response.jobs import JobResponse


class TestJobsClass(TestCase):
    """Jobs class unit tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        self.test_profile = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Jobs class."""
        jobs = Jobs(self.test_profile)
        self.assertIsInstance(jobs, Jobs)

    @mock.patch("requests.Session.send")
    def test_cancel_job(self, mock_send_request):
        """Test cancelling a job sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).cancel_job("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_hold_job(self, mock_send_request):
        """Test holding a job sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).hold_job("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_modified_version_hold_job(self, mock_send_request):
        """Test holding a job sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        with self.assertRaises(ValueError):
            Jobs(self.test_profile).hold_job("TESTJOB2", "JOB00084", modify_version="3.0")

    @mock.patch("requests.Session.send")
    def test_modified_version_release_job(self, mock_send_request):
        """Test holding a job sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        with self.assertRaises(ValueError):
            Jobs(self.test_profile).release_job("TESTJOB2", "JOB00084", modify_version="3.0")

    @mock.patch("requests.Session.send")
    def test_release_job(self, mock_send_request):
        """Test releasing a job sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).release_job("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_list_jobs(self, mock_send_request):
        """Test list jobs sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "class": "T",
                "files-url": "https://tsthost:443/zosmf/restjobs/jobs/TESTJI1XCFPLX01E1BE8B01.......%3A/files",
                "job-correlator": "TESTJI1XCFPLX01E1BE8B01.......:",
                "jobid": "TESTJI1",
                "jobname": "TESTJN1",
                "owner": "TSTUSR",
                "phase": 0,
                "phasename": "Job is on the hard copy queue",
                "retcode": "CC 0000",
                "status": "OUTPUT",
                "subsystem": "JES2",
                "type": "JOB",
                "url": "https://tsthost:443/zosmf/restjobs/jobs/TESTJI1XCFPLX01E1BE8B01.......%3A"
            }
        ]
        mock_send_request.return_value = mock_response
        result = Jobs(self.test_profile).list_jobs()
        assert len(result) == 1
        assert isinstance(result[0], JobResponse)
        self.assertEqual(mock_send_request.call_count, 1)

    @mock.patch("requests.Session.send")
    def test_list_jobs_ext(self, mock_send_request):
        """Test list jobs sends request with exec-data fetched"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "class": "T",
                "files-url": "https://tsthost:443/zosmf/restjobs/jobs/TESTJI2XCFPLX01E1BE8B01.......%3A/files",
                "job-correlator": "TESTJI2XCFPLX01E1BE8B01.......:",
                "jobid": "TESTJI2",
                "jobname": "TSTPREF",
                "owner": "TSTOWR",
                "phase": 0,
                "phasename": "Job is actively executing",
                "retcode": "CC 0000",
                "status": "ACTIVE",
                "subsystem": "JES2",
                "type": "JOB",
                "url": "https://tsthost:443/zosmf/restjobs/jobs/TESTJI2XCFPLX01E1BE8B01.......%3A",
                "exec-ended": "2025-11-05T13:52:21.920Z",
                "exec-member": "SMFT",
                "exec-started": "2025-11-05T13:52:21.310Z",
                "exec-submitted": "2025-11-05T13:52:21.290Z",
                "exec-system": "SYST"
            }
        ]
        mock_send_request.return_value = mock_response
        result = Jobs(self.test_profile).list_jobs("TSTOWR", "TSTPREF", 100, "SOME-USER-COR", True, 'ACTIVE')
        assert len(result) == 1
        assert isinstance(result[0], JobResponse)
        assert result[0].exec_system is not None
        assert isinstance(result[0].exec_submitted, datetime)
        self.assertEqual(mock_send_request.call_count, 1)

    @mock.patch("requests.Session.send")
    def test_change_job_class(self, mock_send_request):
        """Test changing the job class sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).change_job_class("TESTJOB2", "JOB00084", "A")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_modified_version_error(self, mock_send_request):
        """Test modified version should raise value error"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        with self.assertRaises(ValueError):
            Jobs(self.test_profile).change_job_class("TESTJOB2", "JOB00084", "A", modify_version="3.0")

    def test_cancel_job_modify_version_parameterized(self):
        """Test cancelling a job with different values sends the expected request"""
        test_values = [
            (("TESTJOB", "JOB$0010", "1.0"), True),
            (("TESTJOBN", "JOB00011", "2.0"), True),
            (("TESTJOB", "JOB00012", "2"), False),
            (("TESTJOBN", "JOB00113", "3.0"), False),
            (("TESTJOB", "JOB00013", "invalid"), False),
        ]

        jobs_test_object = Jobs(self.test_profile)

        for test_case in test_values:
            mock_response = mock.Mock()
            mock_response.json.return_value = {}
            jobs_test_object.request_handler.perform_request = mock_response.json

            if test_case[1]:
                jobs_test_object.cancel_job(*test_case[0])
                custom_args = jobs_test_object._create_custom_request_arguments()
                custom_args["json"] = {
                    "request": "cancel",
                    "version": test_case[0][2],
                }
                job_url = "{}/{}".format(test_case[0][0], test_case[0][1])
                job_url_adjusted = jobs_test_object._encode_uri_component(job_url)
                self.assertNotRegex(job_url_adjusted, r"\$")
                custom_args["url"] = "https://mock-url.com:443/zosmf/restjobs/jobs/{}".format(job_url_adjusted)
                jobs_test_object.request_handler.perform_request.assert_called_once_with(
                    "PUT", custom_args, expected_code=[202, 200]
                )
            else:
                with self.assertRaises(ValueError) as e_info:
                    jobs_test_object.cancel_job(*test_case[0])
                self.assertEqual(str(e_info.exception), 'Accepted values for modify_version: "1.0" or "2.0"')
