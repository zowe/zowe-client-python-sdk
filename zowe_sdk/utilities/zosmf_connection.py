"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""


class ZosmfConnection:
    """
    Class used to represent a z/OSMF connection.

    ...

    Attributes
    ----------
    zosmf_host
        The z/OSMF host address
    zosmf_user
        The user for the z/OSMF REST API
    zosmf_password
        The password for the z/OSMF REST API
    ssl_verification
        The value for the requests ssl verification parameter
    """

    def __init__(
        self,
        zosmf_host,
        zosmf_user,
        zosmf_password,
        ssl_verification
    ):
        """Construct a ZosmfConnection object."""
        self.zosmf_host = zosmf_host
        self.zosmf_user = zosmf_user
        self.zosmf_password = zosmf_password
        self.ssl_verification = ssl_verification
