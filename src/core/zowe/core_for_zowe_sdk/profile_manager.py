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
from typing import Union

import jsonc

from .constants import constants
from .exceptions import ProfileNotFound, SecureProfileLoadFailed, SecureValuesNotFound
from .profile_constants import GLOBAL_CONFIG_NAME, TEAM_CONFIG, USER_CONFIG

HAS_KEYRING = True
try:
    import keyring
except ImportError:
    HAS_KEYRING = False

HOME = os.path.expanduser("~")
GLOBAL_CONFIG_PATH = os.path.join(HOME, ".zowe", f"{GLOBAL_CONFIG_NAME}.config.json")
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
    location: Union[str, None] = None
    profiles: Union[dict, None] = None
    defaults: Union[dict, None] = None
    secure_props: Union[dict, None] = None

    @property
    def filename(self) -> str:
        if self.type == TEAM_CONFIG:
            return f"{self.name}.config.json"

        if self.type == USER_CONFIG:
            return f"{self.name}.config.user.json"

        return self.name

    @property
    def filepath(self) -> Union[str, None]:
        if not self.location:
            return None

        print(self.filename, self.location)
        return os.path.join(self.location, self.filename)

    def init_from_file(self) -> dict:
        if self.filepath is None:
            self.autodiscover_config_dir()

        if self.filepath is None:
            raise FileNotFoundError(f"Could not find the file {self.filename}")

        with open(self.filepath, encoding="UTF-8", mode="r") as fileobj:
            profile_jsonc = jsonc.load(fileobj)

        print(profile_jsonc)
        self.profiles = profile_jsonc["profiles"]
        self.defaults = profile_jsonc["defaults"]

        self.load_secure_props()

    def get_profile(
        self, profile_name: Union[str, None], profile_type: Union[str, None]
    ):
        if self.profiles is None:
            self.init_from_file()

        if profile_name is None and profile_type is None:
            raise ProfileNotFound(
                "Could not find profile as both profile_name and profile_type is not set."
            )

        if profile_name is None:
            profile_name = self.get_profilename_from_profiletype(
                profile_type=profile_type
            )

        props: dict = self.load_profile_properties(profile_name=profile_name)

        try:
            base_profile = self.get_profilename_from_profiletype(profile_type="base")
        except ProfileNotFound:
            if self.type == TEAM_CONFIG:
                warnings.warn(f"Base profile not found in {self.filepath}")
        else:
            base_props = self.load_profile_properties(profile_name=base_profile)
            props.update(base_props)

        return props

    def autodiscover_config_dir(self):
        """
        Autodiscover Zowe z/OSMF Team Config files by going up the path from
        current working directory

        Return path if it finds the config directory,
        Else, it returns None
        """

        current_dir = CURRENT_DIR
        config_dir = None

        while config_dir is None:
            path = os.path.join(current_dir, self.filename)

            if os.path.isfile(path):
                config_dir = current_dir

            # check if have arrived at the root directory
            if current_dir == os.path.dirname(current_dir):
                break

            current_dir = os.path.dirname(current_dir)

        self.location = config_dir

    def get_profilename_from_profiletype(self, profile_type: str) -> str:
        """
        Return exact profilename of the profile to load from the mentioned type

        First tries to look into the defaults, if not found,
        then it tries to iterate through the profiles
        """
        try:
            # try to get the profilename from defaults
            try:
                profilename = self.defaults[profile_type]
            except KeyError:
                warnings.warn("Given profile type has no default profilename")
            else:
                return profilename

            # iterate through the profiles and check if profile is found
            for (key, value) in self.profiles.items():
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

    def load_profile_properties(self, profile_name: str) -> dict:
        """
        Load exact profile properties (without prepopulated fields from base profile)
        from the profile dict and populate fields from the secure credentials storage
        """
        try:
            props = self.profiles[profile_name]["properties"]
        except Exception as exc:
            return {}

        secure_fields: list = self.profiles[profile_name].get("secure", [])

        # load properties with key as profile.{profile_name}.properties.{*}
        for (key, value) in self.secure_props.items():
            if re.match("profiles\\." + profile_name + "\\.properties\\.[a-z]+", key):
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

        secure_config_json = jsonc.loads(base64.b64decode(secure_config).decode())

        # first look for credentials stored for currently loaded config
        # then look for default credential stored for user_directory/.zowe/zowe.config.json
        try:
            self.secure_props = secure_config_json[self.location]
        except KeyError:
            try:
                self.secure_props = secure_config_json[GLOBAL_CONFIG_PATH]
            except KeyError as exc:
                raise warnings.warn(
                    f"No credentials found for loaded {self.filename} file as well as for global config"
                ) from exc
            else:
                warnings.warn(
                    f"Credentials not found for given config, using global credentials {GLOBAL_CONFIG_PATH}"
                )


