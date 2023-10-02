"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""


class InvalidRequestMethod(Exception):
    """Class used to represent an invalid request method exception."""

    def __init__(self, input_method):
        """
        Parameters
        ----------
        input_method: str
            The invalid HTTP method used
        """
        super().__init__("Invalid HTTP method input {}".format(input_method))


class UnexpectedStatus(Exception):
    """Class used to represent an unexpected request response status exception."""

    def __init__(self, expected, received, request_output):
        """
        Parameters
        ----------
        expected
            The expected status code
        received
            The received status code
        request_output
            The output from the request
        """
        super().__init__(
            "The status code from z/OSMF was: {}\nExpected: {}\nRequest output: {}".format(
                received, expected, request_output
            )
        )


class RequestFailed(Exception):
    """Class used to represent a request failure exception."""

    def __init__(self, status_code, request_output):
        """
        Parameters
        ----------
        status_code
            The status code from the failed request
        request_output
            The output from the request
        """
        super().__init__("HTTP Request has failed with status code {}. \n {}".format(status_code, request_output))


class FileNotFound(Exception):
    """Class used to represent a file not found exception."""

    def __init__(self, input_path):
        """
        Parameters
        ----------
        input_path
            The invalid input path
        """
        super().__init__("The path {} provided is not a file.".format(input_path))


class MissingConnectionArgs(Exception):
    """Class used to represent a missing connection argument exception."""

    def __init__(self):
        super().__init__(
            "You must provide host, user, and password for a z/OSMF "
            "connection, or the name of a z/OSMF profile that exists on your "
            "system."
        )


class SecureProfileLoadFailed(Exception):
    """Class used to represent a secure profile load failure exception."""

    def __init__(self, profile_name: str = "unknown", error_msg: str = "error"):
        """
        Parameters
        ----------
        profile_name
            The name of the profile it failed to load
        error_msg
            The error message received while trying to load the profile
        """
        super().__init__("Failed to load secure profile '{}' because '{}'".format(profile_name, error_msg))


class ProfileNotFound(Exception):
    """Class used to represent a profile load failure exception."""

    def __init__(self, profile_name: str = "unknown", error_msg: str = "error"):
        """
        Parameters
        ----------
        profile_name
            The name of the profile it failed to load
        error_msg
            The error message received while trying to load the profile
        """

        super().__init__("Failed to load profile '{}' because '{}'".format(profile_name, error_msg))


class SecureValuesNotFound(Exception):
    """Class used to represent a profile load failure exception."""

    def __init__(self, values: set):
        """
        Parameters
        ----------
        values
            The list of secure values not found
        """
        super().__init__("Failed to load secure values: {}".format(str(values)))


class UnsupportedAuthType(Exception):
    """Class used to represent an unsupported authentication type exception."""

    def __init__(self, auth_type: str):
        """
        Parameters
        ----------
        auth_type
            The type of authentication on the session
        """
        super().__init__("Unsupported authentication type: {}".format(auth_type))
