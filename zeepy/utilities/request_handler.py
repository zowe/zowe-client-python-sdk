'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''

from .exceptions import UnexpectedStatus
from .exceptions import RequestFailed
from .exceptions import InvalidRequestMethod
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestHandler():

    def __init__(self, session_arguments: dict):
        self.session_arguments = session_arguments

    def perform_request(self, method: str, request_arguments: dict, expected_code: int = 200) -> dict:
        valid_requests = ['GET', 'POST', 'PUT', 'DELETE']
        if method not in valid_requests:
            raise InvalidRequestMethod(method)
        else:
            session = requests.Session()
            request_object = requests.Request(method=method, **request_arguments)
            prepared = session.prepare_request(request_object)
            self.response = session.send(prepared, **self.session_arguments)
        return self.validate_response(expected_code)

    def validate_response(self, expected_code: int) -> dict:
        # Automatically checks if status code is between 200 and 400
        if self.response:
            if self.response.status_code != expected_code:
                raise UnexpectedStatus(expected_code, self.response.status_code, self.response.text)
            else:
                try:
                    return self.response.json()
                except:
                    return {'response': self.response.text}
        else:
            output_str = str(self.response.request.url)
            output_str += "\n" + str(self.response.request.headers)
            output_str += "\n" + str(self.response.request.body)
            raise RequestFailed(self.response.status_code, output_str)
