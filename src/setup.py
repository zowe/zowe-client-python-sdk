from setuptools import setup

setup(
    name='zowe',
    version='0.0.4',
    description='Zowe Python SDK',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "Programming Language :: Python :: 3"],
    install_requires=['zowe_zos_console_for_zowe_sdk',
                      'zowe_zos_files_for_zowe_sdk',
                      'zowe_zos_tso_for_zowe_sdk',
                      'zowe_zos_jobs_for_zowe_sdk',
                      'zowe_zosmf_for_zowe_sdk'],
)
