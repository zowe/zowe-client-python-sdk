import logging
import os


class Log:
    """Class used to represent a logger

    Attributes
    -------
    loggers: set
        The set of all loggers
    """

    dirname = os.path.join(os.path.expanduser("~"), ".zowe/logs")

    os.makedirs(dirname, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(dirname, "python_sdk_logs.log"),
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    loggers = set()

    @staticmethod
    def registerLogger(name: str):
        """
        Create and register a logger

        Parameters
        ----------
        name: str
            name for the logger

        Returns
        -------
        Logger
            A Logger object named after the file where it is created
        """
        logger = logging.getLogger(name)
        Log.loggers.add(logger)
        return logger

    @staticmethod
    def setAllLoggerLevel(level: int):
        """
        Set display level for all loggers

        Parameters
        ----------
        level: int
            The intended logger level
        """
        for logger in Log.loggers:
            logger.setLevel(level)

    @staticmethod
    def close(logger):
        """
        Disable a logger

        Parameters
        ----------
        logger: Logger
            The logger to be turned off
        """
        logger.disabled = True

    @staticmethod
    def open(logger):
        """
        Enable a logger

        Parameters
        ----------
        logger: Logger
            The logger to be turned on
        """
        logger.disabled = False

    @staticmethod
    def closeAll():
        """
        Disable all loggers
        """
        for logger in Log.loggers:
            logger.disabled = True

    @staticmethod
    def openAll():
        """
        Enable all loggers
        """
        for logger in Log.loggers:
            logger.disabled = False
