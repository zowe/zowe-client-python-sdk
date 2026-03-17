"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from zowe.core_for_zowe_sdk import SdkApi

from .response import (
    ConsoleResponse,
    GetLogMessagesResponse,
    IssueCommandResponse,
    UnsuccessfulGetLogMessagesResponse,
)


class Console(SdkApi):  # type: ignore
    """
    Class used to represent the base z/OSMF Console API.

    Parameters
    ----------
    connection : dict[str, Any]
       A profile in dict (json) format
    log : bool
        Flag to disable logger
    """

    def __init__(self, connection: dict[str, Any], log: bool = True):
        super().__init__(connection, "/zosmf/restconsoles/", logger_name=__name__, log=log)

    def issue_command(
        self,
        command: str,
        console: Optional[str] = None,
        system: Optional[str] = None
    ) -> IssueCommandResponse:
        """Issues a command on z/OS Console.

        Parameters
        ----------
        command : str
            The z/OS command to be executed
        console : Optional[str]
            Name of the console that should be used to execute the command (default is None)
        system : Optional[str]
            Name of the system in the same sysplex that the command is routed to
            (default is None, that means the local system)

        Returns
        -------
        IssueCommandResponse
            A JSON containing the response from the console command
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}consoles/{}".format(self._request_endpoint, console or "defcn")
        request_body = {"cmd":command}
        if system is not None:
            request_body["system"] = system
        custom_args["json"] = request_body
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return IssueCommandResponse(response_json)

    def get_response(self, response_key: str, console: Optional[str] = None) -> ConsoleResponse:
        """
        Collect outstanding synchronous z/OS Console response messages.

        Parameters
        ----------
        response_key : str
            The command response key from the Issue Command request.
        console : Optional[str]
            The console that should be used to get the command response.

        Returns
        -------
        ConsoleResponse
            A JSON containing the response to the command
        """
        custom_args = self._create_custom_request_arguments()
        request_url = "{}consoles/{}/solmsgs/{}".format(self._request_endpoint, console or "defcn", response_key)
        custom_args["url"] = request_url
        response_json = self.request_handler.perform_request("GET", custom_args)
        return ConsoleResponse(response_json)
    
    def get_log_messages(
        self,
        time: Optional[datetime] = None,
        timestamp: Optional[int] = None,
        time_range: Optional[str] = None,
        hardcopy: Optional[Literal["OPERLOG", "SYSLOG"]] = None,
        sys_name: Optional[str] = None,
        direction: Optional[Literal["backward", "forward"]] = None
    ) -> GetLogMessagesResponse | UnsuccessfulGetLogMessagesResponse:
        """
        Retrieve messages from hardcopy logs on the system.
        
        The maximum return size of the log is 10000.
        If more than 10000 logs exist in the timeframe, the system returns the first 10000 logs.

        See more at: `Get messages from a hardcopy log`_
        .. _Get messages from a hardcopy log:
           https://www.ibm.com/docs/en/zos/3.2.0?topic=services-get-messages-from-hardcopy-log
        
        Parameters
        ----------
        time : Optional[datetime]
            Specifies when z/OSMF starts to retrieve messages.
            This value is used if the timestamp parameter is not specified.
        timestamp : Optional[int]
            Specifies the UNIX timestamp, which is the number of milliseconds since 1970-01-01 UTC.
            This parameter is specified, the "time" parameter is ignored.
        time_range : Optional[str]
            Specifies the time range for which the log is to be retrieved.
            Supported time units include s, m, and h for seconds, minutes, and hours.
            The format is nnnu, where nnn is a number 1-999 and u is one of the time units "s", "m", or "h".
            For example, 999s of 20m.
            The default is 10m.
        hardcopy : Optional[Literal['OPERLOG', 'SYSLOG']]
            Specify the source where the logs come from.
            If not specified, the API tries OPERLOG first.
            If the OPERLOG is not enabled on the system, the API returns the SYSLOG.
        sys_name : Optional[str]
            The name of the system on which the SYSLOG resides.
        direction : Optional[Literal['backward', 'forward']]
            Specifies the direction (from a specified time) in which messages are retrieved.
            The default is "backward", meaning that messages are retrieved backward from the specified time.

        Returns
        -------
        GetLogMessagesResponse | UnsuccessfulGetLogMessagesResponse
            A response content for a successful/unsuccessful get messages request response
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}v1/log".format(self._request_endpoint)
        params = {}
        if time is not None and timestamp is not None:
            self.logger.warning(
                'Both "time" and "timestamp" query parameters are provided. "time" parameter is ignored'
            )
            time = None
        if time is not None:
            if time.tzinfo is not None and time.tzinfo != timezone.utc:
                self.logger.warning(
                    f'"time" query parameter is not in UTC timezone ({time.tzinfo}). Conversion to UTC will occur'
                )
                time = time.astimezone(timezone.utc)
            params["time"] = time
        if timestamp:
            params["timestamp"] = timestamp
        if time_range:
            params["timeRange"] = time_range
        if hardcopy:
            params["hardcopy"] = hardcopy
        if sys_name:
            params["sysName"] = sys_name
        if direction:
            params["direction"] = direction
        custom_args["params"] = params
        response_json = self.request_handler.perform_request("GET", custom_args, expected_code=[200, 400, 500])
        return (
            GetLogMessagesResponse(response_json)
            if "returnCode" not in response_json.keys()
            else UnsuccessfulGetLogMessagesResponse(response_json)
        )
