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
class IssueCommandResponse:
    """Issue command response dataclass."""

    cmd_response_key: Optional[str] = None
    cmd_response_url: Optional[str] = None
    cmd_response_uri: Optional[str] = None
    cmd_response: Optional[str] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> str:
        """Get item by key."""
        return str(self.__dict__[key.replace("-", "_")])

    def __setitem__(self, key: str, value: str) -> None:
        """Set item by key."""
        self.__dict__[key.replace("-", "_")] = value


@dataclass
class ConsoleResponse:
    """Console response dataclass."""

    cmd_response: Optional[str] = None
    sol_key_detected: Optional[bool] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item by key."""
        self.__dict__[key.replace("-", "_")] = value
