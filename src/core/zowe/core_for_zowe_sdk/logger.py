"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import logging
import os


class Log:
    """
    Class used to represent a logger.

    Attributes
    ----------
    loggers: set
        The set of all loggers
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
    """

    dirname: str = os.path.join(os.path.expanduser("~"), ".zowe/logs")
    os.makedirs(dirname, exist_ok=True)
    file_handler: logging.FileHandler = logging.FileHandler(os.path.join(dirname, "python_sdk_logs.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", "%m/%d/%Y %I:%M:%S %p")
    )
    console_handler: logging.StreamHandler = logging.StreamHandler()

    file_output: bool = True
    console_output: bool = True

    loggers: set = set()

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
    def set_all_logger_level(level: int):
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
    def close(logger: logging.Logger):
        """
        Disable a logger.

        Parameters
        ----------
        logger: logging.Logger
            The logger to be turned off
        """
        logger.disabled = True

    @staticmethod
    def open(logger: logging.Logger):
        """
        Enable a logger.

        Parameters
        ----------
        logger: logging.Logger
            The logger to be turned on
        """
        logger.disabled = False

    @staticmethod
    def close_all():
        """Disable all loggers."""
        for logger in Log.loggers:
            logger.disabled = True

    @staticmethod
    def open_all():
        """Enable all loggers."""
        for logger in Log.loggers:
            logger.disabled = False

    @staticmethod
    def close_console_output():
        """Turn off log output to console."""
        Log.console_output = False
        for logger in Log.loggers:
            logger.removeHandler(Log.console_handler)

    @staticmethod
    def open_console_output():
        """Turn on log output to console."""
        Log.console_output = True
        for logger in Log.loggers:
            logger.addHandler(Log.console_handler)

    @staticmethod
    def set_console_output_level(level: int):
        """
        Set the level for the console handler.

        Parameters
        ----------
        level: int
            The intended console output level
        """
        Log.console_handler.level = level

    @staticmethod
    def close_file_output():
        """Turn off log output to a file."""
        Log.file_output = False
        for logger in Log.loggers:
            logger.removeHandler(Log.file_handler)

    @staticmethod
    def open_file_output():
        """Turn on log output to a file."""
        Log.file_output = True
        for logger in Log.loggers:
            logger.addHandler(Log.file_handler)

    @staticmethod
    def set_file_output_level(level: int):
        """
        Set the level for the file handler.

        Parameters
        ----------
        level: int
            The intended file output level
        """
        Log.file_handler.level = level
