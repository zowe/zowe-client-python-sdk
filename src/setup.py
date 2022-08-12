from setuptools import setup
from _version import __version__

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
    install_requires=['zowe_zos_console_for_zowe_sdk',
                      'zowe_zos_files_for_zowe_sdk',
                      'zowe_zos_tso_for_zowe_sdk',
                      'zowe_zos_jobs_for_zowe_sdk',
                      'zowe_zosmf_for_zowe_sdk'],
)
