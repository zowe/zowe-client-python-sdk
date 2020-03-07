"""
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
"""
from ..utilities import ZosmfApi


class Files(ZosmfApi):
    """Base class for Files API"""
    def __init__(self, connection):
        super().__init__(connection, "/zosmf/restfiles/")

    def list_dsn(self, name_pattern):
        """Return a list of datasets based on the provided pattern"""
        custom_args = self.create_custom_request_arguments()
        custom_args["params"] = {"dslevel": name_pattern}
        custom_args["url"] = "{}ds".format(self.request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def list_dsn_members(self, dataset_name):
        """Return a list of members on a given PDS/PDSE"""
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}/member".format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json['items']

    def get_dsn_content(self, dataset_name):
        """Retrieves the contents of a given dataset"""
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def write_to_dsn(self, dataset_name, data):
        """Write content to an existing dataset"""
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        custom_args["data"] = data
        custom_args["headers"] = {"Content-Type": "text/plain"}
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[204, 201]
        )
        return response_json
