"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from .exceptions import UnexpectedStatus
from .exceptions import RequestFailed
from .exceptions import InvalidRequestMethod
import requests
import urllib3


class RequestHandler:
    """
    Class used to handle HTTP/HTTPS requests.

    ...

    Attributes
    ----------
    session_arguments
        zowe sdk session arguments
    valid_methods
        list of supported request methods

    Methods
    -------
    handle_ssl_warnings()
        Turn off urllib3 warnings if ssl verification is off
    perform_request(method, request_arguments, expected_code=[200])
        Prepares and execute a request based on given parameters
    validate_method()
        Validates if request method is supported
    send_request()
        Creates a session and execute an HTTP/HTTPS request
    validate_response()
        Validates the request response based on expected response codes
    normalize_response()
        Normalizes the request response object to a JSON format
    """

    def __init__(self, session_arguments):
        """
        Construct a RequestHandler object.

        Parameters
        ----------
        session_arguments
            The Zowe SDK session arguments
        """
        self.session_arguments = session_arguments
        self.valid_methods = ["GET", "POST", "PUT", "DELETE"]
        self.handle_ssl_warnings()

    def handle_ssl_warnings(self):
        """Turn off warnings if the SSL verification argument if off."""
        if not self.session_arguments['verify']:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def perform_request(self, method, request_arguments, expected_code=[200]):
        """Execute an HTTP/HTTPS requests from given arguments and return validated response (JSON).

        Parameters
        ----------
        method
            The request method that should be used
        request_arguments
            The dictionary containing the required arguments for the execution of the request
        expected_code
            The list containing the acceptable response codes (default is [200])

        Returns
        -------
        normalized_response
            normalized request response in json (dictionary)
        """
        self.method = method
        self.request_arguments = request_arguments
        self.expected_code = expected_code
        self.validate_method()
        self.send_request()
        self.validate_response()
        return self.normalize_response()

    def validate_method(self):
        """Check if the input request method for the request is supported.

        Raises
        ------
        InvalidRequestMethod
            If the input request method is not supported
        """
        if self.method not in self.valid_methods:
            raise InvalidRequestMethod(self.method)

    def send_request(self):
        """Build a custom session object, prepare it with a custom request and send it."""
        session = requests.Session()
        request_object = requests.Request(method=self.method, **self.request_arguments)
        prepared = session.prepare_request(request_object)
        self.response = session.send(prepared, **self.session_arguments)

    def validate_response(self):
        """Validate if request response is acceptable based on expected code list.

        Raises
        ------
        UnexpectedStatus
            If the response status code is not in the expected code list
        RequestFailed
            If the HTTP/HTTPS request fails
        """
        # Automatically checks if status code is between 200 and 400
        if self.response:
            if self.response.status_code not in self.expected_code:
                raise UnexpectedStatus(self.expected_code, self.response.status_code, self.response.text)
        else:
            output_str = str(self.response.request.url)
            output_str += "\n" + str(self.response.request.headers)
            output_str += "\n" + str(self.response.request.body)
            output_str += "\n" + str(self.response.text)
            raise RequestFailed(self.response.status_code, output_str)

    def normalize_response(self):
        """Normalize the response object to a JSON format.

        Returns
        -------
        json
            A normalized JSON for the request response
        """
        try:
            return self.response.json()
        except:
            return {"response": self.response.text}
