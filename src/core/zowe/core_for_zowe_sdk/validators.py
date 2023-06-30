"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import commentjson
from jsonschema import validate
import os
import requests


def validate_config_json(path_config_json: str, path_schema_json: str):
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
    if path_schema_json[:8] in ("https://", "http://"):
        response = requests.get(path_schema_json)
        schema_data = response.content.decode("utf-8")
        schema_json = commentjson.load(schema_data)
    
    # checks if the path_schema_json is a file
    elif os.path.isfile(path_schema_json):
        with open(path_schema_json) as file:
            schema_json = commentjson.load(file)
        
    # if there is no path_schema_json it will return None
    else: 
        return None
    
    with open(path_config_json) as file:
        config_json = commentjson.load(file)

    return validate(instance=config_json, schema=schema_json)
