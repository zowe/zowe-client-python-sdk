"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import os.path
import uuid

from setuptools import setup

from _version import __version__

src_dir = os.path.realpath(os.path.dirname(__file__))
uuid4 = uuid.uuid4()


def resolve_sdk_dep(sdk_name: str, version_spec: str) -> str:
    # if os.path.exists(os.path.join(src_dir, sdk_name, "zowe")):
    #     # Handle building from a Git checkout
    #     # Based on https://github.com/lab-cosmo/equistore/blob/master/python/equistore-torch/setup.py#L212
    #     sdk_dir = os.path.realpath(os.path.join(src_dir, sdk_name))
    #     return f"zowe.{sdk_name}_for_zowe_sdk@file://{sdk_dir}"
    # else:
    return f"zowe.{sdk_name}_for_zowe_sdk{version_spec}"


if __name__ == "__main__":
    setup(
        name="zowe-python-sdk-bundle",
        version=__version__,
        description="Zowe Python SDK",
        long_description=open("../README.md", "r").read(),
        long_description_content_type="text/markdown",
        url="https://github.com/zowe/zowe-client-python-sdk",
        author="Zowe",
        author_email="zowe.robot@gmail.com",
        license="EPL-2.0",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.9",
            "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        ],
        install_requires=[
            resolve_sdk_dep("zos_console", "==" + __version__),
            resolve_sdk_dep("zos_files", "==" + __version__),
            resolve_sdk_dep("zos_tso", "==" + __version__),
            resolve_sdk_dep("zos_jobs", "==" + __version__),
            resolve_sdk_dep("zosmf", "==" + __version__),
        ],
        py_modules=[],
    )
