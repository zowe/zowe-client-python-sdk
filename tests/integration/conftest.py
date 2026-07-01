"""Pytest configuration for integration tests."""

import logging

import pytest

from zowe.core_for_zowe_sdk.logger import Log


@pytest.fixture(autouse=True)
def suppress_sdk_console_logging():
    """Silence SDK console log output during integration tests.

    Keeps test output clean; on failure pytest's own capture surfaces
    relevant context without the logger noise cluttering the dots.
    """
    Log.set_console_output_level(logging.CRITICAL)
