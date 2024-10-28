"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""


class ProfileNotFoundWarning(Warning):
    """
    A warning that is raised when a user profile cannot be found.

    Parameters
    ----------
    message : str
        A string describing the warning.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """Return a string representation of the warning message.

        Returns
        -------
        str
            a string representation of the warning message
        """
        return repr(self.message)


class ProfileParsingWarning(Warning):
    """
    A warning that is raised when there is an error while parsing a user profile.

    Parameters
    ----------
    message : str
        A human-readable string describing the warning.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """Return a string representation of the warning message.

        Returns
        -------
        str
            a string representation of the warning message
        """
        return repr(self.message)


class ConfigNotFoundWarning(Warning):
    """
    A warning that is raised when a configuration file is not found.

    Parameters
    ----------
    message : str
        A human-readable string describing the warning.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """Return a string representation of the warning message.

        Returns
        -------
        str
            a string representation of the warning message
        """
        return repr(self.message)


class SecurePropsNotFoundWarning(Warning):
    """
    A warning that is raised when secure properties are not found.

    Parameters
    ----------
    message : str
        A human-readable string describing the warning.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """Return a string representation of the warning message.

        Returns
        -------
        str
            a string representation of the warning message
        """
        return repr(self.message)
