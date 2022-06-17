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
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def cancel_job(self, jobname, jobid):
        """Cancels the a job

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES

        Returns
        -------
        response_json
            A JSON containing the result of the request execution
        """

        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code = [202])
        return response_json

    def delete_job(self, jobname, jobid):
        """Delete the given job on JES.

        Parameters
        ----------
        jobname: str
            The name of the job
        jobid: str
            The job id on JES

        Returns
        -------
        response_json
            A JSON containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/{}".format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("DELETE", custom_args, expected_code = [202])
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
        custom_args = self._create_custom_request_arguments()
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
        custom_args = self._create_custom_request_arguments()
        request_body = {"file": "//\'%s\'" % jcl_path}
        custom_args["json"] = request_body
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
        custom_args = self._create_custom_request_arguments()
        custom_args["data"] = str(jcl)
        custom_args["headers"] = {"Content-Type": "text/plain", "X-CSRF-ZOSMF-HEADER": ""}
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[201]
        )
        return response_json


    def get_spool_files(self,correlator):
        """Retrieve the spool files for a job identified by the correlator.

        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files".format(correlator)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json
        
    def get_jcl_text(self,correlator):
        """Retrieve the input JCL text for job with specified correlator
        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files/JCL/records".format(correlator)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json        

    def get_spool_file_contents(self,correlator,id):
        """Retrieve the contents of a single spool file from a job


        Parameters
        ----------
        correlator: str
            The correlator of the job. This is the value of the key 'job-correlator' in the status json

        id: str
            The id number of the spool file. This is returned in the get_spool_files return json

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """
        custom_args = self._create_custom_request_arguments()
        job_url = "{}/files/{}/records".format(correlator,id)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def get_job_output_as_files(self,status,output_dir):
        """This method will get all the spool files as well as the submitted jcl text in separate files in the specified
        output directory. The structure will be as follows:

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
        status: json
            The response json describing the job to be used. (i.e. from the last get_status call)

        output_dir: str
            The output directory where the output files will be stored. The directory does not have to exist yet

        Returns
        -------
        json
            A JSON containing the result of the request execution
        """

        _job_name   = status['jobname']
        _job_id     = status['jobid']
        _job_correlator = status['job-correlator']

        _output_dir = os.path.join(output_dir,_job_name,_job_id)
        os.makedirs(_output_dir,exist_ok=True)
        _output_file = os.path.join(output_dir,_job_name,_job_id,'jcl.txt')
        _data_spool_file = self.get_jcl_text(_job_correlator)
        _dataset_content = _data_spool_file['response']
        _out_file = open(_output_file,'w')
        _out_file.write(_dataset_content)
        _out_file.close()

        _spool = self.get_spool_files(_job_correlator)
        for _spool_file in _spool:
            _stepname = _spool_file['stepname']
            _ddname = _spool_file['ddname']
            _spoolfile_id = _spool_file['id']
            _output_dir = os.path.join(output_dir,_job_name,_job_id,_stepname)
            os.makedirs(_output_dir,exist_ok=True)
        
            _output_file = os.path.join(output_dir,_job_name,_job_id,_stepname,_ddname)
            _data_spool_file = self.get_spool_file_contents(_job_correlator,_spoolfile_id)
            _dataset_content = _data_spool_file['response']
            _out_file = open(_output_file,'w')
            _out_file.write(_dataset_content)
            _out_file.close()

        return
