from zowe.core_for_zowe_sdk import SdkApi


class Console(SdkApi):
    """
    Class used to represent the base z/OSMF Console API.

    ...

    Attributes
    ----------
    connection
        Connection object
    """

    def __init__(self, connection):
        """
        Construct a Console object.

        Parameters
        ----------
        connection
            The connection object
        """
        super().__init__(connection, "/zosmf/restconsoles/consoles/defcn", logger_name=__name__)

    def issue_command(self, command, console=None):
        """Issues a command on z/OS Console.

        Parameters
        ----------
        command
            The z/OS command to be executed
        console
            The console that should be used to execute the command (default is None)

        Returns
        -------
        json
            A JSON containing the response from the console command
        """
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = self._request_endpoint.replace("defcn", console or "defcn")
        request_body = {"cmd": command}
        custom_args["json"] = request_body
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json

    def get_response(self, response_key, console=None):
        """
        Collect outstanding synchronous z/OS Console response messages.

        Parameters
        ----------
        response_key
            The command response key from the Issue Command request.
        console
            The console that should be used to get the command response.
        Returns
        -------
        json
            A JSON containing the response to the command
        """
        custom_args = self._create_custom_request_arguments()
        request_url = "{}/solmsgs/{}".format(console or "defcn", response_key)
        custom_args["url"] = self._request_endpoint.replace("defcn", request_url)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json
