"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from .exceptions import MissingConnectionArgs
from .logger import Log


class ApiConnection:
    """
    Class used to represent a connection with a REST API.

    Parameters
    ----------
    host_url: str
        The base url of the rest api host
    user: str
        The user of the rest api
    password: str
        The password for the user
    ssl_verification: bool
        Options for ssl verification. True by default.

    Raises
    ------
    MissingConnectionArgs
        Missing connection argument.
    """

    def __init__(self, host_url: str, user: str, password: str, ssl_verification: bool = True):
        __logger = Log.register_logger(__name__)
        if not host_url or not user or not password:
            __logger.error("Missing connection argument")
            raise MissingConnectionArgs()

        self.host_url = host_url
        self.user = user
        self.password = password
        self.ssl_verification = ssl_verification
