import importlib.util
import os

import commentjson
from jsonschema import ValidationError, validate
from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk.validators import validate_config_json

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures")
CWD = os.getcwd()
CRED_DICT: dict = {}
SECURE_CONFIG_PROPS: bytes


def keyring_get_password(serviceName: str, username: str):
    global SECURE_CONFIG_PROPS
    return SECURE_CONFIG_PROPS


def keyring_get_password_exception():
    raise Exception
    
class TestValidateConfigJsonClass(TestCase):
    """Testing the validate_config_json function"""

    def setUp(self):
        self.setUpPyfakefs()
        loader = importlib.util.find_spec("jsonschema")
        module_path = loader.origin
        self.fs.add_real_directory(os.path.dirname(module_path))
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