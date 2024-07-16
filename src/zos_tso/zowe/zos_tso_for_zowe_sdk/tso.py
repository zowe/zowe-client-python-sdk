"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

import json

from zowe.core_for_zowe_sdk import SdkApi, constants


class Tso(SdkApi):
    """
    Class used to represent the base z/OSMF TSO API.

    Attributes
    ----------
    connection
        Connection object
    session_not_found
        Constant for the session not found tso message id
    """

    def __init__(self, connection, tso_profile=None):
        """
        Construct a Tso object.

        Parameters
        ----------
        connection
            The connection object
        """
        super().__init__(connection, "/zosmf/tsoApp/tso", logger_name=__name__)
        self.session_not_found = constants["TsoSessionNotFound"]
        self.tso_profile = tso_profile or {}

    def issue_command(self, command):
        """Issues a TSO command.

        This function will first initiate a TSO session, retrieve the
        session key, send the command and finally terminate the session

        Parameters
        ----------
        command: str
            TSO command to be executed

        Returns
        -------
        list
            A list containing the output from the TSO command
        """
        session_key = self.start_tso_session()
        command_output = self.send_tso_message(session_key, command)
        tso_messages = self.retrieve_tso_messages(command_output)
        while not any("TSO PROMPT" in message for message in command_output) or not tso_messages:
            command_output = self.__get_tso_data(session_key)
            tso_messages += self.retrieve_tso_messages(command_output)
        self.end_tso_session(session_key)
        return tso_messages

    def start_tso_session(
        self,
        proc=None,
        chset=None,
        cpage=None,
        rows=None,
        cols=None,
        rsize=None,
        acct=None,
    ):
        """Start a TSO session.

        Parameters
        ----------
        proc: str, optional
            Proc parameter for the TSO session (default is "IZUFPROC")
        chset: str, optional
            Chset parameter for the TSO session (default is "697")
        cpage: str, optional
            Cpage parameter for the TSO session (default is "1047")
        rows: str, optional
            Rows parameter for the TSO session (default is "204")
        cols: str, optional
            Cols parameter for the TSO session (default is "160")
        rsize: str, optional
            Rsize parameter for the TSO session (default is "4096")
        acctL str, optional
            Acct parameter for the TSO session (default is "DEFAULT")

        Returns
        -------
        str
            The 'servletKey' key for the created session (if successful)
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["params"] = {
            "proc": proc or self.tso_profile.get("logonProcedure", "IZUFPROC"),
            "chset": chset or self.tso_profile.get("characterSet", "697"),
            "cpage": cpage or self.tso_profile.get("codePage", "1047"),
            "rows": rows or self.tso_profile.get("rows", "204"),
            "cols": cols or self.tso_profile.get("columns", "160"),
            "rsize": rsize or self.tso_profile.get("regionSize", "4096"),
            "acct": acct or self.tso_profile.get("account", "DEFAULT"),
        }
        response_json = self.request_handler.perform_request("POST", custom_args)
        return response_json["servletKey"]

    def send_tso_message(self, session_key, message):
        """Send a command to an existing TSO session.

        Parameters
        ----------
        session_key: str
            The session key of an existing TSO session
        message: str
            The message/command to be sent to the TSO session

        Returns
        -------
        list
            A non-normalized list from TSO containing the result from the command
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self._request_endpoint, str(session_key))
        # z/OSMF TSO API requires json to be formatted in specific way without spaces
        request_json = {"TSO RESPONSE": {"VERSION": "0100", "DATA": str(message)}}
        custom_args["data"] = json.dumps(request_json, separators=(",", ":"))
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json["tsoData"]

    def ping_tso_session(self, session_key):
        """Ping an existing TSO session and returns if it is still available.

        Parameters
        ----------
        session_key: str
            The session key of an existing TSO session

        Returns
        -------
        str
            A string informing if the ping was successful or not.
            Where the options are: 'Ping successful' or 'Ping failed'
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}/{}/{}".format(self._request_endpoint, "ping", str(session_key))
        response_json = self.request_handler.perform_request("PUT", custom_args)
        message_id_list = self.parse_message_ids(response_json)
        return "Ping successful" if self.session_not_found not in message_id_list else "Ping failed"

    def end_tso_session(self, session_key):
        """Terminates an existing TSO session.

        Parameters
        ----------
        session_key: str
            The session key of an existing TSO session

        Returns
        -------
        str
            A string informing if the session was terminated successfully or not
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self._request_endpoint, session_key)
        response_json = self.request_handler.perform_request("DELETE", custom_args)
        message_id_list = self.parse_message_ids(response_json)
        return "Session ended" if self.session_not_found not in message_id_list else "Session already ended"

    def parse_message_ids(self, response_json):
        """Parse TSO response and retrieve only the message ids.

        Parameters
        ----------
        response_json: dict
            The JSON containing the TSO response

        Returns
        -------
        list
            A list containing the TSO response message ids
        """
        return [message["messageId"] for message in response_json["msgData"]] if "msgData" in response_json else []

    def retrieve_tso_messages(self, response_json):
        """Parse the TSO response and retrieve all messages.

        Parameters
        ----------
        response_json: dict
            The JSON containing the TSO response

        Returns
        -------
        list
            A list containing the TSO response messages
        """
        return [message["TSO MESSAGE"]["DATA"] for message in response_json if "TSO MESSAGE" in message]

    def __get_tso_data(self, session_key):
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self._request_endpoint, session_key)
        command_output = self.request_handler.perform_request("GET", custom_args)["tsoData"]
        return command_output
