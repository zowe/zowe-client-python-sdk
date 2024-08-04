"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from dataclasses import dataclass
from typing import Optional

from . import session_constants
from .logger import Log


@dataclass
class ISession:
    """Class to represent session parameters."""

    host: str
    port: int = session_constants.DEFAULT_HTTPS_PORT
    reject_unauthorized: bool = True
    user: Optional[str] = None
    password: Optional[str] = None
    protocol: str = session_constants.HTTPS_PROTOCOL
    base_path: Optional[str] = None
    type: Optional[str] = None
    token_type: Optional[str] = None
    token_value: Optional[str] = None
    cert: Optional[str] = None


class Session:
    """
    Class used to set connection details received from a ProfileManager or manually set by passing and ISession object.

    Parameters
    ----------
    props : dict
        Profile and properties

    Raises
    ------
    Exception
        Exception thrown when cert key is not provided
    """

    def __init__(self, props: dict) -> None:
        # set host and port
        self.__logger = Log.register_logger(__name__)

        if props.get("host") is not None:
            self.session: ISession = ISession(host=props.get("host"))
        else:
            self.__logger.error("Host not supplied")
            raise Exception("Host must be supplied")

        # determine authentication type
        if props.get("user") is not None and props.get("password") is not None:
            self.session.user = props.get("user")
            self.session.password = props.get("password")
            self.session.reject_unauthorized = props.get("rejectUnauthorized")
            self.session.type = session_constants.AUTH_TYPE_BASIC
        elif props.get("tokenType") is not None and props.get("tokenValue") is not None:
            self.session.token_type = props.get("tokenType")
            self.session.token_value = props.get("tokenValue")
            self.session.type = session_constants.AUTH_TYPE_TOKEN
        elif props.get("tokenValue") is not None:
            self.session.token_value = props.get("tokenValue")
            self.session.type = session_constants.AUTH_TYPE_BEARER
        elif props.get("certFile") is not None:
            if props.get("certKeyFile"):
                self.session.cert = (props.get("certFile"), props.get("certKeyFile"))
            else:
                self.__logger.error("A certificate key file must be provided when certFile is specified")
                raise Exception("A certificate key file must be provided when certFile is specified")
            self.session.reject_unauthorized = props.get("rejectUnauthorized")
            self.session.type = session_constants.AUTH_TYPE_CERT_PEM
        else:
            self.session.type = session_constants.AUTH_TYPE_NONE
            self.__logger.info("Authentication method not supplied")
            # raise Exception("An authentication method must be supplied")

        # set additional parameters
        self.session.base_path = props.get("basePath")
        self.session.port = props.get("port", self.session.port)
        self.session.protocol = props.get("protocol", self.session.protocol)
        self.session.reject_unauthorized = False if props.get("rejectUnauthorized") == False else True

    def load(self) -> ISession:
        """
        Load a ISession object.

        Returns
        -------
        ISession
            A custom ISession object.
        """
        return self.session

    @property
    def host_url(self) -> str:
        """
        Return the formatted host URL.

        Returns
        -------
        str
            the formatted host URL
        """
        base_path = self.session.base_path or ""
        return f"{self.session.protocol}://{self.session.host}:{self.session.port}{base_path}"
