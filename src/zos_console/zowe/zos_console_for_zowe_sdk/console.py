"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from typing import Optional, Any

from zowe.core_for_zowe_sdk import SdkApi

from .response import ConsoleResponse, IssueCommandResponse


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
        super().__init__(connection, "/zosmf/restconsoles/consoles/defcn", logger_name=__name__, log=log)

    def issue_command(self, command: str, console: Optional[str] = None) -> IssueCommandResponse:
        """Issues a command on z/OS Console.

        Parameters
        ----------
        command : str
            The z/OS command to be executed
        console : Optional[str]
            Name of the console that should be used to execute the command (default is None)

        Returns
        -------
        IssueCommandResponse
            A JSON containing the response from the console command
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = self._request_endpoint.replace("defcn", console or "defcn")
        request_body = {"cmd": command}
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
        request_url = "{}/solmsgs/{}".format(console or "defcn", response_key)
        custom_args["url"] = self._request_endpoint.replace("defcn", request_url)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return ConsoleResponse(response_json)
