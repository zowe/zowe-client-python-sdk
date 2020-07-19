from setuptools import setup

setup(
    name='zowe',
    version='0.0.1',
    install_requires=['keyring', 'pyyaml',
                      'requests>=2.22',
                      'zowe_zos_console_for_sdk',
                      'zowe_zos_files_for_sdk',
                      'zowe_zos_tso_for_sdk',
                      'zowe_zos_jobs_for_sdk',
                      'zowe_zosmf_for_sdk'],
)
