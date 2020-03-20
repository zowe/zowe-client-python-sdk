"""
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
"""
from ..utilities import ZosmfApi
from ..utilities.exceptions import FileNotFound
import os


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

    def download_dsn(self, dataset_name, output_file):
        """Retrieves the contents of a dataset and saves it to a given file"""
        response_json = self.get_dsn_content(dataset_name)
        dataset_content = response_json['response']
        out_file = open(output_file, 'w')
        out_file.write(dataset_content)
        out_file.close()

    def upload_file_to_dsn(self, input_file, dataset_name):
        """Upload contents of a given file and uploads it to a dataset"""
        if os.path.isfile(input_file):
            in_file = open(input_file, 'r')
            file_contents = in_file.read()
            response_json = self.write_to_dsn(dataset_name, file_contents)
        else:
            raise FileNotFound(input_file)
