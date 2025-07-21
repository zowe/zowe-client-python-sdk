"""Unit tests for the Zowe Python SDK z/OSMF package."""

import unittest
from unittest import mock

from zowe.zosmf_for_zowe_sdk import Zosmf


class TestZosmfClass(unittest.TestCase):
    """Zosmf class unit tests."""

    def setUp(self):
        """Setup fixtures for Zosmf class."""
        self.connection_dict = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Zosmf class."""
        zosmf = Zosmf(self.connection_dict)
        self.assertIsInstance(zosmf, Zosmf)

    @mock.patch("requests.Session.send")
    def test_list_systems(self, mock_send_request):
        """Listing z/OSMF systems should send a REST request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Zosmf(self.connection_dict).list_systems()
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_response_timeout_header_added(self, mock_send_request):
        """Response timeout should add the X-IBM-Response-Timeout header to requests."""
        connection_with_timeout = self.connection_dict.copy()
        connection_with_timeout["responseTimeout"] = "5"

        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        # Call a method that triggers a request
        Zosmf(connection_with_timeout).list_systems()

        # Verify the request was called and inspect the headers
        mock_send_request.assert_called_once()
        # Get the PreparedRequest object from the call args
        prepared_request = mock_send_request.call_args[0][0]
        self.assertIn("X-IBM-Response-Timeout", prepared_request.headers)
        self.assertEqual(prepared_request.headers["X-IBM-Response-Timeout"], "5")

