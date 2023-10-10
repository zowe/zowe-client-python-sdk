"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import base64
import commentjson
import importlib.util
import json
import keyring
import os
import shutil
import unittest

from jsonschema import validate, ValidationError, SchemaError
from pyfakefs.fake_filesystem_unittest import TestCase
from unittest import mock
from unittest.mock import patch

from zowe.core_for_zowe_sdk.validators import validate_config_json
from zowe.core_for_zowe_sdk import (
    ApiConnection,
    ConfigFile,
    ProfileManager,
    CredentialManager,
    RequestHandler,
    SdkApi,
    ZosmfProfile,
    exceptions,
    session_constants,
    custom_warnings,
    constants,
)

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
        common_props = {
            "host": "mock-url.com",
            "port": 443,
            "protocol": "https",
            "rejectUnauthorized": True
        }
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

        actual_not_empty = sdk_api._encode_uri_component('MY.STRING@.TEST#.$HERE(MBR#NAME)')
        expected_not_empty = 'MY.STRING%40.TEST%23.%24HERE(MBR%23NAME)'
        self.assertEqual(actual_not_empty, expected_not_empty)

        actual_wildcard = sdk_api._encode_uri_component('GET.#DS.*')
        expected_wildcard = 'GET.%23DS.*'
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

    @mock.patch("requests.Session.send")
    def test_perform_streamed_request(self, mock_send_request):
        """Performing a streamed request should call 'send_request' method"""
        mock_send_request.return_value = mock.Mock(status_code=200)
        request_handler = RequestHandler(self.session_arguments)
        request_handler.perform_streamed_request("GET", {"url": "https://www.zowe.org"})
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

