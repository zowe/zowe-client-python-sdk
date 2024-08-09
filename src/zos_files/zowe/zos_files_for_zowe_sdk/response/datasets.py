"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DatasetListResponse:
    items: Optional[List[dict]] = None
    returnedRows: Optional[int] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict, attributes: bool) -> None:
        for key, value in response.items():
            if key == "items":
                value = (
                    [DatasetResponse(**x) for x in value] if attributes else [SimpleDatasetResponse(**x) for x in value]
                )
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class SimpleDatasetResponse:
    dsname: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class DatasetResponse:
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
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class MemberListResponse:
    items: Optional[List[dict]] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict, attributes: bool) -> None:
        for key, value in response.items():
            if key == "items":
                value = (
                    [MemberResponse(**x) for x in value] if attributes else [SimpleMemberResponse(**x) for x in value]
                )
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class SimpleMemberResponse:
    member: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class MemberResponse:
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
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value
