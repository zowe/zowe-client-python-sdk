'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
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