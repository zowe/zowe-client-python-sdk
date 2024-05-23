"""
Zowe Python SDK - Core package
"""

from .config_file import ConfigFile
from .connection import ApiConnection
from .constants import constants
from .credential_manager import CredentialManager
from .exceptions import *
from .profile_manager import ProfileManager
from .request_handler import RequestHandler
from .sdk_api import SdkApi
from .session import Session
from .session_constants import *
from .zosmf_profile import ZosmfProfile

import logging
import os

dirname = os.path.join(os.path.expanduser("~"), ".zowe/logs")

if not os.path.isdir(dirname):
    os.makedirs(dirname)

logging.basicConfig(
    filename=os.path.join(dirname, "python_sdk_logs.log"),
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
