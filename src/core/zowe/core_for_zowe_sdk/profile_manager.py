"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
import os.path
import warnings
from copy import deepcopy
from typing import Optional

import jsonschema
from deepmerge import always_merger

from .config_file import ConfigFile, Profile
from .credential_manager import CredentialManager
from .custom_warnings import (
    ConfigNotFoundWarning,
    ProfileNotFoundWarning,
    SecurePropsNotFoundWarning,
)
from .exceptions import ProfileNotFound, SecureProfileLoadFailed, SecureValuesNotFound
from .logger import Log
from .profile_constants import (
    BASE_PROFILE,
    GLOBAL_CONFIG_NAME,
    TEAM_CONFIG,
    USER_CONFIG,
)

HAS_KEYRING = True


HOME = os.path.expanduser("~")
GLOBAL_CONFIG_LOCATION = os.path.join(HOME, ".zowe")
GLOBAL_CONFIG_PATH = os.path.join(GLOBAL_CONFIG_LOCATION, f"{GLOBAL_CONFIG_NAME}.config.json")
CURRENT_DIR = os.getcwd()


class ProfileManager:
    """
    Profile Manager contains the logic to merge the different properties of profiles
    (from the Project Config and the Project User Config as well as the Global Config and Global User Config).
    This class handles all the exceptions raised in the Config File to provide a smooth user experience.
    """

    def __init__(self, appname: str = "zowe", show_warnings: bool = True):
        self.__appname = appname
        self.__show_warnings = show_warnings

        self.__project_config = ConfigFile(type=TEAM_CONFIG, name=appname)
        self.__project_user_config = ConfigFile(type=USER_CONFIG, name=appname)

        self.__logger = Log.registerLogger(__name__)

        self.__global_config = ConfigFile(type=TEAM_CONFIG, name=GLOBAL_CONFIG_NAME)
        try:
            self.__global_config.location = GLOBAL_CONFIG_LOCATION
        except Exception:
            self.__logger.warning("Could not find Global Config Directory")
            warnings.warn(
                "Could not find Global Config Directory, please provide one.",
                ConfigNotFoundWarning,
            )

        self.__global_user_config = ConfigFile(type=USER_CONFIG, name=GLOBAL_CONFIG_NAME)
        try:
            self.__global_user_config.location = GLOBAL_CONFIG_LOCATION
        except Exception:
            self.__logger.warning("Could not find Global User Config Directory")
            warnings.warn(
                "Could not find Global User Config Directory, please provide one.",
                ConfigNotFoundWarning,
            )

    @property
    def config_appname(self) -> str:
        """Returns the app name"""
        return self.__appname

    @property
    def config_dir(self) -> Optional[str]:
        """Returns the folder path to where the Zowe z/OSMF Team Project Config files are located."""
        return self.__project_config.location

    @config_dir.setter
    def config_dir(self, dirname: str) -> None:
        """
        Set directory/folder path to where Zowe z/OSMF Team Project Config files are located
        """
        self.__project_config.location = dirname
        self.__project_user_config.location = dirname

    @property
    def user_config_dir(self) -> Optional[str]:
        """Returns the folder path to where the Zowe z/OSMF User Project Config files are located."""
        return self.__project_user_config.location

    @user_config_dir.setter
    def user_config_dir(self, dirname: str) -> None:
        """Set directory/folder path to where Zowe z/OSMF User Project Config files are located"""
        self.__project_user_config.location = dirname

    @property
    def config_filename(self) -> str:
        """Return the filename for Zowe z/OSMF Team Project Config"""
        return self.__project_config.filename

    @property
    def config_filepath(self) -> Optional[str]:
        """Get the full Zowe z/OSMF Team Project Config filepath"""
        return self.__project_config.filepath

    @staticmethod
    def get_env(cfg: ConfigFile, cwd=None) -> dict:
        """
        Maps the env variables to the profile properties

        Returns
        -------
        Dictionary
            Containing profile properties from env variables (prop: value)
        """

        props = cfg.schema_list(cwd)
        if props == []:
            return {}

        env, env_var = {}, {}

        for var in list(os.environ.keys()):
            if var.startswith("ZOWE_OPT"):
                env[var[len("ZOWE_OPT_") :].lower()] = os.environ.get(var)

        for k, v in env.items():
            word = k.split("_")

            if len(word) > 1:
                k = word[0] + word[1].capitalize()
            else:
                k = word[0]

            if k in list(props.keys()):
                if props[k]["type"] == "number":
                    env_var[k] = int(v)

                elif props[k]["type"] == "string":
                    env_var[k] = str(v)

                elif props[k]["type"] == "boolean":
                    env_var[k] = bool(v)

        return env_var

    @staticmethod
    def get_profile(
        cfg: ConfigFile,
        profile_name: Optional[str],
        profile_type: Optional[str],
        validate_schema: Optional[bool] = True,
    ) -> Profile:
        """
        Get just the profile from the config file (overriden with base props in the config file)

        Returns
        -------
        Profile

            NamedTuple (data, name, secure_props_not_found)
        """

        logger = Log.registerLogger(__name__)

        cfg_profile = Profile()
        try:
            cfg_profile = cfg.get_profile(
                profile_name=profile_name, profile_type=profile_type, validate_schema=validate_schema
            )
        except jsonschema.exceptions.ValidationError as exc:
            logger.error(f"Instance was invalid under the provided $schema property, {exc}")
            raise jsonschema.exceptions.ValidationError(
                f"Instance was invalid under the provided $schema property, {exc}"
            )
        except jsonschema.exceptions.SchemaError as exc:
            logger.error(f"The provided schema is invalid, {exc}")
            raise jsonschema.exceptions.SchemaError(f"The provided schema is invalid, {exc}")
        except jsonschema.exceptions.UndefinedTypeCheck as exc:
            logger.error(f"A type checker was asked to check a type it did not have registered, {exc}")
            raise jsonschema.exceptions.UndefinedTypeCheck(
                f"A type checker was asked to check a type it did not have registered, {exc}"
            )
        except jsonschema.exceptions.UnknownType as exc:
            logger.error(f"Unknown type is found in schema_json, {exc}")
            raise jsonschema.exceptions.UnknownType(f"Unknown type is found in schema_json, {exc}")
        except jsonschema.exceptions.FormatError as exc:
            logger.error(f"Validating a format config_json failed for schema_json, {exc}")
            raise jsonschema.exceptions.FormatError(f"Validating a format config_json failed for schema_json, {exc}")
        except ProfileNotFound:
            if profile_name:
                logger.warning(f"Profile '{profile_name}' not found in file '{cfg.filename}'")
                warnings.warn(
                    f"Profile '{profile_name}' not found in file '{cfg.filename}', returning empty profile instead.",
                    ProfileNotFoundWarning,
                )
            else:
                logger.warning(f"Profile of type '{profile_type}' not found in file '{cfg.filename}'")
                warnings.warn(
                    f"Profile of type '{profile_type}' not found in file '{cfg.filename}', returning empty profile"
                    f" instead.",
                    ProfileNotFoundWarning,
                )
        except Exception as exc:
            logger.warning(
                f"Could not load '{cfg.filename}' at '{cfg.filepath}'" f"because {type(exc).__name__}'{exc}'"
            )
            warnings.warn(
                f"Could not load '{cfg.filename}' at '{cfg.filepath}'" f"because {type(exc).__name__}'{exc}'.",
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
        suppress_config_file_warnings: Optional[bool] = True,
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
            self.__logger.error(f"Failed to load profile as both profile_name and profile_type are not set")
            raise ProfileNotFound(
                profile_name=profile_name,
                error_msg="Could not find profile as both profile_name and profile_type is not set.",
            )

        if not self.__show_warnings:
            warnings.simplefilter("ignore")

        profile_props: dict = {}
        env_var: dict = {}
        missing_secure_props = []  # track which secure props were not loaded

        defaults_merged: dict = {}
        profiles_merged: dict = {}
        cfg_name = None
        cfg_schema = None
        cfg_schema_dir = None

        for cfg_layer in (
            self.__project_user_config,
            self.__project_config,
            self.__global_user_config,
            self.__global_config,
        ):
            if cfg_layer.profiles is None:
                try:
                    cfg_layer.init_from_file(validate_schema, suppress_config_file_warnings)
                except SecureProfileLoadFailed:
                    self.__logger.warning(f"Could not load secure properties for {cfg_layer.filepath}")
                    warnings.warn(
                        f"Could not load secure properties for {cfg_layer.filepath}",
                        SecurePropsNotFoundWarning,
                    )
            if cfg_layer.defaults:
                for name, value in cfg_layer.defaults.items():
                    defaults_merged[name] = defaults_merged.get(name, value)
            if not cfg_name and cfg_layer.name:
                cfg_name = cfg_layer.name
            if not cfg_schema and cfg_layer.schema_property:
                cfg_schema = cfg_layer.schema_property
                cfg_schema_dir = cfg_layer._location

        usrProject = self.__project_user_config.profiles or {}
        project = self.__project_config.profiles or {}
        project_temp = always_merger.merge(deepcopy(project), usrProject)

        usrGlobal = self.__global_user_config.profiles or {}
        global_ = self.__global_config.profiles or {}
        global_temp = always_merger.merge(deepcopy(global_), usrGlobal)

        profiles_merged = project_temp
        for name, value in global_temp.items():
            if name not in profiles_merged:
                profiles_merged[name] = value

        cfg = ConfigFile(
            type="Merged Config",
            name=cfg_name,
            profiles=profiles_merged,
            defaults=defaults_merged,
            schema_property=cfg_schema,
        )
        profile_loaded = self.get_profile(cfg, profile_name, profile_type, validate_schema)
        if profile_loaded:
            profile_props = profile_loaded.data
            missing_secure_props.extend(profile_loaded.missing_secure_props)

        if override_with_env:
            env_var = {**self.get_env(cfg, cfg_schema_dir)}

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
                self.__logger.error(f"Failed to load secure values: {missing_props}")
                raise SecureValuesNotFound(values=missing_props)

        warnings.resetwarnings()

        for k in profile_props:
            if k in env_var:
                profile_props[k] = env_var[k]

        return profile_props

    def get_highest_priority_layer(self, json_path: str) -> Optional[ConfigFile]:
        """
        Get the highest priority layer (configuration file) based on the given profile name

        Parameters
        -------
        profile_name: str
            The name of the profile to look for in the layers.

        Returns
        -------
        Optional[ConfigFile]
            The highest priority layer (configuration file) that contains the specified profile, or None if the profile is not found in any layer.
        """
        highest_layer = None
        longest_match = ""
        layers = [self.__project_user_config, self.__project_config, self.__global_user_config, self.__global_config]

        original_name = layers[0].get_profile_name_from_path(json_path)

        for layer in layers:
            try:
                layer.init_from_file()
            except FileNotFoundError:
                continue
            parts = original_name.split(".")
            current_name = ""

            while parts:
                current_name = ".".join(parts)
                profile = layer.find_profile(current_name, layer.profiles)

                if profile is not None and len(current_name) > len(longest_match):
                    highest_layer = layer
                    longest_match = current_name

                else:
                    parts.pop()
            if original_name == longest_match:
                break

            if highest_layer is None:
                highest_layer = layer

        if highest_layer is None:
            self.__logger.error(f"Could not find a valid layer for {json_path}")
            raise FileNotFoundError(f"Could not find a valid layer for {json_path}")

        return highest_layer

    def set_property(self, json_path, value, secure=None) -> None:
        """
        Set a property in the profile, storing it securely if necessary.

        Parameters
        -------
        json_path: str
            The JSON path of the property to set.
        value: str
            The value to be set for the property.
        secure: bool
            If True, the property will be stored securely. Default is None.
        """

        # highest priority layer for the given profile name
        highest_priority_layer = self.get_highest_priority_layer(json_path)

        # Set the property in the highest priority layer

        highest_priority_layer.set_property(json_path, value, secure=secure)

    def set_profile(self, profile_path: str, profile_data: dict) -> None:
        """
        Set a profile in the highest priority layer (configuration file) based on the given profile name

        Parameters
        -------
        profile_path: str
            The path of the profile to be set. eg: profiles.zosmf
        profile_data: dict
            The data of the profile to set.
        """
        highest_priority_layer = self.get_highest_priority_layer(profile_path)

        highest_priority_layer.set_profile(profile_path, profile_data)

    def save(self) -> None:
        """
        Save the layers (configuration files) to disk.
        """
        layers = [self.__project_user_config, self.__project_config, self.__global_user_config, self.__global_config]

        for layer in layers:
            layer.save(False)
        CredentialManager.save_secure_props()
