'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''
from ..utilities import ZosmfApi
import os

class Jobs(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/restjobs/jobs/')

    def get_job_status(self, jobname, jobid):
        custom_args = self.create_custom_request_arguments()
        job_url = '{}/{}'.format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        custom_args['url'] = request_url
        response_json = self.request_handler.perform_request('GET', custom_args)
        return response_json

    def list_jobs(self, owner=None, prefix='*', max_jobs=1000, user_correlator=None):
        custom_args = self.create_custom_request_arguments()
        params = {'prefix': prefix, 'max-jobs': max_jobs}
        params['owner'] = owner if owner else self.connection.zosmf_user
        if user_correlator: params['user-correlator'] = user_correlator 
        custom_args['params'] = params
        response_json = self.request_handler.perform_request('GET', custom_args)
        return response_json

    def submit_from_mainframe(self, jcl_path):
        custom_args = self.create_custom_request_arguments()
        request_body = '{"file": "//\'%s\'"}' % (jcl_path)
        custom_args['data'] = request_body
        response_json = self.request_handler.perform_request('PUT', custom_args, expected_code=201)
        return response_json

    def submit_from_local_file(self, jcl_path):
        if os.path.isfile(jcl_path):
            jcl_file = open(jcl_path, 'r')
            file_content = jcl_file.read()
            jcl_file.close()
            return self.submit_plaintext(file_content)
        else:
            raise FileNotFoundError("Provided argument is not a file path {}".format(jcl_path))

    def submit_plaintext(self, jcl):
        custom_args = self.create_custom_request_arguments()
        custom_args['data'] = str(jcl)
        custom_args['headers'] = {'Content-Type': 'text/plain'}
        response_json = self.request_handler.perform_request('PUT', custom_args, expected_code=201)
        return response_json
