"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
import base64
import sys
from typing import Optional

import commentjson

from .constants import constants
from .exceptions import SecureProfileLoadFailed

HAS_KEYRING = True
try:
    from zowe.secrets_for_zowe_sdk import keyring
except ImportError:
    HAS_KEYRING = False


class CredentialManager:
    secure_props = {}

    @staticmethod
    def load_secure_props() -> None:
        """
        load secure_props stored for the given config file
        Returns
        -------
        None

        if keyring is not initialized, set empty value
        """
        if not HAS_KEYRING:
            CredentialManager.secure_props = {}
            return

        try:
            service_name = constants["ZoweServiceName"]
            secret_value = CredentialManager._retrieve_credential(service_name)
            # Handle the case when secret_value is None
            if secret_value is None:
                return

        except Exception as exc:
            raise SecureProfileLoadFailed(constants["ZoweServiceName"], error_msg=str(exc)) from exc

        secure_config: str
        secure_config = secret_value.encode()
        secure_config_json = commentjson.loads(base64.b64decode(secure_config).decode())
        # update the secure props
        CredentialManager.secure_props = secure_config_json

    @staticmethod
    def _retrieve_credential(service_name: str) -> Optional[str]:
        """
        Retrieve the credential from the keyring or storage.
        If the credential exceeds the maximum length, retrieve it in parts.
        Parameters
        ----------
        service_name: str
            The service name for the credential retrieval
        Returns
        -------
        str
            The retrieved  encoded credential
        """
        encoded_credential = keyring.get_password(service_name, constants["ZoweAccountName"])
        if encoded_credential is None and sys.platform == "win32":
            # Retrieve the secure value with an index
            index = 1
            temp_value = keyring.get_password(service_name, f"{constants['ZoweAccountName']}-{index}")
            while temp_value is not None:
                if encoded_credential is None:
                    encoded_credential = temp_value
                else:
                    encoded_credential += temp_value
                index += 1
                temp_value = keyring.get_password(service_name, f"{constants['ZoweAccountName']}-{index}")

        return encoded_credential

    @staticmethod
    def delete_credential(service_name: str, account_name: str) -> None:
        """
        Delete the credential from the keyring or storage.
        If the keyring.delete_password function is not available, iterate through and delete credentials.
        Parameters
        ----------
        service_name: str
            The service name for the credential deletion
        account_name: str
            The account name for the credential deletion
        Returns
        -------
        None
        """

        keyring.delete_password(service_name, account_name)

        # Handling multiple credentials stored when the operating system is Windows
        if sys.platform == "win32":
            index = 1
            while True:
                field_name = f"{account_name}-{index}"
                service_name = f"{service_name}-{index}"
                if not keyring.delete_password(service_name, field_name):
                    break
                index += 1

    @staticmethod
    def save_secure_props() -> None:
        """
        Set secure_props for the given config file
        Returns
        -------
        None
        """
        if not HAS_KEYRING:
            return

        service_name = constants["ZoweServiceName"]
        credential = CredentialManager.secure_props
        # Check if credential is a non-empty string
        if credential:
            is_win32 = sys.platform == "win32"

            encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
            if is_win32:
                # Delete the existing credential
                CredentialManager.delete_credential(service_name, constants["ZoweAccountName"])
            # Check if the encoded credential exceeds the maximum length for win32
            if is_win32 and len(encoded_credential) > constants["WIN32_CRED_MAX_STRING_LENGTH"]:
                # Split the encoded credential string into chunks of maximum length
                chunk_size = constants["WIN32_CRED_MAX_STRING_LENGTH"]
                encoded_credential += "\0"
                chunks = [encoded_credential[i : i + chunk_size] for i in range(0, len(encoded_credential), chunk_size)]
                # Set the individual chunks as separate keyring entries
                for index, chunk in enumerate(chunks, start=1):
                    field_name = f"{constants['ZoweAccountName']}-{index}"
                    keyring.set_password(service_name, field_name, chunk)

            else:
                # Credential length is within the maximum limit or not on win32, set it as a single keyring entry
                keyring.set_password(service_name, constants["ZoweAccountName"], encoded_credential)
