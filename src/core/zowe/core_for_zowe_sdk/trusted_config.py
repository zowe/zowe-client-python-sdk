import json
import os
import stat
import sys
from enum import StrEnum
from pathlib import Path


class ZoweConfigEnvVar(StrEnum):
    ALLOW_UNTRUSTED_DIRS = "ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS"
    ALLOW_WORLD_WRITABLE = "ZOWE_CONFIG_ALLOW_WORLD_WRITABLE"


class TrustedConfigManager:
    __settings_key = "trustedConfigDirs"

    @property
    def cli_home_dir(self) -> str:
        return os.environ.get("ZOWE_CLI_HOME", os.path.join(os.path.expanduser("~"), ".zowe"))

    @property
    def local_storage_path(self) -> str:
        return os.path.join(self.cli_home_dir, "settings", "imperative.json")

    def __has_env(self, env_var: ZoweConfigEnvVar) -> bool:
        value = os.environ.get(env_var)
        return value is not None and (value == "1" or value.lower() == "true")

    def is_world_writable(self, file_path):
        if sys.platform == "win32" or self.__has_env(ZoweConfigEnvVar.ALLOW_WORLD_WRITABLE):
            return False
        return bool(os.stat(file_path).st_mode & stat.S_IWOTH)

    def is_dir_trusted(self, dir_path, prompt_fn=None) -> bool:
        if os.environ.get("CI") is not None or self.__has_env(ZoweConfigEnvVar.ALLOW_UNTRUSTED_DIRS):
            return True
        if dir_path == os.getcwd():
            return True
        if not Path(dir_path).is_relative_to(Path.home()):
            return True
        if dir_path in self.list_trusted():
            return True
        return prompt_fn(dir_path) if prompt_fn else False

    def __load_settings_json(self):
        settings_json_path = self.local_storage_path
        settings_json = {}
        if os.path.isfile(settings_json_path):
            with open(settings_json_path, "r", encoding="utf-8") as fp:
                settings_json = json.load(fp)
        if self.__settings_key not in settings_json:
            settings_json[self.__settings_key] = []
        return settings_json

    def list_trusted(self) -> set[str]:
        settings_json = self.__load_settings_json()
        return set(settings_json[self.__settings_key])

    def add_trusted(self, dir_path):
        settings_json = self.__load_settings_json()
        if dir_path not in settings_json[self.__settings_key]:
            settings_json[self.__settings_key].append(dir_path)
            with open(self.local_storage_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(settings_json, indent=2) + "\n")

    def remove_trusted(self, dir_path):
        settings_json = self.__load_settings_json()
        if dir_path in settings_json[self.__settings_key]:
            settings_json[self.__settings_key].remove(dir_path)
            with open(self.local_storage_path, "w", encoding="utf-8") as fp:
                fp.write(json.dumps(settings_json, indent=2) + "\n")
