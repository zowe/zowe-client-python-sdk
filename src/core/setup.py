from pkg_resources import get_distribution
from setuptools import setup, find_namespace_packages

setup(
    name="zowe_core_for_zowe_sdk",
    version=get_distribution("zowe").version,
    description="Zowe Python SDK - Core package",
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
    ],
    install_requires=["requests", "urllib3", "pyyaml", "jsoncparser"],
    packages=find_namespace_packages(include=["zowe.*"]),
)