class ProfileManager:
    def __init__(self, appname: str = "zowe"):
        print(CURRENT_DIR)
        self._appname = appname

        self.project_config = ConfigFile(type=TEAM_CONFIG, name=appname)
        self.project_user_config = ConfigFile(type=USER_CONFIG, name=appname)

        self.global_config = ConfigFile(type=TEAM_CONFIG, name=GLOBAL_CONFIG_NAME)
        self.global_user_config = ConfigFile(type=USER_CONFIG, name=GLOBAL_CONFIG_NAME)

    @property
    def config_appname(self) -> str:
        """Returns the app name"""
        return self._appname

    @property
    def config_dir(self) -> Union[str, None]:
        """Returns the folder path to where the Zowe z/OSMF Team Project Config files are located."""
        return self.project_config.directory

    @config_dir.setter
    def config_dir(self, dirname: str) -> None:
        """
        Set directory/folder path to where Zowe z/OSMF Team Project Config files are located
        """
        if os.path.isdir(dirname):
            self.project_config.location = dirname
        else:
            raise FileNotFoundError(f"given path {dirname} is not valid")

    @property
    def user_config_dir(self) -> Union[str, None]:
        """Returns the folder path to where the Zowe z/OSMF User Project Config files are located."""
        return self.project_user_config.location

    @user_config_dir.setter
    def user_config_dir(self, dirname: str) -> None:
        """Set directory/folder path to where Zowe z/OSMF User Project Config files are located"""
        if os.path.isdir(dirname):
            self.project_user_config.location = dirname
        else:
            raise FileNotFoundError(f"given path {dirname} is not valid")

    @property
    def config_filename(self) -> str:
        """Return the filename for Zowe z/OSMF Team Project Config"""
        return self.project_config.filename

    @property
    def config_filepath(self) -> Union[str, None]:
        """Get the full Zowe z/OSMF Team Project Config filepath"""
        return self.project_config.filepath

    def load(
        self,
        profile_name: Union[str, None] = None,
        profile_type: Union[str, None] = None,
    ) -> dict:
        if profile_name is None and profile_type is None:
            raise ProfileNotFound(
                "Could not find profile as both profile_name and profile_type is not set."
            )

        service_profile: dict = {}

        project_profile: dict = self.project_config.get_profile(
            profile_name=profile_name, profile_type=profile_type
        )
        project_user_profile: dict = self.project_user_config.get_profile(
            profile_name=profile_name, profile_type=profile_type
        )

        self.global_config.init_from_file()
        if profile_name:
            global_base_profile: dict = self.global_config.load_profile_properties(
                profile_name=profile_name
            )
        else:
            try:
                gb_profile_name = self.global_config.get_profilename_from_profiletype(
                    profile_type=profile_type
                )
                global_base_profile: dict = self.global_config.load_profile_properties(
                    profile_name=gb_profile_name
                )
                service_profile.update(global_base_profile)
            except Exception:
                warnings.warn("Could not find global base profile")

        self.global_user_config.init_from_file()
        if profile_name:
            global_user_profile: dict = self.global_config.load_profile_properties(
                profile_name=profile_name
            )
        else:
            try:
                gu_profile_name = self.global_config.get_profilename_from_profiletype(
                    profile_type=profile_type
                )
                global_user_profile: dict = self.global_config.load_profile_properties(
                    profile_name=gu_profile_name
                )
                service_profile.update(global_user_profile)
            except Exception:
                warnings.warn("Could not find global user profile")

        service_profile.update(project_profile)
        service_profile.update(project_user_profile)

        return service_profile