class TestZosmfProfileManager(TestCase):
    """ProfileManager class unit tests."""

    def setUp(self):
        """Setup fixtures for ZosmfProfile class."""
        # setup pyfakefs
        self.session_arguments = {"verify": False}
        self.setUpPyfakefs()
        self.original_file_path = os.path.join(FIXTURES_PATH, "zowe.config.json")
        self.original_user_file_path = os.path.join(
            FIXTURES_PATH, "zowe.config.user.json"
        )
        self.original_invalid_file_path = os.path.join(
            FIXTURES_PATH, "invalid.zowe.config.json"
        )
        self.original_nested_file_path = os.path.join(
            FIXTURES_PATH, "nested.zowe.config.json"
        )
        self.original_schema_file_path = os.path.join(
            FIXTURES_PATH, "zowe.schema.json"
        )
        self.original_invalid_schema_file_path = os.path.join(
            FIXTURES_PATH, "invalid.zowe.schema.json"
        )
        self.original_invalidUri_file_path = os.path.join(
            FIXTURES_PATH, "invalidUri.zowe.config.json"
        )
        self.original_invalidUri_schema_file_path = os.path.join(
            FIXTURES_PATH, "invalidUri.zowe.schema.json"
        )

        loader = importlib.util.find_spec('jsonschema')
        module_path = loader.origin
        self.fs.add_real_directory(os.path.dirname(module_path))

        self.fs.add_real_file(self.original_file_path)
        self.fs.add_real_file(self.original_user_file_path)
        self.fs.add_real_file(self.original_nested_file_path)
        self.fs.add_real_file(self.original_schema_file_path)
        self.fs.add_real_file(self.original_invalid_file_path)
        self.fs.add_real_file(self.original_invalid_schema_file_path)
        self.fs.add_real_file(self.original_invalidUri_file_path)
        self.fs.add_real_file(self.original_invalidUri_schema_file_path)
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

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_autodiscovery_and_base_profile_loading(self, get_pass_func):
        """
        Test loading of correct file by autodiscovering from current working directory
        also load by profile_type correctly populating fields from base profile
        and secure credentials
        """

        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        os.chdir(CWD)
        shutil.copy(self.original_file_path, cwd_up_file_path)

        self.setUpCreds(cwd_up_file_path, {
            "profiles.base.properties.user": "user",
            "profiles.base.properties.password": "password",
        })

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

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_custom_file_and_custom_profile_loading(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, self.custom_filename)
        shutil.copy(self.original_file_path, custom_file_path)

        self.setUpCreds(custom_file_path, {
            "profiles.zosmf.properties.user": "user",
            "profiles.zosmf.properties.password": "password",
        })

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

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_custom_file_and_custom_profile_loading_with_nested_profile(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, self.custom_filename)
        shutil.copy(self.original_nested_file_path, custom_file_path)

        self.setUpCreds(custom_file_path, {
            "profiles.zosmf.properties.user": "user",
            "profiles.zosmf.properties.password": "password",
        })

        # Test
        prof_manager = ProfileManager(appname=self.custom_appname)
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="lpar1.zosmf", validate_schema=False)
        self.assertEqual(prof_manager.config_filepath, custom_file_path)

        expected_props = {
            "host": "example1.com",
            "rejectUnauthorized": True,
            "port": 443
        }
        self.assertEqual(props, expected_props)

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_user_overriden_properties(self, get_pass_func):
        """
        Test overriding of properties from user config,
        also load by profile_name correctly populating fields from base profile
        and secure credentials
        """

        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        os.chdir(CWD)
        shutil.copy(self.original_file_path, cwd_up_file_path)
        shutil.copy(self.original_user_file_path, cwd_up_dir_path)

        self.setUpCreds(cwd_up_file_path, {
            "profiles.zosmf.properties.user": "user",
            "profiles.zosmf.properties.password": "password",
        })

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

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_exception(self, get_pass_func):
        """
        Test correct exceptions are being thrown when a profile is
        not found.

        Only the filename will be set
        """
        with self.assertWarns(custom_warnings.ProfileNotFoundWarning):
            # Setup
            cwd_up_dir_path = os.path.dirname(CWD)
            cwd_up_file_path = os.path.join(
                cwd_up_dir_path, f"{self.custom_appname}.config.json"
            )
            os.chdir(CWD)
            shutil.copy(self.original_file_path, cwd_up_file_path)

            # Test
            config_file = ConfigFile(name=self.custom_appname, type="team_config")
            props: dict = config_file.get_profile(profile_name="non_existent_profile", validate_schema=False)

    @patch("keyring.get_password", side_effect=keyring_get_password_exception)
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
            props: dict = prof_manager.load("base")

    @patch("keyring.get_password", side_effect=keyring_get_password)
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

    @patch("sys.platform", "win32")
    @patch("zowe.core_for_zowe_sdk.CredentialManager._retrieve_credential")
    def test_load_secure_props(self, retrieve_cred_func):
        """
        Test loading secure_props from keyring or storage.
        """
        service_name = constants["ZoweServiceName"]
        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        os.chdir(CWD)
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path:
            {
            "profiles.base.properties.user": "user",
            "profiles.base.properties.password": "password"
            }
        }
        self.setUpCreds(cwd_up_file_path, credential)
        base64_encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        encoded_credential = base64_encoded_credential.encode('utf-16le').decode()
        retrieve_cred_func.return_value = encoded_credential

        # call the load_secure_props method
        credential_manager = CredentialManager()
        credential_manager.load_secure_props()
        retrieve_cred_func.assert_called_once_with(service_name)
        # Verify the secure_props
        expected_secure_props = credential
        self.assertEqual(credential_manager.secure_props, expected_secure_props)

    @patch("sys.platform", "win32")
    @patch("keyring.delete_password")
    def test_delete_credential(self, delete_pass_func):
        """
        Test the delete_credential method for deleting credentials from keyring.
        """
        def side_effect(*args, **kwargs):
            if side_effect.counter < 2:
                side_effect.counter += 1
                raise keyring.errors.PasswordDeleteError
            else:
                return None
        side_effect.counter = 0

        # custom side effect function for the mock
        delete_pass_func.side_effect = side_effect
        credential_manager = CredentialManager()
        service_name = constants['ZoweServiceName']
        account_name = constants['ZoweAccountName']
        # Delete the credential
        credential_manager.delete_credential(service_name, account_name)
        expected_calls = [
            mock.call(service_name, account_name),
            mock.call(f"{service_name}-1", f"{account_name}-1"),
        ]
        delete_pass_func.assert_has_calls(expected_calls)

    @patch("sys.platform", "win32")
    @patch("keyring.get_password", side_effect=["password", None, "part1", "part2\0", None])
    def test_retrieve_credential(self, get_pass_func):
        """
        Test the _retrieve_credential method for retrieving credentials from keyring.
        """
        credential_manager = CredentialManager()
        service_name = f"{constants['ZoweServiceName']}/{constants['ZoweAccountName']}"

        # Scenario 1: Retrieve password directly
        expected_password1 = "password".encode('utf-16le').decode()
        expected_password1 = expected_password1[:-1]
        retrieve_credential1 = credential_manager._retrieve_credential(constants['ZoweServiceName'])
        self.assertEqual(retrieve_credential1, expected_password1)
        get_pass_func.assert_called_with(service_name, constants["ZoweAccountName"])

        # Scenario 2: Retrieve password in parts
        expected_password2 = "part1part2".encode('utf-16le').decode()
        retrieve_credential2 = credential_manager._retrieve_credential(constants['ZoweServiceName'])
        retrieve_credential2 = retrieve_credential2[:-1]
        self.assertEqual(retrieve_credential2, expected_password2)
        get_pass_func.assert_any_call(service_name, constants["ZoweAccountName"])
        get_pass_func.assert_any_call(f"{service_name}-1", f"{constants['ZoweAccountName']}-1")
        get_pass_func.assert_any_call(f"{service_name}-2", f"{constants['ZoweAccountName']}-2")

    @patch("sys.platform", "win32")
    @patch("keyring.get_password", side_effect=[None,None])
    def test_retrieve_credential_encoding_errors(self, get_pass_func):
        """
        Test the _retrieve_credential method for handling encoding errors and None values.
        """
        service_name = f"{constants['ZoweServiceName']}/{constants['ZoweAccountName']}"
        result=CredentialManager._retrieve_credential(constants['ZoweServiceName'])
        self.assertIsNone(result)
        get_pass_func.assert_called_with(f"{service_name}-1", f"{constants['ZoweAccountName']}-1")


    @patch("sys.platform", "win32")
    @patch("keyring.set_password")
    @patch("zowe.core_for_zowe_sdk.CredentialManager._retrieve_credential")
    @patch("zowe.core_for_zowe_sdk.CredentialManager.delete_credential")
    def test_save_secure_props_normal_credential(self, delete_pass_func, retrieve_cred_func, set_pass_func):
        """
        Test the save_secure_props method for saving credentials to keyring.
        """

        # Set up mock values and expected results
        service_name = constants["ZoweServiceName"] + "/" + constants["ZoweAccountName"]
        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        os.chdir(CWD)
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path:
            {
            "profiles.base.properties.user": "samadpls",
            "profiles.base.properties.password": "password"
            }
        }
        self.setUpCreds(cwd_up_file_path,credential)
        encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        retrieve_cred_func.return_value = None

        CredentialManager.secure_props =  credential
        CredentialManager.save_secure_props()
        # delete the existing credential
        delete_pass_func.return_value = None
        # Verify the keyring function call
        set_pass_func.assert_called_once_with(
            service_name,
            constants['ZoweAccountName'],
            encoded_credential
        )

    @patch("sys.platform", "win32")
    @patch("zowe.core_for_zowe_sdk.CredentialManager._retrieve_credential")
    @patch("keyring.set_password")
    @patch("zowe.core_for_zowe_sdk.CredentialManager.delete_credential")
    def test_save_secure_props_exceed_limit(self, delete_pass_func, set_pass_func, retrieve_cred_func):

        # Set up mock values and expected results
        service_name = constants["ZoweServiceName"] + "/" + constants["ZoweAccountName"]
        # Setup - copy profile to fake filesystem created by pyfakefs
        cwd_up_dir_path = os.path.dirname(CWD)
        cwd_up_file_path = os.path.join(cwd_up_dir_path, "zowe.config.json")
        os.chdir(CWD)
        shutil.copy(self.original_file_path, cwd_up_file_path)
        credential = {
            cwd_up_file_path:
            {
            "profiles.base.properties.user": "user",
            "profiles.base.properties.password": "a" * (constants["WIN32_CRED_MAX_STRING_LENGTH"] + 1)
            }
        }
        self.setUpCreds(cwd_up_file_path, credential)
        base64_encoded_credential = base64.b64encode(commentjson.dumps(credential).encode()).decode()
        base64_encoded_credential+='\0'
        encoded_credential = base64_encoded_credential.encode('utf-16le').decode()
        retrieve_cred_func.return_value = encoded_credential

        CredentialManager.secure_props =  credential
        CredentialManager.save_secure_props()

        # delete the existing credential
        delete_pass_func.return_value = None

        expected_calls = []
        chunk_size = constants["WIN32_CRED_MAX_STRING_LENGTH"]
        chunks = [base64_encoded_credential[i: i + chunk_size] for i in range(0, len(base64_encoded_credential), chunk_size)]
        for index, chunk in enumerate(chunks, start=1):
            field_name = f"{constants['ZoweAccountName']}-{index}"
            service_names = f"{service_name}-{index}"
            password=(chunk + '\0' *(len(chunk)%2)).encode().decode('utf-16le')
            expected_calls.append(mock.call(
                service_names,
                field_name,
                password
            ))
        set_pass_func.assert_has_calls(expected_calls)

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_valid_schema(self, get_pass_func):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
        shutil.copy(self.original_nested_file_path, custom_file_path)
        shutil.copy(self.original_schema_file_path, self.custom_dir)
        os.chdir(self.custom_dir)

        self.setUpCreds(custom_file_path, {
            "profiles.zosmf.properties.user": "user",
            "profiles.zosmf.properties.password": "password",
        })

        # Test
        prof_manager = ProfileManager(appname="zowe")
        prof_manager.config_dir = self.custom_dir
        props: dict = prof_manager.load(profile_name="zosmf")

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_invalid_schema(self, get_pass_func):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        with self.assertRaises(ValidationError):
            custom_file_path = os.path.join(self.custom_dir, "invalid.zowe.config.json")
            # shutil.copy(self.original_invalid_file_path, custom_file_path)
            # shutil.copy(self.original_invalid_schema_file_path, self.custom_dir)
            os.chdir(self.custom_dir)
            with open(self.original_file_path, 'r') as f:
                original_config = commentjson.load(f)
            original_config["$schema"] = "./invalid.zowe.schema.json"
            with open(os.path.join(self.custom_dir, "invalid.zowe.config.json"), 'w') as f:
                commentjson.dump(original_config, f)

            self.setUpCreds(custom_file_path, {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            })

            # Test
            prof_manager = ProfileManager(appname="invalid.zowe")
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load(profile_name="zosmf", validate_schema=True)

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_invalid_schema_internet_URI(self, get_pass_func):
        """
        Test Validation, no error should be raised for valid schema
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        with self.assertRaises(SchemaError):
            custom_file_path = os.path.join(self.custom_dir, "invalidUri.zowe.config.json")
            shutil.copy(self.original_invalidUri_file_path, custom_file_path)
            shutil.copy(self.original_invalidUri_schema_file_path, self.custom_dir)
            os.chdir(self.custom_dir)

            self.setUpCreds(custom_file_path, {
                "profiles.zosmf.properties.user": "user",
                "profiles.zosmf.properties.password": "password",
            })

            # Test
            prof_manager = ProfileManager(appname="invalidUri.zowe")
            prof_manager.config_dir = self.custom_dir
            props: dict = prof_manager.load(profile_name="zosmf", validate_schema=True)

    @patch("keyring.get_password", side_effect=keyring_get_password)
    def test_profile_loading_with_env_variables(self, get_pass_func):
        """
        Test loading of correct file given a filename and directory,
        also load by profile_name correctly populating fields from custom
        profile and secure credentials
        """
        # Setup - copy profile to fake filesystem created by pyfakefs
        os.environ["ZOWE_OPT_HOST"] = "aaditya"
        custom_file_path = os.path.join(self.custom_dir, "zowe.config.json")
        shutil.copy(self.original_nested_file_path, custom_file_path)
        shutil.copy(self.original_schema_file_path, self.custom_dir)
        os.chdir(self.custom_dir)

        self.setUpCreds(custom_file_path, {
            "profiles.zosmf.properties.user": "user",
            "profiles.zosmf.properties.password": "password",
        })

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



class TestValidateConfigJsonClass(unittest.TestCase):
    """Testing the validate_config_json function"""

    def test_validate_config_json_valid(self):
        """Test validate_config_json with valid config.json matching schema.json"""
        path_to_config = FIXTURES_PATH + "/zowe.config.json"
        path_to_schema = FIXTURES_PATH + "/zowe.schema.json"

        config_json = commentjson.load(open(path_to_config))
        schema_json = commentjson.load(open(path_to_schema))

        expected = validate(config_json, schema_json)
        result = validate_config_json(path_to_config, path_to_schema, cwd = FIXTURES_PATH)

        self.assertEqual(result, expected)

    def test_validate_config_json_invalid(self):
        """Test validate_config_json with invalid config.json that does not match schema.json"""
        path_to_invalid_config = FIXTURES_PATH + "/invalid.zowe.config.json"
        path_to_invalid_schema = FIXTURES_PATH + "/invalid.zowe.schema.json"

        invalid_config_json = commentjson.load(open(path_to_invalid_config))
        invalid_schema_json = commentjson.load(open(path_to_invalid_schema))

        with self.assertRaises(ValidationError) as expected_info:
            validate(invalid_config_json, invalid_schema_json)

        with self.assertRaises(ValidationError) as actual_info:
            validate_config_json(path_to_invalid_config, path_to_invalid_schema, cwd = FIXTURES_PATH)

        self.assertEqual(str(actual_info.exception), str(expected_info.exception))
