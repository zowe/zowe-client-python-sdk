"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Union

from zowe.core_for_zowe_sdk.zosmf_profile2 import ProfileManager
from . import session_constants


@dataclass
class ISession:
    """
    Class to represent session parameters
    """

    hostname: str
    port: int
    rejectUnauthorised: bool = True
    user: Union[str, None] = None
    password: Union[str, None] = None
    protocol: Union[str, None] = None
    basePath: Union[str, None] = None
    type: Union[str, None] = None
    base64EncodeAuth: Union[str, None] = None
    tokenType: Union[str, None] = None
    tokenValue: Union[str, None] = None


class Session:
    """
    Class used to represent connection details
    """

    def __init__(self, props: dict) -> ISession:
        # set hostname and port
        if props["hostname"] is not None and props["port"] is not None:
            self.session: ISession = ISession(
                hostname=props["hostname"], port=props["port"]
            )
        else:
            raise "Hostname and Port must be supplied"

        # determine authentication type
        if props["user"] is not None and props["password"] is not None:
            self.session.user = props["user"]
            self.session.password = props["password"]
            self.session.type = session_constants.AUTH_TYPE_BASIC
        elif props["tokenType"] is not None and props["tokenValue"] is not None:
            self.session.tokenType = props["tokenType"]
            self.session.tokenValue = props["tokenValue"]
            self.session.type = session_constants.AUTH_TYPE_TOKEN
        else:
            raise "An authentication method must be supplied"

        return self.session

    @property
    def host_url(self) -> str:
        return f"{self.session.protocol}://{self.session.host}:{self.session.port}"
