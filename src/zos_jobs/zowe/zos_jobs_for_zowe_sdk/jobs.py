"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
from typing import List, Optional

from zowe.core_for_zowe_sdk import SdkApi

from .response import JobResponse, SpoolResponse, StatusResponse


class Jobs(SdkApi):
    """
    Class used to represent the base z/OSMF Jobs API.

    It includes all operations related to datasets.

    Parameters
    ----------
    connection : dict
        A profile for connection in dict (json) format
    """

    def __init__(self, connection: dict):
        super().__init__(connection, "/zosmf/restjobs/jobs/", logger_name=__name__)

    def get_job_status(self, jobname: str, jobid: str) -> JobResponse:
        """
        Retrieve the status of a given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES

        Returns
        -------
        JobResponse
            A JSON object containing the status of the job on JES
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return JobResponse(response_json)

    def cancel_job(self, jobname: str, jobid: str, modify_version: str = "2.0") -> StatusResponse:
        """
        Cancel a job.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        modify_version: str
            Default ("2.0") specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Raises
        ------
        ValueError
            Thrown if the modify_version is invalid

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        if modify_version not in ("1.0", "2.0"):
            self.logger.error('Modify version not accepted; Must be "1.0" or "2.0"')
            raise ValueError('Accepted values for modify_version: "1.0" or "2.0"')

        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        custom_args["json"] = {"request": "cancel", "version": modify_version}

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[202, 200])
        return StatusResponse(response_json)

    def delete_job(self, jobname: str, jobid: str, modify_version: str = "2.0") -> StatusResponse:
        """
        Delete the given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        modify_version: str
            Default ("2.0") specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Raises
        ------
        ValueError
            Thrown if the modify_version is invalid

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        if modify_version not in ("1.0", "2.0"):
            self.logger.error('Modify version not accepted; Must be "1.0" or "2.0"')
            raise ValueError('Accepted values for modify_version: "1.0" or "2.0"')

        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        custom_args["headers"]["X-IBM-Job-Modify-Version"] = modify_version

        response_json = self.request_handler.perform_request("DELETE", custom_args, expected_code=[202, 200])
        return StatusResponse(response_json)

    def _issue_job_request(self, req: dict, jobname: str, jobid: str, modify_version: str) -> StatusResponse:
        """
        Issue a job request.

        Parameters
        ----------
        req: dict
            A json representation of the request
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        modify_version: str
            "2.0" specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        custom_args["json"] = {**req, "version": modify_version}

        custom_args["headers"]["X-IBM-Job-Modify-Version"] = modify_version

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[202, 200])
        return StatusResponse(response_json)

    def change_job_class(
        self, jobname: str, jobid: str, class_name: str, modify_version: str = "2.0"
    ) -> StatusResponse:
        """
        Change the job class.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        class_name: str
            The name of class to be set to
        modify_version: str
            Default ("2.0") specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Raises
        ------
        ValueError
            Thrown if the modify_version is invalid

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        if modify_version not in ("1.0", "2.0"):
            self.logger.error('Accepted values for modify_version: "1.0" or "2.0"')
            raise ValueError('Accepted values for modify_version: "1.0" or "2.0"')

        response = self._issue_job_request({"class": class_name}, jobname, jobid, modify_version)
        return response

    def hold_job(self, jobname: str, jobid: str, modify_version: str = "2.0") -> StatusResponse:
        """
        Hold the given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        modify_version: str
            Default ("2.0") specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Raises
        ------
        ValueError
            Thrown if the modify_version is invalid

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        if modify_version not in ("1.0", "2.0"):
            self.logger.error('Accepted values for modify_version: "1.0" or "2.0"')
            raise ValueError('Accepted values for modify_version: "1.0" or "2.0"')

        response = self._issue_job_request({"request": "hold"}, jobname, jobid, modify_version)
        return response

    def release_job(self, jobname: str, jobid: str, modify_version: str = "2.0") -> StatusResponse:
        """
        Release the given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES
        modify_version: str
            Default ("2.0") specifies that the request is to be processed synchronously.
            For asynchronous processing - change the value to "1.0"

        Raises
        ------
        ValueError
            Thrown if the modify_version is invalid

        Returns
        -------
        StatusResponse
            A JSON object containing the result of the request execution
        """
        if modify_version not in ("1.0", "2.0"):
            self.logger.error('Modify version not accepted; Must be "1.0" or "2.0"')
            raise ValueError('Accepted values for modify_version: "1.0" or "2.0"')

        response = self._issue_job_request({"request": "release"}, jobname, jobid, modify_version)
        return response

    def list_jobs(
        self,
        owner: Optional[str] = None,
        prefix: str = "*",
        max_jobs: int = 1000,
        user_correlator: Optional[str] = None,
    ) -> List[JobResponse]:
        """
        Retrieve list of jobs on JES based on the provided arguments.

        Parameters
        ----------
        owner: Optional[str]
            The job owner (default is zosmf user)
        prefix: str
            The job name prefix (default is `*`)
        max_jobs: int
            The maximum number of jobs in the output (default is 1000)
        user_correlator: Optional[str]
            The z/OSMF user correlator attribute (default is None)

        Returns
        -------
        List[JobResponse]
            A list of jobs on JES queue based on the given parameters
        """
        custom_args = self._create_custom_request_arguments()
        params = {"prefix": prefix, "max-jobs": max_jobs}
        if owner:
            params["owner"] = owner
        if user_correlator:
            params["user-correlator"] = user_correlator
        custom_args["params"] = params
        response_json = self.request_handler.perform_request("GET", custom_args)
        response = []
        for item in response_json:
            response.append(JobResponse(item))
        return response

    def submit_from_mainframe(self, jcl_path: str) -> JobResponse:
        """
        Submit a job from a given dataset.

        Parameters
        ----------
        jcl_path: str
            The dataset where the JCL is located

        Returns
        -------
        JobResponse
            A JSON object containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        request_body = {"file": "//'%s'" % jcl_path}
        custom_args["json"] = request_body
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[201])
        return JobResponse(response_json)

    def submit_from_local_file(self, jcl_path: str) -> JobResponse:
        """
        Submit a job from local file.

        This function will internally call the `submit_plaintext`
        function in order to submit the contents of the given input
        file

        Parameters
        ----------
        jcl_path: str
            Path to the local file where the JCL is located

        Raises
        ------
        FileNotFoundError
            If the local file provided is not found

        Returns
        -------
        JobResponse
            A JSON object containing the result of the request execution
        """
        if os.path.isfile(jcl_path):
            with open(jcl_path, "r", encoding="utf-8") as jcl_file:
                file_content = jcl_file.read()
            return self.submit_plaintext(file_content)
        else:
            self.logger.error("Provided argument is not a file path {}".format(jcl_path))
            raise FileNotFoundError("Provided argument is not a file path {}".format(jcl_path))

    def submit_plaintext(self, jcl: str) -> JobResponse:
        """
        Submit a job from plain text input.

        Parameters
        ----------
        jcl: str
            The plain text JCL to be submitted

        Returns
        -------
        JobResponse
            A JSON object containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["data"] = str(jcl)
        custom_args["headers"] = {"Content-Type": "text/plain", "X-CSRF-ZOSMF-HEADER": ""}
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[201])
        return JobResponse(response_json)

    def get_spool_files(self, correlator: str) -> List[SpoolResponse]:
        """
        Retrieve the spool files for a job identified by the correlator.

        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        Returns
        -------
        List[SpoolResponse]
            A JSON object containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files".format(correlator)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        response = []
        for item in response_json:
            response.append(SpoolResponse(item))
        return response

    def get_jcl_text(self, correlator: str) -> str:
        """
        Retrieve the input JCL text for job with specified correlator.

        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        Returns
        -------
        str
            A str object containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files/JCL/records".format(correlator)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def get_spool_file_contents(self, correlator: str, id: str) -> str:
        """
        Retrieve the contents of a single spool file from a job.

        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        id: str
            The id number of the spool file. This is returned in the get_spool_files return json

        Returns
        -------
        str
            The contents of the spool file
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files/{}/records".format(correlator, id)
        request_url = "{}{}".format(self._request_endpoint, self._encode_uri_component(job_url))
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def get_job_output_as_files(self, status: dict, output_dir: str):
        """
        Get all spool files and submitted jcl text in separate files in the specified output directory.

        The structure will be as follows:
        --<output directory>
        |
        file: jcl.txt
        |
        dir: jobname
            |
                    dir: jobid
                        |
                        dir: stepname
                            |
                            file: spool file <nn>
                            ...

        Parameters
        ----------
        status: dict
            The response json describing the job to be used. (i.e. from the last get_status call)
        output_dir: str
            The output directory where the output files will be stored. The directory does not have to exist yet
        """
        job_name = status["jobname"]
        job_id = status["jobid"]
        job_correlator = status["job-correlator"]

        output_dir = os.path.join(output_dir, job_name, job_id)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, job_name, job_id, "jcl.txt")
        data_spool_file = self.get_jcl_text(job_correlator)
        dataset_content = data_spool_file
        with open(output_file, "w", encoding="utf-8") as out_file:
            out_file.write(dataset_content)

        spool = self.get_spool_files(job_correlator)
        for spool_file in spool:
            stepname = spool_file["stepname"]
            ddname = spool_file["ddname"]
            spoolfile_id = spool_file["id"]
            output_dir = os.path.join(output_dir, job_name, job_id, stepname)
            os.makedirs(output_dir, exist_ok=True)

            output_file = os.path.join(output_dir, job_name, job_id, stepname, ddname)
            data_spool_file = self.get_spool_file_contents(job_correlator, spoolfile_id)
            dataset_content = data_spool_file
            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(dataset_content)
