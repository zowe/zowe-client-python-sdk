import sys
from setuptools import setup, find_namespace_packages
sys.path.append("..")
from _version import __version__

setup(
    name='zowe_zos_console_for_zowe_sdk',
    version=__version__,
    description='Zowe Python SDK - z/OS Console package',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)"],
    install_requires=['zowe.core_for_zowe_sdk~=' + __version__],
    packages=find_namespace_packages(include=['zowe.*'])
)
