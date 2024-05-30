import unittest

from zowe.core_for_zowe_sdk import (
    ApiConnection,
    exceptions
)

class TestApiConnectionClass(unittest.TestCase):
    """ApiConnection class unit tests."""

    def setUp(self):
        """Setup ApiConnection fixtures."""
        self.url = "https://mock-url.com"
        self.user = "Username"
        self.password = "Password"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of ApiConnection class."""
        api_connection = ApiConnection(self.url, self.user, self.password)
        self.assertIsInstance(api_connection, ApiConnection)

    def test_object_should_raise_custom_error_without_url(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if host_url is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url="", user=self.user, password=self.password)

    def test_object_should_raise_custom_error_without_user(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if user is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url=self.url, user="", password=self.password)

    def test_object_should_raise_custom_error_without_password(self):
        """Instantiation of ApiConnection object should raise MissingConnectionArgs if password is blank."""
        with self.assertRaises(exceptions.MissingConnectionArgs):
            ApiConnection(host_url=self.url, user=self.user, password="")