"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from zowe.core_for_zowe_sdk import SdkApi
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
from zowe.zos_files_for_zowe_sdk.constants import FileType, zos_file_constants
from zowe.zos_files_for_zowe_sdk.response import DatasetListResponse, MemberListResponse

_ZOWE_FILES_DEFAULT_ENCODING = zos_file_constants["ZoweFilesDefaultEncoding"]


class DatasetOption:
    """A dataclass that represents options for creating a dataset.

    Parameters
    ----------
    like : Optional[str]
        The dataset name to copy attributes from
    volser : Optional[str]
        The volume serial number that identifies where the dataset resides or should be allocated
    unit : Optional[str]
        Specifies the type of device on which the dataset is to be stored
    dsorg : Optional[str]
        Defines the organization of the dataset (PS for sequential, PO for partitioned, DA for direct access)
    alcunit : Optional[str]
        Specifies the unit of space allocation for the dataset (CYL for cylinders, TRK for tracks, BLK for blocks)
    primary : Optional[int]
        The amount of primary space to allocate for the dataset
    secondary : Optional[int]
        The amount of secondary space to allocate if the primary space is exhausted
    dirblk : Optional[int]
        The number of directory blocks to allocate for a partitioned dataset
    avgblk : Optional[int]
        The average block size for the dataset
    recfm : Optional[str]
        The format of the records in the dataset
    blksize : Optional[int]
        The physical block size used for the dataset
    lrecl : Optional[int]
        The length of the logical records in the dataset
    storclass : Optional[str]
        Specifies the storage class to be used for the dataset
    mgmtclass : Optional[str]
        Specifies the management class
    dataclass : Optional[str]
        Specifies the data class for the dataset
    dsntype : Optional[str]
        Specifies the type of dataset
    """

    def __init__(
        self,
        like: Optional[str] = None,
        volser: Optional[str] = None,
        unit: Optional[str] = None,
        dsorg: Optional[str] = None,
        alcunit: Optional[str] = None,
        primary: Optional[int] = None,
        secondary: Optional[int] = None,
        dirblk: Optional[int] = None,
        avgblk: Optional[int] = None,
        recfm: Optional[str] = None,
        blksize: Optional[int] = None,
        lrecl: Optional[int] = None,
        storclass: Optional[str] = None,
        mgmtclass: Optional[str] = None,
        dataclass: Optional[str] = None,
        dsntype: Optional[str] = None,
    ) -> None:
        self.__like = like
        self.volser = volser
        self.unit = unit
        self.dsorg = dsorg
        self.alcunit = alcunit
        self.primary = primary
        self.secondary = secondary
        self.dirblk = dirblk
        self.avgblk = avgblk
        self.recfm = recfm
        self.lrecl = lrecl
        self.blksize = blksize
        self.storclass = storclass
        self.mgmtclass = mgmtclass
        self.dataclass = dataclass
        self.dsntype = dsntype

    @property
    def volser(self) -> Optional[str]:
        """Get the volume serial number."""
        return self.__volser

    @volser.setter
    def volser(self, volser: Optional[str]):
        """Set the volume serial number."""
        self.__volser = volser

    @property
    def unit(self) -> Optional[str]:
        """Get the type of device."""
        return self.__unit

    @unit.setter
    def unit(self, unit: Optional[str]):
        """Set the type of device."""
        self.__unit = unit

    @property
    def dsorg(self) -> Optional[str]:
        """Get the organization of the dataset."""
        return self.__dsorg

    @dsorg.setter
    def dsorg(self, dsorg: Optional[str]):
        """Set the organization of the dataset."""
        if dsorg not in ("PO", "PS", None):
            raise ValueError("'dsorg' must be 'PO', 'PS', or None")
        self.__dsorg = dsorg

    @property
    def alcunit(self) -> Optional[str]:
        """Get the unit of space allocation."""
        return self.__alcunit

    @alcunit.setter
    def alcunit(self, alcunit: Optional[str]):
        """Set the unit of space allocation."""
        if alcunit is None:
            if self.like is not None:
                self.__alcunit = None
            else:
                self.__alcunit = "TRK"
        elif alcunit not in ("CYL", "TRK"):
            raise KeyError("'alcunit' must be 'CYL' or 'TRK'")
        else:
            self.__alcunit = alcunit

    @property
    def primary(self) -> Optional[int]:
        """Get the primary space allocation."""
        return self.__primary

    @primary.setter
    def primary(self, primary: Optional[int]):
        """Set the primary space allocation."""
        if primary is not None:
            if primary > 16777215:
                raise ValueError("Given primary space allocation exceeds track limit of 16,777,215")
        self.__primary = primary

    @property
    def secondary(self) -> Optional[int]:
        """Get the secondary space allocation."""
        return self.__secondary

    @secondary.setter
    def secondary(self, secondary: Optional[int]):
        """Set the secondary space allocation."""
        if self.primary is not None:
            secondary = secondary if secondary is not None else int(self.primary / 10)
            if secondary > 16777215:
                raise ValueError("Given secondary space allocation exceeds track limit of 16,777,215")
            self.__secondary = secondary

    @property
    def dirblk(self) -> Optional[int]:
        """Get the number of directory blocks."""
        return self.__dirblk

    @dirblk.setter
    def dirblk(self, dirblk: Optional[int]):
        """Set the number of directory blocks."""
        self.__dirblk = dirblk

    @property
    def avgblk(self) -> Optional[int]:
        """Get the average block size."""
        return self.__avgblk

    @avgblk.setter
    def avgblk(self, avgblk: Optional[int]):
        """Set the average block size."""
        self.__avgblk = avgblk

    @property
    def recfm(self) -> Optional[str]:
        """Get the record format."""
        return self.__recfm

    @recfm.setter
    def recfm(self, recfm: Optional[str]):
        """Set the record format."""
        if recfm is None:
            if self.like is not None:
                self.__recfm = None
            else:
                self.__recfm = "F"
        elif recfm not in ("F", "FB", "V", "VB", "U", "FBA", "FBM", "VBA", "VBM"):
            raise KeyError(
                "'recfm' must be one of the following: 'F', 'FB', 'V', 'VB', 'U', 'FBA', 'FBM', 'VBA', 'VBM'"
            )
        else:
            self.__recfm = recfm

    @property
    def blksize(self) -> Optional[int]:
        """Get the physical block size."""
        return self.__blksize

    @blksize.setter
    def blksize(self, blksize: Optional[int]):
        """Set the physical block size."""
        if blksize is None:
            if self.like is not None:
                self.__blksize = None
            else:
                if self.lrecl is not None:
                    self.__blksize = self.lrecl
        else:
            self.__blksize = blksize

    @property
    def lrecl(self) -> Optional[int]:
        """Get the length of logical records."""
        return self.__lrecl

    @lrecl.setter
    def lrecl(self, lrecl: Optional[int]):
        """Set the length of logical records."""
        self.__lrecl = lrecl

    @property
    def storclass(self) -> Optional[str]:
        """Get the storage class."""
        return self.__storclass

    @storclass.setter
    def storclass(self, storclass: Optional[str]):
        """Set the storage class."""
        self.__storclass = storclass

    @property
    def mgmtclass(self) -> Optional[str]:
        """Get the management class."""
        return self.__mgmtclass

    @mgmtclass.setter
    def mgmtclass(self, mgmtclass: Optional[str]):
        """Set the management class."""
        self.__mgmtclass = mgmtclass

    @property
    def dataclass(self) -> Optional[str]:
        """Get the data class."""
        return self.__dataclass

    @dataclass.setter
    def dataclass(self, dataclass: Optional[str]):
        """Set the data class."""
        self.__dataclass = dataclass

    @property
    def dsntype(self) -> Optional[str]:
        """Get the type of dataset."""
        return self.__dsntype

    @dsntype.setter
    def dsntype(self, dsntype: Optional[str]):
        """Set the type of dataset."""
        self.__dsntype = dsntype

    @property
    def like(self) -> Optional[str]:
        """Get the dataset name to copy attributes from."""
        return self.__like

    def to_dict(self) -> dict:
        """Return the DatasetOption as a dict."""
        return {key.replace("_DatasetOption__", ""): value for key, value in self.__dict__.items() if value is not None}


