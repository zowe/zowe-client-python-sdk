"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import os
from unittest import mock

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk import SdkApi, session_constants


class TestSdkApiClass(TestCase):
    """SdkApi class unit tests."""

    def setUp(self):
        """Setup fixtures for SdkApi class."""
        common_props = {"host": "mock-url.com", "port": 443, "protocol": "https", "rejectUnauthorized": True}
        self.basic_props = {**common_props, "user": "Username", "password": "Password"}
        self.bearer_props = {**common_props, "tokenValue": "BearerToken"}
        self.token_props = {**common_props, "tokenType": "MyToken", "tokenValue": "TokenValue"}
        self.cert_props = {**common_props, "rejectUnauthorized": False, "certFile": "cert", "certKeyFile": "certKey"}
        self.default_url = "https://default-api.com/"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of SdkApi class."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertIsInstance(sdk_api, SdkApi)

    def test_object_should_be_instance_with_logger_set_to_false(self):
        """Created object should be instance with logger set to False of SdkApi class."""
        sdk_api = SdkApi(self.basic_props, self.default_url, log=False)
        self.assertEqual(sdk_api.logger.disabled, True)

    @mock.patch("requests.Session.close")
    def test_context_manager_closes_session(self, mock_close_request):

        mock_close_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        with SdkApi(self.basic_props, self.default_url) as api:
            pass

        mock_close_request.assert_called_once()

    @mock.patch("logging.Logger.error")
    def test_session_no_host_logger(self, mock_logger_error: mock.MagicMock):
        props = {}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("Host", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    def test_session_combined_cert_logger(self, mock_logger_error: mock.MagicMock):
        props = {"host": "test", "certFile": "test"}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("certificate key", mock_logger_error.call_args[0][0])

    def test_should_handle_none_auth(self):
        props = {"host": "test"}
        sdk_api = SdkApi(props, self.default_url)
        self.assertEqual(sdk_api.session.password, None)

    def test_should_handle_cert_auth(self):
        props = self.cert_props
        sdk_api = SdkApi(props, self.default_url)
        self.assertEqual(sdk_api.session.cert, (self.cert_props["certFile"], self.cert_props["certKeyFile"]))

    def test_should_handle_basic_auth(self):
        """Created object should handle basic authentication."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BASIC)
        self.assertEqual(
            sdk_api._request_arguments["auth"],
            (self.basic_props["user"], self.basic_props["password"]),
        )

    def test_should_handle_bearer_auth(self):
        """Created object should handle bearer authentication."""
        sdk_api = SdkApi(self.bearer_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BEARER)
        self.assertEqual(
            sdk_api._default_headers["Authorization"],
            "Bearer " + self.bearer_props["tokenValue"],
        )

    def test_should_handle_token_auth(self):
        """Created object should handle token authentication."""
        sdk_api = SdkApi(self.token_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_TOKEN)
        self.assertEqual(
            sdk_api._default_headers["Cookie"],
            self.token_props["tokenType"] + "=" + self.token_props["tokenValue"],
        )

    def test_encode_uri_component(self):
        """Test string is being adjusted to the correct URL parameter"""

        sdk_api = SdkApi(self.basic_props, self.default_url)

        actual_not_empty = sdk_api._encode_uri_component("MY.STRING@.TEST#.$HERE(MBR#NAME)")
        expected_not_empty = "MY.STRING%40.TEST%23.%24HERE(MBR%23NAME)"
        self.assertEqual(actual_not_empty, expected_not_empty)

        actual_wildcard = sdk_api._encode_uri_component("GET.#DS.*")
        expected_wildcard = "GET.%23DS.*"
        self.assertEqual(actual_wildcard, expected_wildcard)

        actual_none = sdk_api._encode_uri_component(None)
        expected_none = None
        self.assertEqual(actual_none, expected_none)

    def test_is_using_apiml(self):
        """Session should be detected as API-ML from a base path or an API-ML token."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertFalse(sdk_api._is_using_apiml())

        base_path_api = SdkApi({**self.basic_props, "basePath": "/api/v1"}, self.default_url)
        self.assertTrue(base_path_api._is_using_apiml())

        token_props = {**self.token_props, "tokenType": session_constants.TOKEN_TYPE_APIML}
        self.assertTrue(SdkApi(token_props, self.default_url)._is_using_apiml())

    def test_encode_uri_path_for_zos_leaves_zosmf_path_unchanged(self):
        """None of the documented z/OS resource special characters require encoding for z/OSMF."""
        sdk_api = SdkApi(self.basic_props, self.default_url)

        self.assertEqual(sdk_api._encode_uri_path_for_zos("MY.DS#NAME$HERE"), "MY.DS#NAME$HERE")
        self.assertEqual(sdk_api._encode_uri_path_for_zos("JOB$0010/JOB00010"), "JOB$0010/JOB00010")

    def test_encode_uri_path_for_zos_encodes_hash_for_apiml(self):
        """API-ML rejects a literal '#' with an HTTP 400 error unless it is encoded."""
        sdk_api = SdkApi({**self.basic_props, "basePath": "/api/v1"}, self.default_url)

        self.assertEqual(sdk_api._encode_uri_path_for_zos("MY.DS#NAME$HERE"), "MY.DS%23NAME$HERE")

    def test_encode_uri_path_for_uss_normalizes_path(self):
        """USS paths should be normalized and stripped of their leading slash."""
        sdk_api = SdkApi(self.basic_props, self.default_url)

        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/user/file"), "u/user/file")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("u/user/file"), "u/user/file")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/user//file"), "u/user/file")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/user/../other"), "u/other")
        # Normalizing against root means .. cannot climb past the service path
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/a/../../../../etc/passwd"), "etc/passwd")

    def test_encode_uri_path_for_uss_encodes_special_characters(self):
        """Characters that z/OSMF rejects should be encoded, and slashes should be preserved."""
        sdk_api = SdkApi(self.basic_props, self.default_url)

        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/my file.txt"), "u/my%20file.txt")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/a%b"), "u/a%25b")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/a+b"), "u/a%2Bb")
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/f?x=1"), "u/f%3Fx=1")
        # API-ML characters stay unencoded on a direct z/OSMF connection
        self.assertEqual(sdk_api._encode_uri_path_for_uss("/u/a#b;c"), "u/a#b;c")

    def test_encode_uri_path_for_uss_encodes_apiml_characters(self):
        """API-ML rejects these characters with an HTTP 400 unless they are encoded."""
        sdk_api = SdkApi({**self.basic_props, "basePath": "/api/v1"}, self.default_url)

        self.assertEqual(
            sdk_api._encode_uri_path_for_uss("/u/a#b;c<d>[e]^{f}|g"),
            "u/a%23b%3Bc%3Cd%3E%5Be%5D%5E%7Bf%7D%7Cg",
        )

    def test_encode_uri_path_for_uss_rejects_unusable_characters(self):
        """Backslashes and double-quotes fail server side either way, so the request is not sent."""
        sdk_api = SdkApi(self.basic_props, self.default_url)

        with self.assertRaises(ValueError) as backslash:
            sdk_api._encode_uri_path_for_uss("/u/a\\b")
        self.assertIn("backslash", str(backslash.exception))

        with self.assertRaises(ValueError) as double_quote:
            sdk_api._encode_uri_path_for_uss('/u/a"b')
        self.assertIn("double-quote", str(double_quote.exception))
