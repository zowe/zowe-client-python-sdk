"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


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
    items: Optional[list[dict[str, Any]]] = None
    returnedRows: Optional[int] = None
    totalRows: Optional[int] = None
    JSONversion: Optional[int] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for key, value in response.items():
            if key == "items":
                value = [USSResponse(**x) for x in value]
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


class USSFileTagType(Enum):
    TEXT = "t"
    BINARY = "b"
    MIXED = "m"

    @classmethod
    def from_string(cls, value: str) -> Optional['USSFileTagType']:
        """Convert string to enum, return None if not valid"""
        for tag_type in cls:
            if tag_type.value == value:
                return tag_type
        return None


@dataclass
class USSFileTag:
    tag_type: Optional['USSFileTagType'] = None
    charset: Optional[str] = None
    is_conversion_enabled: Optional[bool] = None

    def __init__(self, response: dict[str, Any]) -> None:
        stdout = response["stdout"]
        if stdout is not None and len(stdout) == 1:
            tag_for_file = stdout[0]

            if " T=on " in tag_for_file:
                self.__setattr__("is_conversion_enabled", True)
            elif " T=off " in tag_for_file:
                self.__setattr__("is_conversion_enabled", False)
            else:
                raise Exception("Unknown response from 'chtag list': {}".format(response))

            (tag_type, charset) = tag_for_file.split("T=")[0].strip().split(" ")
            self.__setattr__("tag_type", USSFileTagType.from_string(tag_type))
            self.__setattr__("charset", charset if charset != "untagged" else None)
        else:
            raise Exception("Unknown response from 'chtag list': {}".format(response))

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value
