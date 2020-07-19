from setuptools import setup, find_namespace_packages

setup(
    name='zowe_core_for_zowe_sdk',
    version='0.0.1',
    packages=find_namespace_packages(include=['zowe.*'])
)