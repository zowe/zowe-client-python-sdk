import os.path
import sys
import uuid
from setuptools import setup, find_namespace_packages
sys.path.append("..")
from _version import __version__

def resolve_sdk_dep(sdk_name, sdk_version):
    if os.path.exists(os.path.join("..", sdk_name)):
        # Handle building from a Git checkout
        # Based on https://github.com/lab-cosmo/equistore/blob/master/python/equistore-torch/setup.py#L212
        return f"zowe.{sdk_name}_for_zowe_sdk@file://../{sdk_name}?{uuid.uuid4()}"
    else:
        return f"zowe.{sdk_name}_for_zowe_sdk~={sdk_version}"

setup(
    name='zowe_zos_jobs_for_zowe_sdk',
    version=__version__,
    description='Zowe Python SDK - z/OS Jobs package',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)"],
    install_requires=[resolve_sdk_dep('core', __version__)],
    packages=find_namespace_packages(include=['zowe.*'])
)
