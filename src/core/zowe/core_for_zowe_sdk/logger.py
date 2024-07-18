"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
"""
Logger module for handling application logging.

This module provides the `Log` class which allows for registering,
setting levels, opening, and closing loggers.
"""

import logging
import os

dirname = os.path.join(os.path.expanduser("~"), ".zowe/logs")

os.makedirs(dirname, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(dirname, "python_sdk_logs.log"),
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


class Log:
    """
    Class used to represent a logger.

    Attributes
    ----------
    loggers: set
        The set of all loggers
    """

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
