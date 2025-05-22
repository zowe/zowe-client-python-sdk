"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class StartResponse:
    servletKey: str
    queueID: Optional[str] = None
    sessionID: Optional[str] = None
    ver: Optional[str] = None
    tsoData: Optional[list[dict[str, str]]] = None
    reused: Optional[bool] = None
    timeout: Optional[bool] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class EndResponse:
    servletKey: str
    msgId: list[str] = field(default_factory=list)
    ver: Optional[str] = None
    reused: Optional[bool] = None
    timeout: Optional[bool] = None
    msgData: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class SendResponse:
    servletKey: str
    tsoData: list[dict[str, Any]]
    ver: Optional[str] = None
    reused: Optional[bool] = None
    timeout: Optional[bool] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class IssueResponse:
    start_response: StartResponse
    send_response: SendResponse
    end_response: EndResponse
    tso_messages: list[str]

    def __init__(self, start: StartResponse, send: SendResponse, end: EndResponse, msg: list[str]) -> None:
        self.start_response = start
        self.send_response = send
        self.end_response = end
        self.tso_messages = msg
