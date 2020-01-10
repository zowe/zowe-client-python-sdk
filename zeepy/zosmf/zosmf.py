'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''
from ..utilities import ZosmfApi

class Zosmf(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/info')

    def get_info(self):
        response_json = self.request_handler.perform_request('GET', self.request_arguments)
        return response_json