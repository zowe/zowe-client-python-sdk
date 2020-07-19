from setuptools import setup, find_namespace_packages

setup(
    name='zowe_zos_console_for_zowe_sdk',
    version='0.0.1',
    install_requires=['zowe.core_for_zowe_sdk'],
    packages=find_namespace_packages(include=['zowe.*'])
)
