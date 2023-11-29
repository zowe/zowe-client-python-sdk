"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import requests
import urllib3

from .exceptions import InvalidRequestMethod, RequestFailed, UnexpectedStatus


class RequestHandler:
    """
    Class used to handle HTTP/HTTPS requests.

    Attributes
    ----------
    session_arguments: dict
        Zowe SDK session arguments
    valid_methods: list
        List of supported request methods
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
        self.__handle_ssl_warnings()

    def __handle_ssl_warnings(self):
        """Turn off warnings if the SSL verification argument if off."""
        if not self.session_arguments["verify"]:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def perform_request(self, method, request_arguments, expected_code=[200]):
        """Execute an HTTP/HTTPS requests from given arguments and return validated response (JSON).

        Parameters
        ----------
        method: str
            The request method that should be used
        request_arguments: dict
            The dictionary containing the required arguments for the execution of the request
        expected_code: int
            The list containing the acceptable response codes (default is [200])

        Returns
        -------
        normalized_response: json
            normalized request response in json (dictionary)
        """
        self.method = method
        self.request_arguments = request_arguments
        self.expected_code = expected_code
        self.__validate_method()
        self.__send_request()
        self.__validate_response()
        return self.__normalize_response()

    def perform_streamed_request(self, method, request_arguments, expected_code=[200]):
        """Execute a streamed HTTP/HTTPS requests from given arguments and return a raw response.

        Parameters
        ----------
        method: str
            The request method that should be used
        request_arguments: dict
            The dictionary containing the required arguments for the execution of the request
        expected_code: int
            The list containing the acceptable response codes (default is [200])

        Returns
        -------
        A raw response data
        """
        self.method = method
        self.request_arguments = request_arguments
        self.expected_code = expected_code
        self.__validate_method()
        self.__send_request(stream=True)
        self.__validate_response()
        return self.response.raw

    def __validate_method(self):
        """Check if the input request method for the request is supported.

        Raises
        ------
        InvalidRequestMethod
            If the input request method is not supported
        """
        if self.method not in self.valid_methods:
            raise InvalidRequestMethod(self.method)

    def __send_request(self, stream=False):
        """Build a custom session object, prepare it with a custom request and send it."""
        session = requests.Session()
        request_object = requests.Request(method=self.method, **self.request_arguments)
        prepared = session.prepare_request(request_object)
        self.response = session.send(prepared, stream=stream, **self.session_arguments)

    def __validate_response(self):
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

    def __normalize_response(self):
        """Normalize the response object to a JSON format.

        Returns
        -------
        A bytes object if the response content type is application/octet-stream,
        a normalized JSON for the request response otherwise
        """
        if self.response.headers.get("Content-Type") == "application/octet-stream":
            return self.response.content
        else:
            try:
                return self.response.json()
            except:
                return {"response": self.response.text}
