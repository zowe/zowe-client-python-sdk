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
import json
import requests
import sys
import warnings
from dataclasses import dataclass, field
from typing import Optional, NamedTuple

import commentjson

from .constants import constants
from .credential_manager import CredentialManager
from .custom_warnings import (
    ProfileNotFoundWarning,
    ProfileParsingWarning,
    SecurePropsNotFoundWarning,
)
from .exceptions import ProfileNotFound, SecureProfileLoadFailed
from .profile_constants import (
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

# Profile datatype is used by ConfigFile to return Profile Data along with
# metadata such as profile_name and secure_props_not_found


class Profile(NamedTuple):
    data: dict = {}
    name: str = ""
    missing_secure_props: list = []


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
    4.3 Schema Property
    5. Secure Properties associated with the file.
    """

    type: str
    name: str
    _location: Optional[str] = None
    profiles: Optional[dict] = None
    defaults: Optional[dict] = None
    secure_props: Optional[dict] = None
    schema_property: Optional[dict] = None
    _missing_secure_props: list = field(default_factory=list)

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

    @property
    def schema_path(self) -> Optional[str]:
        self.schema_property

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
        self.jsonc = profile_jsonc
        self.schema_property = profile_jsonc.get("$schema", None)

        # loading secure props is done in load_profile_properties
        # since we want to try loading secure properties only when
        # we know that the profile has saved properties
        #  CredentialManager.load_secure_props()

    def schema_list(
        self,
    ) -> list:
        """
        Loads the schema properties
        in a sorted order according to the priority
        
        Returns
        -------
        Dictionary
        
            Returns the profile properties from schema (prop: value)
        """

        schema = self.schema_property
        if schema is None:
            return []

        if schema.startswith("https://") or schema.startswith("http://"):
            schema_json = requests.get(schema).json()

        elif not os.path.isabs(schema):
            schema = os.path.join(self.location, schema)
            with open(schema) as f:
                schema_json = json.load(f)
        
        elif os.path.isfile(schema):
            with open(schema) as f:
                schema_json = json.load(f)
        else:
            return []

        profile_props:dict = {}
        schema_json = dict(schema_json)
        
        for props in schema_json['properties']['profiles']['patternProperties']["^\\S*$"]["allOf"]:
            props = props["then"]
            
            while "properties" in props:
                props = props.pop("properties")
                profile_props = props

        return profile_props

    def get_profile(
        self,
        profile_name: Optional[str] = None,
        profile_type: Optional[str] = None,
    ) -> Profile:
        """
        Load given profile including secure properties and excluding values from base profile
        Returns
        -------
        Profile
            Returns a namedtuple called Profile
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

        return Profile(props, profile_name, self._missing_secure_props)

    def autodiscover_config_dir(self) -> None:
        """
        Autodiscover Zowe z/OSMF Team Config files by going up the path from
        current working directory
        Returns
        -------
        None

        Sets path if it finds the config directory,
        Else, it raises an Exception
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
        Returns profilename from given profiletype as defined in the team config profile
        Returns
        -------
        str

        Return the exact profilename of the profile to load from the mentioned type.
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

    def find_profile(self, path: str, profiles: dict):
        """
        Find a profile at a specified location from within a set of nested profiles
        Returns
        -------
        dictionary

            The profile object that was found, or None if not found
        """
        segments = path.split(".")
        for k, v in profiles.items():
            if len(segments) == 1 and segments[0] == k:
                return v
            elif segments[0] == k and v.get("profiles"):
                segments.pop(0)
                return self.find_profile(".".join(segments), v["profiles"])
        return None

    def load_profile_properties(self, profile_name: str) -> dict:
        """
        Load profile properties given profile_name including secure properties
        Returns
        -------
        dictionary

            Object containing profile properties

        Load exact profile properties (without prepopulated fields from base profile)
        from the profile dict and populate fields from the secure credentials storage
        """
        props = {}
        lst = profile_name.split(".")
        secure_fields: list = []

        while len(lst) > 0:
            profile_name = ".".join(lst)
            profile = self.find_profile(profile_name, self.profiles)
            if profile is not None:
                props = {**profile.get("properties", {}), **props}
                secure_fields.extend(profile.get("secure", []))
            else:
                warnings.warn(
                    f"Profile {profile_name} not found",
                    ProfileNotFoundWarning
                )
            lst.pop()

        # load secure props only if there are secure fields
        if secure_fields:
            CredentialManager.load_secure_props()
            self.secure_props=CredentialManager.secure_props.get(self.filepath, {})
            # load properties with key as profile.{profile_name}.properties.{*}
            for (key, value) in self.secure_props.items():
                if re.match(
                    "profiles\\." + profile_name + "\\.properties\\.[a-z]+", key
                ):
                    property_name = key.split(".")[-1]
                    if property_name in secure_fields:
                        props[property_name] = value
                        secure_fields.remove(property_name)

            # if len(secure_fields) > 0:
            #     self._missing_secure_props.extend(secure_fields)

        return props

    def __set_or_create_nested_profile(self, profile_name, profile_data):
        """
        Set or create a nested profile.
        """
        path = self.get_profile_path_from_name(profile_name)
        keys = path.split(".")[1:]
        nested_profiles = self.profiles
        for key in keys:
            nested_profiles = nested_profiles.setdefault(key, {})
        nested_profiles.update(profile_data)

    def __is_secure(self, json_path: str, property_name: str) -> bool:
        """
        Check whether the given JSON path corresponds to a secure property.

        Parameters:
            json_path (str): The JSON path of the property to check.
            property_name (str): The name of the property to check.

        Returns:
            bool: True if the property should be stored securely, False otherwise.
        """

        profile = self.find_profile(json_path, self.profiles)
        if profile and profile.get("secure"):
            return property_name in profile["secure"]
        return False

    def set_property(self, json_path, value, secure=None) -> None:
        """
        Set a property in the profile, storing it securely if necessary.

        Parameters:
            json_path (str): The JSON path of the property to set.
            value (str): The value to be set for the property.
            profile_name (str): The name of the profile to set the property in.
            secure (bool): If True, the property will be stored securely. Default is None.
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
        current_properties = current_profile.setdefault("properties", {})
        current_secure = current_profile.setdefault("secure", [])
        if is_secure:
            CredentialManager.load_secure_props()
            if not is_property_secure:
                current_secure.append(property_name)

            CredentialManager.secure_props[self.filepath] = {
                **CredentialManager.secure_props.get(self.filepath, {}), json_path: value}
            current_properties.pop(property_name, None)

        else:
            if is_property_secure:
                current_secure.remove(property_name)
            current_properties[property_name] = value

        current_profile["properties"] = current_properties
        current_profile["secure"] = current_secure
        self.__set_or_create_nested_profile(profile_name, current_profile)

    def set_profile(self, profile_path: str, profile_data: dict) -> None: 
        """
        Set a profile in the config file.

        Parameters:
            profile_path (str): The path of the profile to be set. eg: profiles.zosmf
            profile_data (dict): The data to be set for the profile.
        """
        if self.profiles is None:
            self.init_from_file()
        profile_name = self.get_profile_name_from_path(profile_path)
        if "secure" in profile_data:
            # Checking if the profile has a 'secure' field with values
            secure_fields = profile_data["secure"]
            current_profile  = self.find_profile(profile_name,self.profiles) or {}
            existing_secure_fields = current_profile.get("secure", [])
            new_secure_fields = [field for field in secure_fields if field not in existing_secure_fields]

            # JSON paths for new secure properties and store their values in CredentialManager.secure_props
            CredentialManager.load_secure_props()
            CredentialManager.secure_props[self.filepath] = {}
            for field in new_secure_fields:
                json_path = f"{profile_path}.properties.{field}"
                profile_value = profile_data["properties"][field]
                CredentialManager.secure_props[self.filepath][json_path] = profile_value
            # Updating the 'secure' field of the profile with the combined list of secure fields
            profile_data["secure"] = existing_secure_fields + new_secure_fields
            # If a field is provided in the 'secure' list and its value exists in 'profile_data', remove it
            profile_data["properties"] = {
                field: value
                for field, value in profile_data.get("properties", {}).items()
                if field not in profile_data["secure"]
            }
        self.__set_or_create_nested_profile(profile_name, profile_data)
        

    def save(self, secure_props=True):
        """
        Save the config file to disk. and secure props to vault
        parameters:
            secure_props (bool): If True, the secure properties will be stored in the vault. Default is False.
        Returns:
            None
        """
        # Update the config file with any changes
        if self.profiles is None:
            warnings.warn(
                    "Profiles are not found.",
                    ProfileNotFoundWarning
                )
        elif any(self.profiles.values()):
            with open(self.filepath, 'w') as file:
                self.jsonc["profiles"] = self.profiles
                commentjson.dump(self.jsonc, file, indent=4)
            if secure_props:
                CredentialManager.save_secure_props()
    

    def get_profile_name_from_path(self, path: str) -> str:
        """
        Get the name of the profile from the given path.
        """
        segments = path.split(".")
        profile_name = ".".join(segments[i] for i in range(1, len(segments), 2) if segments[i - 1] != "properties")
        return profile_name
    
    def get_profile_path_from_name(self, short_path: str) -> str:
        """
        Get the path of the profile from the given name.
        """
        return re.sub(r'(^|\.)', r'\1profiles.', short_path)