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
import sys
import warnings
from dataclasses import dataclass
from typing import Tuple, Optional

import commentjson

from .constants import constants
from .custom_warnings import (
    ProfileNotFoundWarning,
    ProfileParsingWarning,
    SecurePropsNotFoundWarning,
)
from .exceptions import ProfileNotFound, SecureProfileLoadFailed, SecureValuesNotFound
from .profile_constants import (
    BASE_PROFILE,
    GLOBAL_CONFIG_NAME,
    TEAM_CONFIG,
    USER_CONFIG,
)

HAS_KEYRING = True
try:
    import keyring
except ImportError:
    HAS_KEYRING = False

HOME = os.path.expanduser("~")
GLOBAl_CONFIG_LOCATION = os.path.join(HOME, ".zowe")
GLOBAL_CONFIG_PATH = os.path.join(
    GLOBAl_CONFIG_LOCATION, f"{GLOBAL_CONFIG_NAME}.config.json"
)
CURRENT_DIR = os.getcwd()


@dataclass
class ConfigFile:
    """
    Class used to represent a single config file.

    Mainly it will have the following details :
    1. Type ("User Config" or "Team Config")
        User Configs override Team Configs.
        User Configs are used to have personalised config details
        that the user don't want to have in the Team Config.
    2. Directory in which the file is located.
    3. Name (excluding .config.json or .config.user.json)
    4. Contents of the file.
    4.1 Profiles
    4.2 Defaults
    5. Secure Properties associated with the file.
    """

    type: str
    name: str
    _location: Optional[str] = None
    profiles: Optional[dict] = None
    defaults: Optional[dict] = None
    secure_props: Optional[dict] = None

    @property
    def filename(self) -> str:
        if self.type == TEAM_CONFIG:
            return f"{self.name}.config.json"

        if self.type == USER_CONFIG:
            return f"{self.name}.config.user.json"

        return self.name

    @property
    def filepath(self) -> Optional[str]:
        if not self.location:
            return None

        return os.path.join(self.location, self.filename)

    @property
    def location(self) -> Optional[str]:
        return self._location

    @location.setter
    def location(self, dirname: str) -> None:
        if os.path.isdir(dirname):
            self._location = dirname
        else:
            raise FileNotFoundError(f"given path {dirname} is not valid")

    def init_from_file(self) -> None:
        """
        Initializes the class variable after
        setting filepath (or if not set, autodiscover the file)
        """
        if self.filepath is None:
            self.autodiscover_config_dir()

        with open(self.filepath, encoding="UTF-8", mode="r") as fileobj:
            profile_jsonc = commentjson.load(fileobj)

        self.profiles = profile_jsonc.get("profiles", {})
        self.defaults = profile_jsonc.get("defaults", {})

        # loading secure props is done in load_profile_properties
        # since we want to try loading secure properties only when
        # we know that the profile has saved properties
        # self.load_secure_props()

    def get_profile(
        self,
        profile_name: Optional[str] = None,
        profile_type: Optional[str] = None,
    ) -> Tuple[dict, str]:
        """
        Load given profile with values populated from base profile
        """
        if self.profiles is None:
            self.init_from_file()

        if profile_name is None and profile_type is None:
            raise ProfileNotFound(
                profile_name=profile_name,
                error_msg="Could not find profile as both profile_name and profile_type is not set.",
            )

        if profile_name is None:
            profile_name = self.get_profilename_from_profiletype(
                profile_type=profile_type
            )

        props: dict = self.load_profile_properties(profile_name=profile_name)

        try:
            base_profile = self.get_profilename_from_profiletype(
                profile_type=BASE_PROFILE
            )
        except ProfileNotFound:
            if self.type == TEAM_CONFIG:
                warnings.warn(
                    f"Base profile not found in {self.filepath}",
                    ProfileNotFoundWarning,
                )
        else:
            base_props = self.load_profile_properties(profile_name=base_profile)
            props.update(base_props)

        return props, profile_name

    def autodiscover_config_dir(self):
        """
        Autodiscover Zowe z/OSMF Team Config files by going up the path from
        current working directory

        Return path if it finds the config directory,
        Else, it returns None
        """

        current_dir = CURRENT_DIR

        while True:
            path = os.path.join(current_dir, self.filename)

            if os.path.isfile(path):
                self.location = current_dir
                return

            # check if have arrived at the root directory
            if current_dir == os.path.dirname(current_dir):
                break

            current_dir = os.path.dirname(current_dir)

        raise FileNotFoundError(f"Could not find the file {self.filename}")

    def get_profilename_from_profiletype(self, profile_type: str) -> str:
        """
        Return exact profilename of the profile to load from the mentioned type

        First tries to look into the defaults, if not found,
        then it tries to iterate through the profiles
        """
        # try to get the profilename from defaults
        try:
            profilename = self.defaults[profile_type]
        except KeyError:
            warnings.warn(
                f"Given profile type '{profile_type}' has no default profilename",
                ProfileParsingWarning,
            )
        else:
            return profilename

        # iterate through the profiles and check if profile is found
        for (key, value) in self.profiles.items():
            try:
                temp_profile_type = value["type"]
                if profile_type == temp_profile_type:
                    return key
            except KeyError:
                warnings.warn(
                    f"Profile '{key}' has no type attribute",
                    ProfileParsingWarning,
                )

        # if no profile with matching type found, we raise an exception
        raise ProfileNotFound(
            profile_name=profile_type,
            error_msg=f"No profile with matching profile_type '{profile_type}' found",
        )

    def load_profile_properties(self, profile_name: str) -> dict:
        """
        Load exact profile properties (without prepopulated fields from base profile)
        from the profile dict and populate fields from the secure credentials storage
        """
        try:
            props = self.profiles[profile_name]["properties"]
        except Exception as exc:
            raise ProfileNotFound("Profile {profile_name} not found", error_msg=exc) from exc

        secure_fields: list = self.profiles[profile_name].get("secure", [])

        # load secure props only if there are secure fields
        if secure_fields:
            self.load_secure_props()

            # load properties with key as profile.{profile_name}.properties.{*}
            for (key, value) in self.secure_props.items():
                if re.match(
                    "profiles\\." + profile_name + "\\.properties\\.[a-z]+", key
                ):
                    property_name = key.split(".")[3]
                    if property_name in secure_fields:
                        props[property_name] = value
                        secure_fields.remove(property_name)

            if len(secure_fields) > 0:
                raise SecureValuesNotFound(secure_fields)

        return props

    def load_secure_props(self) -> None:
        """
        load secure_props stored for the given config

        if keyring is not initialized, set empty value
        """
        if not HAS_KEYRING:
            self.secure_props = {}
            return

        try:
            service_name = constants["ZoweServiceName"]

            if sys.platform == "win32":
                service_name += "/" + constants["ZoweAccountName"]

            secret_value = keyring.get_password(
                service_name, constants["ZoweAccountName"]
            )

        except Exception as exc:
            raise SecureProfileLoadFailed(
                constants["ZoweServiceName"], error_msg=str(exc)
            ) from exc

        secure_config: str
        if sys.platform == "win32":
            secure_config = secret_value.encode("utf-16")
        else:
            secure_config = secret_value

        secure_config_json = commentjson.loads(base64.b64decode(secure_config).decode())

        # first look for credentials stored for currently loaded config
        # then look for default credential stored for user_directory/.zowe/zowe.config.json
        try:
            self.secure_props = secure_config_json[self.location]
        except KeyError:
            try:
                self.secure_props = secure_config_json[GLOBAL_CONFIG_PATH]
            except KeyError as exc:
                raise SecureProfileLoadFailed(
                    constants["ZoweServiceName"],
                    error_msg="No credentials found for loaded config file as well as for global config",
                ) from exc
            else:
                warnings.warn(
                    f"Credentials not found for given config, using global credentials {GLOBAL_CONFIG_PATH}",
                    SecurePropsNotFoundWarning,
                )
