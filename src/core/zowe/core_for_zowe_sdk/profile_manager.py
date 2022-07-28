"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import base64
import os.path
import re
import warnings
from typing import Union
import sys

import jsonc

from .constants import constants
from .exceptions import ProfileNotFound, SecureProfileLoadFailed

HAS_KEYRING = True
try:
    import keyring
except ImportError:
    HAS_KEYRING = False


class ProfileManager:
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

    def __init__(self, appname: str = "zowe"):
        self._appname = appname
        self._config_dir = None
        self._config_filename = f"{self._appname}.config.json"
        self._config_filepath = None

    @property
    def config_appname(self) -> str:
        """Returns the app name"""
        return self._appname

    @property
    def config_dir(self) -> Union[str, None]:
        """Returns the folder path to where the Zowe z/OSMF Team Profile Config files are located."""
        return self._config_dir

    @config_dir.setter
    def config_dir(self, dirname: str) -> None:
        """Set directory/folder path to where Zowe z/OSMF Team Profile Config files are located"""
        if os.path.isdir(dirname):
            self._config_dir = dirname
        else:
            raise FileNotFoundError(f"given path {dirname} is not valid")

    @property
    def config_filename(self) -> str:
        """Return the filename for Zowe z/OSMF Team Profile Config"""
        return self._config_filename

    @property
    def config_filepath(self) -> Union[str, None]:
        """Get the full Zowe z/OSMF Team Config filepath"""
        return self._config_filepath

    def autodiscover_config_dir(self) -> None:
        """Autodiscover Zowe z/OSMF Team Profile Config files by going up the path from
        current working directory"""

        current_dir = os.getcwd()

        while self._config_dir is None:
            path = os.path.join(current_dir, self._config_filename)

            if os.path.isfile(path):
                self._config_dir = current_dir

            # check if have arrived at the root directory
            if current_dir == os.path.dirname(current_dir):
                break

            current_dir = os.path.dirname(current_dir)

        if self._config_dir is None:
            raise FileNotFoundError(f"No config file found on path {current_dir}")

    def get_profilename_from_profiletype(
        self, profile_jsonc: dict, profile_type: str
    ) -> str:
        """
        Return exact profilename of the profile to load from the mentioned type

        First tries to look into the defaults, if not found,
        then it tries to iterate through the profiles
        """
        try:
            # try to get the profilename from defaults
            try:
                profilename = profile_jsonc["defaults"][profile_type]
            except KeyError:
                warnings.warn("Given profile type has no default profilename")
            else:
                return profilename

            # iterate through the profile and check if profile is found
            for (key, value) in profile_jsonc["profiles"].items():
                try:
                    temp_profile_type = value["type"]
                    if profile_type == temp_profile_type:
                        return key
                except KeyError:
                    warnings.warn(f"Profile {key} has no type attribute")

            # if no profile with matching type found, we raise an exception
            raise ProfileNotFound(
                profile_name=profile_type,
                error_msg=f"No profile with matching profile_type {profile_type} found",
            )
        except ProfileNotFound as exc:
            raise exc

    def load_profile_properties(self, profile_jsonc: dict, profile_name: str) -> dict:
        """
        Load exact profile properties (without prepopulated fields from base profile)
        from the profile dict and populate fields from the secure credentials storage
        """
        try:
            props = profile_jsonc["profiles"][profile_name]["properties"]
        except KeyError as exc:
            raise ProfileNotFound(
                profile_name=profile_name, error_msg=str(exc)
            ) from exc

        secure_props = self.load_credentials()

        # load properties with key as profile.{profile_name}.properties.{*}
        for (key, value) in secure_props.items():
            if re.match("profiles\\." + profile_name + "\\.properties\\.[a-z]+", key):
                property_name = key.split(".")[3]
                props[property_name] = value

        return props

    def load_base_profile_properties(self, profile_jsonc: dict) -> dict:
        """
        Load base profile
        """
        base_props: dict = {}

        try:
            base_profile_name = self.get_profilename_from_profiletype(
                profile_jsonc=profile_jsonc, profile_type="base"
            )
            base_props = profile_jsonc["profiles"][base_profile_name].get(
                "properties", {}
            )
        except KeyError as exc:
            raise ProfileNotFound(
                profile_name=base_profile_name, error_msg=str(exc)
            ) from exc

        secure_props = self.load_credentials()

        # load properties with key as profile.{profile_name}.properties.{*}
        for (key, value) in secure_props.items():
            if re.match(
                "profiles\\." + base_profile_name + "\\.properties\\.[a-z]+", key
            ):
                property_name = key.split(".")[3]
                base_props[property_name] = value

        return base_props

    def load(
        self,
        profile_name: Union[str, None] = None,
        profile_type: Union[str, None] = None,
        profile_args: Union[dict, None] = None,
    ) -> dict:
        """Load z/OSMF connection details from a z/OSMF profile.

        Returns
        -------
        zosmf_connection
            z/OSMF connection object

        We will be loading properties from a bottom up fashion,
        the bottom being the base/default profile properties
        and the up being the explicitly mentioned Profile.

        Loading Order :
            Base Profile Properties
        Overriding Order:
            Service Profile (profile explicitly mentioned) properties
            Profile args
        """

        # load config file
        if self._config_dir is None:
            self.autodiscover_config_dir()

        self._config_filepath = os.path.join(self._config_dir, self._config_filename)

        with open(self._config_filepath, encoding="UTF-8", mode="r") as fileobj:
            profile_jsonc = jsonc.load(fileobj)

        # load profile
        if profile_type is None and profile_name is None:
            raise ValueError(
                "Both profile_type and profile_name cannot be empty at the same time."
            )

        service_profile = {}

        # load base profile
        base_profile: dict = self.load_base_profile_properties(
            profile_jsonc=profile_jsonc
        )
        service_profile.update(base_profile)

        # load given profile
        if profile_name is None:
            profile_name = self.get_profilename_from_profiletype(
                profile_jsonc=profile_jsonc, profile_type=profile_type
            )

        required_profile: dict = self.load_profile_properties(
            profile_jsonc=profile_jsonc, profile_name=profile_name
        )
        service_profile.update(required_profile)

        # apply profile args
        if profile_args:
            service_profile.update(profile_args)

        return service_profile

    def load_credentials(self) -> dict:
        """
        return credentials stored for the given config
        """
        credentials: dict = {}

        try:
            service_name = constants["ZoweServiceName"]

            if sys.platform == "win32":
                service_name += "/" + constants["ZoweAccountName"]

            secure_config = keyring.get_password(
                service_name, constants["ZoweAccountName"]
            )

        except Exception as exc:
            raise SecureProfileLoadFailed(
                constants["ZoweServiceName"], error_msg=str(exc)
            ) from exc

        secure_config_json = jsonc.loads(base64.b64decode(secure_config).decode())

        # first look for credentials stored for currently loaded config
        # then look for default credential stored for user_directory/.zowe/zowe.config.json
        try:
            credentials = secure_config_json[self._config_filepath]
        except KeyError:
            try:
                home = os.path.expanduser("~")
                global_config_path = os.path.join(home, ".zowe", "zowe.config.json")
                credentials = secure_config_json[global_config_path]
            except KeyError as exc:
                raise Exception(
                    "No credentials found for loaded config file as well as for global config"
                ) from exc
            else:
                warnings.warn(
                    f"Credentials not found for given config, using global credentials {global_config_path}"
                )

        return credentials
