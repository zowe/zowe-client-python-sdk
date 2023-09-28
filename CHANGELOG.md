# Change Log

All notable changes to the Zowe Client Python SDK will be documented in this file.

## Recent Changes

- Bug: Fixed profile merge order to match Node.js SDK 
- Feature: Added method to load profile properties from environment variables
- Bugfix: Fixed exception handling in session.py [#213] (https://github.com/zowe/zowe-client-python-sdk/issues/213)
- Feature: Added a CredentialManager class to securely retrieve values from credentials and manage multiple credential entries on Windows [#134](https://github.com/zowe/zowe-client-python-sdk/issues/134)
- Bugfix: Fixed issue for datasets and jobs with special characters in URL [#211] (https://github.com/zowe/zowe-client-python-sdk/issues/211)
- Feature: Added method to load profile properties from environment variables
- BugFix: Validation of zowe.config.json file matching the schema [#192](https://github.com/zowe/zowe-client-python-sdk/issues/192)
