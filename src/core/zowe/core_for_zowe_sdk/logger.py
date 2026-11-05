"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import logging
import os
import subprocess
import sys
import getpass
from typing import Any


def restrict_to_owner(path: str, mode: int) -> None:
    """
    Restrict a file or directory to owner-only access, across platforms.

    Parameters
    ----------
    path: str
        The file or directory to restrict
    mode: int
        The POSIX permission bits to apply on non-Windows platforms (e.g. 0o700 for a
        directory, 0o600 for a file)
    """
    if sys.platform == "win32":
        username = getpass.getuser()
        if username:
            subprocess.run(
                ["icacls", path, "/inheritance:r", "/grant:r", "{}:F".format(username)],
                check=False,
                capture_output=True,
            )
    else:
        os.chmod(path, mode)


class Log:
    """
    Class used to represent a logger.

    Attributes
    ----------
    dirname: str
        Path where the log file is saved
    file_handler: logging.FileHandler
        Shared FileHandler object for managing log file output
    console_handler: logging.StreamHandler
        Shared StreamHandler object for managing log console output
    file_output: bool
        Specifies whether log messages would be saved to a file. True by default.
    console_output: bool
        Specifies whether log messages would be printed out on console. True by default.
    loggers: set[logging.Logger]
        The set of all loggers
    """

    dirname: str = os.path.join(os.path.expanduser("~"), ".zowe/logs")
    os.makedirs(dirname, mode=0o700, exist_ok=True)
    restrict_to_owner(dirname, 0o700)
    __log_filename: str = os.path.join(dirname, "python_sdk_logs.log")

    __log_fd = os.open(__log_filename, os.O_CREAT | os.O_APPEND, 0o600)
    os.close(__log_fd)
    restrict_to_owner(__log_filename, 0o600)
    file_handler: logging.FileHandler = logging.FileHandler(__log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", "%m/%d/%Y %I:%M:%S %p")
    )
    console_handler: logging.StreamHandler = logging.StreamHandler()  # pylint: disable=unsubscriptable-object

    file_output: bool = True
    console_output: bool = True

    loggers: set[logging.Logger] = set()

    @staticmethod
    def register_logger(name: str) -> logging.Logger:
        """
        Create and register a logger.

        Parameters
        ----------
        name: str
            The name for the logger.

        Returns
        -------
        logging.Logger
            A Logger object named after the file where it is created.
        """
        logger = logging.getLogger(name)
        if Log.console_output:
            logger.addHandler(Log.console_handler)
        if Log.file_output:
            logger.addHandler(Log.file_handler)
        logger.propagate = False
        Log.loggers.add(logger)
        return logger

    @staticmethod
    def set_all_logger_level(level: int) -> None:
        """
        Set display level for all loggers.

        Parameters
        ----------
        level: int
            The intended logger level
        """
        for logger in Log.loggers:
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)

    @staticmethod
    def close(logger: logging.Logger) -> None:
        """
        Disable a logger.

        Parameters
        ----------
        logger: logging.Logger
            The logger to be turned off
        """
        logger.disabled = True

    @staticmethod
    def open(logger: logging.Logger) -> None:
        """
        Enable a logger.

        Parameters
        ----------
        logger: logging.Logger
            The logger to be turned on
        """
        logger.disabled = False

    @staticmethod
    def close_all() -> None:
        """Disable all loggers."""
        for logger in Log.loggers:
            logger.disabled = True

    @staticmethod
    def open_all() -> None:
        """Enable all loggers."""
        for logger in Log.loggers:
            logger.disabled = False

    @staticmethod
    def close_console_output() -> None:
        """Turn off log output to console."""
        Log.console_output = False
        for logger in Log.loggers:
            logger.removeHandler(Log.console_handler)

    @staticmethod
    def open_console_output() -> None:
        """Turn on log output to console."""
        Log.console_output = True
        for logger in Log.loggers:
            logger.addHandler(Log.console_handler)

    @staticmethod
    def set_console_output_level(level: int) -> None:
        """
        Set the level for the console handler.

        Parameters
        ----------
        level: int
            The intended console output level
        """
        Log.console_handler.level = level

    @staticmethod
    def close_file_output() -> None:
        """Turn off log output to a file."""
        Log.file_output = False
        for logger in Log.loggers:
            logger.removeHandler(Log.file_handler)

    @staticmethod
    def open_file_output() -> None:
        """Turn on log output to a file."""
        Log.file_output = True
        for logger in Log.loggers:
            logger.addHandler(Log.file_handler)

    @staticmethod
    def set_file_output_level(level: int) -> None:
        """
        Set the level for the file handler.

        Parameters
        ----------
        level: int
            The intended file output level
        """
        Log.file_handler.level = level
