import logging
import os

class Log:
    """root logger setup and a funtion to customize logger level"""

    dirname = os.path.join(os.path.expanduser("~"), ".zowe/logs")

    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    logging.basicConfig(
        filename=os.path.join(dirname, "python_sdk_logs.log"),
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    @staticmethod
    def setLoggerLevel(level: int):
        logging.root.setLevel(level)