"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import Any, Optional

CAMEL_TO_SNAKE_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')


def to_snake_case(src_str: str) -> str:
    """
    Convert camel case string (cameCaseString) to a snake case string (snake_case_string).

    Parameters
    ----------
    src_str : str
        The string to convert

    Returns
    -------
    str
        The converted string
    """
    return CAMEL_TO_SNAKE_CASE_PATTERN.sub('_', src_str).lower()


@dataclass
class IssueCommandResponse:
    cmd_response_key: Optional[str] = None
    cmd_response_url: Optional[str] = None
    cmd_response_uri: Optional[str] = None
    cmd_response: Optional[str] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> str:
        return str(self.__dict__[key.replace("-", "_")])

    def __setitem__(self, key: str, value: str) -> None:
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class ConsoleResponse:
    cmd_response: Optional[str] = None
    sol_key_detected: Optional[bool] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class LogMessageResponse:
    """
    Log message response object.
    See more at [Messages JSON object](https://www.ibm.com/docs/en/zos/3.2.0?topic=services-get-messages-from-hardcopy-log#IZUHPINFO_API_GetMessagesandLogs.dita__table_qby_q2x_ypb)

    Parameters
    ----------
    cart : Optional[str]
        Eight character command and response token (CART).
    color : Optional[str]
        The color of the message.
    job_name : Optional[str]
        The name of the job that generates the message.
    message : Optional[str]
        The content of the message.
    message_id : Optional[str]
        The message ID.
    reply_id : Optional[str]
        Reply ID, in decimal.
    system : Optional[str]
        Original eight character system name.
    type : Optional[str]
        HARDCOPY.
    sub_type : Optional[str]
        Indicate whether the message is a DOM, WTOR, or HOLD message.
    time : Optional[datetime]
        For example, “Thu Feb 03 03:00 GMT 2021”.
    timestamp : Optional[int]
        UNIX timestamp (milliseconds since epoch). For example, 1621920830109.
    """
    
    cart: Optional[str] = None
    color: Optional[str] = None
    job_name: Optional[str] = None
    message: Optional[str] = None
    message_id: Optional[str] = None
    reply_id: Optional[str] = None
    system: Optional[str] = None
    type: Optional[str] = None
    sub_type: Optional[str] = None
    time: Optional[datetime] = None
    timestamp: Optional[int] = None

    def __init__(self, raw_data: dict[str, Any]) -> None:
        for raw_key, raw_value in raw_data.items():
            key = to_snake_case(raw_key)
            match(key):
                case "time":
                    value = datetime.strptime(raw_value, "%a %b %d %H:%M:%S %Z %Y")
                case _:
                    value = raw_value
            super().__setattr__(key, value)
    
    def __getitem__(self, key: str) -> Any:
        return self.__dict__[to_snake_case(key)]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[to_snake_case(key)] = value


@dataclass
class GetLogMessagesResponse:
    """
    Get log messages response object.
    See more at [Response content for a successful Get Messages request](https://www.ibm.com/docs/en/zos/3.2.0?topic=services-get-messages-from-hardcopy-log#IZUHPINFO_API_GetMessagesandLogs.dita__getcmdresponse)

    Parameters
    ----------
    timezone : Optional[tz]
        The timezone of the z/OS system.
    total_items : Optional[int]
        Total number of messages returned in the response.
    next_timestamp : Optional[int]
        The UNIX timestamp (milliseconds).
    items : Optional[list[LogMessageResponse]]
        Array of log messages.
    source : Optional[str]
        Indicates the source of the messages.
    """
    timezone: Optional[tz] = None
    total_items: Optional[int] = None
    next_timestamp: Optional[int] = None
    items: Optional[list[LogMessageResponse]] = None
    source: Optional[str] = None
    
    def __init__(self, response: dict[str, Any]) -> None:
        for raw_key, raw_value in response.items():
            key = to_snake_case(raw_key)
            match(key):
                case "timezone":
                    value = tz(timedelta(hours=raw_value if raw_value is not None else 0))
                case "items":
                    value = [LogMessageResponse(x) for x in raw_value] if not raw_value == None else None
                case _:
                    value = raw_value
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[to_snake_case(key)]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[to_snake_case(key)] = value


@dataclass
class UnsuccessfulGetLogMessagesResponse:
    """
    Get log messages response object for an unsuccessful request.
    See more at [Response content for an unsuccessful Get Messages request](https://www.ibm.com/docs/en/zos/3.2.0?topic=services-get-messages-from-hardcopy-log#IZUHPINFO_API_GetMessagesandLogs.dita__table_b2g_sgx_ypb)

    Parameters
    ----------
    return_code : Optional[int]
        Identifies the category of error.
    reason_code : Optional[int]
        Identifies the specific error.
    reason : Optional[str]
        Text that describes the cause of the error.
    """
    return_code: Optional[int] = None
    reason_code: Optional[int] = None
    reason: Optional[str] = None
    
    def __init__(self, response: dict[str, Any]) -> None:
        for raw_key, value in response.items():
            key = to_snake_case(raw_key)
            super().__setattr__(key, value)

    def __getitem__(self, key):
        return self.__dict__[to_snake_case(key)]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[to_snake_case(key)] = value
