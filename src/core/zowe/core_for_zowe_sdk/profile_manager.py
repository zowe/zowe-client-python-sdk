"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os.path
import os
import warnings
import jsonschema
from typing import Optional

from .config_file import ConfigFile, Profile
from .custom_warnings import (
    ConfigNotFoundWarning,
    ProfileNotFoundWarning,
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

    def __init__(self, appname: str = "zowe", show_warnings: bool = True):
        self._appname = appname
        self._show_warnings = show_warnings

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
    def get_env(
        cfg: ConfigFile,
    ) -> dict:
        """
        Maps the env variables to the profile properties
        
        Returns
        -------
        Dictionary

            Containing profile properties from env variables (prop: value)
        """
        
        props = cfg.schema_list()
        if props == []:
            return {}
        
        env, env_var = {}, {}
        
        for var in list(os.environ.keys()):
            if var.startswith("ZOWE_OPT"):
                env[var[len("ZOWE_OPT_"):].lower()] = os.environ.get(var)
                
        for k, v in env.items():
            word = k.split("_")

            if len(word) > 1:
                k = word[0]+word[1].capitalize()
            else:
                k = word[0]

            if k in list(props.keys()):
                if props[k]['type'] == "number":
                    env_var[k] = int(v)

                elif props[k]['type'] == "string":
                    env_var[k] = str(v)

                elif props[k]['type'] == "boolean":
                    env_var[k] = bool(v)

        return env_var
                                 
    @staticmethod
    def get_profile(
        cfg: ConfigFile,
        profile_name: Optional[str],
        profile_type: Optional[str],
        config_type: Optional[str],
        validate_schema: Optional[bool] = True,
    ) -> Profile:
        """
        Get just the profile from the config file (overriden with base props in the config file)

        Returns
        -------
        Profile

            NamedTuple (data, name, secure_props_not_found)
        """

        cfg_profile = Profile()
        try:
            cfg_profile = cfg.get_profile(
                profile_name=profile_name, profile_type=profile_type, validate_schema=validate_schema
            )
        except jsonschema.exceptions.ValidationError as exc:
            raise jsonschema.exceptions.ValidationError(
                f"Instance was invalid under the provided $schema property, {exc}"
            )
        except jsonschema.exceptions.SchemaError as exc:
            raise jsonschema.exceptions.SchemaError(
                f"The provided schema is invalid, {exc}"
            )
        except jsonschema.exceptions.UndefinedTypeCheck as exc:
            raise jsonschema.exceptions.UndefinedTypeCheck(
                f"A type checker was asked to check a type it did not have registered, {exc}"
            )
        except jsonschema.exceptions.UnknownType as exc:
            raise jsonschema.exceptions.UnknownType(
                f"Unknown type is found in schema_json, exc"
            )
        except jsonschema.exceptions.FormatError as exc:
            raise jsonschema.exceptions.FormatError(
                f"Validating a format config_json failed for schema_json, {exc}"
            )
        except ProfileNotFound:
            if profile_name:
                warnings.warn(
                    f"Profile '{profile_name}' not found in file '{cfg.filename}', returning empty profile instead.",
                    ProfileNotFoundWarning,
                )
            else:
                warnings.warn(
                    f"Profile of type '{profile_type}' not found in file '{cfg.filename}', returning empty profile"
                    f" instead.",
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
        
        return cfg_profile

    def load(
        self,
        profile_name: Optional[str] = None,
        profile_type: Optional[str] = None,
        check_missing_props: bool = True,
        validate_schema: Optional[bool] = True,
        override_with_env: Optional[bool] = False,
    ) -> dict:
        """Load connection details from a team config profile.
        Returns
        -------
        dictionary

            Object containing connection details

        We will load properties from config files in the following order, from
        highest to lowest priority:
        1. Project User Config (./zowe.config.user.json)
        2. Project Config (./zowe.config.json)
        3. Global User Config (~/zowe.config.user.json)
        4. Global Config (~/zowe.config.json)

        If `profile_type` is not base, then we will load properties from both
        `profile_type` and base profiles and merge them together.
        """
        if profile_name is None and profile_type is None:
            raise ProfileNotFound(
                profile_name=profile_name,
                error_msg="Could not find profile as both profile_name and profile_type is not set.",
            )

        if not self._show_warnings:
            warnings.simplefilter("ignore")

        config_layers = {
            "Project User Config": self.project_user_config,
            "Project Config": self.project_config,
            "Global User Config": self.global_user_config,
            "Global Config": self.global_config,
        }
        profile_props: dict = {}
        schema_path = None
        env_var: dict = {}

        missing_secure_props = []  # track which secure props were not loaded

        for i, (config_type, cfg) in enumerate(config_layers.items()):
            profile_loaded = self.get_profile(
                cfg, profile_name, profile_type, config_type, validate_schema
            )
            # TODO Why don't user and password show up here for Project User Config?
            # Probably need to update load_profile_properties method in config_file.py
            if profile_loaded.name and not profile_name:
                profile_name = (
                    profile_loaded.name
                )  # Define profile name that will be merged from other layers
            profile_props = {**profile_loaded.data, **profile_props}
            
            missing_secure_props.extend(profile_loaded.missing_secure_props)

            if override_with_env:
                env_var = {**self.get_env(cfg)}

            if i == 1 and profile_props:
                break  # Skip loading from global config if profile was found in project config

        if profile_type != BASE_PROFILE:
            profile_props = {
                **self.load(profile_type=BASE_PROFILE, check_missing_props=False),
                **profile_props,
            }

        if check_missing_props:
            missing_props = set()
            for item in missing_secure_props:
                if item not in profile_props.keys():
                    missing_props.add(item)

            if len(missing_props) > 0:
                raise SecureValuesNotFound(values=missing_props)

        warnings.resetwarnings()

        for k, v in profile_props.items():
            if k in env_var:
                profile_props[k] = env_var[k]

        return profile_props
