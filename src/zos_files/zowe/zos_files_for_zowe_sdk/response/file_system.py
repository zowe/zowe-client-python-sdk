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
class FileSystemResponse:
    name: Optional[str] = None
    mountpoint: Optional[str] = None
    fstname: Optional[str] = None
    status: Optional[str] = None
    mode: Optional[List[str]] = None
    dev: Optional[int] = None
    fstype: Optional[int] = None
    bsize: Optional[int] = None
    bavail: Optional[int] = None
    blocks: Optional[int] = None
    sysname: Optional[str] = None
    readibc: Optional[int] = None
    writeibc: Optional[int] = None
    diribc: Optional[int] = None
    mountparm: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class FileSystemListResponse:
    items: Optional[List[FileSystemResponse]] = None
    returnedRows: Optional[int] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict) -> None:
        for key, value in response.items():
            if key == "items":
                value = [FileSystemResponse(**x) for x in value]
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value
