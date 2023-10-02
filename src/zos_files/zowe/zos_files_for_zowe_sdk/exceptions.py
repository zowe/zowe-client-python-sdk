"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from .constants import zos_file_constants


class InvalidPermsOption(Exception):
    """Class used to represent an invalid permission value."""

    def __init__(self, value: int):
        """
        Parameters
        ----------
        value
            The value of the permission option
        """
        super().__init__("Invalid zos-files create command 'perms' option: {}".format(value))


class MaxAllocationQuantityExceeded(Exception):
    """Class used to represent an invalid allocation quantity."""

    def __init__(self):
        super().__init__(
            "Maximum allocation quantity of {} exceeded".format(zos_file_constants["MaxAllocationQuantity"])
        )
