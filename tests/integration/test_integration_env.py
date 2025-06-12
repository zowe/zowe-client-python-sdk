"""Test isolated environment setup for integration tests."""

def test_isolated_env_does_not_touch_real_home(isolated_test_env):
    config_path = isolated_test_env["config_path"]
    config_file = isolated_test_env["config_file"]

    assert config_path.exists(), f"Missing config at {config_path}"
    assert config_file.exists()
    assert "profiles" in config_file.read_text()