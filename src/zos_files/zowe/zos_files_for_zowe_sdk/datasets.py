"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
from dataclasses import dataclass
from typing import Optional

from zowe.core_for_zowe_sdk import SdkApi
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
from zowe.zos_files_for_zowe_sdk.constants import FileType, zos_file_constants

_ZOWE_FILES_DEFAULT_ENCODING = zos_file_constants["ZoweFilesDefaultEncoding"]


@dataclass
class DatasetOption:
    """A dataclass that represents options for creating a dataset

    Attributes
    ----------
    like: str
        The dataset name to copy attributes from
    volser: str
        The volume serial number that identifies where the dataset resides or should be allocated
    unit: str
        Specifies the type of device on which the dataset is to be stored
    dsorg: str
        Defines the organization of the dataset (PS for sequential, PO for partitioned, DA for direct access)
    alcunit: str
        Specifies the unit of space allocation for the dataset (CYL for cylinders, TRK for tracks, BLK for blocks)
    primary: int
        The amount of primary space to allocate for the dataset
    secondary: int
        The amount of secondary space to allocate if the primary space is exhausted
    dirblk: int
        The number of directory blocks to allocate for a partitioned dataset
    avgblk: int
        The average block size for the dataset
    recfm: str
        The format of the records in the dataset
    blksize: int
        The physical block size used for the dataset
    lrecl: int
        The length of the logical records in the dataset
    storclass: str
        Specifies the storage class to be used for the dataset
    mgnclass: str
        Specifies the management class for the dataset
    dataclass: str
        Specifies the data class for the dataset
    dsntype: str
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
        mgntclass: Optional[str] = None,
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
        self.mgntclass = mgntclass
        self.dataclass = dataclass
        self.dsntype = dsntype

    @property
    def volser(self) -> Optional[str]:
        return self.__volser

    @volser.setter
    def volser(self, volser: Optional[str]):
        self.__volser = volser

    @property
    def unit(self) -> Optional[str]:
        return self.__unit

    @unit.setter
    def unit(self, unit: Optional[str]):
        self.__unit = unit

    @property
    def dsorg(self) -> Optional[str]:
        return self.__dsorg

    @dsorg.setter
    def dsorg(self, dsorg: Optional[str]):
        if dsorg not in ("PO", "PS", None):
            raise ValueError("'dsorg' must be 'PO', 'PS', or None")
        self.__dsorg = dsorg

    @property
    def alcunit(self) -> Optional[str]:
        return self.__alcunit

    @alcunit.setter
    def alcunit(self, alcunit: Optional[str]):
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
        return self.__primary

    @primary.setter
    def primary(self, primary: Optional[int]):
        if primary is not None:
            if primary > 16777215:
                raise ValueError("Given primary space allocation exceeds track limit of 16,777,215")
        self.__primary = primary

    @property
    def secondary(self) -> Optional[int]:
        return self.__secondary

    @secondary.setter
    def secondary(self, secondary: Optional[int]):
        if self.primary is not None:
            secondary = secondary if secondary is not None else int(self.primary / 10)
            if secondary > 16777215:
                raise ValueError("Given secondary space allocation exceeds track limit of 16,777,215")
            self.__secondary = secondary

    @property
    def dirblk(self) -> Optional[int]:
        return self.__dirblk

    @dirblk.setter
    def dirblk(self, dirblk: Optional[int]):
        self.__dirblk = dirblk

    @property
    def avgblk(self) -> Optional[int]:
        return self.__avgblk

    @avgblk.setter
    def avgblk(self, avgblk: Optional[int]):
        self.__avgblk = avgblk

    @property
    def recfm(self) -> Optional[str]:
        return self.__recfm

    @recfm.setter
    def recfm(self, recfm: Optional[str]):
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
        return self.__blksize

    @blksize.setter
    def blksize(self, blksize: Optional[int]):
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
        return self.__lrecl

    @lrecl.setter
    def lrecl(self, lrecl: Optional[int]):
        self.__lrecl = lrecl

    @property
    def storclass(self) -> Optional[str]:
        return self.__storclass

    @storclass.setter
    def storclass(self, storclass: Optional[str]):
        self.__storclass = storclass

    @property
    def mgntclass(self) -> Optional[str]:
        return self.__mgntclass

    @mgntclass.setter
    def mgntclass(self, mgntclass: Optional[str]):
        self.__mgntclass = mgntclass

    @property
    def dataclass(self) -> Optional[str]:
        return self.__dataclass

    @dataclass.setter
    def dataclass(self, dataclass: Optional[str]):
        self.__dataclass = dataclass

    @property
    def dsntype(self) -> Optional[str]:
        return self.__dsntype

    @dsntype.setter
    def dsntype(self, dsntype: Optional[str]):
        self.__dsntype = dsntype

    @property
    def like(self) -> Optional[str]:
        return self.__like

    def to_dict(self) -> dict:
        """Return the DatasetOption as a dict

        Returns
        -------
        dict
        """
        return {key.replace("_DatasetOption__", ""): value for key, value in self.__dict__.items() if value is not None}


class Datasets(SdkApi):
    """
    Class used to represent the base z/OSMF Datasets API
    which includes all operations related to datasets.

    Attributes
    ----------
    connection
        connection object
    """

    def __init__(self, connection):
        """
        Construct a Datasets object.

        Parameters
        ----------
        connection
            The z/OSMF connection object (generated by the ZoweSDK object)

        Also update header to accept gzip encoded responses
        """
        super().__init__(connection, "/zosmf/restfiles/", logger_name=__name__)
        self._default_headers["Accept-Encoding"] = "gzip"

    def list(self, name_pattern, return_attributes=False):
        """Retrieve a list of datasets based on a given pattern.

        Parameters
        ----------
        name_pattern : str
            The pattern to match dataset names.
        return_attributes : bool, optional
            Whether to return dataset attributes along with the names. Defaults to False.

        Returns
        -------
        list of dict
            A JSON with a list of dataset names (and attributes if specified) matching the given pattern.
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["params"] = {"dslevel": self._encode_uri_component(name_pattern)}
        custom_args["url"] = "{}ds".format(self._request_endpoint)

        if return_attributes:
            custom_args["headers"]["X-IBM-Attributes"] = "base"

        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def list_members(self, dataset_name, member_pattern=None, member_start=None, limit=1000, attributes="member"):
        """Retrieve the list of members on a given PDS/PDSE.

        Parameters
        -------
        dataset_name: str
            The name of the dataset
        member_pattern: str
            Filters members by name pattern.
        member_start: str
            The starting point for listing members.
        limit: int
            The maximum number of members returned.
        attributes: str
            The member attributes to retrieve.

        Returns
        -------
        json
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
        return response_json["items"]  # type: ignore

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
        """
        Copy a dataset or member to another dataset or member.

        Parameters
        -------
        from_dataset_name: str
            Name of the dataset to copy from
        to_dataset_name: str
            Name of the dataset to copy to
        from_member_name: str
            Name of the member to copy from
        volser: str
            Volume serial number of the dataset to copy from
        alias: bool
            Alias of the dataset to copy from
        to_member_name: str
            Name of the member to copy to
        enq: str
            Enqueue type for the dataset to copy from
        replace: bool
            If true, members in the target data set are replaced.

        Returns
        -------
        json
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

    def create(self, dataset_name, options: Optional[DatasetOption] = None):
        """
        Create a sequential or partitioned dataset.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to be created
        options: DatasetOption
            A DatasetOption class with property options of the dataset

        Returns
        -------
        json
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

    def create_default(self, dataset_name: str, default_type: str):
        """
        Create a dataset with default options set.
        Default options depend on the requested type.

        Parameters
        ----------
        dataset_name: str
            The name of the dataset
        default_type: str
            The type of the dataset: "partitioned", "sequential", "classic", "c" or "binary"

        Returns
        -------
        json
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

    def get_content(self, dataset_name, stream=False):
        """Retrieve the contents of a given dataset.

        Parameters
        -------
        dataset_name: str
            The name of the dataset
        stream: bool
            Specifies

        Returns
        -------
        json
            A JSON with the contents of a given dataset
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        response_json = self.request_handler.perform_request("GET", custom_args, stream=stream)
        return response_json

    def get_binary_content(self, dataset_name, stream=False, with_prefixes=False):
        """
        Retrieve the contents of a given dataset as a binary bytes object.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to retrieve
        with_prefixes: boolean
            If True include a 4 byte big endian record len prefix. Default: False

        Returns
        -------
        response
            A response object from the requests library
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

    def write(self, dataset_name, data, encoding=_ZOWE_FILES_DEFAULT_ENCODING):
        """Write content to an existing dataset.

        Parameters
        ----------
        dataset_name: str
            Name of the dataset to retrieve
        data: str
            Content to be written
        encoding:
            Specifies encoding schema

        Returns
        -------
        json
            A JSON containing the result of the operation
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))
        custom_args["data"] = data
        custom_args["headers"]["Content-Type"] = "text/plain; charset={}".format(encoding)
        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[204, 201])
        return response_json

    def download(self, dataset_name, output_file):
        """Retrieve the contents of a dataset and saves it to a given file.

        Parameters
        -------
        dataset_name: str
            Name of the dataset to be downloaded
        output_file: str
            Name of the file to be saved locally
        """
        response = self.get_content(dataset_name, stream=True)
        with open(output_file, "w", encoding="utf-8") as f:
            for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
                f.write(chunk)

    def download_binary(self, dataset_name, output_file, with_prefixes=False):
        """Retrieve the contents of a binary dataset and saves it to a given file.

        Parameters
        ----------
        dataset_name:str
            Name of the dataset to download
        output_file:str
            Name of the local file to create
        with_prefixes:boolean
            If true, include a four big endian bytes record length prefix. The default is False
        """
        response = self.get_binary_content(dataset_name, with_prefixes=with_prefixes, stream=True)
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)

    def upload_file(self, input_file, dataset_name, encoding=_ZOWE_FILES_DEFAULT_ENCODING, binary=False):
        """Upload contents of a given file and uploads it to a dataset.

        Parameters
        -------
        input_file: str
            Name of the file to be uploaded
        dataset_name: str
            Name of the dataset to be created
        encoding: str
            Specifies the encoding schema
        binary: bool
            specifies whether the file is binary
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

    def recall_migrated(self, dataset_name: str, wait=False):
        """
        Recalls a migrated data set.

        Parameters
        ----------
        dataset_name: str
            Name of the data set

        wait: bool
            If true, the function waits for completion of the request, otherwise the request is queued

        Returns
        -------
        json
            A JSON containing the result of the operation
        """

        data = {"request": "hrecall", "wait": wait}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def delete_migrated(self, dataset_name: str, purge=False, wait=False):
        """
        Deletes migrated data set.

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
        json
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

    def migrate(self, dataset_name: str, wait=False):
        """
        Migrates the data set.

        Parameters
        ----------
        dataset_name: str
            Name of the data set

        wait: bool
            If true, the function waits for completion of the request, otherwise the request is queued.

        Returns
        -------
        json
            A JSON containing the result of the operation
        """

        data = {"request": "hmigrate", "wait": wait}

        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}ds/{}".format(self._request_endpoint, self._encode_uri_component(dataset_name))

        response_json = self.request_handler.perform_request("PUT", custom_args, expected_code=[200])
        return response_json

    def rename(self, before_dataset_name: str, after_dataset_name: str):
        """
        Renames the data set.

        Parameters
        ----------
        before_dataset_name: str
            The source data set name.

        after_dataset_name: str
            New name for the source data set.

        Returns
        -------
        json
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

    def rename_member(self, dataset_name: str, before_member_name: str, after_member_name: str, enq=""):
        """
        Renames the data set member.

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

        Returns
        -------
        json
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

    def delete(self, dataset_name, volume=None, member_name=None):
        """Deletes a sequential or partitioned data.

        Parameters
        ----------
        dataset_name: str
            The name of the dataset
        volume: str
            The optional volume serial number
        member_name: str
            The name of the member to be deleted

        Returns
        -------
        json
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
        self, from_filename, to_dataset_name, to_member_name=None, type=FileType.TEXT, replace=False
    ):
        """
        Copy a USS file to dataset.

        Parameters
        ----------
        from_filename: str
            Name of the file to copy from.
        to_dataset_name: str
            Name of the dataset to copy to.
        to_member_name: str
            Name of the member to copy to.
        type: FileType, optional
            Type of the file to copy from. Default is FileType.TEXT.
        replace: bool, optional
            If true, members in the target dataset are replaced.

        Returns
        -------
        json
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
