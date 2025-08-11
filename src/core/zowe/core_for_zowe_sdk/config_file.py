"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import json
import os.path
import re
import warnings
from copy import deepcopy
from dataclasses import dataclass, field
from typing import NamedTuple, Optional, Any, Union

import commentjson
import requests

from .credential_manager import CredentialManager
from .custom_warnings import ProfileNotFoundWarning, ProfileParsingWarning
from .exceptions import ProfileNotFound
from .logger import Log
from .profile_constants import GLOBAL_CONFIG_NAME, TEAM_CONFIG, USER_CONFIG
from .validators import validate_config_json

HOME = os.path.expanduser("~")
GLOBAL_CONFIG_LOCATION = os.path.join(HOME, ".zowe")
GLOBAL_CONFIG_PATH = os.path.join(GLOBAL_CONFIG_LOCATION, f"{GLOBAL_CONFIG_NAME}.config.json")
CURRENT_DIR = os.getcwd()

# Profile datatype is used by ConfigFile to return Profile Data along with
# metadata such as profile_name and secure_props_not_found


class Profile(NamedTuple):
    """Class to represent a profile."""

    data: dict[str, Any] = {}
    name: str = ""
    missing_secure_props: list[str] = []


@dataclass
class ConfigFile:
    """
    Class used to represent a single config file.

    Mainly it will have the following details :
        1. Type ("User Config" or "Team Config")
            -------
            User Configs override Team Configs.
            User Configs are used to have personalised config details
            that the user don't want to have in the Team Config.
        2. Directory in which the file is located.
        3. Name (excluding .config.json or .config.user.json)
        4. Contents of the file.
            4.1 Profiles
            4.2 Defaults
            4.3 Schema Property
        5. Secure Properties associated with the file.
    """

    type: str
    name: str
    _location: Optional[str] = None
    profiles: Optional[dict[str, Any]] = None
    defaults: Optional[dict[str, Any]] = None
    schema_property: Optional[dict[str, Any]] = None
    secure_props: Optional[dict[str, Any]] = None
    jsonc: Optional[dict[str, Any]] = None
    _missing_secure_props: list[str] = field(default_factory=list)

    __suppress_config_file_warnings: Optional[bool] = True,
    __logger = Log.register_logger(__name__)

    @property
    def filename(self) -> str:
        # noqa: D102
        if self.type == TEAM_CONFIG:
            return f"{self.name}.config.json"

        if self.type == USER_CONFIG:
            return f"{self.name}.config.user.json"

        return self.name

    @property
    def filepath(self) -> Optional[str]:
        # noqa: D102
        if not self.location:
            return None

        return os.path.join(self.location, self.filename)

    @property
    def location(self) -> Optional[str]:
        # noqa: D102
        return self._location

    @location.setter
    def location(self, dirname: str) -> None:
        # noqa: D102
        if os.path.isdir(dirname):
            self._location = dirname
        else:
            self.__logger.error(f"given path {dirname} is not valid")
            raise FileNotFoundError(f"given path {dirname} is not valid")

    def init_from_file(
        self,
        validate_schema: Optional[bool] = True
    ) -> None:
        """
        Initialize the class variable after setting filepath (or if not set, autodiscover the file).

        Parameters
        ----------
        validate_schema: Optional[bool]
            True if validation is preferred, false otherwise
        """
        if self.filepath is None:
            try:
                self.autodiscover_config_dir()
            except FileNotFoundError:
                pass

        if self.filepath is None or not os.path.isfile(self.filepath):
            if not self.__suppress_config_file_warnings:
                self.__logger.warning(f"Config file does not exist at {self.filepath}")
                warnings.warn(f"Config file does not exist at {self.filepath}")
            return

        with open(self.filepath, encoding="UTF-8", mode="r") as fileobj:
            profile_jsonc = commentjson.load(fileobj)

        self.profiles = profile_jsonc.get("profiles", {}) if profile_jsonc.get("profiles", {}) is not None else []
        self.schema_property = profile_jsonc.get("$schema", None)
        self.defaults = profile_jsonc.get("defaults", {})
        self.jsonc = profile_jsonc

        if validate_schema:
            self.validate_schema()

        CredentialManager.load_secure_props()
        self.__load_secure_properties()

    def validate_schema(self) -> None:
        """Get the $schema_property from the config and load the schema."""
        if self.schema_property is None:  # check if the $schema property is not defined
            if not self.__suppress_config_file_warnings:
                self.__logger.warning(f"Could not find $schema property")
                warnings.warn(f"Could not find $schema property")
        else:
            jsonc_data: dict[str, Any] = self.jsonc if self.jsonc is not None else {}
            schema_data: str = str(self.schema_property) if isinstance(self.schema_property, (str, dict)) else ""
            cwd: str = self.location if isinstance(self.location, str) else ""
            validate_config_json(jsonc_data, schema_data, cwd=cwd)

    def schema_list(self, cwd: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Load the schema properties in a sorted order according to the priority.

        Parameters
        ----------
        cwd: Optional[str]
            current working directory

        Returns
        -------
        list[dict[str, Any]]
            properties from schema
        """
        schema: Optional[Union[str, dict[str, Any]]] = self.schema_property

        # Ensure schema is a string, otherwise return empty list
        if not isinstance(schema, str):
            return []

        schema_json: dict[str, Any] = {}

        if schema.startswith(("https://", "http://")):
            try:
                response = requests.get(schema)
                response.raise_for_status()  # Ensure it's a valid response
                schema_json = response.json()
            except requests.RequestException as e:
                if not self.__suppress_config_file_warnings:
                    warnings.warn(f"Invalid schema request: {e}")
                    self.__logger.warning(f"Invalid schema request: {e}")
                return []

        elif schema.startswith("file://") or os.path.isfile(schema):
            try:
                schema_path = schema.replace("file://", "")
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_json = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                if not self.__suppress_config_file_warnings:
                    warnings.warn(f"Invalid schema file '{schema_path}': {e}")
                    self.__logger.warning(f"Invalid schema file '{schema_path}': {e}")
                return []

        elif not os.path.isabs(schema):
            try:
                schema_path = os.path.join(self.location or cwd or "", schema)
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema_json = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                if not self.__suppress_config_file_warnings:
                    warnings.warn(f"Invalid JSON in schema file '{schema_path}': {e}")
                    self.__logger.warning(f"Invalid JSON in schema file '{schema_path}': {e}")
                return []
        else:
            return []

        # Ensure schema_json is a dictionary
        if not isinstance(schema_json, dict):
            return []

        profile_props: dict[str, Any] = {}

        try:
            profile_schema = schema_json["properties"]["profiles"]["patternProperties"]["^\\S*$"]["allOf"]
            for props in profile_schema:
                props = props["then"]
                while "properties" in props:
                    props = props.pop("properties")
                    profile_props = props
        except (KeyError, TypeError):
            return []

        return [profile_props] if profile_props else []

    def get_profile(
        self,
        profile_name: Optional[str] = None,
        profile_type: Optional[str] = None,
        validate_schema: Optional[bool] = True,
    ) -> Profile:
        """
        Load given profile including secure properties and excluding values from base profile.

        Parameters
        ----------
        profile_name: Optional[str]
            Name of the profile
        profile_type: Optional[str]
            Type of the profile
        validate_schema: Optional[bool]
            True if validation is preferred

        Raises
        ------
        ProfileNotFound
            Cannot find profile

        Returns
        -------
        Profile
            Returns a namedtuple called Profile
        """
        if self.profiles is None:
            self.init_from_file(validate_schema)

        if profile_name is None and profile_type is None:
            self.__logger.error(f"Failed to load profile: profile_name and profile_type were not provided.")
            raise ProfileNotFound(
                profile_name="",
                error_msg="Could not find profile as both profile_name and profile_type is not set.",
            )

        if profile_name is None:
            profile_name = self.get_profilename_from_profiletype(profile_type=profile_type or "")
        
        props: dict[str, Any] = self.load_profile_properties(profile_name=profile_name)

        return Profile(props, profile_name, self._missing_secure_props)

    def autodiscover_config_dir(self) -> None:
        """
        Autodiscover Zowe z/OSMF Team Config files by going up the path from current working directory.

        Sets path if it finds the config directory, Else, it raises an Exception.

        Raises
        ------
        FileNotFoundError
            Cannot find file in directory.
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
        Return profilename from given profiletype as defined in the team config profile.

        Parameters
        ----------
        profile_type: str
            Type of the profile

        Returns
        -------
        str
            The exact profilename of the profile to load from the mentioned type.

        Raises
        ------
        ProfileNotFound
            Cannot find profile
        """
        # try to get the profilename from defaults
        if self.defaults is not None and profile_type in self.defaults:
            return str(self.defaults[profile_type])

        if not self.__suppress_config_file_warnings:
            self.__logger.warning(f"Given profile type '{profile_type}' has no default profile name")
            warnings.warn(
                f"Given profile type '{profile_type}' has no default profile name",
                ProfileParsingWarning,
            )

        # Ensure profiles exist before iterating
        if self.profiles is None:
            self.__logger.error("No profiles found in the configuration")
            raise ProfileNotFound(
                profile_name=profile_type,
                error_msg="No profiles found in the configuration",
            )

        # iterate through the profiles and check if profile is found
        for key, value in self.profiles.items():
            try:
                temp_profile_type = value["type"]
                if profile_type == temp_profile_type:
                    return key
            except KeyError:
                if not self.__suppress_config_file_warnings:
                    self.__logger.warning(f"Profile '{key}' has no type attribute")
                    warnings.warn(
                        f"Profile '{key}' has no type attribute",
                        ProfileParsingWarning,
                    )

        # if no profile with matching type found, we raise an exception
        self.__logger.error(f"No profile with matching profile_type '{profile_type}' found")
        raise ProfileNotFound(
            profile_name=profile_type,
            error_msg=f"No profile with matching profile_type '{profile_type}' found",
        )

    def find_profile(self, path: str, profiles: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Find a profile at a specified location from within a set of nested profiles.

        Parameters
        ----------
        path: str
            The location to look for the profile
        profiles: dict[str, Any]
            A dict of nested profiles

        Returns
        -------
        Optional[dict[str, Any]]
            The profile object that was found, or None if not found
        """
        segments = path.split(".")
        for k, v in profiles.items():
            if not isinstance(v, dict):  # Ensure v is a dictionary
                if not self.__suppress_config_file_warnings:
                        self.__logger.warning("Invalid profile passed when schame validation is off")
                continue  # Skip invalid entries

            if segments[0] == k:
                if len(segments) == 1:
                    return v  # Ensured to be dict[str, Any]
                elif isinstance(v.get("profiles"), dict):
                    segments.pop(0)
                    return self.find_profile(".".join(segments), v["profiles"])  # Recursive call
        return None

    def load_profile_properties(self, profile_name: str) -> dict[str, Any]:
        """
        Load profile properties given profile_name including secure properties.

        Load exact profile properties (without prepopulated fields from base profile)
        from the profile dict and populate fields from the secure credentials storage

        Parameters
        ----------
        profile_name: str
            Name of the profile

        Returns
        -------
        dict[str, Any]
            Object containing profile properties

        Raises
        ------
        ValueError
            Profile cannot be None
        """
        props: dict[str, Any] = {}
        lst = profile_name.split(".")
        secure_fields: list[str] = []

        if self.profiles is None:  # Prevent NoneType issue
            raise ValueError("Profiles have not been initialized")

        while len(lst) > 0:
            profile_name = ".".join(lst)
            profile = self.find_profile(profile_name, self.profiles)

            if profile is not None:
                props = {**profile.get("properties", {}), **props}
                secure_fields.extend(profile.get("secure", []))  # Ensures secure_fields gets a list
            else:
                self.__logger.warning(f"Profile {profile_name} not found")
                warnings.warn(f"Profile {profile_name} not found", ProfileNotFoundWarning)

            lst.pop()

        return props

    def __load_secure_properties(self) -> None:
        """Inject secure properties that have been loaded from the vault into the profiles object."""
        secure_props = CredentialManager.secure_props.get(self.filepath or "", {})
        for key, value in secure_props.items():
            segments = [name for i, name in enumerate(key.split(".")) if i % 2 == 1]
            profiles_obj = self.profiles
            property_name = segments.pop()
            for i, profile_name in enumerate(segments):
                if profiles_obj is None or not isinstance(profiles_obj, dict):
                    break
                if profile_name in profiles_obj:
                    profiles_obj = profiles_obj[profile_name]
                    if not isinstance(profiles_obj, dict):
                        break
                    if i == len(segments) - 1:
                        profiles_obj.setdefault("properties", {})
                        profiles_obj["properties"][property_name] = value
                else:
                    break

    def __extract_secure_properties(
        self, profiles_obj: dict[str, Any], json_path: Optional[str] = "profiles"
    ) -> dict[str, Any]:
        """
        Extract secure properties from the profiles object for storage in the vault.

        Parameters
        ----------
        profiles_obj : dict[str, Any]
            The profiles object from which secure properties are extracted.
        json_path : Optional[str]
            The JSON path used as a base in the vault for storing secure properties.

        Returns
        -------
        dict[str, Any]
            A dictionary of secure properties keyed by JSON path in the vault.
        """
        secure_props = {}
        for key, value in profiles_obj.items():
            for property_name in value.get("secure", []):
                if property_name in value.get("properties", {}):
                    secure_props[f"{json_path}.{key}.properties.{property_name}"] = value["properties"].pop(
                        property_name
                    )
            if value.get("profiles"):
                secure_props.update(self.__extract_secure_properties(value["profiles"], f"{json_path}.{key}.profiles"))
        return secure_props

    def __set_or_create_nested_profile(self, profile_name: str, profile_data: dict[str, Any]) -> None:
        """
        Set or create a nested profile within the profiles structure.

        Parameters
        ----------
        profile_name : str
            The dot-separated path name of the profile to set or create.
        profile_data : dict[str, Any]
            The data to set in the specified profile.
        """
        path = self.get_profile_path_from_name(profile_name)
        keys = path.split(".")[1:]
        nested_profiles = self.profiles
        if not isinstance(nested_profiles, dict):
            return
        for key in keys:
            nested_profiles = nested_profiles.setdefault(key, {})
        nested_profiles.update(profile_data)

    def __is_secure(self, json_path: str, property_name: str) -> bool:
        """
        Determine if a property should be stored securely based on its presence in the secure list.

        Parameters
        ----------
        json_path : str
            The JSON path of the property within the profiles structure.
        property_name : str
            The name of the property to check for secure storage requirements.

        Returns
        -------
        bool
            True if the property is listed to be stored securely, False otherwise.
        """
        profile = self.find_profile(json_path, self.profiles)
        if profile and profile.get("secure"):
            return property_name in profile["secure"]
        return False

    def set_property(self, json_path: str, value: str, secure: Optional[bool] = None) -> None:
        """
        Set a property in the profile, storing it securely if necessary.

        Parameters
        ----------
        json_path: str
            The JSON path of the property to set.
        value: str
            The value to be set for the property.
        secure: Optional[bool]
            If True, the property will be stored securely. Default is None.
        """
        if self.profiles is None:
            self.init_from_file()

        # Checking whether the property should be stored securely or in plain text
        property_name = json_path.split(".")[-1]
        profile_name = self.get_profile_name_from_path(json_path)
        # check if the property is already secure
        is_property_secure = self.__is_secure(profile_name, property_name)
        is_secure = secure if secure is not None else is_property_secure

        current_profile = self.find_profile(profile_name, self.profiles) or {}

        if not isinstance(current_profile, dict):
            current_profile = {}

        current_properties = current_profile.setdefault("properties", {})
        current_secure = current_profile.setdefault("secure", [])
        current_properties[property_name] = value
        if is_secure and not is_property_secure:
            current_secure.append(property_name)
        elif not is_secure and is_property_secure:
            current_secure.remove(property_name)

        current_profile["properties"] = current_properties
        current_profile["secure"] = current_secure
        self.__set_or_create_nested_profile(profile_name, current_profile)

    def set_profile(self, profile_path: str, profile_data: dict[str, Any]) -> None:
        """
        Set a profile in the config file.

        Parameters
        ----------
        profile_path: str
            The path of the profile to be set. eg: profiles.zosmf
        profile_data: dict[str, Any]
            The data to be set for the profile.
        """
        if self.profiles is None:
            self.init_from_file()
        profile_name = self.get_profile_name_from_path(profile_path)
        if "secure" in profile_data:
            # Checking if the profile has a 'secure' field with values
            secure_fields = profile_data["secure"]
            current_profile = self.find_profile(profile_name, self.profiles) or {}
            existing_secure_fields = current_profile.get("secure", [])
            new_secure_fields = [field for field in secure_fields if field not in existing_secure_fields]

            # Updating the 'secure' field of the profile with the combined list of secure fields
            profile_data["secure"] = existing_secure_fields + new_secure_fields
            # If a field is provided in the 'secure' list and its value exists in 'profile_data', remove it
            profile_data["properties"] = {
                **current_profile.get("properties", {}),
                **profile_data.get("properties", {}),
            }
        self.__set_or_create_nested_profile(profile_name, profile_data)

    def save(self, update_secure_props: Optional[bool] = True) -> None:
        """
        Save the config file to disk. and secure props to vault.

        Parameters
        ----------
        update_secure_props: Optional[bool]
            If True, the secure properties will be stored in the vault. Default is True.

        Raises
        ------
        ValueError
            Filepath must be set and valid.
        """
        if not isinstance(self.filepath, str):
            raise ValueError("Filepath is not set or invalid")

        # Updating the config file with any changes
        if not any(self.profiles.values()):
            return

        profiles_temp = deepcopy(self.profiles)
        secure_props = self.__extract_secure_properties(profiles_temp)

        CredentialManager.secure_props[self.filepath] = secure_props
        with open(self.filepath, "w") as file:
            self.jsonc["profiles"] = profiles_temp
            commentjson.dump(self.jsonc, file, indent=4)
        if update_secure_props:
            CredentialManager.save_secure_props()

    def get_profile_name_from_path(self, path: str) -> str:
        """
        Get the name of the profile from the given path.

        Parameters
        ----------
        path: str
            The location to look for the profile

        Returns
        -------
        str
            Returns the profile name
        """
        segments = path.split(".")
        profile_name = ".".join(segments[i] for i in range(1, len(segments), 2) if segments[i - 1] != "properties")
        return profile_name

    def get_profile_path_from_name(self, short_path: str) -> str:
        """
        Get the path of the profile from the given name.

        Parameters
        ----------
        short_path: str
            Partial path of profile

        Returns
        -------
        str
            Returns the full profile path
        """
        return re.sub(r"(^|\.)", r"\1profiles.", short_path)
    
    def suppress_config_warnings(self, value: bool) -> None:
        """
        Suppress warnings in config files.

        Parameters
        ----------
        value: bool
            Warnings are shown or not 
        """
        self.__suppress_config_file_warnings = value
        
