"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import json
import os
import stat
import sys
from enum import StrEnum
from pathlib import Path


class ZoweConfigEnvVar(StrEnum):
    """Environment variables that relax config file security checks."""

    ALLOW_UNTRUSTED_DIRS = "ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS"
    ALLOW_WORLD_WRITABLE = "ZOWE_CONFIG_ALLOW_WORLD_WRITABLE"


class TrustedConfigManager:
    """
    Manage the list of directories whose Zowe config files are trusted.

    Trusted directories are persisted under the "trustedConfigDirs" key in
    `<ZOWE_CLI_HOME>/settings/imperative.json`, which is shared with Zowe CLI.
    """

    __settings_key = "trustedConfigDirs"

    @property
    def cli_home_dir(self) -> str:
        """Return the Zowe CLI home directory (ZOWE_CLI_HOME, or ~/.zowe if unset)."""
        return os.environ.get("ZOWE_CLI_HOME", os.path.join(os.path.expanduser("~"), ".zowe"))

    @property
    def local_storage_path(self) -> str:
        """Return the path of the settings file that stores trusted directories."""
        return os.path.join(self.cli_home_dir, "settings", "imperative.json")

    def __has_env(self, env_var: ZoweConfigEnvVar) -> bool:
        """Return True if the environment variable is set to "1" or "true" (case-insensitive)."""
        value = os.environ.get(env_var)
        return value is not None and (value == "1" or value.lower() == "true")

    def is_world_writable(self, file_path) -> bool:
        """
        Check whether a file is writable by all users.

        Always returns False on Windows or when ZOWE_CONFIG_ALLOW_WORLD_WRITABLE is enabled.

        Parameters
        ----------
        file_path: str
            Path of the file to check

        Returns
        -------
        bool
            True if the file has the world-writable permission bit set
        """
        if sys.platform == "win32" or self.__has_env(ZoweConfigEnvVar.ALLOW_WORLD_WRITABLE):
            return False
        return bool(os.stat(file_path).st_mode & stat.S_IWOTH)

    def is_dir_trusted(self, dir_path, prompt_fn=None) -> bool:
        """
        Determine whether config files in a directory can be trusted.

        A directory is trusted if any of the following apply:
            - running in CI, or ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS is enabled
            - it is the current working directory
            - it is outside the user's home directory
            - it was previously added to the trusted list

        Otherwise, `prompt_fn` is called to ask the user; with no `prompt_fn` the directory is untrusted.

        Parameters
        ----------
        dir_path: str
            Directory containing the config file
        prompt_fn: Optional[Callable[[str], bool]]
            Function that receives `dir_path` and returns True if the user trusts it

        Returns
        -------
        bool
            True if the directory is trusted
        """
        if os.environ.get("CI") is not None or self.__has_env(ZoweConfigEnvVar.ALLOW_UNTRUSTED_DIRS):
            return True
        if dir_path == os.getcwd():
            return True
        if not Path(dir_path).is_relative_to(Path.home()):
            return True
        if dir_path in self.list_trusted():
            return True
        return prompt_fn(dir_path) if prompt_fn else False

    def __load_settings_json(self) -> dict:
        """Load the settings file, ensuring the trusted directories key exists."""
        settings_json_path = self.local_storage_path
        settings_json = {}
        if os.path.isfile(settings_json_path):
            with open(settings_json_path, "r", encoding="utf-8") as fp:
                settings_json = json.load(fp)
        if self.__settings_key not in settings_json:
            settings_json[self.__settings_key] = []
        return settings_json

    def list_trusted(self) -> set[str]:
        """Return the set of directories currently marked as trusted."""
        settings_json = self.__load_settings_json()
        return set(settings_json[self.__settings_key])

    def add_trusted(self, dir_path) -> None:
        """
        Add a directory to the trusted list and save it to the settings file.

        Parameters
        ----------
        dir_path: str
            Directory to trust
        """
        settings_json = self.__load_settings_json()
        if dir_path not in settings_json[self.__settings_key]:
            settings_json[self.__settings_key].append(dir_path)
            with open(self.local_storage_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(settings_json, indent=2) + "\n")

    def remove_trusted(self, dir_path) -> None:
        """
        Remove a directory from the trusted list and save the settings file.

        Parameters
        ----------
        dir_path: str
            Directory to stop trusting
        """
        settings_json = self.__load_settings_json()
        if dir_path in settings_json[self.__settings_key]:
            settings_json[self.__settings_key].remove(dir_path)
            with open(self.local_storage_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(settings_json, indent=2) + "\n")
