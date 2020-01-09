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

from .exceptions import UnexpectedStatus
from .exceptions import RequestFailed
from .exceptions import InvalidRequestMethod
import requests 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RequestHandler():

    def perform_request(self, method, request_arguments, expected_code=200):
        if method == 'get':
            self.response = requests.get(**request_arguments)
        elif method == 'post':
            self.response = requests.post(**request_arguments)
        elif method == 'put':

            self.response = requests.put(**request_arguments)
        elif method == 'delete':
            self.response = requests.delete(**request_arguments)
        else:
            raise InvalidRequestMethod(method)
        return self.validate_response(expected_code)


    def validate_response(self, expected_code):
        # Automatically checks if status code is between 200 and 400
        if self.response:
            if self.response.status_code != expected_code:
                raise UnexpectedStatus(expected_code, self.response.status_code, self.response.text)
            else:
                return self.response.json()
        else:
            output_str = str(self.response.request.url)
            output_str += "\n" + str(self.response.request.headers)
            output_str += "\n" +  str(self.response.request.body)
            raise RequestFailed(self.response.status_code, output_str)


