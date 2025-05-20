import pytest


@pytest.fixture
def isolated_test_env(tmp_path):
    project_dir = tmp_path / "project"
    global_dir = tmp_path / "global"
    project_dir.mkdir()
    global_dir.mkdir()

    return {
        "project_dir": project_dir,
        "global_dir": global_dir
    }
