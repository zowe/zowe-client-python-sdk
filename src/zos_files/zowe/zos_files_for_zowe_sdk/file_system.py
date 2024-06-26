"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from zowe.core_for_zowe_sdk import SdkApi
from zowe.zos_files_for_zowe_sdk import constants, exceptions

_ZOWE_FILES_DEFAULT_ENCODING = constants.zos_file_constants["ZoweFilesDefaultEncoding"]


class FileSystems(SdkApi):
    """
    Class used to represent the base z/OSMF FileSystems API
    which includes all operations related to file systems.

    ...

    Attributes
    ----------
    connection
        connection object
    """

    def __init__(self, connection):
        """
        Construct a FileSystems object.

        Parameters
        ----------
        connection
            The z/OSMF connection object (generated by the ZoweSDK object)

        Also update header to accept gzip encoded responses
        """
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__)
        self._default_headers["Accept-Encoding"] = "gzip"

    def create(self, file_system_name, options={}):
        """
        Create a z/OS UNIX zFS Filesystem.

        Parameter
        ---------
        file_system_name: str - the name for the file system

        Returns
        -------
        json - A JSON containing the result of the operation
        """
        for key, value in options.items():
            if key == "perms":
                if value < 0 or value > 777:
                    self.logger.error("Invalid Permissions Option.")
                    raise exceptions.InvalidPermsOption(value)

            if key == "cylsPri" or key == "cylsSec":
                if value > constants.zos_file_constants["MaxAllocationQuantity"]:
                    self.logger.error("Maximum allocation quantity exceeded.")
                    raise exceptions.MaxAllocationQuantityExceeded

        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/zfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        return response_json

    def delete(self, file_system_name):
        """
        Deletes a zFS Filesystem
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/zfs/{}".format(self._request_endpoint, file_system_name)
        response_json = self.request_handler.perform_request("DELETE", custom_args, expected_code=[204])
        return response_json

    def mount(self, file_system_name, mount_point, options={}, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Mounts a z/OS UNIX file system on a specified directory.
        Parameter
        ---------
        file_system_name: str - the name for the file system
        mount_point: str - mount point to be used for mounting the UNIX file system
        options: dict - A JSON of request body options

        Returns
        -------
        json - A JSON containing the result of the operation
        """
        options["action"] = "mount"
        options["mount-point"] = mount_point
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[204])
        return response_json

    def unmount(self, file_system_name, options={}, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Unmounts a z/OS UNIX file system on a specified directory.

        Parameter
        ---------
        file_system_name: str - the name for the file system
        options: dict - A JSON of request body options

        Returns
        -------
        json - A JSON containing the result of the operation
        """
        options["action"] = "unmount"
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}mfs/{}".format(self._request_endpoint, file_system_name)
        custom_args["json"] = options
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[204])
        return response_json

    def list(self, file_path_name=None, file_system_name=None):
        """
        list all mounted filesystems, or the specific filesystem mounted at a given path, or the
        filesystem with a given Filesystem name.

        Parameter
        ---------
        file_path: str - the UNIX directory that contains the files and directories to be listed.
        file_system_name: str - the name for the file system to be listed

        Returns
        -------
        json - A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()

        custom_args["params"] = {"path": file_path_name, "fsname": file_system_name}
        custom_args["url"] = "{}mfs".format(self._request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args, expected_code=[200])
        return response_json
