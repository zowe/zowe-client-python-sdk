"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""
import sys, warnings , base64 
from typing import Optional
import commentjson
from zowe.core_for_zowe_sdk import constants
from zowe.core_for_zowe_sdk.exceptions import (
    SecureProfileLoadFailed
    )

HAS_KEYRING = True
try:
    import keyring

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
            is_win32 = sys.platform == "win32"
            if is_win32:
                service_name += "/" + constants["ZoweAccountName"]
                
            secret_value = CredentialManager._retrieve_credential(service_name)
            # Handle the case when secret_value is None
            if secret_value is None:
                return 

        except Exception as exc:
            raise SecureProfileLoadFailed(
                constants["ZoweServiceName"], error_msg=str(exc)
            ) from exc

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
        is_win32 = sys.platform == "win32"
        if is_win32:
            service_name += "/" + constants["ZoweAccountName"]
        encoded_credential = keyring.get_password(service_name, constants["ZoweAccountName"])
        if encoded_credential is None and is_win32:
            # Filter or suppress specific warning messages
            warnings.filterwarnings("ignore", message="^Retrieved an UTF-8 encoded credential")
            # Retrieve the secure value with an index
            index = 1
            temp_value = keyring.get_password(f"{service_name}-{index}", f"{constants['ZoweAccountName']}-{index}")
            while temp_value is not None:
                if encoded_credential is None:
                    encoded_credential = temp_value
                else:
                    encoded_credential += temp_value
                index += 1
                temp_value = keyring.get_password(f"{service_name}-{index}", f"{constants['ZoweAccountName']}-{index}")
                
        if encoded_credential is not None and encoded_credential.endswith("\0"):
            encoded_credential = encoded_credential[:-1]

        try:
            return encoded_credential.encode('utf-16le').decode()
        except (UnicodeDecodeError, AttributeError):
            # The credential is not encoded in UTF-16
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
        
        try:
            keyring.delete_password(service_name, account_name)  
        except keyring.errors.PasswordDeleteError:
            # Handling multiple credentials stored when the operating system is Windows
            if sys.platform == "win32":
                # Delete the secure value with an index
                index = 1
                while True:
                    field_name = f"{account_name}-{index}"
                    try:
                        keyring.delete_password(f"{service_name}-{index}", field_name)
                    except keyring.errors.PasswordDeleteError:
                        break
                    index += 1
    
    @staticmethod
    def save_secure_props()-> None:
        """
        Set secure_props for the given config file
        Returns
        -------
        None
        """
        if not HAS_KEYRING:
            return
        
        # Filter or suppress specific warning messages
        warnings.filterwarnings("ignore", message="^Retrieved an UTF-8 encoded credential")
        service_name = constants["ZoweServiceName"]
        credential =  CredentialManager.secure_props
        # Check if credential is a non-empty string
        if credential:
            is_win32 = sys.platform == "win32"
            #  = "UTF-16" if is_win32 else "UTF-8"
            if is_win32:
                service_name += "/" + constants["ZoweAccountName"] 
            
            # Load existing credentials, if any
            existing_credential = CredentialManager._retrieve_credential(service_name)
            if existing_credential:
                    
                # Decode the existing credential and update secure_props
                existing_credential_bytes = base64.b64decode(existing_credential).decode()
                existing_secure_props = commentjson.loads(existing_credential_bytes)
                existing_secure_props.update(credential)
                # Encode the credential
                encoded_credential = base64.b64encode(commentjson.dumps(existing_secure_props).encode()).decode()
                # Delete the existing credential
                CredentialManager.delete_credential(service_name , constants["ZoweAccountName"])
            else:
                # Encode the credential
                encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode() 
            # Check if the encoded credential exceeds the maximum length for win32
            if is_win32 and len(encoded_credential) > constants["WIN32_CRED_MAX_STRING_LENGTH"]:
                # Split the encoded credential string into chunks of maximum length
                chunk_size = constants["WIN32_CRED_MAX_STRING_LENGTH"]
                chunks = [encoded_credential[i: i + chunk_size] for i in range(0, len(encoded_credential), chunk_size)]
                chunks[-1]+= '\0'
                # Set the individual chunks as separate keyring entries
                for index, chunk in enumerate(chunks, start=1):
                    password=(chunk + '\0' *(len(chunk)%2)).encode().decode('utf-16le')
                    field_name = f"{constants['ZoweAccountName']}-{index}"
                    keyring.set_password(f"{service_name}-{index}", field_name, password)
                    
            else:
                # Credential length is within the maximum limit or not on win32, set it as a single keyring entry
                keyring.set_password(
                    service_name, constants["ZoweAccountName"], 
                    encoded_credential)