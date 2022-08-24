"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import json
from jsonschema import validate


def validate_config_json(path_config_json: str, path_schema_json: str):
    """
    Function validating that zowe.config.json file matches zowe.schema.json.


    Parameters
    ----------
        path_config - requires absolute path to zowe.config.json

        path_schema - requires absolute path to zowe.schema.json

    Returns
    -------
        None if config file matches schema.
    """

    config_json = ""
    schema_json = ""

    with open(path_config_json) as f:
        config_json = json.load(f)

    with open(path_schema_json) as f:
        schema_json = json.load(f)


    return validate(
                instance=config_json,
                schema=schema_json
                )
