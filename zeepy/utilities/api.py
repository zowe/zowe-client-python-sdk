"""
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
"""
from .request_handler import RequestHandler
from .constants import constants


class ZosmfApi:
    """Abstract class for z/OSMF API classes"""
    def __init__(self, connection, default_url):
        self.connection = connection
        self.constants = constants
        self.default_service_url = default_url
        self.default_headers = {"Content-type": "application/json"}
        self.request_endpoint = "https://{base_url}{service}".format(
            base_url=self.connection.zosmf_host, service=self.default_service_url
        )
        self.request_arguments = {
            "url": self.request_endpoint,
            "auth": (self.connection.zosmf_user, self.connection.zosmf_password),
            "headers": self.default_headers,
        }
        self.session_arguments = {
            "verify": self.connection.ssl_verification,
            "timeout": 30,
        }
        self.request_handler = RequestHandler(self.session_arguments)

    def create_custom_request_arguments(self):
        """Creates a copy of the default request arguments"""
        return self.request_arguments.copy()
