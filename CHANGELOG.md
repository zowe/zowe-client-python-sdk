# Change Log

All notable changes to the Zowe Client Python SDK will be documented in this file.

## Recent Changes

<<<<<<< HEAD
- Bug: Default encoding for I/O operations should be UTF-8 
- Feature: Added method to load profile properties from environment variables
=======
### Bug Fixes

- Fixed 'create_data_set' to accept "FBA", "FBM", "VBA", "VBM" as valid recfm [#240](https://github.com/zowe/zowe-client-python-sdk/issues/240)
- Return response instead of raw from streamed requests

## `1.0.0-dev12`

### Bug Fixes

- Fixed Secrets SDK requiring LD_LIBRARY_PATH to be defined when installed from wheel on Linux [#229](https://github.com/zowe/zowe-client-python-sdk/issues/229)
- Fixed 'issue_command' Console API function to provide custom console name [#231](https://github.com/zowe/zowe-client-python-sdk/issues/231)

## `1.0.0-dev11`

### Enhancements

- Added method to save secure profile properties to vault [#72](https://github.com/zowe/zowe-client-python-sdk/issues/72)
- Added method to save profile properties to zowe.config.json file [#73](https://github.com/zowe/zowe-client-python-sdk/issues/73)
- Added CredentialManager class to securely retrieve values from credentials and manage multiple credential entries on Windows [#134](https://github.com/zowe/zowe-client-python-sdk/issues/134)
- Added method to load profile properties from environment variables [#136](https://github.com/zowe/zowe-client-python-sdk/issues/136)
- Added validation of zowe.config.json file matching the schema [#192](https://github.com/zowe/zowe-client-python-sdk/issues/192)
- Added Secrets SDK for storing client secrets in OS keyring [#208](https://github.com/zowe/zowe-client-python-sdk/issues/208)

### Bug Fixes

- Fixed profile merge order to match Node.js SDK [#190](https://github.com/zowe/zowe-client-python-sdk/issues/190)
- Fixed issue for datasets and jobs with special characters in URL [#211](https://github.com/zowe/zowe-client-python-sdk/issues/211)
- Fixed exception handling in session.py [#213](https://github.com/zowe/zowe-client-python-sdk/issues/213)
>>>>>>> 80c6a66785746ec730684d04aa70064b2da6e397
