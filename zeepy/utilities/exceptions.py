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


class InvalidRequestMethod(Exception):

    def __init__(self, input_method):
        super().__init__("Invalid HTTP method input {}".format(input_method))

class UnexpectedStatus(Exception):

    def __init__(self, expected, received, request_output):
        super().__init__("The status code from z/OSMF was {} it was expected {}. \n {}".format(received, expected, request_output))

class RequestFailed(Exception):

    def __init__(self, status_code, request_output):
        super().__init__("HTTP Request has failed with status code {}. \n {}".format(status_code, request_output))


