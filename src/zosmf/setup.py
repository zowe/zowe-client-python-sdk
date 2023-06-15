import os.path
import sys
import uuid
from setuptools import setup, find_namespace_packages
sys.path.append("..")
from _version import __version__

src_dir = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

def resolve_sdk_dep(sdk_name, version_spec):
    if os.path.exists(os.path.join(src_dir, sdk_name, "zowe")):
        # Handle building from a Git checkout
        # Based on https://github.com/lab-cosmo/equistore/blob/master/python/equistore-torch/setup.py#L212
        sdk_dir = os.path.realpath(os.path.join(src_dir, sdk_name))
        return f"zowe.{sdk_name}_for_zowe_sdk@file://{sdk_dir}?{uuid.uuid4()}"
    else:
        return f"zowe.{sdk_name}_for_zowe_sdk{version_spec}"

setup(
    name='zowe_zosmf_for_zowe_sdk',
    version=__version__,
    description='Zowe Python SDK - z/OSMF package',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)"],
    install_requires=[resolve_sdk_dep('core', '~=' + __version__)],
    packages=find_namespace_packages(include=['zowe.*'])
)
