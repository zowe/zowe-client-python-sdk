"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from .constants import constants


messages = {
    "MaxAllocationQuantityExceeded": f"Maximum allocation quantity of " \
                                        f"{constants['MaxAllocationQuantity']} exceeded",
    "InvalidPermsOption": "Invalid zos-files create command 'perms' option: "
}