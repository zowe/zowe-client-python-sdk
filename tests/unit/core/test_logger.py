"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import logging
import os
import stat
import sys
import unittest
from unittest import mock

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk.logger import Log, restrict_to_owner


class test_logger_setLoggerLevel(TestCase):

    def test_logger_setLoggerLevel(self):
        """Test setLoggerLevel"""
        test_logger = Log.register_logger("test")
        test_value = logging.DEBUG
        Log.set_all_logger_level(test_value)
        self.assertEqual(test_logger.level, test_value)

    def test_single_logger(self):
        test_logger = Log.register_logger("test")
        # logger.Log.close(test_logger.name)
        with self.assertLogs(test_logger.name, level="WARNING") as log:
            Log.close(test_logger)
            test_logger.error("hi")
            self.assertEqual(0, len(log.output))

            Log.open(test_logger)
            test_logger.error("hi")
            self.assertIn("hi", log.output[0])

    def test_all_loggers(self):
        test_1 = Log.register_logger("1")
        test_2 = Log.register_logger("2")
        with self.assertLogs(test_1.name, level="WARNING") as log1, self.assertLogs(
            test_2.name, level="WARNING"
        ) as log2:
            Log.close_all()

            test_1.error("hi")
            self.assertEqual(0, len(log1.output))

            test_2.error("hi")
            self.assertEqual(0, len(log2.output))

            Log.open_all()

            test_1.error("hi")
            self.assertIn("hi", log1.output[0])

            test_2.info("hi")
            self.assertEqual(0, len(log2.output))

            test_2.error("hi")
            self.assertIn("hi", log2.output[0])

    def test_console_handler(self):
        Log.close_console_output()
        test = Log.register_logger("test")
        self.assertIn(Log.file_handler, test.handlers)
        self.assertNotIn(Log.console_handler, test.handlers)

        Log.open_console_output()
        self.assertIn(Log.console_handler, test.handlers)

        Log.set_console_output_level(logging.ERROR)
        self.assertEqual(logging.ERROR, Log.console_handler.level)

    def test_file_handler(self):
        Log.close_file_output()
        test = Log.register_logger("test")
        self.assertIn(Log.console_handler, test.handlers)
        self.assertNotIn(Log.file_handler, test.handlers)

        Log.open_file_output()
        self.assertIn(Log.file_handler, test.handlers)

        Log.set_file_output_level(logging.ERROR)
        self.assertEqual(logging.ERROR, Log.file_handler.level)

    @unittest.skipIf(
        sys.platform == "win32",
        "os.stat().st_mode permission bits don't reflect NTFS ACLs; owner-only "
        "restriction on Windows is enforced via icacls instead, not POSIX mode bits.",
    )
    def test_log_directory_and_file_are_owner_only(self):
        """The log directory and file should not be readable/writable by group or others, since log
        content may include request/response details."""
        dir_mode = stat.S_IMODE(os.stat(Log.dirname).st_mode)
        self.assertEqual(dir_mode, 0o700)

        log_file = os.path.join(Log.dirname, "python_sdk_logs.log")
        file_mode = stat.S_IMODE(os.stat(log_file).st_mode)
        self.assertEqual(file_mode, 0o600)

    @mock.patch("zowe.core_for_zowe_sdk.logger.subprocess.run")
    @mock.patch("zowe.core_for_zowe_sdk.logger.getpass.getuser", return_value="testuser")
    @mock.patch("zowe.core_for_zowe_sdk.logger.sys.platform", "win32")
    def test_restrict_to_owner_uses_icacls_on_windows(self, mock_getuser, mock_run):
        """On Windows, restrict_to_owner should rewrite the ACL via icacls instead of chmod,
        since os.chmod() there only toggles the read-only attribute."""
        restrict_to_owner("C:\\fake\\path", 0o700)

        mock_run.assert_called_once_with(
            ["icacls", "C:\\fake\\path", "/inheritance:r", "/grant:r", "testuser:F"],
            check=False,
            capture_output=True,
        )

    @mock.patch("zowe.core_for_zowe_sdk.logger.os.chmod")
    @mock.patch("zowe.core_for_zowe_sdk.logger.subprocess.run")
    @mock.patch("zowe.core_for_zowe_sdk.logger.sys.platform", "linux")
    def test_restrict_to_owner_uses_chmod_on_posix(self, mock_run, mock_chmod):
        """On non-Windows platforms, restrict_to_owner should use chmod and never shell out."""
        restrict_to_owner("/fake/path", 0o700)

        mock_chmod.assert_called_once_with("/fake/path", 0o700)
        mock_run.assert_not_called()
