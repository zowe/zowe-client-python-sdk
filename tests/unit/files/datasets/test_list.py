"""Unit tests for the Zowe Python SDK z/OS Files package."""

from unittest import TestCase, mock

from zowe.zos_files_for_zowe_sdk import Files
from zowe.zos_files_for_zowe_sdk.response.datasets import (
    MemberResponse,
    SimpleMemberResponse,
    UndefRecfmMemberResponse,
)


class TestListClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    @mock.patch("requests.Session.send")
    def test_list_dsn(self, mock_send_request):
        """Test list DSN sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        test_values = [("MY.DSN", False), ("MY.DSN", True)]
        for test_case in test_values:
            Files(self.test_profile).list_dsn(*test_case)
            mock_send_request.assert_called()

    @mock.patch("requests.Session.send")
    def test_list_members_mem_name(self, mock_send_request):
        """Test list members sends request and receives members with member name only"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {
            "items": [{"member": "TEST1"}, {"member": "TEST2"}],
            "returnedRows":1,
            "JSONversion":1
        }

        dataset_name = "TEST.PDS"
        member_pattern = None
        member_start = None
        limit = 1000
        attributes = "member"

        result = self.files_instance.list_dsn_members(dataset_name, member_pattern, member_start, limit, attributes)
        mock_send_request.assert_called()

        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertIn(dataset_name, prepared_request.url)
        self.assertEqual(prepared_request.headers["X-IBM-Max-Items"], str(limit))
        self.assertEqual(prepared_request.headers["X-IBM-Attributes"], attributes)

        self.assertEqual(len(result.items), 2)
        self.assertTrue(isinstance(result.items[0], SimpleMemberResponse))
        self.assertTrue(isinstance(result.items[1], SimpleMemberResponse))

    @mock.patch("requests.Session.send")
    def test_list_members_base(self, mock_send_request):
        """Test list members sends request and receives a member with attributes"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {
            "items": [
                {
                    "member":"MEMTEST",
                    "vers":1,
                    "mod":0,
                    "c4date":"2015/08/12",
                    "m4date":"2015/08/12",
                    "cnorc":22,
                    "inorc":22,
                    "mnorc":0,
                    "mtime":"05:48",
                    "msec":"43",
                    "user":"IBMUSER",
                    "sclm":"N"
                }
            ],
            "returnedRows":1,
            "JSONversion":1
        }

        dataset_name = "TEST.PDS"
        member_pattern = "MEM*"
        member_start = None
        limit = 1000
        attributes = "base"

        result = self.files_instance.list_dsn_members(dataset_name, member_pattern, member_start, limit, attributes)
        mock_send_request.assert_called()

        self.assertEqual(len(result.items), 1)
        self.assertTrue(isinstance(result.items[0], MemberResponse))
    
    @mock.patch("requests.Session.send")
    def test_list_members_mem_name_total(self, mock_send_request):
        """Test list members sends request and receives members with member name only + total rows"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {
            "items": [{"member": "MEMBER1"}, {"member": "MEMBER2"}],
            "totalRows": 3,
            "returnedRows":2,
            "JSONversion":1
        }

        dataset_name = "TEST.PDS"
        member_pattern = None
        member_start = "MEMBER1"
        limit = 3
        attributes = "member,total"

        result = self.files_instance.list_dsn_members(dataset_name, member_pattern, member_start, limit, attributes)
        mock_send_request.assert_called()

        self.assertEqual(len(result.items), 2)
        self.assertTrue(isinstance(result.items[0], SimpleMemberResponse))
        self.assertTrue(isinstance(result.items[1], SimpleMemberResponse))

    @mock.patch("requests.Session.send")
    def test_list_members_base_total(self, mock_send_request):
        """Test list members sends request and receives undefined members + total rows"""
        self.files_instance = Files(self.test_profile)
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)
        mock_send_request.return_value.json.return_value = {
            "items": [
                {
                    "member": "MEMBER0",
                    "ac": "00",
                    "amode": "31",
                    "attr": "RN RU",
                    "rmode": "ANY",
                    "size": "00008250",
                    "ttr": "057B13"
                }, 
                {
                    "member": "MEMBER1",
                    "ac": "00",
                    "alias-of": "SOMEXSSI",
                    "amode": "31",
                    "attr": "RN RU",
                    "rmode": "ANY",
                    "size": "0001A5F8",
                    "ttr": "031F04"
                }
            ],
            "totalRows": 5,
            "returnedRows":2,
            "JSONversion":1
        }

        dataset_name = "TEST.PDS"
        member_pattern = "MEM*"
        member_start = None
        limit = 2
        attributes = "base,total"

        result = self.files_instance.list_dsn_members(dataset_name, member_pattern, member_start, limit, attributes)
        mock_send_request.assert_called()

        self.assertEqual(len(result.items), 2)
        self.assertTrue(isinstance(result.items[0], UndefRecfmMemberResponse))
        self.assertTrue(isinstance(result.items[1], UndefRecfmMemberResponse))
