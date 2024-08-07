"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import unittest
from unittest import mock

from zowe.core_for_zowe_sdk import RequestHandler, exceptions


class TestRequestHandlerClass(unittest.TestCase):
    """RequestHandler class unit tests."""

    def setUp(self):
        """Setup fixtures for RequestHandler class."""
        self.session_arguments = {"verify": False}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of RequestHandler class."""
        request_handler = RequestHandler(self.session_arguments)
        self.assertIsInstance(request_handler, RequestHandler)

    @mock.patch("logging.Logger.debug")
    @mock.patch("logging.Logger.error")
    @mock.patch("requests.Session.send")
    def test_perform_streamed_request(
        self, mock_send_request, mock_logger_error: mock.MagicMock, mock_logger_debug: mock.MagicMock
    ):
        """Performing a streamed request should call 'send_request' method"""
        mock_send_request.return_value = mock.Mock(status_code=200)
        request_handler = RequestHandler(self.session_arguments)
        request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, stream=True)

        mock_logger_error.assert_not_called()
        mock_logger_debug.assert_called()
        self.assertIn("Request method: GET", mock_logger_debug.call_args[0][0])
        mock_send_request.assert_called_once()
        self.assertTrue(mock_send_request.call_args[1]["stream"])

    @mock.patch("logging.Logger.error")
    def test_logger_unmatched_status_code(self, mock_logger_error: mock.MagicMock):
        """Test logger with unexpected status code"""
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, expected_code=[0], stream=True)
        except exceptions.UnexpectedStatus:
            mock_logger_error.assert_called_once()
            self.assertIn("The status code", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    def test_logger_perform_request_invalid_method(self, mock_logger_error: mock.MagicMock):
        """Test logger with invalid request method"""
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("Invalid method", {"url": "https://www.zowe.org"}, stream=True)
        except exceptions.InvalidRequestMethod:
            mock_logger_error.assert_called_once()
            self.assertIn("Invalid HTTP method input", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    @mock.patch("requests.Session.send")
    def test_logger_invalid_status_code(self, mock_send_request, mock_logger_error: mock.MagicMock):
        mock_send_request.return_value = mock.Mock(ok=False)
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, stream=True)
        except exceptions.RequestFailed:
            mock_logger_error.assert_called_once()
            self.assertIn("HTTP Request has failed", mock_logger_error.call_args[0][0])
        mock_logger_error.assert_called_once

    @mock.patch("requests.Session.send")
    def test_empty_text(self, mock_send_request):
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/json"}, text="", status_code=200
        )
        request_handler = RequestHandler(self.session_arguments)
        response = request_handler.perform_request("GET", {"url": "https://www.zowe.org"})
        self.assertTrue(response == None)
