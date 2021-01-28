"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
from zowe.core_for_zowe_sdk import SdkApi
import os


class Jobs(SdkApi):
    """
    Class used to represent the base z/OSMF Jobs API.

    Attributes
    ----------
    connection
        Connection object
    """

    def __init__(self, connection):
        """
        Construct a Jobs object.

        Parameters
        ----------
        connection
            The connection object
        """
        super().__init__(connection, "/zosmf/restjobs/jobs/")

    def get_job_status(self, jobname, jobid):
        """Retrieve the status of a given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES

        Returns
        -------
        response_json
            A JSON object containing the status of the job on JES
        """
        custom_args = self.__create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def list_jobs(self, owner=None,  prefix="*", max_jobs=1000, user_correlator=None):
        """Retrieve list of jobs on JES based on the provided arguments.

        Parameters
        ----------
        owner: str, optional
            The job owner (default is zosmf user)
        prefix: str, optional
            The job name prefix (default is `*`)
        max_jobs: int, optional
            The maximum number of jobs in the output (default is 1000)
        user_correlator: str, optional
            The z/OSMF user correlator attribute (default is None)

        Returns
        -------
        json
            A JSON containing a list of jobs on JES queue based on the given parameters
        """
        custom_args = self.__create_custom_request_arguments()
        params = {"prefix": prefix, "max-jobs": max_jobs}
        params["owner"] = owner if owner else self.connection.user
        if user_correlator:
            params["user-correlator"] = user_correlator
        custom_args["params"] = params
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def submit_from_mainframe(self, jcl_path):
        """Submit a job from a given dataset.

        Parameters
        ----------
        jcl_path: str
            The dataset where the JCL is located

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """
        custom_args = self.__create_custom_request_arguments()
        request_body = '{"file": "//\'%s\'"}' % (jcl_path)
        custom_args["data"] = request_body
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[201]
        )
        return response_json

    def submit_from_local_file(self, jcl_path):
        """Submit a job from local file.

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
        json
            A JSON containing the result of the request execution
        """
        if os.path.isfile(jcl_path):
            jcl_file = open(jcl_path, "r")
            file_content = jcl_file.read()
            jcl_file.close()
            return self.submit_plaintext(file_content)
        else:
            raise FileNotFoundError("Provided argument is not a file path {}".format(jcl_path))

    def submit_plaintext(self, jcl):
        """Submit a job from plain text input.

        Parameters
        ----------
        jcl: str
            The plain text JCL to be submitted

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """
        custom_args = self.__create_custom_request_arguments()
        custom_args["data"] = str(jcl)
        custom_args['headers']['Content-Type'] = 'text/plain'
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[201]
        )
        return response_json
