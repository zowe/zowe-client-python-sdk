"""Unit tests for the Zowe Python SDK z/OS Console package."""

import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
from unittest.mock import patch

from zowe.zos_console_for_zowe_sdk import Console
from zowe.zos_console_for_zowe_sdk.response.console import (
    GetLogMessagesResponse,
    UnsuccessfulGetLogMessagesResponse,
)


class TestConsoleClass(unittest.TestCase):
    """Console class unit tests."""

    def setUp(self):
        """Setup fixtures for Console class."""
        self.session_details = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of Console class."""
        console = Console(self.session_details)
        self.assertIsInstance(console, Console)

    @mock.patch("requests.Session.send")
    def test_issue_command_makes_request_to_the_default_console(self, mock_send):
        """Issued command should be sent to the correct default console name if no name is specified"""

        def send_request_side_effect(self, **other_args):
            assert "/defcn" in self.url
            mock_response = mock.Mock()
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            return mock_response

        mock_send.side_effect = send_request_side_effect
        Console(self.session_details).issue_command("TESTCMD")

    @mock.patch("requests.Session.send")
    def test_issue_command_makes_request_to_the_custom_console(self, mock_send):
        """Issued command should be sent to the correct custom console name if the console name is specified"""

        def send_request_side_effect(self, **other_args):
            assert "/TESTCNSL" in self.url
            mock_response = mock.Mock()
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            return mock_response

        mock_send.side_effect = send_request_side_effect
        Console(self.session_details).issue_command("TESTCMD", "TESTCNSL")

    @mock.patch("requests.Session.send")
    def test_issue_command_makes_request_to_the_specified_system(self, mock_send):
        """Issued command should be sent to the specified system if the system argument is specified"""

        def send_request_side_effect(self, **other_args):
            assert '"system":"TSYS"' in self.body.decode("utf-8").replace(" ", "")
            mock_response = mock.Mock()
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            return mock_response

        mock_send.side_effect = send_request_side_effect
        Console(self.session_details).issue_command("TESTCMD", system="TSYS")

    @mock.patch("requests.Session.send")
    def test_get_response_should_return_messages(self, mock_send_request):
        """Getting z/OS Console response messages on sending a response key"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response
        Console(self.session_details).get_response("console-key")
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_log_messages_should_return_operlog_messages_backward(self, mock_send_request):
        """OPERLOG messages list should be returned with backwards-directed messages by default."""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'cart': '0',
                    'color': 'green',
                    'jobName': 'TSTJOB1 ',
                    'message': ' XYZ1234I Some Test Log Message 1',
                    'messageId': '12568902641',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:03 GMT 2026',
                    'timestamp': 1777563423710,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '0',
                    'color': 'green',
                    'jobName': 'TSTJOB1 ',
                    'message': ' XYZ1234I Some Test Log Message 2',
                    'messageId': '12568902897',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:03 GMT 2026',
                    'timestamp': 1777563423710,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '-4326849890606516752',
                    'color': 'green',
                    'jobName': 'TSTJOB2 ',
                    'message': ' XYZ1235I Some Other Test Log Message 1',
                    'messageId': '11362899953',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:04 GMT 2026',
                    'timestamp': 1777563424830,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '-4326849890606516752',
                    'color': 'green',
                    'jobName': '        ',
                    'message': ' SOME SDSF COMMAND',
                    'messageId': '11362900209',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:04 GMT 2026',
                    'timestamp': 1777563424830,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '-4326849890606516752',
                    'color': 'green',
                    'jobName': '        ',
                    'message': ' IEE341I TSTPROG           NOT ACTIVE',
                    'messageId': '11362900465',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:04 GMT 2026',
                    'timestamp': 1777563424830,
                    'type': 'HARDCOPY'
                }
            ],
            'nextTimestamp': 1777563396310,
            'source': 'OPERLOG',
            'timezone': 2,
            'totalitems': 5
        }
        mock_send_request.return_value = mock_response
        result = Console(self.session_details).get_log_messages(time_range="120s", sys_name="TSTSYS")
        mock_send_request.assert_called_once()
        assert isinstance(result, GetLogMessagesResponse)
        assert len(result.items) == 5
        assert result.source == "OPERLOG"

    @mock.patch("requests.Session.send")
    def test_get_log_messages_should_return_syslog_messages_forward(self, mock_send_request):
        """SYSLOG messages list should be returned with forwards-directed messages by default."""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'cart': '',
                    'color': '',
                    'jobName': 'TSTJOB3 ',
                    'message': 'XYZ1312I Some Test Message 1',
                    'messageId': '',
                    'replyId': '',
                    'subType': 'NULL',
                    'system': 'TLPR',
                    'time': 'Thu Apr 30 15:50:06 GMT 2026',
                    'timestamp': 1777564206900,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '',
                    'color': '',
                    'jobName': 'TSTJOB3 ',
                    'message': 'XYZ1312I Some Test Message 2',
                    'messageId': '',
                    'replyId': '',
                    'subType': 'NULL',
                    'system': 'TLPR',
                    'time': 'Thu Apr 30 15:50:06 GMT 2026',
                    'timestamp': 1777564206900,
                    'type': 'HARDCOPY'
                },
                {
                    'cart': '',
                    'color': '',
                    'jobName': 'TSTJOB3 ',
                    'message': 'XYZ1312I Some Test Message 3',
                    'messageId': '',
                    'replyId': '',
                    'subType': 'NULL',
                    'system': 'TLPR',
                    'time': 'Thu Apr 30 15:50:06 GMT 2026',
                    'timestamp': 1777564206900,
                    'type': 'HARDCOPY'
                },
            ],
            'nextTimestamp': 0,
            'source': 'SYSLOG',
            'timezone': 2,
            'totalitems': 3
        }
        mock_send_request.return_value = mock_response
        result = Console(self.session_details).get_log_messages(hardcopy="SYSLOG", direction="forward", timestamp=1777564196310)
        mock_send_request.assert_called_once()
        assert isinstance(result, GetLogMessagesResponse)
        assert len(result.items) == 3
        assert result.source == "SYSLOG"
        
    @mock.patch("requests.Session.send")
    def test_get_log_messages_should_return_by_timestamp_when_time_and_timestamp_provided(self, mock_send_request):
        """Log messages should be returned with filtering by timestamp when both time and timestamp are speficied."""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'cart': '0',
                    'color': 'green',
                    'jobName': 'TSTJOB1 ',
                    'message': ' XYZ1234I Some Test Log Message 1',
                    'messageId': '12568902641',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:03 GMT 2026',
                    'timestamp': 1777563423710,
                    'type': 'HARDCOPY'
                }
            ],
            'nextTimestamp': 1777563396310,
            'source': 'OPERLOG',
            'timezone': 2,
            'totalitems': 1
        }
        mock_send_request.return_value = mock_response
        console = Console(self.session_details)
        with patch.object(console.logger, "warning") as mock_warning:
            result = console.get_log_messages(direction="forward", time=datetime.now(), timestamp=1777564196310)
            mock_warning.assert_called_once_with(
                'Both "time" and "timestamp" query parameters are provided. "time" parameter is ignored'
            )
            mock_send_request.assert_called_once()
            assert isinstance(result, GetLogMessagesResponse)
            assert len(result.items) == 1
    
    @mock.patch("requests.Session.send")
    def test_get_log_messages_should_return_by_time_with_custom_timezone(self, mock_send_request):
        """Log messages should be returned from the specified time with the timezone specified."""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'cart': '0',
                    'color': 'green',
                    'jobName': 'TSTJOB1 ',
                    'message': ' XYZ1234I Some Test Log Message 1',
                    'messageId': '12568902641',
                    'replyId': '0',
                    'subType': 'NULL',
                    'system': 'TSTSYS  ',
                    'time': 'Thu Apr 30 15:37:03 GMT 2026',
                    'timestamp': 1777563423710,
                    'type': 'HARDCOPY'
                }
            ],
            'nextTimestamp': 1777563396310,
            'source': 'OPERLOG',
            'timezone': 2,
            'totalitems': 1
        }
        mock_send_request.return_value = mock_response
        console = Console(self.session_details)
        with patch.object(console.logger, "warning") as mock_warning:
            test_datetime = datetime.now(tz=timezone(timedelta(hours=3)))
            result = console.get_log_messages(direction="forward", time=test_datetime)
            mock_warning.assert_called_once_with(
                f'"time" query parameter is not in UTC timezone ({test_datetime.tzinfo}). Conversion to UTC will occur'
            )
            mock_send_request.assert_called_once()
            assert isinstance(result, GetLogMessagesResponse)
            assert len(result.items) == 1

    @mock.patch("requests.Session.send")
    def test_get_log_messages_produces_error(self, mock_send_request):
        """An error with return code and reason should be produced."""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 400
        mock_response.json.return_value = {'returnCode': 1, 'reasonCode': 2, 'reason': 'Some Test Error'}
        mock_send_request.return_value = mock_response
        result = Console(self.session_details).get_log_messages()
        mock_send_request.assert_called_once()
        assert isinstance(result, UnsuccessfulGetLogMessagesResponse)
