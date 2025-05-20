"""Unit tests for the Zowe Python SDK z/OS UNIX System Services (USS) package."""

import unittest
from unittest.mock import MagicMock, patch

from zowe.zos_uss_for_zowe_sdk import Uss


class TestUss(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "host": "example.com",
            "user": "Username",
            "password": "Password",
            "port": 22,
        }
        self.uss = Uss(connection=self.profile)

    @patch("paramiko.SSHClient")
    def test_connect(self, mock_ssh_client):
        self.uss.connect()
        mock_ssh_client.assert_called_once()
        self.assertIsNotNone(self.uss.ssh_client)

    @patch("paramiko.SSHClient")
    def test_disconnect(self, mock_ssh_client):
        mock_ssh = mock_ssh_client.return_value
        self.uss.ssh_client = mock_ssh
        self.uss.disconnect()
        mock_ssh.close.assert_called_once()

    @patch("paramiko.SSHClient")
    def test_execute_command(self, mock_ssh_client):
        mock_ssh = mock_ssh_client.return_value
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_stdout.read.return_value = b"Command executed successfully"
        mock_stderr.read.return_value = b""
        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        self.uss.ssh_client = mock_ssh
        stdout, stderr = self.uss.execute_command("ls -la")
        self.assertEqual(stdout, "Command executed successfully")
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
