"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os.path
import warnings
from typing import Tuple, Union

from .config_file import ConfigFile
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

    @staticmethod
    def get_profile(
        cfg: ConfigFile,
        profile_name: Union[str, None],
        profile_type: Union[str, None],
        config_type: str,
    ) -> Tuple[dict, str]:
        """Get just the profile from the config file (overriden with base props in the config file)"""

        cfg_profile: dict = {}
        cfg_profile_name: str = ""

        try:
            cfg_profile, cfg_profile_name = cfg.get_profile(
                profile_name=profile_name, profile_type=profile_type
            )
        except ProfileNotFound:
            warnings.warn(
                f"Profile not found in file '{cfg.filename}', trying to return base profile instead.",
                ProfileNotFoundWarning,
            )
            try:
                cfg_profile, cfg_profile_name = cfg.get_profile(
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
            return cfg_profile, cfg_profile_name

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
        project_profile, project_profile_name = self.get_profile(
            self.project_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Project Config",
        )

        # get Project User Profile
        project_user_profile, project_user_profile_name = self.get_profile(
            self.project_user_config,
            profile_name=profile_name,
            profile_type=profile_type,
            config_type="Project User Config",
        )
        project_profile.update(project_user_profile)

        # get Global Base Profile
        global_base_profile, global_base_profile_name = self.get_profile(
            self.global_config,
            profile_name=None,
            profile_type="base",
            config_type="Global Config",
        )

        # get Global Base User Profile
        global_base_user_profile, global_base_user_profile_name = self.get_profile(
            self.global_user_config,
            profile_name=None,
            profile_type="base",
            config_type="Global User Config",
        )
        global_base_profile.update(global_base_user_profile)

        # get Global Profile
        global_profile, global_profile_name = self.get_profile(
            self.global_config,
            profile_name=None,
            profile_type="base",
            config_type="Global Config",
        )

        # get Global User Profile
        global_user_profile, global_user_profile_name = self.get_profile(
            self.global_user_config,
            profile_name=None,
            profile_type="base",
            config_type="Global User Config",
        )
        global_profile.update(global_user_profile)

        # now update service profile
        service_profile.update(global_base_profile)

        if global_profile_name != project_profile_name:
            service_profile.update(global_profile)

        service_profile.update(project_profile)

        return service_profile
