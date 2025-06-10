import unittest
from pathlib import Path
from unittest import TestCase

import pytest


@pytest.fixture
def isolated_test_env(tmp_path):
    config_path = Path(__file__).resolve().parent.parent.parent / "zowe.config.json"

    config_file = tmp_path / "zowe.config.json"
    config_file.write_text(config_path.read_text())

    return {
        "config_path": config_path, 
        "config_file": config_file
        }

class TestIsolatedEnv(unittest.TestCase):
    """Base class for isolated test environments."""
    @pytest.fixture(autouse=True)
    def _setup_test_env(self, isolated_test_env):
        self.isolated_test_env = isolated_test_env