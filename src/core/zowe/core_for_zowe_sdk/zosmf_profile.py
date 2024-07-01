"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import base64
import os.path

import yaml

from .connection import ApiConnection
from .constants import constants
from .exceptions import SecureProfileLoadFailed
from .logger import Log

HAS_KEYRING = True
try:
    from zowe.secrets_for_zowe_sdk import keyring
except ImportError:
    HAS_KEYRING = False


class ZosmfProfile:
    """
    Class used to represent a Zowe z/OSMF profile.

    Description
    -----------
    This class is only used when there is already a Zowe z/OSMF profile created
    and the user opted to use the profile instead of passing the credentials directly
    in the object constructor.

    Attributes
    ----------
    profile_name: str
        Zowe z/OSMF profile name
    """

    def __init__(self, profile_name):
        """
        Construct a ZosmfProfile object.

        Parameters
        ----------
        profile_name
            The name of the Zowe z/OSMF profile
        """
        self.__profile_name = profile_name
        self.__logger = Log.registerLogger(__name__)

    @property
    def profiles_dir(self):
        """Return the os path for the Zowe z/OSMF profiles."""
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".zowe", "profiles", "zosmf")

    def load(self):
        """Load z/OSMF connection details from a z/OSMF profile.

        Returns
        -------
        zosmf_connection
            z/OSMF connection object
        """
        profile_file = os.path.join(self.profiles_dir, "{}.yaml".format(self.__profile_name))

        with open(profile_file, "r") as fileobj:
            profile_yaml = yaml.safe_load(fileobj)

        zosmf_host = profile_yaml["host"]
        if "port" in profile_yaml:
            zosmf_host += ":{}".format(profile_yaml["port"])

        zosmf_user = profile_yaml["user"]
        zosmf_password = profile_yaml["password"]
        if zosmf_user.startswith(constants["SecureValuePrefix"]) and zosmf_password.startswith(
            constants["SecureValuePrefix"]
        ):
            zosmf_user, zosmf_password = self.__load_secure_credentials()

        zosmf_ssl_verification = True
        if "rejectUnauthorized" in profile_yaml:
            zosmf_ssl_verification = profile_yaml["rejectUnauthorized"]

        return ApiConnection(zosmf_host, zosmf_user, zosmf_password, zosmf_ssl_verification)

    def __get_secure_value(self, name):
        service_name = constants["ZoweCredentialKey"]
        account_name = "zosmf_{}_{}".format(self.__profile_name, name)

        secret_value = keyring.get_password(service_name, account_name)

        # Handle the case when secret_value is None
        if secret_value is None:
            secret_value = ""

        secret_value = base64.b64decode(secret_value).decode().strip('"')

        return secret_value

    def __load_secure_credentials(self):
        """Load secure credentials for a z/OSMF profile."""
        if not HAS_KEYRING:
            self.__logger.error(f"{self.__profile_name} keyring module not installed")
            raise SecureProfileLoadFailed(self.__profile_name, "Keyring module not installed")

        try:
            zosmf_user = self.__get_secure_value("user")
            zosmf_password = self.__get_secure_value("password")
        except Exception as e:
            self.__logger.error(f"Failed to load secure profile '{self.__profile_name}' because '{e}'")
            raise SecureProfileLoadFailed(self.__profile_name, e)
        else:
            return (zosmf_user, zosmf_password)
