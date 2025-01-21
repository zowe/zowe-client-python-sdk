"""Integration tests for the Zowe Python SDK z/OS UNIX System Services (USS) package."""

import unittest
from unittest.mock import patch, MagicMock
from zowe.zos_uss_for_zowe_sdk import Uss

class TestUss(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "hostname": "example.com",
            "username": "user",
            "password": "pass",
            "port": 22,
        }
        self.uss = Uss(self.profile)

    @patch("paramiko.SSHClient")
    def test_connect(self, mock_ssh_client):
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        self.uss.connect()
        mock_client.connect.assert_called_with(
            hostname="example.com", username="user", password="pass", port=22
        )

    @patch("paramiko.SSHClient")
    def test_execute_command(self, mock_ssh_client):
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"command output"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

        self.uss.connect()
        output, error = self.uss.execute_command("ls -l")
        self.assertEqual(output, "command output")
        self.assertEqual(error, "")
