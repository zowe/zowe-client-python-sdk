z/OS Jobs Package
=================

Contains APIs to interact with jobs on z/OS (using z/OSMF jobs REST endpoints).

API Examples
------------

<strong>A Jobs class method for canceling a job.</strong>  

```
    def cancel_job(self, jobname, jobid):        
        """Cancels the job

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
        custom_args["json"] = {"request": "cancel"}
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code = [202])
        return response_json
```

<strong>A Jobs class method for getting a job's status.</strong>  

```
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
```

<strong>A Jobs class method for retrieving a list of jobs based on their owner.</strong>   

```
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
```

<strong>A Jobs class method for submitting a job from a given dataset.</strong>  

```
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
```
