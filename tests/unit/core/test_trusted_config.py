"""Unit tests for the Zowe Python SDK Core package."""

import json
import os
import sys
import unittest
from unittest import mock

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk.trusted_config import TrustedConfigManager, ZoweConfigEnvVar


class TestTrustedConfigManager(TestCase):
    """TrustedConfigManager class unit tests."""

    def setUp(self):
        """Setup fixtures for TrustedConfigManager class."""
        self.setUpPyfakefs()
        self.cli_home = os.path.join(os.path.expanduser("~"), ".zowe")
        self.settings_path = os.path.join(self.cli_home, "settings", "imperative.json")
        self.manager = TrustedConfigManager()
        self.outside_dir = os.path.abspath(os.path.join(os.sep, "opt", "shared"))
        # absolute on every platform (a bare "/a" has no drive letter on Windows)
        self.dir_a, self.dir_b, self.dir_missing, self.real_dir, self.link_dir = (
            os.path.abspath(os.path.join(os.sep, name)) for name in ("a", "b", "missing", "real", "link")
        )

        # start from a clean environment so results don't depend on the host
        # (don't clear the whole environment: Windows needs USERPROFILE to expand "~")
        env_patcher = mock.patch.dict(os.environ)
        env_patcher.start()
        self.addCleanup(env_patcher.stop)
        for var in ("CI", "ZOWE_CLI_HOME", *list(ZoweConfigEnvVar)):
            os.environ.pop(var, None)

    def _write_settings(self, content):
        """Write the given dict to the fake settings file."""
        self.fs.create_file(self.settings_path, contents=json.dumps(content))

    def test_cli_home_dir_default(self):
        """Test that cli_home_dir defaults to ~/.zowe"""
        self.assertEqual(self.manager.cli_home_dir, self.cli_home)

    def test_cli_home_dir_from_env(self):
        """Test that cli_home_dir honors ZOWE_CLI_HOME"""
        custom_home = os.path.abspath(os.path.join(os.sep, "custom", "home"))
        with mock.patch.dict(os.environ, {"ZOWE_CLI_HOME": custom_home}):
            self.assertEqual(self.manager.cli_home_dir, custom_home)
            self.assertEqual(self.manager.local_storage_path, os.path.join(custom_home, "settings", "imperative.json"))

    def test_local_storage_path(self):
        """Test that local_storage_path points to the imperative.json settings file"""
        self.assertEqual(self.manager.local_storage_path, self.settings_path)

    @unittest.skipIf(sys.platform == "win32", "POSIX permissions only")
    def test_is_world_writable_true(self):
        """Test that is_world_writable detects the world-writable permission bit"""
        self.fs.create_dir("/data")
        os.chmod("/data", 0o777)
        self.assertTrue(self.manager.is_world_writable("/data"))

    def test_is_world_writable_false(self):
        """Test that is_world_writable is False when other users cannot write"""
        self.fs.create_dir("/data")
        os.chmod("/data", 0o755)
        self.assertFalse(self.manager.is_world_writable("/data"))

    @unittest.skipIf(sys.platform == "win32", "POSIX permissions only")
    def test_is_world_writable_bypassed_by_env(self):
        """Test that ZOWE_CONFIG_ALLOW_WORLD_WRITABLE disables the world-writable check"""
        self.fs.create_dir("/data")
        os.chmod("/data", 0o777)
        for value in ("1", "true", "TRUE"):
            with mock.patch.dict(os.environ, {ZoweConfigEnvVar.ALLOW_WORLD_WRITABLE: value}):
                self.assertFalse(self.manager.is_world_writable("/data"))

    @unittest.skipIf(sys.platform == "win32", "POSIX permissions only")
    def test_is_world_writable_env_ignores_other_values(self):
        """Test that env var values other than 1/true do not bypass the check"""
        self.fs.create_dir("/data")
        os.chmod("/data", 0o777)
        with mock.patch.dict(os.environ, {ZoweConfigEnvVar.ALLOW_WORLD_WRITABLE: "0"}):
            self.assertTrue(self.manager.is_world_writable("/data"))

    def test_is_world_writable_windows(self):
        """Test that is_world_writable is always False on Windows"""
        self.fs.create_dir("/data")
        os.chmod("/data", 0o777)
        with mock.patch("sys.platform", "win32"):
            self.assertFalse(self.manager.is_world_writable("/data"))

    def test_is_dir_trusted_in_ci(self):
        """Test that all directories are trusted when the CI environment variable is set"""
        with mock.patch.dict(os.environ, {"CI": "true"}):
            self.assertTrue(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_in_ci_empty_string(self):
        """Test that CI set to an empty string does not trust all directories"""
        with mock.patch.dict(os.environ, {"CI": ""}):
            self.assertFalse(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_bypassed_by_env(self):
        """Test that ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS trusts all directories"""
        with mock.patch.dict(os.environ, {ZoweConfigEnvVar.ALLOW_UNTRUSTED_DIRS: "1"}):
            self.assertTrue(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_current_directory(self):
        """Test that the current working directory is trusted"""
        self.fs.create_dir(self.outside_dir)
        os.chdir(self.outside_dir)
        self.assertTrue(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_inside_home(self):
        """Test that directories inside the home directory are trusted"""
        self.assertTrue(self.manager.is_dir_trusted(os.path.join(os.path.expanduser("~"), "project")))

    def test_is_dir_trusted_home_symlink_to_outside(self):
        """Test that a symlink inside home pointing outside it is not trusted"""
        self.fs.create_dir(self.outside_dir)
        link = os.path.join(os.path.expanduser("~"), "project")
        self.fs.create_symlink(link, self.outside_dir)
        self.assertFalse(self.manager.is_dir_trusted(link))

    def test_is_dir_trusted_in_trusted_list(self):
        """Test that a directory in the trusted list is trusted"""
        self._write_settings({"trustedConfigDirs": [self.outside_dir]})
        self.assertTrue(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_untrusted(self):
        """Test that an unknown directory outside home is untrusted without a prompt"""
        self.assertFalse(self.manager.is_dir_trusted(self.outside_dir))

    def test_is_dir_trusted_prompt_fn(self):
        """Test that prompt_fn decides trust for an unknown directory and receives its path"""
        accept = mock.Mock(return_value=True)
        reject = mock.Mock(return_value=False)

        self.assertTrue(self.manager.is_dir_trusted(self.outside_dir, accept))
        self.assertFalse(self.manager.is_dir_trusted(self.outside_dir, reject))
        accept.assert_called_once_with(self.outside_dir)
        reject.assert_called_once_with(self.outside_dir)

    def test_is_dir_trusted_prompt_fn_not_called_when_trusted(self):
        """Test that prompt_fn is not called for a directory that is already trusted"""
        prompt_fn = mock.Mock()
        self.assertTrue(self.manager.is_dir_trusted(os.path.join(os.path.expanduser("~"), "project"), prompt_fn))
        prompt_fn.assert_not_called()

    def test_list_trusted_no_settings_file(self):
        """Test that list_trusted returns an empty set when the settings file doesn't exist"""
        self.assertEqual(self.manager.list_trusted(), set())

    def test_list_trusted_missing_key(self):
        """Test that list_trusted returns an empty set when the key is absent from the settings file"""
        self._write_settings({"other": "value"})
        self.assertEqual(self.manager.list_trusted(), set())

    def test_list_trusted(self):
        """Test that list_trusted returns the directories saved in the settings file"""
        self._write_settings({"trustedConfigDirs": [self.dir_a, self.dir_b]})
        self.assertEqual(self.manager.list_trusted(), {self.dir_a, self.dir_b})

    def test_list_trusted_skips_relative_path_with_warning(self):
        """Test that list_trusted drops relative paths and logs a warning"""
        self._write_settings({"trustedConfigDirs": [self.dir_a, "relative/dir"]})
        with self.assertLogs(level="WARNING") as logs:
            self.assertEqual(self.manager.list_trusted(), {self.dir_a})
        self.assertEqual(len(logs.records), 1)
        self.assertIn("relative/dir", logs.output[0])
        self.assertIn("cannot be relative, contain '..', or contain a symbolic link", logs.output[0])

    def test_list_trusted_skips_symlink_with_warning(self):
        """Test that list_trusted drops symbolic links and logs a warning"""
        self.fs.create_dir(self.real_dir)
        self.fs.create_symlink(self.link_dir, self.real_dir)
        self._write_settings({"trustedConfigDirs": [self.real_dir, self.link_dir]})
        with self.assertLogs(level="WARNING") as logs:
            self.assertEqual(self.manager.list_trusted(), {self.real_dir})
        self.assertIn(self.link_dir, logs.output[0])

    def test_list_trusted_valid_paths_no_warning(self):
        """Test that list_trusted logs nothing when all paths are valid"""
        self._write_settings({"trustedConfigDirs": [self.dir_a]})
        with self.assertNoLogs(level="WARNING"):
            self.manager.list_trusted()

    def test_add_trusted_relative_path_raises(self):
        """Test that add_trusted rejects relative paths without writing the settings file"""
        with self.assertRaises(ValueError):
            self.manager.add_trusted("relative/dir")
        self.assertFalse(os.path.exists(self.settings_path))

    def test_add_trusted_non_normalized_path_raises(self):
        """Test that add_trusted rejects paths containing ".." without writing the settings file"""
        with self.assertRaises(ValueError):
            self.manager.add_trusted(os.path.join(self.dir_a, "..", "b"))
        self.assertFalse(os.path.exists(self.settings_path))

    def test_list_trusted_skips_non_normalized_path_with_warning(self):
        """Test that list_trusted drops paths containing ".." and logs a warning"""
        bad = os.path.join(self.dir_a, "..", "b")
        self._write_settings({"trustedConfigDirs": [self.dir_a, bad]})
        with self.assertLogs(level="WARNING"):
            self.assertEqual(self.manager.list_trusted(), {self.dir_a})

    def test_add_trusted_symlink_raises(self):
        """Test that add_trusted rejects symbolic links without writing the settings file"""
        self.fs.create_dir(self.real_dir)
        self.fs.create_symlink(self.link_dir, self.real_dir)
        with self.assertRaises(ValueError):
            self.manager.add_trusted(self.link_dir)
        self.assertFalse(os.path.exists(self.settings_path))

    def test_list_trusted_skips_path_under_symlinked_parent(self):
        """Test that list_trusted drops paths whose parent directory is a symbolic link"""
        child = os.path.join(self.link_dir, "child")
        self.fs.create_dir(os.path.join(self.real_dir, "child"))
        self.fs.create_symlink(self.link_dir, self.real_dir)
        self._write_settings({"trustedConfigDirs": [self.dir_a, child]})
        with self.assertLogs(level="WARNING") as logs:
            self.assertEqual(self.manager.list_trusted(), {self.dir_a})
        self.assertIn(child, logs.output[0])

    def test_add_trusted_symlinked_parent_raises(self):
        """Test that add_trusted rejects paths under a symlinked parent without writing the settings file"""
        self.fs.create_dir(os.path.join(self.real_dir, "child"))
        self.fs.create_symlink(self.link_dir, self.real_dir)
        with self.assertRaises(ValueError):
            self.manager.add_trusted(os.path.join(self.link_dir, "child"))
        self.assertFalse(os.path.exists(self.settings_path))

    def test_add_trusted(self):
        """Test that add_trusted persists a directory without duplicating it"""
        self.manager.add_trusted(self.dir_a)
        self.manager.add_trusted(self.dir_a)
        with open(self.settings_path, encoding="utf-8") as fp:
            self.assertEqual(json.load(fp), {"trustedConfigDirs": [self.dir_a]})

    def test_add_trusted_creates_settings_dir(self):
        """Test that add_trusted creates the settings directory if it doesn't exist"""
        self.assertFalse(os.path.exists(os.path.dirname(self.settings_path)))
        self.manager.add_trusted(self.dir_a)
        self.assertEqual(self.manager.list_trusted(), {self.dir_a})

    def test_add_trusted_preserves_other_settings(self):
        """Test that add_trusted keeps unrelated settings in the file"""
        self._write_settings({"other": "value", "trustedConfigDirs": [self.dir_a]})
        self.manager.add_trusted(self.dir_b)
        with open(self.settings_path, encoding="utf-8") as fp:
            self.assertEqual(json.load(fp), {"other": "value", "trustedConfigDirs": [self.dir_a, self.dir_b]})

    def test_remove_trusted(self):
        """Test that remove_trusted deletes a directory from the settings file"""
        self._write_settings({"trustedConfigDirs": [self.dir_a, self.dir_b]})
        self.manager.remove_trusted(self.dir_a)
        self.assertEqual(self.manager.list_trusted(), {self.dir_b})

    def test_remove_trusted_not_in_list(self):
        """Test that remove_trusted leaves the file unchanged for an unknown directory"""
        self._write_settings({"trustedConfigDirs": [self.dir_a]})
        self.manager.remove_trusted(self.dir_missing)
        self.assertEqual(self.manager.list_trusted(), {self.dir_a})
