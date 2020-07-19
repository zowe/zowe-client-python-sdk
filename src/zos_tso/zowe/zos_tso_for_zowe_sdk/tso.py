"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from zowe.core import SdkApi


class Tso(SdkApi):
    """
    Class used to represent the base z/OSMF TSO API.

    ...

    Attributes
    ----------
    connection
        connection object
    session_not_found
        constant for the session not found tso message id

    Methods
    -------
    issue_command(command)
        Executes a TSO command
    start_tso_session(...)
        Starts a TSO session based on given parameters
    send_tso_message(session_key, message)
        Send a message to an existing TSO session
    ping_tso_session(session_key)
        Test if tso session is still available
    end_tso_session(session_key)
        Terminates an existing TSO session
    parse_message_ids(response_json)
        Parses the TSO message ids from response
    retrieve_tso_messages(response_json)
        Parses the TSO response messages
    """

    def __init__(self, connection):
        """
        Construct a Tso object.

        Parameters
        ----------
        connection
            The connection object
        """
        super().__init__(connection, "/zosmf/tsoApp/tso")
        self.session_not_found = self.constants["TsoSessionNotFound"]

    def issue_command(self, command):
        """Issues a TSO command.

        This function will first initiate a TSO session, retrieve the
        session key, send the command and finally terminate the session

        Parameters
        ----------
        command
            TSO command to be executed

        Returns
        -------
        tso_messages
            A list containing the output from the TSO command
        """
        session_key = self.start_tso_session()
        command_output = self.send_tso_message(session_key, command)
        tso_messages = self.retrieve_tso_messages(command_output)
        self.end_tso_session(session_key)
        return tso_messages

    def start_tso_session(
        self,
        proc="IZUFPROC",
        chset="697",
        cpage="1047",
        rows="204",
        cols="160",
        rsize="4096",
        acct="DEFAULT",
    ):
        """Start a TSO session.

        Parameters
        ----------
        proc
            Proc parameter for the TSO session (default is "IZUFPROC")
        chset
            Chset parameter for the TSO session (default is "697")
        cpage
            Cpage parameter for the TSO session (default is "1047")
        rows
            Rows parameter for the TSO session (default is "204")
        cols
            Cols parameter for the TSO session (default is "160")
        rsize
            Rsize parameter for the TSO session (default is "4096")
        acct
            Acct parameter for the TSO session (default is "DEFAULT")

        Returns
        -------
        servletKey
            The key for the created session (if successful)
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["params"] = {
            "proc": proc,
            "chset": chset,
            "cpage": cpage,
            "rows": rows,
            "cols": cols,
            "rsize": rsize,
            "acct": acct,
        }
        response_json = self.request_handler.perform_request("POST", custom_args)
        return response_json["servletKey"]

    def send_tso_message(self, session_key, message):
        """Send a command to an existing TSO session.

        Parameters
        ----------
        session_key
            The session key of an existing TSO session
        message
            The message/command to be sent to the TSO session

        Returns
        -------
        tsoData
            A non-normalized list from TSO containing the result from the command
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self.request_endpoint, str(session_key))
        custom_args["data"] = '{"TSO RESPONSE":{"VERSION":"0100","DATA":"%s"}}' % (
            str(message)
        )
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json["tsoData"]

    def ping_tso_session(self, session_key):
        """Ping an existing TSO session and returns if it is still available.

        Parameters
        ----------
        session_key
            The session key of an existing TSO session

        Returns
        -------
        ping_result
            A string informing if the ping was successful or not
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}/{}/{}".format(
            self.request_endpoint, "ping", str(session_key)
        )
        response_json = self.request_handler.perform_request("PUT", custom_args)
        message_id_list = self.parse_message_ids(response_json)
        return (
            "Ping successful"
            if self.session_not_found not in message_id_list
            else "Ping failed"
        )

    def end_tso_session(self, session_key):
        """Terminates an existing TSO session.

        Parameters
        ----------
        session_key
            The session key of an existing TSO session

        Returns
        -------
        function_result
            A string informing if the session was terminated successfully or not
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self.request_endpoint, session_key)
        response_json = self.request_handler.perform_request("DELETE", custom_args)
        message_id_list = self.parse_message_ids(response_json)
        return (
            "Session ended"
            if self.session_not_found not in message_id_list
            else "Session already ended"
        )

    def parse_message_ids(self, response_json):
        """Parse TSO response and retrieve only the message ids.

        Parameters
        ----------
        response_json
            The JSON containing the TSO response

        Returns
        -------
        message_ids
            A list containing the TSO response message ids
        """
        return (
            [message["messageId"] for message in response_json["msgData"]]
            if "msgData" in response_json
            else []
        )

    def retrieve_tso_messages(self, response_json):
        """Parse the TSO response and retrieve all messages.

        Parameters
        ----------
        response_json
            The JSON containing the TSO response

        Returns
        -------
        tso_messages
            A list containing the TSO response messages
        """
        return [
            message["TSO MESSAGE"]["DATA"]
            for message in response_json
            if "TSO MESSAGE" in message
        ]
