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
class Plugin:
    pluginVersion: Optional[str] = None
    pluginDefaultName: Optional[str] = None
    pluginStatus: Optional[str] = None

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value


@dataclass
class ZosmfResponse:
    zos_version: Optional[str] = None
    zosmf_port: Optional[str] = None
    zosmf_version: Optional[str] = None
    zosmf_hostname: Optional[str] = None
    plugins: list[Plugin] = field(default_factory=list)
    zosmf_saf_realm: Optional[str] = None
    zosmf_full_version: Optional[str] = None
    api_version: Optional[str] = None

    def __init__(self, response: dict[str, Any]) -> None:
        for k, value in response.items():
            key = k.replace("-", "_")
            if key == "plugins":
                value = [Plugin(**x) for x in value]
            super().__setattr__(key, value)

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key.replace("-", "_")]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key.replace("-", "_")] = value
