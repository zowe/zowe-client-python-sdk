'''
Copyright 2020 Guilherme Cartier de Palma

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License. 
'''

from ..utilities import ZosmfApi
import requests 
import os

class Jobs(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/restjobs/jobs/')

    def get_job_status(self, jobname, jobid):
        job_url = '{}/{}'.format(jobname, jobid)
        request_url = "{}{}".format(self.request_endpoint, job_url)
        response = requests.get(request_url,
                                auth=(self.connection.zosmf_user, self.connection.zosmf_password),
                                headers=self.default_headers, 
                                verify=self.connection.ssl_verification,
                                timeout=30)
        return self.response_handler.validate_response(response)

    def list_jobs(self, owner=None, prefix='*', max_jobs=1000, user_correlator=None):
        if owner:
            params = {'owner': owner, 'prefix': prefix, 'max-jobs': max_jobs}
        else:
            params = {'owner': self.connection.zosmf_user, 'prefix': prefix, 'max-jobs': max_jobs}
        if user_correlator:
            params['user-correlator'] = user_correlator
        response = requests.get(self.request_endpoint,
                                auth=(self.connection.zosmf_user, self.connection.zosmf_password),
                                headers=self.default_headers, 
                                verify=self.connection.ssl_verification,
                                timeout=30)
        return self.response_handler.validate_response(response)

    def submit_from_mainframe(self, jcl_path):
        request_body = '{"file": "//\'%s\'"}' % (jcl_path)
        response = requests.put(self.request_endpoint,
                                data=request_body,
                                auth=(self.connection.zosmf_user, self.connection.zosmf_password),
                                headers=self.default_headers, 
                                verify=self.connection.ssl_verification,
                                timeout=30)
        return self.response_handler.validate_response(response, 201)

    def submit_from_local_file(self, jcl_path):
        if os.path.isfile(jcl_path):
            jcl_file = open(jcl_path, 'r')
            file_content = jcl_file.read()
            jcl_file.close()
            return self.submit_plaintext(file_content)
        else:
            raise FileNotFoundError("Provided argument is not a file path {}".format(jcl_path))

    def submit_plaintext(self, jcl):
        response = requests.put(self.request_endpoint,
                                data=str(jcl),
                                auth=(self.connection.zosmf_user, self.connection.zosmf_password),
                                headers={'Content-Type': 'text/plain'}, 
                                verify=self.connection.ssl_verification,
                                timeout=30)
        return self.response_handler.validate_response(response, 201)
