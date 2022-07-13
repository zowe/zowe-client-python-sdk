"""Unit tests for the Zowe Python SDK Core package."""

import unittest
from unittest import mock
from zowe.core_for_zowe_sdk import ApiConnection, SdkApi, RequestHandler, ZosmfProfile
from zowe.core_for_zowe_sdk import exceptions


class TestApiConnectionClass(unittest.TestCase):
    """ApiConnection class unit tests."""

    def setUp(self):
        """Setup ApiConnection fixtures."""
        self.url = 'https://mock-url.com'
        self.user = 'Username'
        self.password = 'Password'

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of ApiConnection class."""
        api_connection = ApiConnection(self.url, self.user, self.password)
        self.assertIsInstance(api_connection, ApiConnection)

    def test_object_should_raise_custom_error_without_url(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if host_url is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url='', user=self.user, password=self.password)

    def test_object_should_raise_custom_error_without_user(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if user is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url=self.url, user='', password=self.password)

    def test_object_should_raise_custom_error_without_password(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if password is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url=self.url, user=self.user, password='')


class TestSdkApiClass(unittest.TestCase):
    """SdkApi class unit tests."""

    def setUp(self):
        """Setup fixtures for SdkApi class."""
        self.connection_dict = {"host_url": "https://mock-url.com",
                                "user": "Username",
                                "password": "Password"}
        self.default_url = 'https://default-api.com/'

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of SdkApi class."""
        sdk_api = SdkApi(self.connection_dict, self.default_url)
        self.assertIsInstance(sdk_api, SdkApi)


class TestRequestHandlerClass(unittest.TestCase):
    """RequestHandler class unit tests."""

    def setUp(self):
        """Setup fixtures for RequestHandler class."""
        self.session_arguments = {'verify': False}

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of RequestHandler class."""
        request_handler = RequestHandler(self.session_arguments)
        self.assertIsInstance(request_handler, RequestHandler)

    @mock.patch('requests.Session.send')
    def test_perform_streamed_request(self, mock_send_request):
        """Performing a streamed request should call 'send_request' method"""
        mock_send_request.return_value = mock.Mock(status_code=200)
        request_handler = RequestHandler(self.session_arguments)
        request_handler.perform_streamed_request("GET", {'url': 'https://www.zowe.org'})
        mock_send_request.assert_called_once()
        self.assertTrue(mock_send_request.call_args[1]["stream"])


class TestZosmfProfileClass(unittest.TestCase):
    """ZosmfProfile class unit tests."""

    def setUp(self):
        """Setup fixtures for ZosmfProfile class."""
        self.profile_name = "MOCK"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of ZosmfProfile class."""
        zosmf_profile = ZosmfProfile(self.profile_name)
        self.assertIsInstance(zosmf_profile, ZosmfProfile)
