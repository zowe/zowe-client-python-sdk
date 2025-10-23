import importlib.util
import os

import json5
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
        config_json = json5.load(open(self.original_file_path))
        schema_json = json5.load(open(self.original_schema_file_path))

        expected = validate(config_json, schema_json)
        result = validate_config_json(self.original_file_path, self.original_schema_file_path, cwd=FIXTURES_PATH)

        self.assertEqual(result, expected)

    def test_validate_config_json_invalid(self):
        """Test validate_config_json with invalid config.json that does not match schema.json"""
        custom_dir = os.path.dirname(FIXTURES_PATH)
        path_to_invalid_config = os.path.join(custom_dir, "invalid.zowe.config.json")
        path_to_invalid_schema = os.path.join(custom_dir, "invalid.zowe.schema.json")

        with open(self.original_file_path, "r") as f:
            original_config = json5.load(f)
        original_config["$schema"] = "invalid.zowe.schema.json"
        original_config["profiles"]["zosmf"]["properties"]["port"] = "10443"
        with open(path_to_invalid_config, "w") as f:
            json5.dump(original_config, f)
        with open(self.original_schema_file_path, "r") as f:
            original_schema = json5.load(f)
        with open(path_to_invalid_schema, "w") as f:
            json5.dump(original_schema, f)
        invalid_config_json = json5.load(open(path_to_invalid_config))
        invalid_schema_json = json5.load(open(path_to_invalid_schema))

        with self.assertRaises(ValidationError) as expected_info:
            validate(invalid_config_json, invalid_schema_json)

        with self.assertRaises(ValidationError) as actual_info:
            validate_config_json(path_to_invalid_config, path_to_invalid_schema, cwd=FIXTURES_PATH)

        self.assertEqual(str(actual_info.exception), str(expected_info.exception))

    def test_validate_config_json_with_block_comments(self):
        """Config with /* block comments */ should load and validate."""
        custom_dir = os.path.dirname(FIXTURES_PATH)
        commented_config_path = os.path.join(custom_dir, "commented.zowe.config.json")
        commented_schema_path = os.path.join(custom_dir, "commented.zowe.schema.json")

        schema_text = """
        {
          /* Top-level block comment in schema */
          "$schema": "http://json-schema.org/draft-07/schema#",
          "type": "object",
          "properties": {
            "$schema": { "type": "string" },
            "profiles": {
              "type": "object",
              "properties": {
                "zosmf": {
                  "type": "object",
                  "properties": {
                    "properties": {
                      "type": "object",
                      "properties": {
                        "host": { "type": "string" },
                        "port": { "type": "integer" }
                      },
                      "required": ["host", "port"]
                    }
                  },
                  "required": ["properties"]
                }
              },
              "required": ["zosmf"]
            }
          },
          "required": ["$schema", "profiles"]
        }
        """

        config_text = """
        {
          /* Block comment before schema reference */
          "$schema": "commented.zowe.schema.json",
          "profiles": {
            /* Block comment inside profiles */
            "zosmf": {
              "properties": {
                "host": "localhost",
                /* Inline block comment between fields */ 
                "port": 10443, /* trailing comma tolerated by JSON5 */
              },
            },
          }
        }
        """

        # Write files to the fake FS
        with open(commented_schema_path, "w", encoding="utf-8") as f:
            f.write(schema_text)
        with open(commented_config_path, "w", encoding="utf-8") as f:
            f.write(config_text)

        loaded_config = json5.load(open(commented_config_path, encoding="utf-8"))
        loaded_schema = json5.load(open(commented_schema_path, encoding="utf-8"))

        expected = validate(loaded_config, loaded_schema)
        result = validate_config_json(commented_config_path, commented_schema_path, cwd=os.path.dirname(commented_config_path))

        self.assertEqual(result, expected)
