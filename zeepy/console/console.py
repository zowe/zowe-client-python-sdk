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

class Console(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/restconsoles/consoles/defcn')
    
    def issue_command(self, command, console=None):
        custom_args = self.create_custom_request_arguments()
        request_body = '{"cmd": "%s"}' % (command)
        custom_args['data'] = request_body
        response_json = self.request_handler.perform_request('PUT', custom_args)
        return response_json