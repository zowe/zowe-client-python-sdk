"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os.path
import warnings
from typing import Union


from .config_file import ConfigFile
from .custom_warnings import ConfigNotFoundWarning, SecurePropsNotFoundWarning
from .exceptions import ProfileNotFound, SecureProfileLoadFailed, SecureValuesNotFound
from .profile_constants import GLOBAL_CONFIG_NAME, TEAM_CONFIG, USER_CONFIG

HAS_KEYRING = True


HOME = os.path.expanduser("~")
GLOBAl_CONFIG_LOCATION = os.path.join(HOME, ".zowe")
GLOBAL_CONFIG_PATH = os.path.join(
    GLOBAl_CONFIG_LOCATION, f"{GLOBAL_CONFIG_NAME}.config.json"
)
CURRENT_DIR = os.getcwd()


class ProfileManager:
    def __init__(self, appname: str = "zowe"):
        self._appname = appname

        self.project_config = ConfigFile(type=TEAM_CONFIG, name=appname)
        self.project_user_config = ConfigFile(type=USER_CONFIG, name=appname)

        self.global_config = ConfigFile(type=TEAM_CONFIG, name=GLOBAL_CONFIG_NAME)
        try:
            self.global_config.location = GLOBAl_CONFIG_LOCATION
        except Exception:
            warnings.warn(
                "Could not find Global Config Directory, please provide one.",
                ConfigNotFoundWarning,
            )

        self.global_user_config = ConfigFile(type=USER_CONFIG, name=GLOBAL_CONFIG_NAME)
        try:
            self.global_user_config.location = GLOBAl_CONFIG_LOCATION
        except Exception:
            warnings.warn(
                "Could not find Global User Config Directory, please provide one.",
                ConfigNotFoundWarning,
            )

    @property
    def config_appname(self) -> str:
        """Returns the app name"""
        return self._appname

    @property
    def config_dir(self) -> Union[str, None]:
        """Returns the folder path to where the Zowe z/OSMF Team Project Config files are located."""
        return self.project_config.location

    @config_dir.setter
    def config_dir(self, dirname: str) -> None:
        """
        Set directory/folder path to where Zowe z/OSMF Team Project Config files are located
        """
        self.project_config.location = dirname
        self.project_user_config.location = dirname

    @property
    def user_config_dir(self) -> Union[str, None]:
        """Returns the folder path to where the Zowe z/OSMF User Project Config files are located."""
        return self.project_user_config.location

    @user_config_dir.setter
    def user_config_dir(self, dirname: str) -> None:
        """Set directory/folder path to where Zowe z/OSMF User Project Config files are located"""
        self.project_user_config.location = dirname

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
        project_profile: dict = {}
        global_profile: dict = {}
        global_base_profile: dict = {}
        project_profile_name: Union[str, None] = None
        global_profile_name: Union[str, None] = None

        # get Project Profile
        try:
            project_profile, project_profile_name = self.project_config.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except Exception as exc:
            warnings.warn(
                f"Could not load Project Config {self.project_config.name} with exception {exc}",
                ConfigNotFoundWarning,
            )

        # get Project User Profile
        try:
            (
                project_user_profile,
                project_user_profile_name,
            ) = self.project_user_config.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except Exception:
            warnings.warn(
                f"Could not load Project Config {self.project_config.name}",
                ConfigNotFoundWarning,
            )
        else:
            project_profile.update(project_user_profile)

        # get Global Base Profile
        try:
            self.global_config.init_from_file()
            (
                global_base_profile,
                global_base_profile_name,
            ) = self.global_config.get_profile(profile_type="base")
        except Exception:
            warnings.warn(
                f"Could not load Global Config {self.global_config.name}",
                ConfigNotFoundWarning,
            )

        # get Global Base User Profile
        try:
            self.global_user_config.init_from_file()
            (
                global_base_user_profile,
                global_base_user_profile_name,
            ) = self.global_user_config.get_profile(profile_type="base")
        except Exception:
            warnings.warn(
                f"Could not load Global User Config {self.global_user_config.name}",
                ConfigNotFoundWarning,
            )
        else:
            global_base_profile.update(global_base_user_profile)

        # get Global Profile
        try:
            self.global_config.init_from_file()
            global_profile, global_profile_name = self.global_config.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except Exception:
            warnings.warn(
                f"Could not load Global Config {self.global_config.name}",
                ConfigNotFoundWarning,
            )

        # get Global User Profile
        try:
            self.global_user_config.init_from_file()
            (
                global_user_profile,
                global_user_profile_name,
            ) = self.global_user_config.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except Exception:
            warnings.warn(
                f"Could not load Global User Config {self.global_user_config.name}",
                ConfigNotFoundWarning,
            )
        else:
            global_profile.update(global_user_profile)

        # now update service profile
        service_profile.update(global_base_profile)

        if global_profile_name != project_profile_name:
            service_profile.update(global_profile)

        service_profile.update(project_profile)

        return service_profile
