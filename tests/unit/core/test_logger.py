"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import logging
import os
from unittest import mock

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk.logger import Log


class test_logger_setLoggerLevel(TestCase):

    def test_logger_setLoggerLevel(self):
        """Test setLoggerLevel"""
        test_logger = Log.registerLogger("test")
        test_value = logging.DEBUG
        Log.setAllLoggerLevel(test_value)
        self.assertEqual(test_logger.level, test_value)

    def test_single_logger(self):
        test_logger = Log.registerLogger("test")
        # logger.Log.close(test_logger.name)
        with self.assertLogs(test_logger.name, level="WARNING") as log:
            Log.close(test_logger)
            test_logger.error("hi")
            self.assertEqual(0, len(log.output))

            Log.open(test_logger)
            test_logger.error("hi")
            self.assertIn("hi", log.output[0])

    def test_all_loggers(self):
        test_1 = Log.registerLogger("1")
        test_2 = Log.registerLogger("2")
        with self.assertLogs(test_1.name, level="WARNING") as log1, self.assertLogs(
            test_2.name, level="WARNING"
        ) as log2:
            Log.closeAll()

            test_1.error("hi")
            self.assertEqual(0, len(log1.output))

            test_2.error("hi")
            self.assertEqual(0, len(log2.output))

            Log.openAll()

            test_1.error("hi")
            self.assertIn("hi", log1.output[0])

            test_2.info("hi")
            self.assertEqual(0, len(log2.output))

            test_2.error("hi")
            self.assertIn("hi", log2.output[0])

    def test_console_handler(self):
        Log.close_console_output()
        test = Log.registerLogger("test")
        self.assertEqual(test.handlers[0], Log.file_handler)

        Log.open_console_output()
        self.assertEqual(test.handlers[1], Log.console_handler)

        Log.set_console_output_level(logging.ERROR)
        self.assertEqual(logging.ERROR, test.handlers[1].level)

    def test_file_handler(self):
        Log.close_file_output()
        test = Log.registerLogger("test")
        self.assertEqual(test.handlers[0], Log.console_handler)

        Log.open_file_output()
        self.assertEqual(test.handlers[1], Log.file_handler)

        Log.set_file_output_level(logging.ERROR)
        self.assertEqual(logging.ERROR, test.handlers[1].level)
