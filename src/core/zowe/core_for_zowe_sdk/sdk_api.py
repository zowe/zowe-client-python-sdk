"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
from .request_handler import RequestHandler
from .profile_manager import ProfileManager
from .session import Session


class SdkApi:
    """
    Abstract class used to represent the base SDK API.

    Attributes
    ----------
    profile: dict
        A dictionary containing the connection arguments
    """

    def __init__(self, profile, default_url):
        self.profile = ProfileManager.load("my_zosmf", "zosmf")
        self.session = Session(**profile)

        self.default_service_url = default_url
        self.default_headers = {
            "Content-type": "application/json",
            "X-CSRF-ZOSMF-HEADER": "",
            "Authorization": f"Bearer {Session.tokenValue}"
        }
        self.request_endpoint = "https://{base_url}{service}".format(
            base_url=self.profile.host_url, service=self.default_service_url
        )
        self.request_arguments = {
            "url": self.request_endpoint,
            "auth": (self.profile.user, self.profile.password),
            "headers": self.default_headers
        }
        if self.session.type is "basic":
            self.request_arguments["auth"] = (self.profile.user, self.profile.password),
        elif self.session.type is "token":
            self.request_arguments["auth"] = self.default_headers["Authorization"]

        self.session_arguments = {
            "verify": self.profile.ssl_verification,
            "timeout": 30
        }
        self.request_handler = RequestHandler(self.session_arguments)

    def _create_custom_request_arguments(self):
        """Create a copy of the default request arguments dictionary.

        This method is required because the way that Python handles
        dictionary creation
        """
        return self.request_arguments.copy()
