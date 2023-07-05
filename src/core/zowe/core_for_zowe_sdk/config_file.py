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
from dataclasses import dataclass, field
from typing import Optional, NamedTuple

import commentjson

from .constants import constants
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
    5. Secure Properties associated with the file.
    """

    type: str
    name: str
    _location: Optional[str] = None
    profiles: Optional[dict] = None
    defaults: Optional[dict] = None
    secure_props: Optional[dict] = None
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
                props = { **profile.get("properties", {}), **props }
                secure_fields.extend(profile.get("secure", []))
            else:
                warnings.warn(
                        f"Profile {profile_name} not found",
                        ProfileNotFoundWarning
                        )
            lst.pop()


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

            # if len(secure_fields) > 0:
            #     self._missing_secure_props.extend(secure_fields)

        return props

    def load_secure_props(self) -> None:
        """
        load secure_props stored for the given config file
        Returns
        -------
        None

        if keyring is not initialized, set empty value
        """
        if not HAS_KEYRING:
            self.secure_props = {}
            return

        try:
            service_name = constants["ZoweServiceName"]

            if sys.platform == "win32":
                service_name += "/" + constants["ZoweAccountName"]
                secret_value = self._retrieve_password(service_name)
            else:
                secret_value = keyring.get_password(
                    service_name, constants["ZoweAccountName"]
                )
            
            # Handle the case when secret_value is None
            if secret_value is None:
                secret_value = ""    

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

        # look for credentials stored for currently loaded config
        try:
            self.secure_props = secure_config_json.get(self.filepath, {})
        except KeyError as exc:
            error_msg = str(exc)
            warnings.warn(
                f"No credentials found for loaded config file '{self.filepath}'"
                f" with error '{error_msg}'",
                SecurePropsNotFoundWarning,
            )
        # self.set_secure_props() 

    def _retrieve_password(self, service_name: str) -> Optional[str]:
        """
        Retrieve the password from the keyring or storage.
        If the password exceeds the maximum length, retrieve it in parts.
        Parameters
        ----------
        service_name: str
            The service name for the password retrieval
        Returns
        -------
        str
            The retrieved password
        """
        password = keyring.get_password(service_name, constants["ZoweAccountName"])

        if password is None:
            # Retrieve the secure value with an index
            index = 1
            temp_value = keyring.get_password(service_name, f"{constants['ZoweAccountName']}-{index}")
            while temp_value is not None:
                if password is None:
                    password = temp_value
                else:
                    password += temp_value
                index += 1
                temp_value = keyring.get_password(service_name, f"{constants['ZoweAccountName']}-{index}")
                
        if password is not None and password.endswith("\0"):
            password = password[:-1]

        return password 
    
    def set_secure_props(self) -> None:
        """
        Set secure_props for the given config file
        Returns
        -------
        None
        """
        if not HAS_KEYRING:
            return

        try:
            service_name = constants["ZoweServiceName"]
            credential = self.secure_props.get(self.filepath, {})
            if sys.platform == "win32":
                service_name += "/" + constants["ZoweAccountName"]
                
                # Load existing credentials
                existing_credential = keyring.get_password(service_name, constants["ZoweAccountName"])

                if existing_credential:
                    # Decode the existing credential and update secure_props
                    existing_secure_props = commentjson.loads(existing_credential)
                    existing_secure_props.update(self.secure_props.get(self.filepath, {}))
                    self.secure_props[self.filepath] = existing_secure_props
                # Check if credential is a non-empty string
                if credential:
                    # Get the username and password from the credential dictionary
                    username = credential.get("profiles.base.properties.user")
                    password = credential.get("profiles.base.properties.password")
                    
                    # Combine the username and password as "username:password"
                    username_password = f"{username}:{password}"
                    
                    # Encode the combined string as base64
                    encoded_credential = base64.b64encode(username_password.encode()).decode()
                    if len(encoded_credential) > constants["WIN32_CRED_MAX_STRING_LENGTH"]:
                        # Split the encoded credential string into chunks of maximum length
                        keyring.delete_password(service_name, constants["ZoweAccountName"])
                        chunk_size = constants["WIN32_CRED_MAX_STRING_LENGTH"]
                        chunks = [encoded_credential[i : i + chunk_size] for i in range(0, len(encoded_credential), chunk_size)]
                        # Append NUL byte to the last chunk
                        chunks[-1] += "\0"
                        # Set the individual chunks as separate keyring entries
                        for index, chunk in enumerate(chunks, start=1):
                            field_name = f"{constants['ZoweAccountName']}-{index}"
                            keyring.set_password(service_name, field_name, chunk)
                else:
                     # Credential length is within the maximum limit, set it as a single keyring entry
                        keyring.set_password(service_name, constants["ZoweAccountName"], "")
            else:
                keyring.set_password(
                    service_name, constants["ZoweAccountName"], 
                    credential)

        except KeyError as exc:
            error_msg = str(exc)
            warnings.warn(
                f"No credentials found for loaded config file '{self.filepath}'"
                f" with error '{error_msg}'",
                SecurePropsNotFoundWarning,
            )
