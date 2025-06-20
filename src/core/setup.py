"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import sys

from setuptools import find_namespace_packages, setup

sys.path.insert(0, "..")
from _version import __version__
from setup import resolve_sdk_dep

setup(
    name="zowe_core_for_zowe_sdk",
    version=__version__,
    description="Zowe Python SDK - Core package",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
    ],
    install_requires=[
        "commentjson~=0.9.0",
        "deepmerge~=1.1.0",
        "jsonschema~=4.17.3",
        "pyyaml~=6.0.1",
        "requests~=2.32.0",
        "urllib3~=2.5.0",
    ],
    extras_require={"secrets": [resolve_sdk_dep("secrets", "~=1.0.0.dev")]},
    packages=find_namespace_packages(include=["zowe.*"]),
)
