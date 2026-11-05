"""Unit tests for the Zowe Python SDK z/OS Jobs package."""

import os
import shutil
import tempfile
from unittest import TestCase, mock

from zowe.zos_jobs_for_zowe_sdk import Jobs


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
    def test_get_job_status(self, mock_send_request):
        """Test getting job status sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {"jobname": "TESTJOB2", "jobid": "JOB00084"}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).get_job_status("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_delete_job(self, mock_send_request):
        """Test deleting a job sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 202
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Jobs(self.test_profile).delete_job("TESTJOB2", "JOB00084")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_spool_files(self, mock_send_request):
        """Test retrieving spool files sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "ddname": "JESMSGLG"}]
        mock_send_request.return_value = mock_response

        result = Jobs(self.test_profile).get_spool_files("J0000001")
        mock_send_request.assert_called_once()
        self.assertEqual(len(result), 1)

    @mock.patch("requests.Session.send")
    def test_get_jcl_text(self, mock_send_request):
        """Test retrieving JCL text sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.status_code = 200
        mock_response.text = "//JOBCARD JOB\n"
        mock_send_request.return_value = mock_response

        result = Jobs(self.test_profile).get_jcl_text("J0000001")
        mock_send_request.assert_called_once()
        self.assertEqual(result, "//JOBCARD JOB\n")

    @mock.patch("requests.Session.send")
    def test_get_spool_file_contents(self, mock_send_request):
        """Test retrieving spool file contents sends a request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.status_code = 200
        mock_response.text = "spool content"
        mock_send_request.return_value = mock_response

        result = Jobs(self.test_profile).get_spool_file_contents("J0000001", "2")
        mock_send_request.assert_called_once()
        self.assertEqual(result, "spool content")

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
                job_url_adjusted = jobs_test_object._encode_uri_path_for_zos(job_url)
                self.assertEqual(job_url_adjusted, job_url)
                custom_args["url"] = "https://mock-url.com:443/zosmf/restjobs/jobs/{}".format(job_url_adjusted)
                jobs_test_object.request_handler.perform_request.assert_called_once_with(
                    "PUT", custom_args, expected_code=[202, 200]
                )
            else:
                with self.assertRaises(ValueError) as e_info:
                    jobs_test_object.cancel_job(*test_case[0])
                self.assertEqual(str(e_info.exception), 'Accepted values for modify_version: "1.0" or "2.0"')

    def _mock_jobs_for_output(self, spool_files):
        """Build a Jobs object with the spool-fetching methods stubbed out."""
        jobs = Jobs(self.test_profile)
        jobs.get_jcl_text = mock.Mock(return_value="//JOBCARD JOB\n")
        jobs.get_spool_files = mock.Mock(return_value=spool_files)
        jobs.get_spool_file_contents = mock.Mock(side_effect=lambda c, sid: "content-{}\n".format(sid))
        return jobs

    def test_get_job_output_as_files_writes_expected_files(self):
        """Spool files and jcl.txt are written under output_dir/jobname/jobid."""
        out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out_dir, ignore_errors=True)
        jobs = self._mock_jobs_for_output([{"stepname": "STEP1", "ddname": "JESMSGLG", "id": "1"}])
        status = {"jobname": "MYJOB", "jobid": "JOB001", "job-correlator": "C1"}

        jobs.get_job_output_as_files(status, out_dir)

        jcl_file = os.path.join(out_dir, "MYJOB", "JOB001", "jcl.txt")
        spool_file = os.path.join(out_dir, "MYJOB", "JOB001", "STEP1", "JESMSGLG")
        self.assertTrue(os.path.isfile(jcl_file))
        self.assertTrue(os.path.isfile(spool_file))
        with open(spool_file, encoding="utf-8") as f:
            self.assertEqual(f.read(), "content-1\n")

    def test_get_job_output_as_files_rejects_absolute_component(self):
        """An absolute jobid must not escape output_dir and raises ValueError."""
        out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out_dir, ignore_errors=True)
        jobs = self._mock_jobs_for_output([])
        status = {"jobname": "MYJOB", "jobid": os.path.join(os.sep, "tmp", "pwn"), "job-correlator": "C2"}

        with self.assertRaises(ValueError):
            jobs.get_job_output_as_files(status, out_dir)

    def test_get_job_output_as_files_rejects_backtrack_component(self):
        """A stepname containing '..' must not escape output_dir and raises ValueError."""
        out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out_dir, ignore_errors=True)
        escaped = os.path.join("..", "..", "evil")
        jobs = self._mock_jobs_for_output([{"stepname": escaped, "ddname": "X", "id": "9"}])
        status = {"jobname": "MYJOB", "jobid": "JOB003", "job-correlator": "C3"}

        with self.assertRaises(ValueError):
            jobs.get_job_output_as_files(status, out_dir)
        self.assertFalse(os.path.exists(os.path.join(out_dir, "..", "..", "evil", "X")))

    def test_get_job_output_as_files_rejects_absolute_child(self):
        """An absolute leaf ddname is not honored even though join would drop the parent."""
        out_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out_dir, ignore_errors=True)
        abs_ddname = os.path.join(os.sep, "etc", "cron.d", "evil")
        jobs = self._mock_jobs_for_output([{"stepname": "STEP1", "ddname": abs_ddname, "id": "7"}])
        status = {"jobname": "MYJOB", "jobid": "JOB004", "job-correlator": "C4"}

        with self.assertRaises(ValueError):
            jobs.get_job_output_as_files(status, out_dir)
        self.assertFalse(os.path.exists(abs_ddname))
