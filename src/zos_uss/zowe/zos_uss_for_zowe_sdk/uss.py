"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Optional, Tuple
import paramiko
from zowe.core_for_zowe_sdk import SdkApi


class Uss(SdkApi):
    """
    Class to interact with Unix System Services (USS) on z/OS via SSH.

    Parameters
    ----------
    connection : dict
        A dictionary containing SSH connection details like hostname, username, password, and port.
    log : bool
        Flag to enable or disable logging.
    """

    def __init__(self, connection: dict, log: bool = True):
        super().__init__(connection, "/zosmf/restfiles/fs", logger_name=__name__, log=log)
        self.connection = connection
        self.ssh_client = None

    def connect(self):
        """Establish an SSH connection using the connection details."""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        hostname=self.connection["host"],
        username=self.connection["user"],
        password=self.connection.get("password"),
        port=self.connection.get("port", 22),

        # Check if a private key file is provided in the connection details.
        # Optionally, a passphrase can be provided via the "passphrase" key.
        if self.connection.get("pkey"):
            passphrase = self.connection.get("passphrase")
            # Load the private key from file. This example uses RSA keys.
            pkey = paramiko.RSAKey.from_private_key_file(self.connection["pkey"], password=passphrase)
            self.ssh_client.connect(
                hostname=hostname,
                username=username,
                pkey=pkey,
                port=port,
            )
        else:
            # Fall back to password authentication if no private key is provided.
            password = self.connection.get("password")
            self.ssh_client.connect(
                hostname=hostname,
                username=username,
                password=password,
                port=port,
            )
        

    def disconnect(self):
        """Close the SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()

    def execute_command(self, command: str, cwd: Optional[str] = None) -> Tuple[str, str]:
        """
        Execute a Unix command over SSH.

        Parameters
        ----------
        command : str
            The command to execute.
        cwd : Optional[str]
            The working directory for the command.

        Returns
        -------
        Tuple[str, str]
            A tuple containing the decoded stdout and stderr.
        """
        if cwd:
            command = f"cd {cwd} && {command}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
