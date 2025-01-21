"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import paramiko

class Uss:
    def __init__(self, profile: dict):
        """
        Initialize the Uss class with a profile object.

        :param profile: A dictionary containing SSH connection details like hostname, username, password, and port.
        """
        self.profile = profile
        self.ssh_client = None

    def connect(self):
        """
        Establish an SSH connection using the profile details.
        """
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(
            hostname=self.profile["hostname"],
            username=self.profile["username"],
            password=self.profile.get("password"),
            port=self.profile.get("port", 22),
        )

    def disconnect(self):
        """
        Close the SSH connection.
        """
        if self.ssh_client:
            self.ssh_client.close()

    def execute_command(self, command: str, cwd: str = None):
        """
        Execute a Unix command over SSH.

        :param command: The command to execute.
        :param cwd: Optional working directory for the command.
        :return: A tuple of (stdout, stderr).
        """
        if cwd:
            command = f"cd {cwd} && {command}"
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
