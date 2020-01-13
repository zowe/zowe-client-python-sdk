'''
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
'''
from ..utilities import ZosmfApi

class Files(ZosmfApi):

    def __init__(self, connection):
        super().__init__(connection, '/zosmf/restfiles/')

    def list_dsn(self, name_pattern):
        custom_args = self.create_custom_request_arguments()
        custom_args['params'] = {'dslevel': name_pattern}
        custom_args['url'] = '{}ds'.format(self.request_endpoint)
        response_json = self.request_handler.perform_request('GET', custom_args)
        return response_json

    def list_dsn_members(self, dataset_name):
        custom_args = self.create_custom_request_arguments()
        custom_args['url'] = '{}ds/{}/member'.format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request('GET', custom_args)
        return response_json

    def get_dsn_content(self, dataset_name):
        custom_args = self.create_custom_request_arguments()
        custom_args['url'] = '{}ds/{}'.format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request('GET', custom_args)
        return response_json
