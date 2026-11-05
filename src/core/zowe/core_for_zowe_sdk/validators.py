"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os
from typing import Any, Union

import json5
from jsonschema import validate

REMOTE_SCHEMA_UNSUPPORTED = "Loading a JSON schema from a remote URL is not supported"


def validate_config_json(path_config_json: Union[str, dict[str, Any]], path_schema_json: str, cwd: str) -> None:
    """
    Validate that zowe.config.json file matches zowe.schema.json.

    Parameters
    ----------
    path_config_json: Union[str, dict[str, Any]]
        Absolute path to zowe.config.json
    path_schema_json: str
        Absolute path to zowe.schema.json
    cwd: str
        Path of the current working directory

    Raises
    ------
    ValueError
        When path_schema_json is a remote URL, which is not supported
    """
    # remote ($schema pointing to an http(s):// URL) schema loading is not supported; only local files may be used
    if path_schema_json.startswith("https://") or path_schema_json.startswith("http://"):
        raise ValueError(
            f"{REMOTE_SCHEMA_UNSUPPORTED}: {path_schema_json}. "
            "Use a local file path for the $schema property instead."
        )

    # checks if the path_schema_json is a file
    elif os.path.isfile(path_schema_json) or path_schema_json.startswith("file://"):
        with open(path_schema_json.replace("file://", "")) as file:
            schema_json = json5.load(file)
    # checks if the path_schema_json is absolute
    elif not os.path.isabs(path_schema_json):
        path_schema_json = os.path.join(cwd, path_schema_json)
        with open(path_schema_json) as file:
            schema_json = json5.load(file)

    # if there is no path_schema_json it will return None
    else:
        return None

    if isinstance(path_config_json, str):
        with open(path_config_json) as file:
            config_json = json5.load(file)
    else:
        config_json = path_config_json

    validate(instance=config_json, schema=schema_json)


def reject_unsafe_component(component: str) -> None:
    """
    Validate that a server-supplied name is usable as a single path segment.

    Parameters
    ----------
    component: str
        The name to be used as one segment of a generated path

    Raises
    ------
    ValueError
        When the name is an absolute path or contains a ".." segment
    """
    normalized = str(component).replace("\\", "/")
    if os.path.isabs(component) or ".." in normalized.split("/"):
        raise ValueError("Invalid path component: {}".format(component))


def is_sub_path(parent: str, child: str) -> bool:
    """
    Check whether a path resolves to a location inside another path.

    Parameters
    ----------
    parent: str
        The directory that is expected to contain the child
    child: str
        The path to be checked

    Returns
    -------
    bool
        True only when child resolves to a location inside parent
    """
    try:
        relative_path = os.path.relpath(os.path.realpath(child), os.path.realpath(parent))
    except ValueError:
        # Raised on Windows when the paths live on different drives
        return False
    segments = relative_path.split(os.sep) if relative_path else []
    if not segments or ".." in segments or os.path.isabs(relative_path):
        return False
    return True


def reject_unsafe_path(base_dir: str, target: str) -> None:
    """
    Validate that a generated path stays inside a base directory.

    Parameters
    ----------
    base_dir: str
        The directory that every generated path must stay within
    target: str
        The generated path to be checked

    Raises
    ------
    ValueError
        When the target resolves outside of base_dir
    """
    if not is_sub_path(base_dir, target):
        raise ValueError("The generated file path is outside the output directory: {}".format(target))
