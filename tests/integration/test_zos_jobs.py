"""Integration tests for the Zowe Python SDK z/OS Jobs package."""
import json
import os

from integration.conftest import TestIsolatedEnv
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_jobs_for_zowe_sdk import Jobs

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
JOBS_FIXTURES_JSON_JSON_PATH = os.path.join(FIXTURES_PATH, "jobs.json")
SAMPLE_JCL_FIXTURE_PATH = os.path.join(FIXTURES_PATH, "sample.jcl")


class TestJobsIntegration(TestIsolatedEnv):
    """Jobs class integration tests."""

    def setUp(self):
        """Setup fixtures for Jobs class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        with open(JOBS_FIXTURES_JSON_JSON_PATH, "r") as fixtures_json:
            self.jobs_fixtures_json = json.load(fixtures_json)
        self.jobs = Jobs(test_profile)
        self.addCleanup(lambda: self.jobs.__exit__(None, None, None))

    def test_get_job_status_should_return_the_status_of_a_job(self):
        """Executing the get_job_status method should return the status of a given job"""
        execution_output = self.jobs.submit_from_mainframe(self.jobs_fixtures_json["TEST_JCL_MEMBER"])
        jobname = execution_output["jobname"]
        jobid = execution_output["jobid"]
        command_output = self.jobs.get_job_status(jobname, jobid)
        self.assertIsNotNone(command_output["status"])

    def test_list_jobs_should_return_valid_spool_information(self):
        """Executing the list_jobs method should return a list of found jobs in JES spool."""
        command_output = self.jobs.list_jobs(owner=self.jobs_fixtures_json["TEST_JCL_OWNER"])
        self.assertIsInstance(command_output, list)

    def test_change_job_class(self):
        """Execute the change_jobs_class should execute successfully."""
        execution_output = self.jobs.submit_from_mainframe(self.jobs_fixtures_json["TEST_JCL_MEMBER"])
        jobname = execution_output["jobname"]
        jobid = execution_output["jobid"]
        classname = self.jobs_fixtures_json["TEST_JCL_CLASS"]
        command_output = self.jobs.change_job_class(jobname, jobid, classname)
        expected_class = self.jobs.get_job_status(jobname, jobid)
        self.assertEqual(expected_class["class"], classname)

    def test_submit_hold_and_release_job_should_execute_properly(self):
        """Execute the hold_job should execute successfully."""
        execution_output = self.jobs.submit_from_mainframe(self.jobs_fixtures_json["TEST_JCL_MEMBER"])
        jobname = execution_output["jobname"]
        jobid = execution_output["jobid"]
        command_output = self.jobs.submit_from_mainframe(self.jobs_fixtures_json["TEST_JCL_MEMBER"])
        command_output = self.jobs.hold_job(jobname, jobid)
        command_output = self.jobs.release_job(jobname, jobid)
        self.assertIsNotNone(command_output["jobid"])

    def test_submit_from_mainframe_should_execute_properly(self):
        """Executing the submit_from_mainframe method should execute successfully."""
        command_output = self.jobs.submit_from_mainframe(self.jobs_fixtures_json["TEST_JCL_MEMBER"])
        jobid = command_output["jobid"]
        self.assertIsNotNone(jobid)

    def test_submit_from_local_file_should_execute_properly(self):
        """Executing the submit_from_local_file method should execute successfully."""
        command_output = self.jobs.submit_from_local_file(SAMPLE_JCL_FIXTURE_PATH)
        jobid = command_output["jobid"]
        self.assertIsNotNone(jobid)

    def test_submit_plaintext_should_execute_properly(self):
        """Executing the submit_plaintext method should execute successfully."""
        command_output = self.jobs.submit_plaintext("\n".join(self.jobs_fixtures_json["TEST_JCL_CODE"]))
        jobid = command_output["jobid"]
        self.assertIsNotNone(jobid)
