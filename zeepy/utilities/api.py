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
from .request_handler import RequestHandler
from .constants import constants

class ZosmfApi:

    def __init__(self, connection, default_url):
        self.connection = connection
        self.constants = constants
        self.default_service_url = default_url
        self.default_headers = {'Content-type': 'application/json'}
        self.request_endpoint = "https://{base_url}{service}".format(base_url=self.connection.zosmf_host, service=self.default_service_url)
        self.request_arguments = {'url': self.request_endpoint, 
                                  'auth': (self.connection.zosmf_user, self.connection.zosmf_password),
                                  'headers': self.default_headers
                                  }
        self.session_arguments = {'verify': self.connection.ssl_verification,
                                  'timeout': 30
                                  }
        self.request_handler = RequestHandler(self.session_arguments)

    def create_custom_request_arguments(self):
        return self.request_arguments.copy()

        