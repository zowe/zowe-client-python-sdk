"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Union

from . import session_constants


@dataclass
class ISession:
    """
    Class to represent session parameters
    """

    hostname: str
    port: int = session_constants.DEFAULT_HTTPS_PORT
    rejectUnauthorized: bool = True
    user: Union[str, None] = None
    password: Union[str, None] = None
    protocol: str = session_constants.HTTPS_PROTOCOL
    basePath: Union[str, None] = None
    type: Union[str, None] = None
    tokenType: Union[str, None] = None
    tokenValue: Union[str, None] = None


class Session:
    """
    Class used to represent connection details
    """

    def __init__(self, props: dict) -> None:
        # set hostname and port
        if props["host"] is not None:
            self.session: ISession = ISession(hostname=props["host"])
        else:
            raise "Hostname and Port must be supplied"

        # determine authentication type
        if props["user"] is not None and props["password"] is not None:
            self.session.user = props["user"]
            self.session.password = props["password"]
            self.session.rejectUnauthorized = props["rejectUnauthorized"]
            self.session.type = session_constants.AUTH_TYPE_BASIC
        elif props["tokenType"] is not None and props["tokenValue"] is not None:
            self.session.tokenType = props["tokenType"]
            self.session.tokenValue = props["tokenValue"]
            self.session.type = session_constants.AUTH_TYPE_TOKEN
        else:
            raise "An authentication method must be supplied"

        # set additional parameters
        self.session.rejectUnauthorized = props.get("rejectUnauthorized", True)

    def load(self) -> ISession:
        return self.session

    @property
    def host_url(self) -> str:
        return f"{self.session.protocol}://{self.session.host}:{self.session.port}"
