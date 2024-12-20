"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Optional

from zowe.core_for_zowe_sdk import SdkApi
from zowe.zos_files_for_zowe_sdk.constants import FileType, zos_file_constants

from .datasets import DatasetOption, Datasets
from .file_system import FileSystems
from .uss import USSFiles

_ZOWE_FILES_DEFAULT_ENCODING = zos_file_constants["ZoweFilesDefaultEncoding"]


class Files(SdkApi):
    """
    Class used to represent the base z/OSMF Files API.

    Attributes
    ----------
    ds: Datasets
        A Datasets class object
    uss: USSFiles
        An USSFiles class object
    fs: FileSystems
        A FileSystems class object

    Parameters
    ----------
    connection: dict
        The z/OSMF connection object (generated by the ZoweSDK object)
    log : bool
        Flag to disable logger
    """

    ds: Datasets
    uss: USSFiles
    fs: FileSystems

    def __init__(self, connection: dict, log: bool = True):
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__, log=log)
        self._default_headers["Accept-Encoding"] = "gzip"
        self.ds = Datasets(connection)
        self.uss = USSFiles(connection)
        self.fs = FileSystems(connection)

    def list_files(self, path):
        """Use uss.list() instead of this deprecated function."""
        return self.uss.list(path)

    def get_file_content_streamed(self, file_path, binary=False):
        """Use uss.get_content_streamed() instead of this deprecated function."""
        return self.uss.get_content_streamed(file_path, binary)

    def get_file_content(self, filepath_name):
        """Use uss.get_content() instead of this deprecated function."""
        return self.uss.get_content(filepath_name)

    def delete_uss(self, filepath_name, recursive=False):
        """Use uss.delete() instead of this deprecated function."""
        return self.uss.delete(filepath_name, recursive)

    def list_dsn(self, name_pattern, return_attributes=False):
        """Use ds.list() instead of this deprecated function."""
        return self.ds.list(name_pattern, return_attributes)

    def list_dsn_members(self, dataset_name, member_pattern=None, member_start=None, limit=1000, attributes="member"):
        """Use ds.list_members() instead of this deprecated function."""
        return self.ds.list_members(dataset_name, member_pattern, member_start, limit, attributes)

    def copy_uss_to_data_set(
        self, from_filename, to_dataset_name, to_member_name=None, type=FileType.TEXT, replace=False
    ):
        """Use ds.copy_uss_to_data_set() instead of this deprecated function."""
        return self.ds.copy_uss_to_data_set(from_filename, to_dataset_name, to_member_name, type, replace)

    def copy_data_set_or_member(
        self,
        from_dataset_name,
        to_dataset_name,
        from_member_name=None,
        volser=None,
        alias=None,
        to_member_name=None,
        enq=None,
        replace=False,
    ):
        """Use ds.copy_data_set_or_member() instead of this deprecated function."""
        return self.ds.copy_data_set_or_member(
            from_dataset_name, to_dataset_name, from_member_name, volser, alias, to_member_name, enq, replace
        )

    def get_dsn_content(self, dataset_name):
        """Use ds.get_content() instead of this deprecated function."""
        return self.ds.get_content(dataset_name)

    def create_data_set(self, dataset_name, options: Optional[DatasetOption] = None):
        """Use ds.create() instead of this deprecated function."""
        return self.ds.create(dataset_name, options)

    def create_default_data_set(self, dataset_name: str, default_type: str):
        """Use ds.create_default() instead of this deprecated function."""
        return self.ds.create_default(dataset_name, default_type)

    def create_uss(self, file_path, type, mode=None):
        """Use uss.create() instead of this deprecated function."""
        return self.uss.create(file_path, type, mode)

    def get_dsn_content_streamed(self, dataset_name):
        """Use ds.get_content() instead of this deprecated function."""
        return self.ds.get_content(dataset_name, stream=True)

    def get_dsn_binary_content(self, dataset_name, with_prefixes=False):
        """Use ds.get_binary_content() instead of this deprecated function."""
        return self.ds.get_binary_content(dataset_name, with_prefixes)

    def get_dsn_binary_content_streamed(self, dataset_name, with_prefixes=False):
        """Use ds.get_binary_content() instead of this deprecated function."""
        return self.ds.get_binary_content(dataset_name, stream=True, with_prefixes=with_prefixes)

    def write_to_dsn(self, dataset_name, data, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Use ds.write() instead of this deprecated function."""
        return self.ds.write(dataset_name, data, encoding)

    def download_dsn(self, dataset_name, output_file):
        """Use ds.download() instead of this deprecated function."""
        self.ds.download(dataset_name, output_file)

    def download_binary_dsn(self, dataset_name, output_file, with_prefixes=False):
        """Use ds.download_binary() instead of this deprecated function."""
        self.ds.download_binary(dataset_name, output_file, with_prefixes)

    def upload_file_to_dsn(self, input_file, dataset_name, encoding=_ZOWE_FILES_DEFAULT_ENCODING, binary=False):
        """Use ds.upload_file() instead of this deprecated function."""
        self.ds.upload_file(input_file, dataset_name, encoding, binary)

    def write_to_uss(self, filepath_name, data, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Use uss.write() instead of this deprecated function."""
        return self.uss.write(filepath_name, data, encoding)

    def upload_file_to_uss(self, input_file, filepath_name, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Use uss.upload() instead of this deprecated function."""
        self.uss.upload(input_file, filepath_name, encoding)

    def download_uss(self, file_path, output_file, binary=False):
        """Use uss.download() instead of this deprecated function."""
        self.uss.download(file_path, output_file, binary)

    def delete_data_set(self, dataset_name, volume=None, member_name=None):
        """Use ds.delete() instead of this deprecated function."""
        return self.ds.delete(dataset_name, volume, member_name)

    def create_zfs_file_system(self, file_system_name, options={}):
        """Use fs.create() instead of this deprecated function."""
        return self.fs.create(file_system_name, options)

    def delete_zfs_file_system(self, file_system_name):
        """Use fs.delete() instead of this deprecated function."""
        return self.fs.delete(file_system_name)

    def mount_file_system(self, file_system_name, mount_point, options={}, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Use fs.mount() instead of this deprecated function."""
        return self.fs.mount(file_system_name, mount_point, options, encoding)

    def unmount_file_system(self, file_system_name, options={}, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Use fs.unmount() instead of this deprecated function."""
        return self.fs.unmount(file_system_name, options, encoding)

    def list_unix_file_systems(self, file_path_name=None, file_system_name=None):
        """Use fs.list() instead of this deprecated function."""
        return self.fs.list(file_path_name, file_system_name)

    def recall_migrated_data_set(self, dataset_name: str, wait=False):
        """Use ds.recall_migrated() instead of this deprecated function."""
        return self.ds.recall_migrated(dataset_name, wait)

    def delete_migrated_data_set(self, dataset_name: str, purge=False, wait=False):
        """Use ds.delete_migrated() instead of this deprecated function."""
        return self.ds.delete_migrated(dataset_name, purge, wait)

    def migrate_data_set(self, dataset_name: str, wait=False):
        """Use ds.migrate() instead of this deprecated function."""
        return self.ds.migrate(dataset_name, wait)

    def rename_data_set(self, before_dataset_name: str, after_dataset_name: str):
        """Use ds.rename() instead of this deprecated function."""
        return self.ds.rename(before_dataset_name, after_dataset_name)

    def rename_data_set_member(self, dataset_name: str, before_member_name: str, after_member_name: str, enq=""):
        """Use ds.rename_member() instead of this deprecated function."""
        return self.ds.rename_member(dataset_name, before_member_name, after_member_name, enq)
