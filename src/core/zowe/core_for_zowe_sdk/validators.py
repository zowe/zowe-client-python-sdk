"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
from typing import Union

import commentjson
import requests
from jsonschema import validate


def validate_config_json(path_config_json: Union[str, dict], path_schema_json: str, cwd: str):
    """
    Function validating that zowe.config.json file matches zowe.schema.json.

    Parameters
    ----------
        path_config: str
            Absolute path to zowe.config.json

        path_schema: str
            Absolute path to zowe.schema.json

    Returns
    -------
        Provides details if config.json doesn't match schema.json, otherwise it returns None.
    """

    # checks if the path_schema_json point to an internet URI and download the schema using the URI
    if path_schema_json.startswith("https://") or path_schema_json.startswith("http://"):
        schema_json = requests.get(path_schema_json).json()

    # checks if the path_schema_json is a file
    elif os.path.isfile(path_schema_json) or path_schema_json.startswith("file://"):
        with open(path_schema_json.replace("file://", "")) as file:
            schema_json = commentjson.load(file)

    # checks if the path_schema_json is absolute
    elif not os.path.isabs(path_schema_json):
        path_schema_json = os.path.join(cwd, path_schema_json)
        with open(path_schema_json) as file:
            schema_json = commentjson.load(file)

    # if there is no path_schema_json it will return None
    else:
        return None

    if isinstance(path_config_json, str):
        with open(path_config_json) as file:
            config_json = commentjson.load(file)
    else:
        config_json = path_config_json

    return validate(instance=config_json, schema=schema_json)
