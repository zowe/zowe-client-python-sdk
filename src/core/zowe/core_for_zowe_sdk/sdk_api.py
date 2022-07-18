"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
from .request_handler import RequestHandler
from .constants import constants
from .session import Session, ISession
from .zosmf_profile2 import ProfileManager
from . import session_constants


class SdkApi:
    """
    Abstract class used to represent the base SDK API.
    """

    def __init__(self, default_url):
        self.profile = ProfileManager()
        self.profile_props = self.profile.load()
        self.session: ISession = Session(self.profile_props)

        self.default_service_url = default_url
        self.default_headers = {
            "Content-type": "application/json",
            "X-CSRF-ZOSMF-HEADER": "",
        }

        self.request_endpoint = "https://{base_url}{service}".format(
            base_url=self.connection.host_url, service=self.default_service_url
        )
        self.request_arguments = {
            "url": self.request_endpoint,
            "headers": self.default_headers,
        }
        self.session_arguments = {
            "verify": self.connection.ssl_verification,
            "timeout": 30,
        }
        self.request_handler = RequestHandler(self.session_arguments)

        if self.session.type == session_constants.AUTH_TYPE_BASIC:
            self.request_arguments["auth"] = (self.session.user, self.session.user)
        elif self.session.type == session_constants.AUTH_TYPE_TOKEN:
            self.default_headers["Authorization"] = f"Bearer {self.session.tokenValue}"
            self.request_arguments["auth"] = self.default_headers["Authorization"]

    def _create_custom_request_arguments(self):
        """Create a copy of the default request arguments dictionary.

        This method is required because the way that Python handles
        dictionary creation
        """
        return self.request_arguments.copy()
