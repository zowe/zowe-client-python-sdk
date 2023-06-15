import os.path
import uuid
from setuptools import setup
from _version import __version__

def resolve_sdk_dep(sdk_name, sdk_version):
    if os.path.exists(sdk_name):
        # Handle building from a Git checkout
        # Based on https://github.com/lab-cosmo/equistore/blob/master/python/equistore-torch/setup.py#L212
        return f"zowe.{sdk_name}_for_zowe_sdk@file://{sdk_name}?{uuid.uuid4()}"
    else:
        return f"zowe.{sdk_name}_for_zowe_sdk=={sdk_version}"

setup(
    name='zowe',
    version=__version__,
    description='Zowe Python SDK',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)"],
    install_requires=[resolve_sdk_dep('zos_console', __version__),
                      resolve_sdk_dep('zos_files', __version__),
                      resolve_sdk_dep('zos_tso', __version__),
                      resolve_sdk_dep('zos_jobs', __version__),
                      resolve_sdk_dep('zosmf', __version__)],
)
