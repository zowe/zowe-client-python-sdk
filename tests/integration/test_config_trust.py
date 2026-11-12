"""Integration tests for trusted config directory handling.

These tests use real temporary directories and files, but redirect HOME and ZOWE_CLI_HOME
to temporary locations so the real Zowe CLI home directory is never read or modified.
No z/OSMF connection is required.
"""

import json
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from zowe.core_for_zowe_sdk import ConfigFile, config_file
from zowe.core_for_zowe_sdk.trusted_config import TrustedConfigManager

TEAM_CONFIG = {
    "profiles": {"base": {"type": "base", "properties": {"host": "zowe.test.cloud", "rejectUnauthorized": False}}},
    "defaults": {"base": "base"},
}


@pytest.fixture(scope="module", autouse=True)
def isolated_home():
    """Redirect HOME and ZOWE_CLI_HOME to a temp dir once for the module, and verify nothing points at the real home.

    This runs before any test. If the SDK would still resolve its settings path outside the
    temp dir, every test errors out before touching the user's real Zowe CLI home.
    """
    root = os.path.realpath(tempfile.mkdtemp(prefix="zowe_trust_test_"))
    home = os.path.join(root, "home")
    cli_home = os.path.join(home, ".zowe")
    os.makedirs(cli_home)

    env = {"HOME": home, "USERPROFILE": home, "ZOWE_CLI_HOME": cli_home}
    try:
        with mock.patch.dict(os.environ, env):
            for var in ("CI", "ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS", "ZOWE_CONFIG_ALLOW_WORLD_WRITABLE"):
                os.environ.pop(var, None)

            settings_path = os.path.realpath(TrustedConfigManager().local_storage_path)
            for path in (settings_path, os.path.realpath(os.path.expanduser("~")), os.path.realpath(Path.home())):
                assert os.path.commonpath([path, root]) == root, f"{path} is outside the temp dir {root}"

            yield {"root": root, "home": home, "cli_home": cli_home}
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def trust_env(isolated_home):
    """Create a fresh project dir (outside home, so untrusted) with a team config and an empty CLI home per test."""
    root, home, cli_home = isolated_home["root"], isolated_home["home"], isolated_home["cli_home"]
    project = os.path.join(root, "project")
    elsewhere = os.path.join(root, "elsewhere")
    shutil.rmtree(cli_home, ignore_errors=True)
    shutil.rmtree(project, ignore_errors=True)
    for d in (cli_home, project, elsewhere):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(project, "zowe.config.json"), "w", encoding="utf-8") as fp:
        json.dump(TEAM_CONFIG, fp)

    # autodiscovery starts from CURRENT_DIR; trust also special-cases os.getcwd(), so use another cwd
    with mock.patch.object(config_file, "CURRENT_DIR", project), mock.patch("os.getcwd", return_value=elsewhere):
        yield {"root": root, "home": home, "cli_home": cli_home, "project": project}


def _autodiscovered_dir(trust_prompt_fn=None):
    """Autodiscover the team config and return its directory, or None if it was skipped."""
    cfg = ConfigFile(type="team_config", name="zowe")
    try:
        cfg.autodiscover_config_dir(trust_prompt_fn)
    except FileNotFoundError:
        return None
    return cfg.location


def test_untrusted_config_is_not_loaded(trust_env):
    """A config outside the home directory that is not trusted is skipped."""
    assert _autodiscovered_dir() is None


def test_config_inside_home_is_trusted(trust_env):
    """A config inside the user's home directory is trusted automatically."""
    home_project = os.path.join(trust_env["home"], "project")
    os.makedirs(home_project)
    with open(os.path.join(home_project, "zowe.config.json"), "w", encoding="utf-8") as fp:
        json.dump(TEAM_CONFIG, fp)

    with mock.patch.object(config_file, "CURRENT_DIR", home_project):
        assert _autodiscovered_dir() == home_project


def test_config_loaded_after_trusting_directory(trust_env):
    """A config is loaded once its directory is listed in trustedConfigDirs."""
    settings_dir = os.path.join(trust_env["cli_home"], "settings")
    os.makedirs(settings_dir)
    with open(os.path.join(settings_dir, "imperative.json"), "w", encoding="utf-8") as fp:
        json.dump({"trustedConfigDirs": [trust_env["project"]]}, fp)

    assert _autodiscovered_dir() == trust_env["project"]


def test_config_loaded_when_prompt_accepts(trust_env):
    """A config is loaded when trust_prompt_fn accepts the directory."""
    prompt_fn = mock.Mock(return_value=True)

    assert _autodiscovered_dir(trust_prompt_fn=prompt_fn) == trust_env["project"]
    prompt_fn.assert_called_with(trust_env["project"])


def test_config_skipped_when_prompt_rejects(trust_env):
    """A config is skipped when trust_prompt_fn rejects the directory."""
    assert _autodiscovered_dir(trust_prompt_fn=lambda _: False) is None


def test_config_loaded_with_untrusted_env_override(trust_env):
    """ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS=1 loads configs from any directory."""
    with mock.patch.dict(os.environ, {"ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS": "1"}):
        assert _autodiscovered_dir() == trust_env["project"]


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions only")
def test_world_writable_config_dir_is_skipped(trust_env):
    """A world-writable directory is skipped even when untrusted dirs are allowed, unless overridden."""
    os.chmod(trust_env["project"], os.stat(trust_env["project"]).st_mode | stat.S_IWOTH)

    with mock.patch.dict(os.environ, {"ZOWE_CONFIG_ALLOW_UNTRUSTED_DIRS": "1"}):
        assert _autodiscovered_dir() is None
        with mock.patch.dict(os.environ, {"ZOWE_CONFIG_ALLOW_WORLD_WRITABLE": "1"}):
            assert _autodiscovered_dir() == trust_env["project"]
