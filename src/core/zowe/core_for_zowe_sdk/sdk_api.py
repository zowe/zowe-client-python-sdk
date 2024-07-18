"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import copy
import urllib

from . import session_constants
from .logger import Log
from .request_handler import RequestHandler
from .session import ISession, Session


class SdkApi:
    """
    Abstract class used to represent the base SDK API.

    Parameters
    ----------
    profile : dict
        Profile information in json (dict) format
    default_url : str
        Default url used for session
    logger_name : str
        Name of the logger (same as the filename by default)
    """

    def __init__(self, profile: dict, default_url: str, logger_name: str = __name__):
        session = Session(profile)
        self.session: ISession = session.load()

        self.logger = Log.register_logger(logger_name)

        self._default_service_url = default_url
        self._default_headers = {
            "Content-Type": "application/json",
            "X-CSRF-ZOSMF-HEADER": "",
        }

        self._request_endpoint = session.host_url + self._default_service_url

        self._request_arguments = {
            "url": self._request_endpoint,
            "headers": self._default_headers,
        }
        self.__session_arguments = {
            "verify": self.session.reject_unauthorized,
            "timeout": 30,
        }
        self.request_handler = RequestHandler(self.__session_arguments, logger_name=logger_name)

        if self.session.type == session_constants.AUTH_TYPE_BASIC:
            self._request_arguments["auth"] = (self.session.user, self.session.password)
        elif self.session.type == session_constants.AUTH_TYPE_BEARER:
            self._default_headers["Authorization"] = f"Bearer {self.session.token_value}"
        elif self.session.type == session_constants.AUTH_TYPE_TOKEN:
            self._default_headers["Cookie"] = f"{self.session.token_type}={self.session.token_value}"
        elif self.session.type == session_constants.AUTH_TYPE_CERT_PEM:
            self.__session_arguments["cert"] = self.session.cert

    def __enter__(self):
        """Return the SdkApi instance."""
        return self

    def __exit__(self, exc_type, exception, traceback):
        """Delete the request handler before exit."""
        del self.request_handler

    def _create_custom_request_arguments(self) -> dict:
        """
        Create a copy of the default request arguments dictionary.

        This method is required because the way that Python handles
        dictionary creation

        Returns
        -------
        dict
            A deepcopy of the request_arguments
        """
        return copy.deepcopy(self._request_arguments)

    def _encode_uri_component(self, str_to_adjust: str) -> str:
        """
        Adjust string to be correct in a URL.

        Parameters
        ----------
        str_to_adjust : str
            The string to encode

        Returns
        -------
        str
            A string with special characters, acceptable for a URL
        """
        return urllib.parse.quote(str_to_adjust, safe="!~*'()") if str_to_adjust is not None else None
