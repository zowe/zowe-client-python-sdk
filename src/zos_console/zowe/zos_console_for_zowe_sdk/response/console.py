"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class IssueCommandResponse:
    cmd_response_key: Optional[str] = None
    cmd_response_url: Optional[str] = None
    cmd_response_uri: Optional[str] = None
    cmd_response: Optional[str] = None

    def __init__(self, response: dict) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> str:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: str) -> None:
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class ConsoleResponse:
    cmd_response: Optional[str] = None
    sol_key_detected: Optional[bool] = None

    def __init__(self, response: dict) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key.replace("-", "_")] = value
