import logging
import os


class Log:
    """root logger setup and a function to customize logger level"""

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
        logger = logging.getLogger(name)
        Log.loggers.add(logger)
        return logger

    @staticmethod
    def setLoggerLevel(level: int):
        for logger in Log.loggers:
            logger.setLevel(level)
