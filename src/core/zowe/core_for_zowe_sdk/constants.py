"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Dict, Union

constants: Dict[str, Union[str,int]] = {
    "SecureValuePrefix": "managed by ",
    "TsoSessionNotFound": "IZUG1126E",
    "ZoweCredentialKey": "Zowe-Plugin",
    "ZoweServiceName": "Zowe",
    "ZoweAccountName": "secure_config_props",
    "WIN32_CRED_MAX_STRING_LENGTH": 2560,
}
