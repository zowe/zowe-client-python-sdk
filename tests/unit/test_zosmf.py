"""Unit tests for the Zowe Python SDK z/OSMF package."""

# Including necessary paths
import sys
import os
from unittest import mock

from zos_files.zowe.zos_files_for_zowe_sdk.files import Files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from zowe.zosmf_for_zowe_sdk import Zosmf


class TestZosmfClass(unittest.TestCase):
    """Zosmf class unit tests."""

    def setUp(self):
        """Setup fixtures for Zosmf class."""
        self.connection_dict = {"host_url": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password"}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Zosmf class."""
        zosmf = Zosmf(self.connection_dict)
        self.assertIsInstance(zosmf, Zosmf)
        
    @mock.patch('requests.Session.send')
    def test_list_systems(self, mock_send_request):
        """Listing z/OSMF systems should send a REST request"""
        mock_send_request.return_value = mock.Mock(status_code=200)
        Files({"plugin_profile": "test"}).list_systems()
        mock_send_request.assert_called_once()