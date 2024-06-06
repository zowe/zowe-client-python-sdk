"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

zos_file_constants = {
    "MaxAllocationQuantity": 16777215,
    "ZoweFilesDefaultEncoding": "utf-8",
}
from enum import Enum


class FileType(Enum):
    BINARY = "binary"
    EXECUTABLE = "executable"
    TEXT = "text"
