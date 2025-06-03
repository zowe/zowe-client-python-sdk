"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Optional, Any

from zowe.core_for_zowe_sdk import SdkApi
from zowe.zos_files_for_zowe_sdk import constants

from .exceptions import InvalidPermsOption, MaxAllocationQuantityExceeded
from .response import FileSystemListResponse

_ZOWE_FILES_DEFAULT_ENCODING = constants.zos_file_constants["ZoweFilesDefaultEncoding"]


class FileSystems(SdkApi):  # type: ignore
    """
    Class used to represent the base z/OSMF FileSystems API.

    It includes all operations related to file systems.

    Parameters
    ----------
    connection : dict[str, Any]
        A profile for connection in dict (json) format
    log : bool
        Flag to disable logger
    """

    def __init__(self, connection: dict[str, Any], log: bool = True):
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__, log=log)
        self._default_headers["Accept-Encoding"] = "gzip"

    def create(self, file_system_name: str, options: dict[str, Any] = {}) -> None:
        """
        Create a z/OS UNIX zFS Filesystem.

        Parameters
        ----------
        file_system_name: str
            Name of the file system
        options: dict[str, Any]
            Specifies file system attributes

        Raises
        ------
        MaxAllocationQuantityExceeded
            Thrown when file system exceeds max allocation quantity
        InvalidPermsOption
            Thrown when invalid permission option is provided
        """
        for key, value in options.items():
            if key == "perms":
                if value < 0 or value > 777:
                    self.logger.error("Invalid Permissions Option.")
                    raise InvalidPermsOption(value)

            if key == "cylsPri" or key == "cylsSec":
                if value > constants.zos_file_constants["MaxAllocationQuantity"]:
                    self.logger.error("Maximum allocation quantity exceeded.")
                    raise MaxAllocationQuantityExceeded()

        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/zfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        self.request_handler.perform_request("POST", custom_args, expected_code=[201])

    def delete(self, file_system_name: str) -> None:
        """
        Delete a zFS Filesystem.

        Parameters
        ----------
        file_system_name: str
            Name of the file system
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/zfs/{}".format(self._request_endpoint, file_system_name)
        self.request_handler.perform_request("DELETE", custom_args, expected_code=[204])

    def mount(
        self,
        file_system_name: str,
        mount_point: str,
        options: dict[str, Any] = {},
        encoding: str = _ZOWE_FILES_DEFAULT_ENCODING,
    ) -> None:
        """
        Mount a z/OS UNIX file system on a specified directory.

        Parameters
        ----------
        file_system_name: str
            Name for the file system
        mount_point: str
            Mount point to be used for mounting the UNIX file system
        options: dict[str, Any]
            A JSON of request body options
        encoding: str
            Specifies optional encoding name (e.g. IBM-1047)
        """
        options["action"] = "mount"
        options["mount-point"] = mount_point
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        self.request_handler.perform_request("PUT", custom_args, expected_code=[204])

    def unmount(
        self, file_system_name: str, options: dict[str, Any] = {}, encoding: str = _ZOWE_FILES_DEFAULT_ENCODING
    ) -> None:
        """
        Unmount a z/OS UNIX file system on a specified directory.

        Parameters
        ----------
        file_system_name: str
            Name for the file system
        options: dict[str, Any]
            A JSON of request body options
        encoding: str
            Specifies optional encoding name (e.g. IBM-1047)
        """
        options["action"] = "unmount"
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        self.request_handler.perform_request("PUT", custom_args, expected_code=[204])

    def list(
        self, file_path_name: Optional[str] = None, file_system_name: Optional[str] = None
    ) -> FileSystemListResponse:
        """
        List all mounted filesystems.

        It could also list the specific filesystem mounted at a given path, or the
        filesystem with a given Filesystem name.

        Parameters
        ----------
        file_path_name: Optional[str]
            USS directory that contains the files and directories to be listed
        file_system_name: Optional[str]
            Name of the file system to be listed

        Returns
        -------
        FileSystemListResponse
            A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()

        custom_args["params"] = {"path": file_path_name, "fsname": file_system_name}
        custom_args["url"] = "{}mfs".format(self._request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args, expected_code=[200])
        return FileSystemListResponse(response_json)
