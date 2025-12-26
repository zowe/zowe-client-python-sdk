"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Any

from zowe.core_for_zowe_sdk import SdkApi
from zowe.zos_files_for_zowe_sdk.constants import zos_file_constants

_MIN_TIMEOUT = zos_file_constants["min_timeout"]
_MAX_TIMEOUT = zos_file_constants["max_timeout"]


class BaseFilesApi(SdkApi):
    """
    Extends the SdkApi class to support headers specific to z/OSMF Files APIs.

    Parameters
    ----------
    profile : dict[str, Any]
        Profile information in json (dict) format
    log : bool
        Flag to disable logger
    """

    def __init__(self, profile: dict[str, Any], log: bool = True):
        super().__init__(profile, "/zosmf/restfiles/", logger_name=__name__, log=log)
        self._default_headers["Accept-Encoding"] = "gzip"
        self._set_response_timeout(profile)

    def _set_response_timeout(self, profile: dict[str, Any]):
        async_threshold = profile.get("asyncThreshold") or profile.get("X-IBM-Async-Threshold")
        resp_to = profile.get("responseTimeout")
        if resp_to is not None:
            try:
                resp_to_int = int(resp_to)
                clamped = max(_MIN_TIMEOUT, min(_MAX_TIMEOUT, resp_to_int))
                if clamped != resp_to_int and hasattr(self, "logger"):
                    self.logger.warning(
                        f"responseTimeout {resp_to_int} out of range; clamped to {clamped} "
                        f"(allowed {_MIN_TIMEOUT}-{_MAX_TIMEOUT})"
                    )
                self._default_headers["X-IBM-Response-Timeout"] = str(clamped)
            except (TypeError, ValueError):
                if hasattr(self, "logger"):
                    self.logger.warning("responseTimeout must be an integer between 5 and 600; header not set")
        else:
            if hasattr(self, "logger"):
                self.logger.info("X-IBM-Async-Threshold present; X-IBM-Response-Timeout will be ignored by z/OSMF")
