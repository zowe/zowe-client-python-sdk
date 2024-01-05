Secrets Package
==================

Contains APIs to store, retrieve, and delete credentials in the end user's operating system (OS) keyring.

This Python package requires the OS keyring to be unlocked before credentials can stored or retrieved. Please follow the [installation guidelines for Zowe CLI](https://docs.zowe.org/stable/user-guide/cli-installcli#installation-guidelines) to ensure that the Secure Credential Store is accessible.

If you are using a headless Linux environment, please consult the following article on Zowe Docs: [Configuring Secure Credential Store on headless Linux operating systems](https://docs.zowe.org/stable/user-guide/cli-configure-scs-on-headless-linux-os). 

Example
------------
```py
from zowe.secrets_for_zowe_sdk import keyring
# Store a short password using the keyring module:
password = "Zowe ❕"
keyring.set_password("Test", "ShortPassword", password)
# Retrieving a password under a given service and account:
assert keyring.get_password("Test", "ShortPassword") == password
# Deleting a password:
assert keyring.delete_password("Test", "ShortPassword")
assert keyring.get_password("Test", "ShortPassword") is None
```