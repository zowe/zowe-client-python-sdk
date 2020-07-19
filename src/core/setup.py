from setuptools import setup, find_namespace_packages

setup(
    name='zowe_core_for_zowe_sdk',
    version='0.0.1',
    description='Zowe Python SDK - Core package',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "License :: OSI Approved :: Eclipse Public License v2.0",
        "Programming Language :: Python :: 3"],
    packages=find_namespace_packages(include=['zowe.*'])
)