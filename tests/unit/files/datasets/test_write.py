from unittest import TestCase, mock
from zowe.zos_files_for_zowe_sdk import Files
from unit.files.constants import profile


class TestWriteClass(TestCase):
    """File class unit tests."""

    def setUp(self):
        """Setup fixtures for File class."""
        self.test_profile = profile

    @mock.patch("requests.Session.send")
    def test_write(self, mock_send_request):
        """Test list members sends request"""
        mock_send_request.return_value = mock.Mock(headers={"Content-Type": "application/json"}, status_code=201)

        Files(self.test_profile).write_to_dsn(dataset_name="ds_name", data="test")
        mock_send_request.assert_called_once()
        prepared_request = mock_send_request.call_args[0][0]
        self.assertEqual(prepared_request.method, "PUT")