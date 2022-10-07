"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os.path
import warnings
from typing import Optional

from .config_file import ConfigFile, Profile
from .custom_warnings import (
    ConfigNotFoundWarning,
    ProfileNotFoundWarning,
    SecurePropsNotFoundWarning,
)
from .exceptions import ProfileNotFound, SecureProfileLoadFailed
from .profile_constants import (
    BASE_PROFILE,
    GLOBAL_CONFIG_NAME,
    TEAM_CONFIG,
    USER_CONFIG,
)

HAS_KEYRING = True


HOME = os.path.expanduser("~")
GLOBAl_CONFIG_LOCATION = os.path.join(HOME, ".zowe")
GLOBAL_CONFIG_PATH = os.path.join(
    GLOBAl_CONFIG_LOCATION, f"{GLOBAL_CONFIG_NAME}.config.json"
)
CURRENT_DIR = os.getcwd()


class ProfileManager:
    """
    Profile Manager contains the logic to merge the different properties of profiles
    (from the Project Config and the Project User Config as well as the Global Config and Global User Config).
    This class handles all the exceptions raised in the Config File to provide a smooth user experience.
    """

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
    def config_dir(self) -> Optional[str]:
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
    def user_config_dir(self) -> Optional[str]:
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
    def config_filepath(self) -> Optional[str]:
        """Get the full Zowe z/OSMF Team Project Config filepath"""
        return self.project_config.filepath

    @staticmethod
    def get_profile(
        cfg: ConfigFile,
        profile_name: Optional[str],
        profile_type: Optional[str],
        config_type: str,
    ) -> Profile:
        """Get just the profile from the config file (overriden with base props in the config file)"""

        cfg_profile = Profile()
        try:
            cfg_profile = cfg.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except ProfileNotFound:
            warnings.warn(
                f"Profile not found in file '{cfg.filename}', trying to return base profile instead.",
                ProfileNotFoundWarning,
            )
            try:
                cfg_profile = cfg.get_profile(
                    profile_name=BASE_PROFILE, profile_type=BASE_PROFILE
                )
            except Exception as exc:
                warnings.warn(
                    f"Base Profile not found in file '{cfg.filename}' because {type(exc).__name__}'{exc}', "
                    f"returning empty profile.",
                    ProfileNotFoundWarning,
                )
        except SecureProfileLoadFailed:
            warnings.warn(
                f"Config '{cfg.filename}' has no saved secure properties.",
                SecurePropsNotFoundWarning,
            )
        except SecurePropsNotFoundWarning:
            if profile_name:
                warnings.warn(
                    f"Secure properties of profile '{profile_name}' from file '{cfg.filename}' were not found "
                    f"hence profile not loaded.",
                    SecurePropsNotFoundWarning,
                )
            else:
                warnings.warn(
                    f"Secure properties of profile type '{profile_type}' from file '{cfg.filename}' were not found "
                    f"hence profile not loaded.",
                    SecurePropsNotFoundWarning,
                )
        except Exception as exc:
            warnings.warn(
                f"Could not load {config_type} '{cfg.filename}' at '{cfg.filepath}'"
                f"because {type(exc).__name__}'{exc}'.",
                ConfigNotFoundWarning,
            )
        finally:
            return cfg_profile

    def load(
        self,
        profile_name: Optional[str] = None,
        profile_type: Optional[str] = None,
    ) -> dict:
        """Load z/OSMF connection details from a z/OSMF profile.
        Returns
        -------
        dictionary

            z/OSMF connection object
        We will be loading properties from a bottom up fashion,
        the bottom being the base/default profile properties
        and the up being the explicitly mentioned Profile.

        Profile loading order :
        1. Global Profile
            1.1 Global Profile from Global Config (populated with base profile)
            1.2 Global User Profile from Global User Config (populated with base profile)
        2. Global Base Profile
            1.1 Global Base Profile form Global Config
            1.1 Global Base User Profile from Global User Config

        3. Project Profile
            3.1 Project Profile from Project Config
            3.2 Project User Profile from Project User Config

        4.If Global Profile and Project Profile have same profile_name,
            we do not load defaults from Global Proifle, instead,
            we user the Global Base Profile
        """
        if profile_name is None and profile_type is None:
            raise ProfileNotFound(
                profile_name=profile_name,
                error_msg="Could not find profile as both profile_name and profile_type is not set.",
            )

        service_profile: dict = {}

        # get Project Profile
        project_profile = self.get_profile(
            self.project_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Project Config",
        )

        # get Project User Profile
        project_user_profile = self.get_profile(
            self.project_user_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Project User Config",
        )
        project_profile.data.update(project_user_profile.data)

        # get Global Base Profile
        global_base_profile = self.get_profile(
            self.global_config,
            profile_name=None,
            profile_type=BASE_PROFILE,
            config_type="Global Config",
        )

        # get Global Base User Profile
        global_base_user_profile = self.get_profile(
            self.global_user_config,
            profile_name=None,
            profile_type=BASE_PROFILE,
            config_type="Global User Config",
        )
        global_base_profile.data.update(global_base_user_profile.data)

        # get Global Profile
        global_profile = self.get_profile(
            self.global_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Global Config",
        )

        # get Global User Profile
        global_user_profile = self.get_profile(
            self.global_user_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Global User Config",
        )
        global_profile.data.update(global_user_profile.data)

        # now update service profile
        service_profile.update(global_base_profile.data)

        if global_profile.name != project_profile.name:
            service_profile.update(global_profile.data)

        service_profile.update(project_profile.data)

        return service_profile
