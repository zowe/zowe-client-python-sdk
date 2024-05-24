"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import base64
import importlib.util
import json
import os
import shutil
import unittest
from unittest import mock
import logging

import commentjson
from jsonschema import SchemaError, ValidationError, validate
from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk import (
    ApiConnection,
    ConfigFile,
    CredentialManager,
    ProfileManager,
    RequestHandler,
    SdkApi,
    ZosmfProfile,
    constants,
    custom_warnings,
    exceptions,
    session_constants,
    logger
)
from zowe.core_for_zowe_sdk.validators import validate_config_json
from zowe.secrets_for_zowe_sdk import keyring

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
CWD = os.getcwd()
CRED_DICT: dict = {}
SECURE_CONFIG_PROPS: bytes


def keyring_get_password(serviceName: str, username: str):
    global SECURE_CONFIG_PROPS
    return SECURE_CONFIG_PROPS


def keyring_get_password_exception():
    raise Exception


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


class TestSdkApiClass(TestCase):
    """SdkApi class unit tests."""

    def setUp(self):
        """Setup fixtures for SdkApi class."""
        common_props = {"host": "mock-url.com", "port": 443, "protocol": "https", "rejectUnauthorized": True}
        self.basic_props = {**common_props, "user": "Username", "password": "Password"}
        self.bearer_props = {**common_props, "tokenValue": "BearerToken"}
        self.token_props = {
            **common_props,
            "tokenType": "MyToken",
            "tokenValue": "TokenValue",
        }
        self.default_url = "https://default-api.com/"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of SdkApi class."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertIsInstance(sdk_api, SdkApi)

    @mock.patch("logging.Logger.error")
    def test_session_no_host_logger(self, mock_logger_error: mock.MagicMock):
        props = {}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("Host", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    def test_session_no_authentication_logger(self, mock_logger_error: mock.MagicMock):
        props = {"host": "test"}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("Authentication", mock_logger_error.call_args[0][0])

    def test_should_handle_basic_auth(self):
        """Created object should handle basic authentication."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BASIC)
        self.assertEqual(
            sdk_api.request_arguments["auth"],
            (self.basic_props["user"], self.basic_props["password"]),
        )

    def test_should_handle_bearer_auth(self):
        """Created object should handle bearer authentication."""
        sdk_api = SdkApi(self.bearer_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BEARER)
        self.assertEqual(
            sdk_api.default_headers["Authorization"],
            "Bearer " + self.bearer_props["tokenValue"],
        )

    def test_should_handle_token_auth(self):
        """Created object should handle token authentication."""
        sdk_api = SdkApi(self.token_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_TOKEN)
        self.assertEqual(
            sdk_api.default_headers["Cookie"],
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
    def test_perform_streamed_request(self, mock_send_request, mock_logger_error: mock.MagicMock, mock_logger_debug: mock.MagicMock):
        """Performing a streamed request should call 'send_request' method"""
        mock_send_request.return_value = mock.Mock(status_code=200)
        request_handler = RequestHandler(self.session_arguments)
        request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, stream = True)

        mock_logger_error.assert_not_called()
        mock_logger_debug.assert_called()

        #
        # # This will fail because parameter also contains the arguments of perform_request
        # mock_logger_debug.assert_called_with("Request method: GET")
        #
        #  But this will pass because we are partially looking for the request method in the first argument
        self.assertIn("Request method: GET", mock_logger_debug.call_args[0][0])

        mock_send_request.assert_called_once()
        self.assertTrue(mock_send_request.call_args[1]["stream"])


    @mock.patch("logging.Logger.error")
    def test_logger_unmatched_status_code(self, mock_logger_error: mock.MagicMock):
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, expected_code= [0], stream = True)
        except exceptions.UnexpectedStatus:
            mock_logger_error.assert_called_once()
            self.assertIn("The status code", mock_logger_error.call_args[0][0])
    
    @mock.patch("logging.Logger.error")
    def test_logger_perform_request_invalid_method(self, mock_logger_error: mock.MagicMock):
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("Invalid method", {"url": "https://www.zowe.org"}, stream = True)
        except exceptions.InvalidRequestMethod:
            mock_logger_error.assert_called_once()
            self.assertIn("Invalid HTTP method input", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    @mock.patch("requests.Session.send")
    def test_logger_invalid_status_code(self, mock_send_request, mock_logger_error: mock.MagicMock):
        mock_send_request.return_value = mock.Mock(ok=False)
        request_handler = RequestHandler(self.session_arguments)
        try:
            request_handler.perform_request("GET", {"url": "https://www.zowe.org"}, stream = True)
        except exceptions.RequestFailed:
            mock_logger_error.assert_called_once()
            self.assertIn("HTTP Request has failed", mock_logger_error.call_args[0][0])
        mock_logger_error.assert_called_once


class TestZosmfProfileClass(unittest.TestCase):
    """ZosmfProfile class unit tests."""

    def setUp(self):
        """Setup fixtures for ZosmfProfile class."""
        self.profile_name = "MOCK"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of ZosmfProfile class."""
        zosmf_profile = ZosmfProfile(self.profile_name)
        self.assertIsInstance(zosmf_profile, ZosmfProfile)


class TestZosmfProfileManager(TestCase):
    """ProfileManager class unit tests."""

    def setUp(self):
        """Setup fixtures for ZosmfProfile class."""
        # setup pyfakefs
        self.session_arguments = {"verify": False}
        self.setUpPyfakefs()
        self.original_file_path = os.path.join(FIXTURES_PATH, "zowe.config.json")
        self.original_user_file_path = os.path.join(FIXTURES_PATH, "zowe.config.user.json")
        self.original_nested_file_path = os.path.join(FIXTURES_PATH, "nested.zowe.config.json")
        self.original_nested_user_file_path = os.path.join(FIXTURES_PATH, "nested.zowe.config.user.json")
        self.original_schema_file_path = os.path.join(FIXTURES_PATH, "zowe.schema.json")

        loader = importlib.util.find_spec("jsonschema")
        module_path = loader.origin
        self.fs.add_real_directory(os.path.dirname(module_path))

        self.fs.add_real_file(self.original_file_path)
        self.fs.add_real_file(self.original_user_file_path)
        self.fs.add_real_file(self.original_nested_file_path)
        self.fs.add_real_file(self.original_nested_user_file_path)
        self.fs.add_real_file(self.original_schema_file_path)
        self.custom_dir = os.path.dirname(FIXTURES_PATH)
        self.custom_appname = "zowe_abcd"
        self.custom_filename = f"{self.custom_appname}.config.json"

        # setup keyring
        home = os.path.expanduser("~")
        self.global_config_path = os.path.join(home, ".zowe", "zowe.config.json")

    def setUpCreds(self, file_path, secure_props):
        global CRED_DICT
        # we are not storing global config properties since they are not
        # accessible within pyfakefs
        # todo : add a test that check loading from gloabl config path
        CRED_DICT = {
            file_path: secure_props,
        }

        global SECURE_CONFIG_PROPS
        SECURE_CONFIG_PROPS = base64.b64encode((json.dumps(CRED_DICT)).encode()).decode()

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_autodiscovery_and_base_profile_loading(self, get_pass_func):
        """
        Test loading of correct file by autodiscovering from current working directory
        also load by profile_type correctly populating fields from base profile
        and secure credentials
        """

        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)

        self.setUpCreds(
            cwd_up_file_path,
            {
                "profiles.base.properties.user": "user",
                "profiles.base.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager()
        props: dict = prof_manager.load(profile_type="base", validate_schema=False)
        self.assertEqual(prof_manager.config_filepath, cwd_up_file_path)

        expected_props = {
            "host": "zowe.test.cloud",
            "rejectUnauthorized": False,
            "user": "user",
            "password": "password",
        }
        self.assertEqual(props, expected_props)

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_custom_file_and_custom_profile_loading(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, self.custom_filename)
        shutil.copy(self.original_file_path, custom_file_path)

        self.setUpCreds(
            custom_file_path,
            {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager(appname=self.custom_appname)
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="zosmf", validate_schema=False)
        self.assertEqual(prof_manager.config_filepath, custom_file_path)

        expected_props = {
            "host": "zowe.test.cloud",
            "rejectUnauthorized": False,
            "user": "user",
            "password": "password",
            "port": 10443,
        }
        self.assertEqual(props, expected_props)

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_custom_file_and_custom_profile_loading_with_nested_profile(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, self.custom_filename)
        shutil.copy(self.original_nested_file_path, custom_file_path)
        shutil.copy(self.original_nested_user_file_path, custom_file_path.replace(".json", ".user.json"))

        self.setUpCreds(
            custom_file_path,
            {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager(appname=self.custom_appname)
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="lpar1.zosmf", validate_schema=False)
        self.assertEqual(prof_manager.config_filepath, custom_file_path)

        expected_props = {
            "host": "example1.com",
            "rejectUnauthorized": True,
            "port": 443,
            "user": "admin",
            "password": "password1",
        }
        self.assertEqual(props, expected_props)

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_user_overridden_properties(self, get_pass_func):
        """
        Test overriding of properties from user config,
        also load by profile_name correctly populating fields from base profile
        and secure credentials
        """

        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        shutil.copy(self.original_user_file_path, cwd_up_file_path.replace(".json", ".user.json"))

        self.setUpCreds(
            cwd_up_file_path,
            {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager()
        props: dict = prof_manager.load(profile_type="zosmf", validate_schema=False)
        self.assertEqual(prof_manager.config_filepath, cwd_up_file_path)

        expected_props = {
            "host": "zowe.test.user.cloud",
            "rejectUnauthorized": False,
            "user": "user",
            "password": "password",
            "port": 10000,
        }
        self.assertEqual(props, expected_props)

    @mock.patch("logging.Logger.warning")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_exception(self, get_pass_func, mock_logger_warning: mock.MagicMock):
        """
        Test correct exceptions are being thrown when a profile is
        not found.

        Only the filename will be set
        """
        with self.assertWarns(custom_warnings.ProfileNotFoundWarning):
            # Setup
            cwd_up_dir_path = os.path.dirname(CWD)
            cwd_up_file_path = os.path.join(cwd_up_dir_path, f"{self.custom_appname}.config.json")
            shutil.copy(self.original_file_path, cwd_up_file_path)

            # Test
            config_file = ConfigFile(name=self.custom_appname, type="team_config")
            props: dict = config_file.get_profile(profile_name="non_existent_profile", validate_schema=False)
            mock_logger_warning.assert_called()

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password_exception)
    def test_secure_props_loading_warning(self, get_pass_func):
        """
        Test correct warnings are being thrown when secure properties
        are not found in keyring.

        Only the config folder will be set
        """
        with self.assertWarns(custom_warnings.SecurePropsNotFoundWarning):
            # Setup
            custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
            shutil.copy(self.original_file_path, custom_file_path)

            # Test
            prof_manager = ProfileManager()
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load("base", validate_schema=False)

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_not_found_warning(self, get_pass_func):
        """
        Test correct warnings are being thrown when profile is not found
        in config file.

        Only the config folder will be set
        """
        with self.assertWarns(custom_warnings.ProfileNotFoundWarning):
            # Setup
            custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
            shutil.copy(self.original_file_path, custom_file_path)

            # Test
            prof_manager = ProfileManager()
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load("non_existent_profile", validate_schema=False)

    @mock.patch("sys.platform", "win32")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._get_credential")
    def test_load_secure_props(self, retrieve_cred_func):
        """
        Test loading secure_props from keyring or storage.
        """
        service_name = constants["ZoweServiceName"]
        account_name = constants["ZoweAccountName"]
        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path: {"profiles.base.properties.user": "user", "profiles.base.properties.password": "password"}
        }
        self.setUpCreds(cwd_up_file_path, credential)
        encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        retrieve_cred_func.return_value = encoded_credential

        # call the load_secure_props method
        credential_manager = CredentialManager()
        credential_manager.load_secure_props()
        retrieve_cred_func.assert_called_once_with(service_name, account_name)
        # Verify the secure_props
        expected_secure_props = credential
        self.assertEqual(credential_manager.secure_props, expected_secure_props)

    @mock.patch("sys.platform", "win32")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.delete_password")
    def test_delete_credential(self, delete_pass_func):
        """
        Test the delete_credential method for deleting credentials from keyring.
        """

        def side_effect(*args, **kwargs):
            if side_effect.counter < 2:
                side_effect.counter += 1
                return False
            else:
                return True

        side_effect.counter = 0

        # custom side effect function for the mock
        delete_pass_func.side_effect = side_effect
        credential_manager = CredentialManager()
        service_name = constants["ZoweServiceName"]
        account_name = constants["ZoweAccountName"]
        # Delete the credential
        credential_manager._delete_credential(service_name, account_name)
        expected_calls = [
            mock.call(service_name, account_name),
            mock.call(service_name, f"{account_name}-1"),
        ]
        delete_pass_func.assert_has_calls(expected_calls)

    @mock.patch("sys.platform", "win32")
    @mock.patch(
        "zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=["password", None, "part1", "part2\0", None]
    )
    def test_retrieve_credential(self, get_pass_func):
        """
        Test the _retrieve_credential method for retrieving credentials from keyring.
        """
        credential_manager = CredentialManager()

        # Scenario 1: Retrieve password directly
        expected_password1 = "password"
        retrieve_credential1 = credential_manager._get_credential(
            constants["ZoweServiceName"], constants["ZoweAccountName"]
        )
        self.assertEqual(retrieve_credential1, expected_password1)
        get_pass_func.assert_called_with(constants["ZoweServiceName"], constants["ZoweAccountName"])

        # Scenario 2: Retrieve password in parts
        expected_password2 = "part1part2"
        retrieve_credential2 = credential_manager._get_credential(
            constants["ZoweServiceName"], constants["ZoweAccountName"]
        )
        self.assertEqual(retrieve_credential2, expected_password2)
        get_pass_func.assert_any_call(constants["ZoweServiceName"], constants["ZoweAccountName"])
        get_pass_func.assert_any_call(constants["ZoweServiceName"], f"{constants['ZoweAccountName']}-1")
        get_pass_func.assert_any_call(constants["ZoweServiceName"], f"{constants['ZoweAccountName']}-2")

    @mock.patch("sys.platform", "win32")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=[None, None])
    def test_retrieve_credential_encoding_errors(self, get_pass_func):
        """
        Test the _retrieve_credential method for handling encoding errors and None values.
        """
        result = CredentialManager._get_credential(constants["ZoweServiceName"], constants["ZoweAccountName"])
        self.assertIsNone(result)
        get_pass_func.assert_called_with(constants["ZoweServiceName"], f"{constants['ZoweAccountName']}-1")

    @mock.patch("sys.platform", "win32")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._set_credential")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._get_credential")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._delete_credential")
    def test_save_secure_props_normal_credential(self, delete_pass_func, retrieve_cred_func, set_pass_func):
        """
        Test the save_secure_props method for saving credentials to keyring.
        """

        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path: {
                "profiles.base.properties.user": "samadpls",
                "profiles.base.properties.password": "password",
            }
        }
        self.setUpCreds(cwd_up_file_path, credential)
        encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        retrieve_cred_func.return_value = None

        CredentialManager.secure_props = credential
        CredentialManager.save_secure_props()
        # delete the existing credential
        delete_pass_func.return_value = None
        # Verify the keyring function call
        set_pass_func.assert_called_once_with(
            constants["ZoweServiceName"], constants["ZoweAccountName"], encoded_credential
        )

    @mock.patch("sys.platform", "win32")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._get_credential")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.set_password")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager._delete_credential")
    def test_save_secure_props_exceed_limit(self, delete_pass_func, set_pass_func, retrieve_cred_func):
        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path: {
                "profiles.base.properties.user": "user",
                "profiles.base.properties.password": "a" * (constants["WIN32_CRED_MAX_STRING_LENGTH"] + 1),
            }
        }
        self.setUpCreds(cwd_up_file_path, credential)
        encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        encoded_credential += "\0"
        retrieve_cred_func.return_value = encoded_credential

        CredentialManager.secure_props = credential
        CredentialManager.save_secure_props()

        # delete the existing credential
        delete_pass_func.return_value = None

        expected_calls = []
        chunk_size = constants["WIN32_CRED_MAX_STRING_LENGTH"]
        chunks = [encoded_credential[i : i + chunk_size] for i in range(0, len(encoded_credential), chunk_size)]
        for index, chunk in enumerate(chunks, start=1):
            field_name = f"{constants['ZoweAccountName']}-{index}"
            expected_calls.append(mock.call(constants["ZoweServiceName"], field_name, chunk))
        set_pass_func.assert_has_calls(expected_calls)

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_valid_schema(self, get_pass_func):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
        shutil.copy(self.original_nested_file_path, custom_file_path)
        shutil.copy(self.original_schema_file_path, self.custom_dir)

        self.setUpCreds(
            custom_file_path,
            {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager(appname="zowe")
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="zosmf")

    @mock.patch("logging.Logger.error")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_invalid_schema(self, get_pass_func, mock_logger_error: mock.MagicMock):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        with self.assertRaises(ValidationError):
            custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
            with open(self.original_file_path, "r") as f:
                original_config = commentjson.load(f)
            original_config["$schema"] = "invalid.zowe.schema.json"
            original_config["profiles"]["zosmf"]["properties"]["port"] = "10443"
            with open(os.path.join(self.custom_dir, "invalid.zowe.config.json"), "w") as f:
                commentjson.dump(original_config, f)
            with open(self.original_schema_file_path, "r") as f:
                original_schema = commentjson.load(f)
            with open(os.path.join(self.custom_dir, "invalid.zowe.schema.json"), "w") as f:
                commentjson.dump(original_schema, f)
            self.setUpCreds(
                custom_file_path,
                {
                    "profiles.zosmf.properties.user": "user",
                    "profiles.zosmf.properties.password": "password",
                },
            )
            
            # Test
            prof_manager = ProfileManager(appname="invalid.zowe")
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load(profile_name="zosmf", validate_schema=True)
            self.assertIn("Instance was invalid under the provided $schema property", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_invalid_schema_internet_URI(self, get_pass_func, mock_logger_error: mock.MagicMock):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        with self.assertRaises(SchemaError):
            custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
            with open(self.original_file_path, "r") as f:
                original_config = commentjson.load(f)
            original_config["$schema"] = "invalidUri.zowe.schema.json"
            with open(os.path.join(self.custom_dir, "invalidUri.zowe.config.json"), "w") as f:
                commentjson.dump(original_config, f)
            with open(self.original_schema_file_path, "r") as f:
                original_schema = commentjson.load(f)
            original_schema["type"] = "invalid"
            with open(os.path.join(self.custom_dir, "invalidUri.zowe.schema.json"), "w") as f:
                commentjson.dump(original_schema, f)

            self.setUpCreds(
                custom_file_path,
                {
                    "profiles.zosmf.properties.user": "user",
                    "profiles.zosmf.properties.password": "password",
                },
            )

            # Test
            prof_manager = ProfileManager(appname="invalidUri.zowe")
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load(profile_name="zosmf", validate_schema=True)
            self.assertIn("The provided schema is invalid", mock_logger_error.call_args[0][0])

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_env_variables(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        os.environ["ZOWE_OPT_HOST"] = "aaditya"
        custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
        custom_schema_file_path = os.path.join(self.custom_dir, "zowe.schema.json")
        shutil.copy(self.original_nested_file_path, custom_file_path)
        shutil.copy(self.original_schema_file_path, custom_schema_file_path)

        self.setUpCreds(
            custom_file_path,
            {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            },
        )

        # Test
        prof_manager = ProfileManager(appname="zowe")
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="lpar1.zosmf", override_with_env=True)

        expected_props = {
            "host": "aaditya",
            "rejectUnauthorized": True,
            "port": 443,
        }
        self.assertEqual(props, expected_props)

    def test_get_highest_priority_layer(self):
        """
        Test that get_highest_priority_layer returns the highest priority layer with a valid profile data dictionary.
        """
        # Set up mock profiles in the layers
        project_user_config = mock.MagicMock(spec=ConfigFile)
        project_user_config.find_profile.return_value = mock.MagicMock()
        project_user_config.find_profile.return_value.data = {"profiles": "zosmf"}

        # Set up the ProfileManager
        profile_manager = ProfileManager()
        profile_manager.project_user_config = project_user_config
        project_user_config.get_profile_name_from_path.return_value = "zosmf"
        # Call the function being tested
        result_layer = profile_manager.get_highest_priority_layer("zosmf")

        # Assert the results
        self.assertEqual(result_layer, project_user_config)

    @mock.patch("zowe.core_for_zowe_sdk.ProfileManager.get_highest_priority_layer")
    def test_profile_manager_set_property(self, get_highest_priority_layer_mock):
        """
        Test that set_property calls the set_property method of the highest priority layer.
        """
        json_path = "profiles.zosmf.properties.user"
        value = "samadpls"
        secure = True

        # Set up mock for the highest priority layer
        highest_priority_layer_mock = mock.MagicMock(spec=ConfigFile)
        get_highest_priority_layer_mock.return_value = highest_priority_layer_mock

        profile_manager = ProfileManager()

        # Mock the behavior of _set_property method in highest_priority_layer
        highest_priority_layer_mock.set_property.return_value = None

        # Call the method being tested
        profile_manager.set_property(json_path, value, secure)

        # Assert the method calls
        highest_priority_layer_mock.set_property.assert_called_with(json_path, value, secure=secure)

    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile.save")
    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager.save_secure_props")
    def test_profile_manager_save(self, mock_save_secure_props, mock_save):
        """
        Test that save calls the save method of all layers.
        """
        profile_manager = ProfileManager()
        profile_manager.save()
        expected_calls = [mock.call(False) for _ in range(4)]
        mock_save.assert_has_calls(expected_calls)
        mock_save_secure_props.assert_called_once()

    @mock.patch("zowe.core_for_zowe_sdk.ProfileManager.get_highest_priority_layer")
    def test_profile_manager_set_profile(self, get_highest_priority_layer_mock):
        """
        Test that set_profile calls the set_profile method of the highest priority layer.
        """
        profile_path = "profiles.zosmf"
        profile_data = {"properties": {"user": "admin", "password": "password1"}}

        highest_priority_layer_mock = mock.MagicMock(spec=ConfigFile)
        get_highest_priority_layer_mock.return_value = highest_priority_layer_mock
        profile_manager = ProfileManager()

        highest_priority_layer_mock.set_profile.return_value = None
        profile_manager.set_profile(profile_path, profile_data)

        highest_priority_layer_mock.set_profile.assert_called_with(profile_path, profile_data)

    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile.get_profile_path_from_name")
    def test_set_or_create_nested_profile(self, mock_get_profile_path):
        """
        Test that __set_or_create_nested_profile calls the get_profile_path_from_name method and sets the profile data.
        """
        mock_get_profile_path.return_value = "profiles.zosmf"
        config_file = ConfigFile(name="zowe_abcd", type="User Config", profiles={})
        profile_data = {"properties": {"user": "samadpls", "password": "password1"}}
        config_file._ConfigFile__set_or_create_nested_profile("zosmf", profile_data)
        expected_profiles = {"zosmf": {"properties": {"user": "samadpls", "password": "password1"}}}
        self.assertEqual(config_file.profiles, expected_profiles)

    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile.find_profile")
    def test_is_secure(self, mock_find_profile):
        """
        Test that __is_secure returns True if the property is secure and False otherwise.
        """
        config_file = ConfigFile(name="zowe_abcd", type="User Config", profiles={})
        mock_find_profile.return_value = {"properties": {"user": "samadpls"}, "secure": ["password"]}
        is_secure_secure = config_file._ConfigFile__is_secure("zosmf", "password")
        is_secure_non_secure = config_file._ConfigFile__is_secure("zosmf", "user")

        self.assertTrue(is_secure_secure)
        self.assertFalse(is_secure_non_secure)

    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile.get_profile_name_from_path")
    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile.find_profile")
    @mock.patch("zowe.core_for_zowe_sdk.ConfigFile._ConfigFile__is_secure")
    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_config_file_set_property(self, get_pass_func, mock_is_secure, mock_find_profile, mock_get_profile_name):
        """
        Test that set_property calls the __is_secure, find_profile and get_profile_name_from_path methods.
        """
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        self.setUpCreds(cwd_up_file_path, {"profiles.zosmf.properties.user": "admin"})
        config_file = ConfigFile(name="zowe_abcd", type="User Config", profiles={})
        mock_is_secure.return_value = False
        mock_find_profile.return_value = {"properties": {"port": 1443}, "secure": []}
        mock_get_profile_name.return_value = "zosmf"

        config_file.set_property("profiles.zosmf.properties.user", "admin", secure=True)

        mock_is_secure.assert_called_with("zosmf", "user")
        mock_find_profile.assert_called_with("zosmf", config_file.profiles)
        mock_get_profile_name.assert_called_with("profiles.zosmf.properties.user")
        self.assertEqual(
            config_file.profiles, {"zosmf": {"properties": {"port": 1443, "user": "admin"}, "secure": ["user"]}}
        )

    def test_get_profile_name_from_path(self):
        """
        Test that get_profile_name_from_path returns the profile name from the path.
        """
        config_file = ConfigFile(name="zowe_abcd", type="User Config")
        profile_name = config_file.get_profile_name_from_path("profiles.lpar1.profiles.zosmf.properties.user")
        self.assertEqual(profile_name, "lpar1.zosmf")

    def test_get_profile_path_from_name(self):
        """
        Test that get_profile_path_from_name returns the profile path from the name.
        """
        config_file = ConfigFile(name="zowe_abcd", type="User Config")
        profile_path_1 = config_file.get_profile_path_from_name("lpar1.zosmf")
        self.assertEqual(profile_path_1, "profiles.lpar1.profiles.zosmf")

    @mock.patch("zowe.secrets_for_zowe_sdk.keyring.get_password", side_effect=keyring_get_password)
    def test_config_file_set_profile_and_save(self, get_pass_func):
        """
        Test the set_profile method.
        """
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        self.setUpCreds(
            cwd_up_file_path, {"profiles.zosmf.properties.user": "abc", "profiles.zosmf.properties.password": "def"}
        )
        initial_profiles = {"zosmf": {"properties": {"port": 1443}, "secure": []}}
        config_file = ConfigFile("User Config", "zowe.config.json", cwd_up_dir_path, profiles=initial_profiles)
        profile_data = {
            "type": "zosmf",
            "properties": {"port": 443, "user": "abc", "password": "def"},
            "secure": ["user", "password"],
        }

        with mock.patch("zowe.core_for_zowe_sdk.ConfigFile.get_profile_name_from_path", return_value="zosmf"):
            with mock.patch("zowe.core_for_zowe_sdk.ConfigFile.find_profile", return_value=initial_profiles["zosmf"]):
                config_file.set_profile("profiles.zosmf", profile_data)

        expected_profiles = {"zosmf": profile_data}
        self.assertEqual(config_file.profiles, expected_profiles)

        config_file.jsonc = {"profiles": expected_profiles}
        with mock.patch("builtins.open", mock.mock_open()):
            config_file.save(False)

        expected_secure_props = {
            cwd_up_file_path: {"profiles.zosmf.properties.user": "abc", "profiles.zosmf.properties.password": "def"}
        }
        expected_profiles = {
            "zosmf": {
                "type": "zosmf",
                "properties": {
                    "port": 443,
                },
                "secure": ["user", "password"],
            }
        }
        self.assertEqual(CredentialManager.secure_props, expected_secure_props)
        self.assertEqual(config_file.jsonc["profiles"], expected_profiles)

    @mock.patch("zowe.core_for_zowe_sdk.CredentialManager.save_secure_props")
    def test_config_file_save(self, mock_save_secure_props):
        """
        Test saving a config file with secure properties.
        """
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        shutil.copy(self.original_file_path, cwd_up_file_path)
        profile_data = {
            "lpar1": {
                "profiles": {"zosmf": {"properties": {"port": 1443, "password": "secret"}, "secure": ["password"]}},
                "properties": {"host": "example.com", "user": "admin"},
                "secure": ["user"],
            }
        }
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            config_file = ConfigFile("User Config", "zowe.config.json", cwd_up_dir_path, profiles=profile_data)
            config_file.jsonc = {"profiles": profile_data}
            config_file.save()

        mock_save_secure_props.assert_called_once()
        mock_file.assert_called_once_with(cwd_up_file_path, "w")
        mock_file.return_value.write.assert_called()
        self.assertIn("user", profile_data["lpar1"]["properties"])
        self.assertNotIn("user", config_file.jsonc["profiles"]["lpar1"]["properties"])
        self.assertEqual(
            ["port"], list(config_file.jsonc["profiles"]["lpar1"]["profiles"]["zosmf"]["properties"].keys())
        )


class TestValidateConfigJsonClass(TestCase):
    """Testing the validate_config_json function"""

    def setUp(self):
        self.setUpPyfakefs()

        self.original_file_path = os.path.join(FIXTURES_PATH, "zowe.config.json")
        self.original_schema_file_path = os.path.join(FIXTURES_PATH, "zowe.schema.json")
        self.fs.add_real_file(self.original_file_path)
        self.fs.add_real_file(self.original_schema_file_path)

    def test_validate_config_json_valid(self):
        """Test validate_config_json with valid config.json matching schema.json"""
        config_json = commentjson.load(open(self.original_file_path))
        schema_json = commentjson.load(open(self.original_schema_file_path))

        expected = validate(config_json, schema_json)
        result = validate_config_json(self.original_file_path, self.original_schema_file_path, cwd=FIXTURES_PATH)

        self.assertEqual(result, expected)

    def test_validate_config_json_invalid(self):
        """Test validate_config_json with invalid config.json that does not match schema.json"""
        custom_dir = os.path.dirname(FIXTURES_PATH)
        path_to_invalid_config = os.path.join(custom_dir, "invalid.zowe.config.json")
        path_to_invalid_schema = os.path.join(custom_dir, "invalid.zowe.schema.json")

        with open(self.original_file_path, "r") as f:
            original_config = commentjson.load(f)
        original_config["$schema"] = "invalid.zowe.schema.json"
        original_config["profiles"]["zosmf"]["properties"]["port"] = "10443"
        with open(path_to_invalid_config, "w") as f:
            commentjson.dump(original_config, f)
        with open(self.original_schema_file_path, "r") as f:
            original_schema = commentjson.load(f)
        with open(path_to_invalid_schema, "w") as f:
            commentjson.dump(original_schema, f)
        invalid_config_json = commentjson.load(open(path_to_invalid_config))
        invalid_schema_json = commentjson.load(open(path_to_invalid_schema))

        with self.assertRaises(ValidationError) as expected_info:
            validate(invalid_config_json, invalid_schema_json)

        with self.assertRaises(ValidationError) as actual_info:
            validate_config_json(path_to_invalid_config, path_to_invalid_schema, cwd=FIXTURES_PATH)

        self.assertEqual(str(actual_info.exception), str(expected_info.exception))


class test_logger_setLoggerLevel(TestCase):
    
    def test_logger_setLoggerLevel(self):
        test_logging = logger.Log()
        test_value = logging.INFO
        test_logging.setLoggerLevel(test_value)
        self.assertEqual(logging.root.level, test_value)