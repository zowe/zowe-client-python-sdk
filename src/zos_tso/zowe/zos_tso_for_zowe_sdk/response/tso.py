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
class StartResponse:
    servletKey: Optional[str] = None
    queueID: Optional[str] = None
    sessionID: Optional[str] = None
    ver: Optional[str] = None
    tsoData: Optional[List[dict]] = None
    reused: Optional[bool] = None
    timeout: Optional[bool] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class EndResponse:
    servletKey: Optional[str] = None
    ver: Optional[str] = None
    reused: Optional[bool] = None
    timeout: Optional[bool] = None
    msgData: Optional[str] = None
    msgId: Optional[List] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class SendResponse:
    servletKey: Optional[str] = None
    ver: Optional[str] = None
    tsoData: Optional[List[dict]] = None
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
    tso_messages: list

    def __init__(self, start, send, end, msg):
        self.start_response = start
        self.send_response = send
        self.end_response = end
        self.tso_messages = msg
