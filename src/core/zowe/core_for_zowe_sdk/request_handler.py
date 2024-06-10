"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import requests
import urllib3
from .logger import Log

from .exceptions import InvalidRequestMethod, RequestFailed, UnexpectedStatus
from .logger import Log


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

    def __init__(self, session_arguments, logger_name = __name__):
        """
        Construct a RequestHandler object.

        Parameters
        ----------
        session_arguments
            The Zowe SDK session arguments

        logger_name
            The logger name of the modules calling request handler
        """
        self.session_arguments = session_arguments
        self.valid_methods = ["GET", "POST", "PUT", "DELETE"]
        self.__handle_ssl_warnings()
        self.__logger = Log.registerLogger(logger_name)

    def __handle_ssl_warnings(self):
        """Turn off warnings if the SSL verification argument if off."""
        if not self.session_arguments["verify"]:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def perform_request(self, method, request_arguments, expected_code=[200], stream = False):
        """Execute an HTTP/HTTPS requests from given arguments and return validated response (JSON).

        Parameters
        ----------
        method: str
            The request method that should be used
        request_arguments: dict
            The dictionary containing the required arguments for the execution of the request
        expected_code: int
            The list containing the acceptable response codes (default is [200])
        stream: boolean
            The boolean value whether the request is stream

        Returns
        -------
        normalized_response: json
            normalized request response in json (dictionary)
        """
        self.method = method
        self.request_arguments = request_arguments
        self.expected_code = expected_code
        self.__logger.debug(f"Request method: {self.method}, Request arguments: {self.request_arguments}, Expected code: {expected_code}")
        self.__validate_method()
        self.__send_request(stream = stream)
        self.__validate_response()
        if stream:
            return self.response
        return self.__normalize_response()

    def __validate_method(self):
        """Check if the input request method for the request is supported.

        Raises
        ------
        InvalidRequestMethod
            If the input request method is not supported
        """
        if self.method not in self.valid_methods:
            self.__logger.error(f"Invalid HTTP method input {self.method}")
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
        if self.response.ok:
            if self.response.status_code not in self.expected_code:
                self.__logger.error(f"The status code from z/OSMF was: {self.expected_code}\nExpected: {self.response.status_code}\nRequest output:{self.response.text}")
                raise UnexpectedStatus(self.expected_code, self.response.status_code, self.response.text)
        else:
            output_str = str(self.response.request.url)
            output_str += "\n" + str(self.response.request.headers)
            output_str += "\n" + str(self.response.request.body)
            output_str += "\n" + str(self.response.text)
            self.__logger.error(f"HTTP Request has failed with status code {self.response.status_code}. \n {output_str}")
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
