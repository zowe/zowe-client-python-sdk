"""
This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zeepy project.
"""

from ..utilities import ZosmfApi


class Tso(ZosmfApi):
    """Base class for TSO API"""
    def __init__(self, connection):
        super().__init__(connection, "/zosmf/tsoApp/tso")
        self.session_not_found = self.constants["TsoSessionNotFound"]

    def issue_command(self, command):
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
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}/{}".format(self.request_endpoint, str(session_key))
        custom_args["data"] = '{"TSO RESPONSE":{"VERSION":"0100","DATA":"%s"}}' % (
            str(message)
        )
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json["tsoData"]

    def ping_tso_session(self, session_key):
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
        return (
            [message["messageId"] for message in response_json["msgData"]]
            if "msgData" in response_json
            else []
        )

    def retrieve_tso_messages(self, response_json):
        return [
            message["TSO MESSAGE"]["DATA"]
            for message in response_json
            if "TSO MESSAGE" in message
        ]
