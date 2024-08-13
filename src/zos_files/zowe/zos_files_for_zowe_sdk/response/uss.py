"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class USSResponse:
    name: Optional[str] = None
    mode: Optional[str] = None
    size: Optional[int] = None
    uid: Optional[int] = None
    user: Optional[str] = None
    gid: Optional[int] = None
    group: Optional[str] = None
    mtime: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class USSListResponse:
    items: Optional[List[dict]] = None
    returnedRows: Optional[int] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict) -> None:
        for key, value in response.items():
            if key == "items":
                value = [USSResponse(**x) for x in value]
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value
