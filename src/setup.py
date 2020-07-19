from setuptools import setup

setup(
    name='zowe',
    version='0.0.1',
    description='Zowe Python SDK',
    url="https://github.com/zowe/zowe-client-python-sdk",
    author="Guilherme Cartier",
    author_email="gcartier94@gmail.com",
    license="EPL-2.0",
    classifiers=[
        "License :: OSI Approved :: Eclipse Public License v2.0",
        "Programming Language :: Python :: 3"],
    install_requires=['keyring',
                      'pyyaml',
                      'requests>=2.22',
                      'zowe_zos_console_for_sdk',
                      'zowe_zos_files_for_sdk',
                      'zowe_zos_tso_for_sdk',
                      'zowe_zos_jobs_for_sdk',
                      'zowe_zosmf_for_sdk'],
)
