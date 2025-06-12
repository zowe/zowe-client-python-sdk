"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Union, Any
from requests import Response

import requests
import urllib3

from .exceptions import InvalidRequestMethod, RequestFailed, UnexpectedStatus
from .logger import Log


class RequestHandler:
    """
    Class used to handle HTTP/HTTPS requests.

    Parameters
    ----------
    session_arguments: dict[str, Any]
        Zowe SDK session arguments
    logger_name: str
        The logger name of the modules calling request handler
    """

    def __init__(self, session_arguments: dict[str, Any], logger_name: str = __name__):
        self.session = requests.Session()
        self.session_arguments = session_arguments
        self.__valid_methods = ["GET", "POST", "PUT", "DELETE"]
        self.__handle_ssl_warnings()
        self.__logger = Log.register_logger(logger_name)

    def __handle_ssl_warnings(self) -> None:
        """Turn off warnings if the SSL verification argument if off."""
        if not self.session_arguments["verify"]:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def perform_request(
        self, method: str, request_arguments: dict[str, Any], expected_code: list[int] = [200], stream: bool = False
    ) -> Union[str, bytes, Response, dict[str, Any], None]:
        """Execute an HTTP/HTTPS requests from given arguments and return validated response (JSON).

        Parameters
        ----------
        method: str
            The request method that should be used
        request_arguments: dict[str, Any]
            The dictionary containing the required arguments for the execution of the request
        expected_code: list[int]
            The list containing the acceptable response codes (default is [200])
        stream: bool
            The boolean value whether the request is stream

        Returns
        -------
        Union[str, bytes, Response, dict[str, Any], None]
            normalized request response in json (dictionary)
        """
        self.__method = method
        self.__request_arguments = request_arguments
        self.__expected_code = expected_code
        self.__logger.debug(
            f"Request method: {self.__method}, Request arguments: {self.__request_arguments}, Expected code: {expected_code}"
        )
        self.__validate_method()
        self.__send_request(stream=stream)
        self.__validate_response()
        if stream:
            return self.__response
        else:
            return self.__normalize_response()

    def __validate_method(self) -> None:
        """Check if the input request method for the request is supported.

        Raises
        ------
        InvalidRequestMethod
            If the input request method is not supported
        """
        if self.__method not in self.__valid_methods:
            self.__logger.error(f"Invalid HTTP method input {self.__method}")
            raise InvalidRequestMethod(self.__method)

    def __send_request(self, stream: bool = False) -> None:
        """
        Build a custom session object, prepare it with a custom request and send it.

        Parameters
        ----------
        stream : bool
            Flag indicates whether it is a streaming requests.
        """
        self.__response = self.session.request(
            method=self.__method, stream=stream, **self.session_arguments, **self.__request_arguments
        )

    def __del__(self) -> None:
        """Clean up the REST session object once it is no longer needed anymore."""
        self.session.close()

    def __validate_response(self) -> None:
        """Validate if request response is acceptable based on expected code list.

        Raises
        ------
        UnexpectedStatus
            If the response status code is not in the expected code list
        RequestFailed
            If the HTTP/HTTPS request fails
        """
        # Automatically checks if status code is between 200 and 400
        if self.__response.ok:
            if self.__response.status_code not in self.__expected_code:
                self.__logger.error(
                    f"The status code from z/OSMF was: {self.__expected_code}\n"
                    f"Expected: {self.__response.status_code}\n"
                    f"Request output: {self.__response.text}"
                )
                raise UnexpectedStatus(self.__expected_code, self.__response.status_code, self.__response.text)
        else:
            output_str = str(self.__response.request.url)
            output_str += "\n" + str(self.__response.request.headers)
            output_str += "\n" + str(self.__response.request.body)
            output_str += "\n" + str(self.__response.text)
            self.__logger.error(
                f"HTTP Request has failed with status code {self.__response.status_code}. \n {output_str}"
            )
            raise RequestFailed(self.__response.status_code, output_str)

    def __normalize_response(self) -> Union[str, bytes, dict[str, Any], None]:
        """
        Normalize the response object to a JSON format.

        Returns
        -------
        Union[str, bytes, dict[str, Any], None]
            Response object at the format based on Content-Type header:
            - `bytes` when the response is binary data
            - `str` when the response is plain text
            - `dict[str, Any]` when the response is json
            - `None` when the response has empty text
        """
        content_type = self.__response.headers.get("Content-Type")
        if content_type == "application/octet-stream":
            return self.__response.content
        elif content_type and content_type.startswith("application/json"):
            return None if self.__response.text == "" else self.__response.json()
        else:
            return self.__response.text
