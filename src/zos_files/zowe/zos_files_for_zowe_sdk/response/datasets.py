"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DatasetListResponse:
    """Dataset list response dataclass."""

    items: Optional[list["DatasetResponse"] | list["SimpleDatasetResponse"]] = None
    returnedRows: Optional[int] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict[str, Any], attributes: bool) -> None:
        for key, value in response.items():
            if key == "items":
                value = (
                    [DatasetResponse(**x) for x in value] if attributes else [SimpleDatasetResponse(**x) for x in value]
                )
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class SimpleDatasetResponse:
    """Simple dataset response dataclass."""

    dsname: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class DatasetResponse:
    """Dataset response dataclass."""

    dsname: Optional[str] = None
    blksz: Optional[str] = None
    catnm: Optional[str] = None
    cdate: Optional[str] = None
    dev: Optional[str] = None
    dsorg: Optional[str] = None
    edate: Optional[str] = None
    extx: Optional[str] = None
    lrecl: Optional[str] = None
    migr: Optional[str] = None
    mvol: Optional[str] = None
    ovf: Optional[str] = None
    rdate: Optional[str] = None
    recfm: Optional[str] = None
    sizex: Optional[str] = None
    spacu: Optional[str] = None
    used: Optional[str] = None
    vol: Optional[str] = None
    vols: Optional[str] = None
    dsntp: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class MemberListResponse:
    """Member list response dataclass."""

    items: Optional[list[dict[str, Any]]] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict[str, Any], attributes: bool) -> None:
        for key, value in response.items():
            if key == "items":
                raw_members_list: list[dict[str, Any]] = value
                if not attributes:
                    members_list = [SimpleMemberResponse(**raw_mem_props) for raw_mem_props in raw_members_list]
                elif len(raw_members_list) != 0:
                    has_undef_recfm_members = False
                    for next_member in raw_members_list:
                        if "ac" in next_member.keys():
                            has_undef_recfm_members = True
                            break
                    members_list = (
                        [UndefRecfmMemberResponse(raw_mem_props) for raw_mem_props in raw_members_list]
                        if has_undef_recfm_members
                        else [MemberResponse(**raw_mem_props) for raw_mem_props in raw_members_list]
                    )
                else:
                    members_list = []
                super().__setattr__(key, members_list)
            else:
                super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class SimpleMemberResponse:
    """Simple member response dataclass."""

    member: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class MemberResponse:
    """Member response dataclass."""

    member: Optional[str] = None
    vers: Optional[int] = None
    mod: Optional[int] = None
    c4date: Optional[str] = None
    m4date: Optional[str] = None
    cnorc: Optional[int] = None
    inorc: Optional[int] = None
    mnorc: Optional[int] = None
    mtime: Optional[str] = None
    msec: Optional[str] = None
    user: Optional[str] = None
    sclm: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key] = value


@dataclass
class UndefRecfmMemberResponse:
    """https://www.ibm.com/docs/en/zos/3.2.0?topic=zdsfri-json-document-specifications-zos-data-set-file-rest-interface-requests#RESTFILES_JSONDocumentSpecifications__pdsUkeypairs"""
    member: Optional[str] = None
    ac: Optional[str] = None
    alias_of: Optional[str] = None
    amode: Optional[str] = None
    rmode: Optional[str] = None
    size: Optional[str] = None
    ttr: Optional[str] = None
    ssi: Optional[str] = None

    def __init__(self, member_props: dict[str, Any]) -> None:
        for k, value in member_props.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key.replace("-", "_")] = value
