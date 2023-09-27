# Change Log

All notable changes to the Zowe Client Python SDK will be documented in this file.

## Recent Changes

- Feature: Added method to load profile properties from environment variables
- Feature: Added a CredentialManager class to securely retrieve values from credentials and manage multiple credential entries on Windows [#134](https://github.com/zowe/zowe-client-python-sdk/issues/134)
- Feature: Added method to Save profile properties to zowe.config.json file [#73](https://github.com/zowe/zowe-client-python-sdk/issues/73)
- Feature: Added method to Save secure profile properties to vault [#72](https://github.com/zowe/zowe-client-python-sdk/issues/72)
- Bugfix: Fixed issue for datasets and jobs with special characters in URL [#211] (https://github.com/zowe/zowe-client-python-sdk/issues/211)
- Bugfix: Fixed exception handling in session.py [#213] (https://github.com/zowe/zowe-client-python-sdk/issues/213)
- BugFix: Validation of zowe.config.json file matching the schema [#192](https://github.com/zowe/zowe-client-python-sdk/issues/192)
