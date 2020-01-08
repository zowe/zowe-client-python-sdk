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

from ..exceptions import UnexpectedStatus
from ..exceptions import RequestFailed

class ResponseHandler():

    def validate_response(self, response, expected_code=200):
        if response:
            if response.status_code != expected_code:
                raise UnexpectedStatus("The status code from z/OSMF was {} it was expected {}. \n {}".format(response.status_code, expected_code, response.text))
            else:
                return response.json()
        else:
            raise RequestFailed("HTTP Request has failed with status code {}. \n {}".format(response.status_code, response.text))