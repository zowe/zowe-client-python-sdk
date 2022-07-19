"""Unit tests for the Zowe Python SDK z/OSMF package."""

# Including necessary paths
from unittest import mock

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
        mock_send_request.assert_called_once()