class Datasets(SdkApi):
    """
    Class used to represent the base z/OSMF Datasets API.

    It includes all operations related to datasets.

    Parameters
    ----------
    connection : dict
        A profile for connection in dict (json) format
    """

    def __init__(self, connection: dict):
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__)
        self._default_headers["Accept-Encoding"] = "gzip"

    def list(self, name_pattern: str, return_attributes: bool = False) -> DatasetListResponse:
        """
        Retrieve a list of datasets based on a given pattern.

        Parameters
        ----------
        name_pattern : str
            The pattern to match dataset names.
        return_attributes : bool
            Whether to return dataset attributes along with the names. Defaults to False.

        Returns
        -------
        DatasetListResponse
            A JSON with a list of dataset names (and attributes if specified) matching the given pattern.
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["params"] = {"dslevel": self._encode_uri_component(name_pattern)}
        custom_args["url"] = "{}ds".format(self._request_endpoint)

        if return_attributes:
            custom_args["headers"]["X-IBM-Attributes"] = "base"

        response_json = self.request_handler.perform_request("GET", custom_args)
        return DatasetListResponse(response_json, return_attributes)

    def list_members(
        self,
        dataset_name: str,
        member_pattern: Optional[str] = None,
        member_start: Optional[str] = None,
        limit: int = 1000,
        attributes: str = "member",
    ) -> MemberListResponse:
        """
        Retrieve the list of members on a given PDS/PDSE.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset
        member_pattern: Optional[str]
            Filters members by name pattern
        member_start: Optional[str]
            The starting point for listing members
        limit: int
            The maximum number of members returned
        attributes: str
            The member attributes to retrieve

        Returns
        -------
        MemberListResponse
            A JSON with a list of members from a given PDS/PDSE
        """
        custom_args = self._create_custom_request_arguments()
        additional_parms = {}
        if member_start is not None:
            additional_parms["start"] = member_start
        if member_pattern is not None:
            additional_parms["pattern"] = member_pattern
        custom_args["params"] = additional_parms
        custom_args["url"] = "{}ds/{}/member".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        custom_args["headers"]["X-IBM-Max-Items"] = "{}".format(limit)
        custom_args["headers"]["X-IBM-Attributes"] = attributes
        response_json = self.request_handler.perform_request("GET", custom_args)
        return MemberListResponse(response_json, (attributes == "base"))

    def copy_data_set_or_member(
        self,
        from_dataset_name: str,
        to_dataset_name: str,
        from_member_name: Optional[str] = None,
        volser: Optional[str] = None,
        alias: Optional[bool] = None,
        to_member_name: Optional[str] = None,
        enq: Optional[str] = None,
        replace: bool = False,
    ) -> dict:
        """
        Copy a dataset or member to another dataset or member.

        Parameters
        ----------
        from_dataset_name: str
            Name of the dataset to copy from
        to_dataset_name: str
            Name of the dataset to copy to
        from_member_name: Optional[str]
            Name of the member to copy from
        volser: Optional[str]
            Volume serial number of the dataset to copy from
        alias: Optional[bool]
            Alias of the dataset to copy from
        to_member_name: Optional[str]
            Name of the member to copy to
        enq: Optional[str]
            Enqueue type for the dataset to copy from
        replace: bool
            If true, members in the target data set are replaced

        Raises
        ------
        ValueError
            Thrown when enq has an invalid value

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {
            "request": "copy",
            "from-dataset": {"dsn": from_dataset_name.strip(), "member": from_member_name},
            "replace": replace,
        }

        path_to_member = f"{to_dataset_name}({to_member_name})" if to_member_name else to_dataset_name
        if enq:
            if enq in ("SHR", "SHRW", "EXCLU"):
                data["enq"] = enq
            else:
                self.logger.error("Invalid value for enq.")
                raise ValueError("Invalid value for enq.")
        if volser:
            data["from-dataset"]["volser"] = volser
        if alias is not None:  # because it can be false so
            data["from-dataset"]["alias"] = alias

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(path_to_member))
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def create(self, dataset_name: str, options: Optional[DatasetOption] = None) -> dict:
        """
        Create a sequential or partitioned dataset.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to be created
        options: Optional[DatasetOption]
            A DatasetOption class with property options of the dataset

        Raises
        ------
        ValueError
            Thrown when a parameter has an invalid value

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        if not options:
            self.logger.error("You must specify dataset options when creating one.")
            raise ValueError("You must specify dataset options when creating one.")

        if options.like is None:
            if options.primary is None or options.lrecl is None:
                self.logger.error("If 'like' is not specified, you must specify 'primary' and 'lrecl'.")
                raise ValueError("If 'like' is not specified, you must specify 'primary' and 'lrecl'.")
            if options.dirblk is not None:
                if options.dsorg == "PS":
                    if options.dirblk != 0:
                        self.logger.error("Can't allocate directory blocks for files.")
                        raise ValueError
                elif options.dsorg == "PO":
                    if options.dirblk == 0:
                        self.logger.error("Can't allocate empty directory blocks.")
                        raise ValueError
        else:
            dsn_attr = self.list(options.like, return_attributes=True)["items"]
            for dsn in dsn_attr:
                if dsn["dsname"] == options.like.upper():
                    options.blksize = int(dsn["blksz"])
                    break

        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        custom_args["json"] = options.to_dict() if options else {}
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        return response_json

    def create_default(self, dataset_name: str, default_type: str) -> dict:
        """
        Create a dataset with default options set.

        Default options depend on the requested type.

        Parameters
        ----------
        dataset_name: str
            The name of the dataset
        default_type: str
            The type of the dataset: "partitioned", "sequential", "classic", "c" or "binary"

        Raises
        ------
        ValueError
            Thrown when a parameter is invalid

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        if default_type not in ("partitioned", "sequential", "classic", "c", "binary"):
            self.logger.error("Invalid type for default data set.")
            raise ValueError("Invalid type for default data set.")

        custom_args = self._create_custom_request_arguments()

        if default_type == "partitioned":
            custom_args["json"] = {
                "alcunit": "CYL",
                "dsorg": "PO",
                "primary": 1,
                "dirblk": 5,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80,
            }
        elif default_type == "sequential":
            custom_args["json"] = {
                "alcunit": "CYL",
                "dsorg": "PS",
                "primary": 1,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80,
            }
        elif default_type == "classic":
            custom_args["json"] = {
                "alcunit": "CYL",
                "dsorg": "PO",
                "primary": 1,
                "recfm": "FB",
                "blksize": 6160,
                "lrecl": 80,
                "dirblk": 25,
            }
        elif default_type == "c":
            custom_args["json"] = {
                "dsorg": "PO",
                "alcunit": "CYL",
                "primary": 1,
                "recfm": "VB",
                "blksize": 32760,
                "lrecl": 260,
                "dirblk": 25,
            }
        elif default_type == "binary":
            custom_args["json"] = {
                "dsorg": "PO",
                "alcunit": "CYL",
                "primary": 10,
                "recfm": "U",
                "blksize": 27998,
                "lrecl": 27998,
                "dirblk": 25,
            }

        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        return response_json

    def get_content(self, dataset_name: str, stream: bool = False) -> dict:
        """
        Retrieve the contents of a given dataset.

        Parameters
        ----------
        dataset_name: str
            The name of the dataset
        stream: bool
            Specifies whether the response is streamed. Default: False

        Returns
        -------
        dict
            A JSON with the contents of a given dataset
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        response_json = self.request_handler.perform_request("GET", custom_args, stream=stream)
        return response_json

    def get_binary_content(self, dataset_name: str, stream: bool = False, with_prefixes: bool = False) -> dict:
        """
        Retrieve the contents of a given dataset as a binary bytes object.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to retrieve
        stream: bool
            Specifies whether the request is streaming
        with_prefixes: bool
            If True include a 4 byte big endian record len prefix. Default: False

        Returns
        -------
        dict
            A JSON with the contents of a given dataset
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        custom_args["headers"]["Accept"] = "application/octet-stream"
        if with_prefixes:
            custom_args["headers"]["X-IBM-Data-Type"] = "record"
        else:
            custom_args["headers"]["X-IBM-Data-Type"] = "binary"
        response = self.request_handler.perform_request("GET", custom_args, stream=stream)
        return response

    def write(self, dataset_name: str, data: str, encoding: str = _ZOWE_FILES_DEFAULT_ENCODING) -> dict:
        """
        Write content to an existing dataset.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to retrieve
        data: str
            Content to be written
        encoding: str
            Specifies encoding name (e.g. IBM-1047)

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        custom_args["data"] = data
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[204, 201])
        return response_json

    def download(self, dataset_name: str, output_file: str) -> None:
        """
        Retrieve the contents of a dataset and saves it to a given file.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to be downloaded
        output_file: str
            Name of the file to be saved locally
        """
        response = self.get_content(dataset_name, stream=True)
        with open(output_file, "w", encoding="utf-8") as f:
            for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
                f.write(chunk)

    def download_binary(self, dataset_name: str, output_file: str, with_prefixes: bool = False) -> None:
        """
        Retrieve the contents of a binary dataset and saves it to a given file.

        Parameters
        ----------
        dataset_name : str
            Name of the dataset to download
        output_file : str
            Name of the local file to create
        with_prefixes : bool
            If true, include a four big endian bytes record length prefix. Default: False
        """
        response = self.get_binary_content(dataset_name, with_prefixes=with_prefixes, stream=True)
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)

    def upload_file(
        self, input_file: str, dataset_name: str, encoding: str = _ZOWE_FILES_DEFAULT_ENCODING, binary: bool = False
    ) -> None:
        """
        Upload contents of a given file and uploads it to a dataset.

        Parameters
        ----------
        input_file: str
            Name of the file to be uploaded
        dataset_name: str
            Name of the dataset to be created
        encoding: str
            Specifies the encoding name (e.g. IBM-1047)
        binary: bool
            specifies whether the file is binary

        Raises
        ------
        FileNotFound
            Thrown when a file is not found at provided location
        """
        if os.path.isfile(input_file):
            if binary:
                with open(input_file, "rb") as in_file:
                    response_json = self.write(dataset_name, in_file)
            else:
                with open(input_file, "r") as in_file:
                    response_json = self.write(dataset_name, in_file.read())
        else:
            self.logger.error(f"File {input_file} not found.")
            raise FileNotFound(input_file)

    def recall_migrated(self, dataset_name: str, wait: bool = False) -> dict:
        """
        Recall a migrated data set.

        Parameters
        ----------
        dataset_name: str
            Name of the data set
        wait: bool
            If true, the function waits for completion of the request, otherwise the request is queued

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {"request": "hrecall", "wait": wait}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def delete_migrated(self, dataset_name: str, purge: bool = False, wait: bool = False) -> dict:
        """
        Delete migrated data set.

        Parameters
        ----------
        dataset_name: str
            Name of the data set
        purge: bool
            If true, the function uses the PURGE=YES on ARCHDEL request, otherwise it uses the PURGE=NO.
        wait: bool
            If true, the function waits for completion of the request, otherwise the request is queued.

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {
            "request": "hdelete",
            "purge": purge,
            "wait": wait,
        }

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def migrate(self, dataset_name: str, wait: bool = False) -> dict:
        """
        Migrate the data set.

        Parameters
        ----------
        dataset_name: str
            Name of the data set
        wait: bool
            If true, the function waits for completion of the request, otherwise the request is queued.

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {"request": "hmigrate", "wait": wait}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def rename(self, before_dataset_name: str, after_dataset_name: str) -> dict:
        """
        Rename the data set.

        Parameters
        ----------
        before_dataset_name: str
            The source data set name.

        after_dataset_name: str
            New name for the source data set.

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {"request": "rename", "from-dataset": {"dsn": before_dataset_name.strip()}}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(
            self._request_endpoint, self._encode_uri_component(after_dataset_name).strip()
        )

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def rename_member(self, dataset_name: str, before_member_name: str, after_member_name: str, enq: str = "") -> dict:
        """
        Rename the data set member.

        Parameters
        ----------
        dataset_name: str
            Name of the data set.
        before_member_name: str
            The source member name.
        after_member_name: str
            New name for the source member.
        enq: str
            Values can be SHRW or EXCLU. SHRW is the default for PDS members, EXCLU otherwise.

        Raises
        ------
        ValueError
            Thrown when a parameter is invalid

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        data = {
            "request": "rename",
            "from-dataset": {
                "dsn": dataset_name.strip(),
                "member": before_member_name.strip(),
            },
        }

        path_to_member = dataset_name.strip() + "(" + after_member_name.strip() + ")"

        if enq:
            if enq in ("SHRW", "EXCLU"):
                data["enq"] = enq.strip()
            else:
                self.logger.error("Invalid value for enq.")
                raise ValueError("Invalid value for enq.")

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(path_to_member))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def delete(self, dataset_name: str, volume: Optional[str] = None, member_name: Optional[str] = None) -> dict:
        """
        Delete a sequential or partitioned data.

        Parameters
        ----------
        dataset_name: str
            The name of the dataset
        volume: Optional[str]
            The optional volume serial number
        member_name: Optional[str]
            The name of the member to be deleted

        Returns
        -------
        dict
            A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()
        if member_name is not None:
            dataset_name = f"{dataset_name}({member_name})"
        url = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        if volume is not None:
            url = "{}ds/-{}/{}".format(self._request_endpoint, volume, self._encode_uri_component(dataset_name))
        custom_args["url"] = url
        response_json = self.request_handler.perform_request("DELETE", custom_args, expected_code=[200, 202, 204])
        return response_json

    def copy_uss_to_data_set(
        self,
        from_filename: str,
        to_dataset_name: str,
        to_member_name: Optional[str] = None,
        type: str = FileType.TEXT,
        replace: bool = False,
    ) -> dict:
        """
        Copy a USS file to dataset.

        Parameters
        ----------
        from_filename: str
            Name of the file to copy from.
        to_dataset_name: str
            Name of the dataset to copy to.
        to_member_name: Optional[str]
            Name of the member to copy to.
        type: str
            Type of the file to copy from. Default is FileType.TEXT.
        replace: bool
            If true, members in the target dataset are replaced.

        Returns
        -------
        dict
            A JSON containing the result of the operation.
        """
        data = {
            "request": "copy",
            "from-file": {"filename": from_filename.strip(), "type": type.value},
            "replace": replace,
        }

        path_to_member = f"{to_dataset_name}({to_member_name})" if to_member_name else to_dataset_name
        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(path_to_member))
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json
