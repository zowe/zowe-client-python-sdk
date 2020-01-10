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

    def __init__(self, session_arguments):
        self.session_arguments = session_arguments

    def perform_request(self, method, request_arguments, expected_code=200):
        valid_requests = ['GET', 'POST', 'PUT', 'DELETE']
        if method not in valid_requests:
            raise InvalidRequestMethod(method)
        else:
            session = requests.Session()
            request_object = requests.Request(method=method, **request_arguments)
            prepared = session.prepare_request(request_object)
            self.response = session.send(prepared, **self.session_arguments)
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


