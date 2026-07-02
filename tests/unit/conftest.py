"""Pytest configuration for unit tests."""

import logging

import pytest

from zowe.core_for_zowe_sdk.logger import Log


@pytest.fixture(autouse=True)
def suppress_sdk_console_logging():
    """Silence SDK console log output before each unit test.

    test_logger.py exercises Log state (open/close/level) and leaves
    console_handler.level at ERROR; this fixture restores CRITICAL before
    every test so noise never leaks into the output.
    """
    Log.set_console_output_level(logging.CRITICAL)
