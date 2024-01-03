"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import urllib

from . import session_constants
from .exceptions import UnsupportedAuthType
from .request_handler import RequestHandler
from .session import ISession, Session


class SdkApi:
    """
    Abstract class used to represent the base SDK API.
    """

    def __init__(self, profile, default_url):
        self.profile = profile
        session = Session(profile)
        self.session: ISession = session.load()

        self.default_service_url = default_url
        self.default_headers = {
            "Content-Type": "application/json",
            "X-CSRF-ZOSMF-HEADER": "",
        }

        self.request_endpoint = session.host_url + self.default_service_url

        self.request_arguments = {
            "url": self.request_endpoint,
            "headers": self.default_headers,
        }
        self.session_arguments = {
            "verify": self.session.rejectUnauthorized,
            "timeout": 30,
        }
        self.request_handler = RequestHandler(self.session_arguments)

        if self.session.type == session_constants.AUTH_TYPE_BASIC:
            self.request_arguments["auth"] = (self.session.user, self.session.password)
        elif self.session.type == session_constants.AUTH_TYPE_BEARER:
            self.default_headers["Authorization"] = f"Bearer {self.session.tokenValue}"
        elif self.session.type == session_constants.AUTH_TYPE_TOKEN:
            self.default_headers["Cookie"] = f"{self.session.tokenType}={self.session.tokenValue}"
        else:
            raise UnsupportedAuthType(self.session.type)

    def _create_custom_request_arguments(self):
        """Create a copy of the default request arguments dictionary.

        This method is required because the way that Python handles
        dictionary creation
        """
        return self.request_arguments.copy()

    def _encode_uri_component(self, str_to_adjust):
        """Adjust string to be correct in a URL

        Returns
        -------
        adjusted_str
            A string with special characters, acceptable for a URL
        """

        return urllib.parse.quote(str_to_adjust, safe="!~*'()") if str_to_adjust is not None else None
