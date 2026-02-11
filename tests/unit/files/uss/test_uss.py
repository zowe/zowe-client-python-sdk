"""Unit tests for the Zowe Python SDK z/OS Files package."""

from unittest import TestCase, mock

import pytest
import requests
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
from zowe.zos_files_for_zowe_sdk import Files
from zowe.zos_files_for_zowe_sdk.constants import ContentType
from zowe.zos_files_for_zowe_sdk.response.uss import USSFileTagType


class TestUssClass(TestCase):
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
    def test_delete_uss(self, mock_send_request):
        """Test deleting a directory recursively sends a request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=204)

        Files(self.test_profile).delete_uss("filepath_name", recursive=True)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get(self, mock_send_request):
        """Test get USS file content sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).uss.get_content("uss_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
    
    @mock.patch("requests.Session.send")
    def test_retrieve_content(self, mock_send_request):
        """Test retrieve USS file content sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).uss.retrieve_content("uss_name")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")

    @mock.patch("requests.Session.send")
    def test_get_content_with_encoding(self, mock_send_request):
        """Test get USS file content with the specified encoding"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "text/plain"}, status_code=200, text="हैलो वर्ल्ड")

        result = Files(self.test_profile).uss.get_content(
            "/some/test/path",
            file_encoding="UTF-8",
            receive_encoding="UTF-8"
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")
        self.assertEqual(result, "हैलो वर्ल्ड")

    @mock.patch("requests.Session.send")
    def test_retrieve_content_with_encoding(self, mock_send_request):
        """Test retrieve USS file content with the specified encoding"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "text/plain"}, status_code=200, text="हैलो वर्ल्ड")

        result = Files(self.test_profile).uss.retrieve_content(
            "/some/test/path",
            remote_file_encoding="UTF-8",
            receive_in_encoding="UTF-8"
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")
        self.assertEqual(result, "हैलो वर्ल्ड")

    @mock.patch("requests.Session.send")
    def test_get_streamed(self, mock_send_request):
        """Test get USS file content streamed sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).uss.get_content_streamed("uss_name", binary=True)
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")

    @mock.patch("requests.Session.send")
    def test_retrieve_content_streamed(self, mock_send_request):
        """Test retrieve USS file content streamed sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=200)

        Files(self.test_profile).uss.retrieve_content("uss_name", content_type=ContentType.BINARY, as_stream=True)
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")

    @mock.patch("requests.Session.send")
    def test_get_content_streamed_with_encoding(self, mock_send_request):
        """Test get response with content in the specified encoding"""
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/octet-stream"}, 
            status_code=200,
            content="हैलो वर्ल्ड".encode()
        )

        result = Files(self.test_profile).uss.get_content_streamed(
            "/some/test/path", 
            file_encoding="UTF-8",
            receive_encoding="UTF-8"
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")
        self.assertEqual(result.content.decode(), "हैलो वर्ल्ड")

    @mock.patch("requests.Session.send")
    def test_retrieve_content_streamed_with_encoding(self, mock_send_request):
        """Test retrieve response with content in the specified encoding"""
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/octet-stream"}, 
            status_code=200,
            content="हैलो वर्ल्ड".encode()
        )

        result = Files(self.test_profile).uss.retrieve_content(
            "/some/test/path", 
            remote_file_encoding="UTF-8",
            receive_in_encoding="UTF-8",
            as_stream=True
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")
        self.assertEqual(result.content.decode(), "हैलो वर्ल्ड")

    @mock.patch("requests.Session.send")
    def test_write_text(self, mock_send_request):
        """Test write USS text file sends correct request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).uss.write("test", "test")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=utf-8")

    @mock.patch("requests.Session.send")
    def test_write_binary(self, mock_send_request):
        """Test write USS binary file sends correct request"""
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/octet-stream", "X-IBM-Data-Type": "binary"}, status_code=204
        )

        Files(self.test_profile).uss.write(filepath_name="test", data="Hello world!".encode())
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "application/octet-stream")

    @mock.patch("requests.Session.send")
    def test_list_uss(self, mock_send_request):
        """Test list USS files sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        Files(self.test_profile).list_files("")
        mock_send_request.assert_called()

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_download_binary(self, mock_file, mock_send_request):
        """Test download a binary USS file"""
        mock_response = mock.Mock(
            spec=requests.Response,
            headers={"Content-Type": "application/octet-stream"},
            status_code=200
        )
        mock_response.iter_content = mock.Mock(return_value=[bytes("हैलो", "UTF-8"), bytes("वर्ल्ड", "UTF-8")])
        mock_send_request.return_value = mock_response

        Files(self.test_profile).uss.download(
            "/some/test/path",
            "/some/test/file",
            binary=True
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")
        mock_file.assert_called_once_with('/some/test/file', 'wb', encoding=None)
        mock_file().write.assert_has_calls([mock.call(bytes("हैलो", "UTF-8")), mock.call(bytes("वर्ल्ड", "UTF-8"))])

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_perform_download_binary(self, mock_file, mock_send_request):
        """Test perform a download of a binary USS file"""
        mock_response = mock.Mock(
            spec=requests.Response,
            headers={"Content-Type": "application/octet-stream"},
            status_code=200
        )
        mock_response.iter_content = mock.Mock(return_value=[bytes("हैलो", "UTF-8"), bytes("वर्ल्ड", "UTF-8")])
        mock_send_request.return_value = mock_response

        Files(self.test_profile).uss.perform_download(
            "/some/test/path",
            "/some/test/file",
            content_type=ContentType.BINARY
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "binary")
        mock_file.assert_called_once_with('/some/test/file', 'wb', encoding=None)
        mock_file().write.assert_has_calls([mock.call(bytes("हैलो", "UTF-8")), mock.call(bytes("वर्ल्ड", "UTF-8"))])

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_download_text(self, mock_file, mock_send_request):
        """Test download a text USS file"""
        mock_response = mock.Mock(
            spec=requests.Response,
            headers={"Content-Type": "application/octet-stream"},
            status_code=200
        )
        mock_response.iter_content = mock.Mock(return_value=[bytes("हैलो", "UTF-8"), bytes("वर्ल्ड", "UTF-8")])
        mock_send_request.return_value = mock_response

        Files(self.test_profile).uss.perform_download(
            "/some/test/path", 
            "/some/test/file", 
            remote_file_encoding="UTF-8", 
            receive_in_encoding="UTF-8"
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")
        mock_file.assert_called_once_with('/some/test/file', 'w', encoding='UTF-8')
        mock_file().write.assert_has_calls([mock.call(bytes("हैलो", "UTF-8")), mock.call(bytes("वर्ल्ड", "UTF-8"))])

    @mock.patch("requests.Session.send")
    def test_download_fail_incorrect_response(self, mock_send_request):
        """Test download a USS file fails because an incorrect response object is received"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "text/plain"}, status_code=200)

        with pytest.raises(TypeError) as e:
            Files(self.test_profile).uss.download(
                "/some/test/path",
                "/some/test/file",
                file_encoding="UTF-8",
                receive_encoding="UTF-8"
            )

        self.assertIn("Expected Response, got", str(e.value))
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")

    @mock.patch("requests.Session.send")
    def test_perform_download_fail_incorrect_response(self, mock_send_request):
        """Test perform a download of a USS file fails because an incorrect response object is received"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "text/plain"}, status_code=200)

        with pytest.raises(TypeError) as e:
            Files(self.test_profile).uss.perform_download(
                "/some/test/path",
                "/some/test/file",
                remote_file_encoding="UTF-8",
                receive_in_encoding="UTF-8"
            )

        self.assertIn("Expected Response, got", str(e.value))
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "GET")
        self.assertEqual(prepared_request.headers["X-IBM-Data-Type"], "text;fileEncoding=UTF-8")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=UTF-8")

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.path.isfile", return_value=True)
    def test_upload_text(self, mock_is_file, mock_file, mock_send_request):
        """Test upload a text USS file"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).uss.upload("/some/test/file", "/some/test/path")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=utf-8")
        mock_is_file.assert_called_once()
        mock_file.assert_called_once_with('/some/test/file', 'r', encoding='utf-8')

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.path.isfile", return_value=True)
    def test_perform_upload_text(self, mock_is_file, mock_file, mock_send_request):
        """Test perform an upload of a text USS file"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).uss.perform_upload("/some/test/file", "/some/test/path")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "text/plain; charset=utf-8")
        mock_is_file.assert_called_once()
        mock_file.assert_called_once_with('/some/test/file', 'r', encoding='utf-8')

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.path.isfile", return_value=True)
    def test_upload_binary(self, mock_is_file, mock_file, mock_send_request):
        """Test upload a binary USS file"""
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/octet-stream", "X-IBM-Data-Type": "binary"}, status_code=204
        )

        binary_data = b"Hello world!"
        mock_file.return_value.read.return_value = binary_data

        Files(self.test_profile).uss.upload("/some/test/file", "/some/test/path", binary=True)
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "application/octet-stream")
        mock_is_file.assert_called_once()
        mock_file.assert_called_once_with('/some/test/file', 'rb')

    @mock.patch("requests.Session.send")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("os.path.isfile", return_value=True)
    def test_perform_upload_binary(self, mock_is_file, mock_file, mock_send_request):
        """Test perform an upload of a binary USS file"""
        mock_send_request.return_value = mock.Mock(
            headers={"Content-Type": "application/octet-stream", "X-IBM-Data-Type": "binary"}, status_code=204
        )

        binary_data = b"Hello world!"
        mock_file.return_value.read.return_value = binary_data

        Files(self.test_profile).uss.perform_upload(
            "/some/test/file",
            "/some/test/path",
            content_type=ContentType.BINARY
        )
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(prepared_request.headers["Content-Type"], "application/octet-stream")
        mock_is_file.assert_called_once()
        mock_file.assert_called_once_with('/some/test/file', 'rb', encoding=None)

    @mock.patch("requests.Session.send")
    @mock.patch("os.path.isfile", return_value=False)
    def test_upload_fail_file_not_found(self, mock_is_file, mock_send_request):
        """Test upload a binary USS file"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        with self.assertRaises(FileNotFound):
            Files(self.test_profile).uss.upload("/some/test/file", "/some/test/path")
        mock_send_request.assert_not_called()
        mock_is_file.assert_called_once()
        mock_is_file.assert_called_once()

    @mock.patch("requests.Session.send")
    @mock.patch("os.path.isfile", return_value=False)
    def test_perform_upload_fail_file_not_found(self, mock_is_file, mock_send_request):
        """Test perform an upload of a binary USS file"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        with self.assertRaises(FileNotFound):
            Files(self.test_profile).uss.perform_upload("/some/test/file", "/some/test/path")
        mock_send_request.assert_not_called()
        mock_is_file.assert_called_once()
        mock_is_file.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_file_tag(self, mock_send_request):
        """Test get a USS file tag sends request"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {"stdout":["m ISO8859-1   T=off /some/test/path"]}
        mock_send_request.return_value = mock_response

        result = Files(self.test_profile).uss.get_file_tag("/some/test/path")

        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")
        self.assertEqual(result.charset, "ISO8859-1")
        self.assertEqual(result.is_conversion_enabled, False)
        self.assertEqual(result.tag_type, USSFileTagType.MIXED)
