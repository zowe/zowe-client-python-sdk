"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""


class InvalidRequestMethod(Exception):
    """
    Class used to represent an invalid request method exception.

    Parameters
    ----------
    input_method: str
        The invalid HTTP method used
    """

    def __init__(self, input_method: str):
        super().__init__("Invalid HTTP method input {}".format(input_method))


class UnexpectedStatus(Exception):
    """
    Class used to represent an unexpected request response status exception.

    Parameters
    ----------
    expected: list[int]
        The list of expected status code
    received: int
        The received status code
    request_output: str
        The output from the request
    """

    def __init__(self, expected: list[int], received: int, request_output: str):
        super().__init__(
            "The status code from z/OSMF was: {}\nExpected: {}\nRequest output: {}".format(
                received, expected, request_output
            )
        )


class RequestFailed(Exception):
    """
    Class used to represent a request failure exception.

    Parameters
    ----------
    status_code: int
        The status code from the failed request
    request_output: str
        The output from the request
    """

    def __init__(self, status_code: int, request_output: str):
        super().__init__("HTTP Request has failed with status code {}. \n {}".format(status_code, request_output))


class FileNotFound(Exception):
    """
    Class used to represent a file not found exception.

    Parameters
    ----------
    input_path: str
        The invalid input path
    """

    def __init__(self, input_path: str):
        super().__init__("The path {} provided is not a file.".format(input_path))


class MissingConnectionArgs(Exception):
    """Class used to represent a missing connection argument exception."""

    def __init__(self) -> None:
        super().__init__(
            "You must provide host, user, and password for a z/OSMF "
            "connection, or the name of a z/OSMF profile that exists on your "
            "system."
        )


class SecureProfileLoadFailed(Exception):
    """
    Class used to represent a secure profile load failure exception.

    Parameters
    ----------
    profile_name: str
        The name of the profile it failed to load
    error_msg: str
        The error message received while trying to load the profile
    """

    def __init__(self, profile_name: str = "unknown", error_msg: str = "error"):
        super().__init__("Failed to load secure profile '{}' because '{}'".format(profile_name, error_msg))


class ProfileNotFound(Exception):
    """
    Class used to represent a profile load failure exception.

    Parameters
    ----------
    profile_name: str
        The name of the profile it failed to load
    error_msg: str
        The error message received while trying to load the profile
    """

    def __init__(self, profile_name: str = "unknown", error_msg: str = "error"):
        super().__init__("Failed to load profile '{}' because '{}'".format(profile_name, error_msg))


class SecureValuesNotFound(Exception):
    """
    Class used to represent a profile load failure exception.

    Parameters
    ----------
    values: set[str]
        The list of secure values not found
    """

    def __init__(self, values: set[str]):
        super().__init__("Failed to load secure values: {}".format(str(values)))


class UnsupportedAuthType(Exception):
    """
    Class used to represent an unsupported authentication type exception.

    Parameters
    ----------
    auth_type: str
        The type of authentication on the session
    """

    def __init__(self, auth_type: str):
        super().__init__("Unsupported authentication type: {}".format(auth_type))
