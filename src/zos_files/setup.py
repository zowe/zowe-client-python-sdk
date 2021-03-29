from setuptools import setup, find_namespace_packages

setup(
    name='zowe_zos_files_for_zowe_sdk',
    version='0.5.0-silk3',
    description='Zowe Python SDK - z/OS Files package',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)"],
    install_requires=['zowe.core_for_zowe_sdk'],
    packages=find_namespace_packages(include=['zowe.*'])
)
