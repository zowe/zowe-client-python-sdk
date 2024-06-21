"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import logging

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk import (
    ProfileManager,
    logger
)

class test_logger_setLoggerLevel(TestCase):
    
    def test_logger_setLoggerLevel(self):
        """Test setLoggerLevel"""
        profile = ProfileManager()
        test_logger = logging.getLogger("zowe.core_for_zowe_sdk.profile_manager")
        test_value = logging.DEBUG
        logger.Log.setLoggerLevel(test_value)
        self.assertEqual(test_logger.level, test_value)