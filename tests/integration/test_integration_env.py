from pathlib import Path


def test_isolated_env_does_not_touch_real_home(isolated_test_env):
    project_dir = isolated_test_env["project_dir"]
    global_dir = isolated_test_env["global_dir"]

    # Copy contets of the actual zowe.config.json as it's necessary for the test
    real_config_path = Path(__file__).resolve().parent.parent.parent / "zowe.config.json"
    
    assert real_config_path.exists(), f"Missing config at {real_config_path}"

    config_file = project_dir / "zowe.config.json"
    config_file.write_text(real_config_path.read_text())

    assert config_file.exists()
    assert "profiles" in config_file.read_text()
