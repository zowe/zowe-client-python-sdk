import sys
import unittest
from unittest.mock import Mock
from unittest.mock import patch
from zeepy.utilities import RequestHandler
from zeepy.utilities.exceptions import InvalidRequestMethod
from zeepy.utilities.exceptions import RequestFailed
from zeepy.utilities.exceptions import UnexpectedStatus
from requests import Session

sys.path.append("..")
test_object = RequestHandler({'verify': False})


class TestRequestHandler(unittest.TestCase):

    def test_validate_method_raised_error_when_method_is_invalid(self):
        test_object.method = 'A'
        self.assertRaises(InvalidRequestMethod, test_object.validate_method)

    def test_validate_response_raise_error_when_status_code_is_unexpected(self):
        test_object.response = Mock()
        test_object.expected_code = '200'
        test_object.response.status_code = '400'
        self.assertRaises(UnexpectedStatus, test_object.validate_response)
