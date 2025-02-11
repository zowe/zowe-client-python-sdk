"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
import base64
from typing import Optional, Any, Dict
import requests


from zowe.core_for_zowe_sdk import SdkApi
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
from zowe.zos_files_for_zowe_sdk.constants import zos_file_constants

from .response import USSListResponse

_ZOWE_FILES_DEFAULT_ENCODING = zos_file_constants["ZoweFilesDefaultEncoding"]


class USSFiles(SdkApi): #type: ignore
    """
    Class used to represent the base z/OSMF USSFiles API.

    It includes all operations related to USS files.

    Parameters
    ----------
    connection: dict
        The z/OSMF connection object (generated by the ZoweSDK object)
    log : bool
        Flag to disable logger
    """

    def __init__(self, connection: dict[str, Any], log: bool = True):
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__, log=log)
        self._default_headers["Accept-Encoding"] = "gzip"

    def list(self, path: str) -> USSListResponse:
        """
        Retrieve a list of USS files based on a given pattern.

        Parameters
        ----------
        path: str
            Path to retrieve the list

        Returns
        -------
        USSListResponse
            A JSON with a list of file names matching the given pattern
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["params"] = {"path": path}
        custom_args["url"] = "{}fs".format(self._request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return USSListResponse(response_json)

    def delete(self, filepath_name: str, recursive: bool = False) -> dict[str, Any]:
        """
        Delete a file or directory.

        Parameters
        ----------
        filepath_name: str
            Path of the file to be deleted
        recursive: bool
            If specified as True, all the files and sub-directories will be deleted.

        Returns
        -------
        dict
            A JSON containing the operation results
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}fs/{}".format(self._request_endpoint, filepath_name.lstrip("/"))
        if recursive:
            custom_args["headers"]["X-IBM-Option"] = "recursive"

        response_json = self.request_handler.perform_request("DELETE", custom_args, expected_code=[204])
        if isinstance(response_json, dict):
            return response_json
        else:
            return {}

    def create(self, file_path: str, type: str, mode: Optional[str] = None) -> dict[str, Any]:
        """
        Add a file or directory.

        Parameters
        ----------
        file_path: str
            Path of the file to add
        type: str
            Specify either "file" or "dir"
        mode: Optional[str]
            Unix permission string (e.g. `rwxr-xr-x`)

        Returns
        -------
        dict
            A JSON containing the operation results
        """
        data = {"type": type, "mode": mode}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}fs/{}".format(self._request_endpoint, file_path.lstrip("/"))
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        if isinstance(response_json, dict):
            return response_json
        else:
            return {}

    def write(self, filepath_name: str, data: str, encoding: str = _ZOWE_FILES_DEFAULT_ENCODING) -> dict[str, Any]:
        """
        Write content to an existing UNIX file.

        Parameters
        ----------
        filepath_name: str
            Path of the file
        data: str
            Contents to be written
        encoding: str
            Specifies the encoding name (e.g. IBM-1047)

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}fs/{}".format(self._request_endpoint, filepath_name.lstrip("/"))
        custom_args["data"] = data
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[204, 201])
        if isinstance(response_json, dict):
            return response_json
        else:
            return {}

    def get_content(self, filepath_name: str) -> dict[str, Any]:
        """
        Retrieve the content of a filename. The complete path must be specified.

        Parameters
        ----------
        filepath_name: str
            Path of the file

        Returns
        -------
        dict
            A JSON with the contents of the specified USS file
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}fs{}".format(self._request_endpoint, filepath_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        if isinstance(response_json, dict):
            return response_json
        else:
            return {}

    def get_content_streamed(self, file_path: str, binary: bool = False) -> Dict[str, Any]:
        """
        Retrieve the contents of a given USS file streamed.

        Parameters
        ----------
        file_path: str
            Path of the file
        binary: bool
            Specifies whether the contents are binary

        Returns
        -------
        dict
            A JSON response with results of the operation
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}fs/{}".format(self._request_endpoint, self._encode_uri_component(file_path.lstrip("/")))
        if binary:
            custom_args["headers"]["X-IBM-Data-Type"] = "binary"
        response = self.request_handler.perform_request("GET", custom_args, stream=True)
        if binary:
            encoded_content = base64.b64encode(response.content).decode("utf-8")
            return {
                "content_type": response.headers.get("Content-Type"),
                "content_length": len(response.content),
                "file_content": encoded_content,
            }
        else:
            try:
                response_json = response.json()
                return response_json if isinstance(response_json, dict) else {}
            except ValueError:
                return {"error": "Failed to parse response as JSON"}

    def download(self, file_path: str, output_file: str, binary: bool = False) -> None:
        """
        Retrieve the contents of a USS file and saves it to a local file.

        Parameters
        ----------
        file_path: str
            Path of the file to be downloaded
        output_file: str
            Name of the file to be saved locally
        binary: bool
            Specifies whether the contents are binary
        """
        response = self.get_content_streamed(file_path, binary)
        if not isinstance(response, requests.Response):
            raise TypeError(f"Expected requests.Response, got {type(response)}")
        with open(output_file, "wb" if binary else "w", encoding="utf-8") as f:
            for chunk in response.iter_content(chunk_size=4096, decode_unicode=not binary):
                f.write(chunk)

    def upload(self, input_file: str, filepath_name: str, encoding: str = _ZOWE_FILES_DEFAULT_ENCODING) -> None:
        """
        Upload contents of a given file and saves it to a file at the given USS path.

        Parameters
        ----------
        input_file: str
            Name of the file to be uploaded
        filepath_name: str
            Path of the file where it will be created
        encoding: str
            Specifies encoding schema

        Raises
        ------
        FileNotFound
            Thrown when specific file is not found.
        """
        if os.path.isfile(input_file):
            with open(input_file, "r", encoding="utf-8") as in_file:
                response_json = self.write(filepath_name, in_file.read())
        else:
            self.logger.error(f"File {input_file} not found.")
            raise FileNotFound(input_file)
