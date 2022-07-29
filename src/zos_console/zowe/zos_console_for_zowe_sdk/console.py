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
        super().__init__(connection, "/zosmf/restconsoles/consoles/defcn")

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
        custom_args = self.__create_custom_request_arguments()
        request_body = '{"cmd": "%s"}' % (command)
        custom_args["data"] = request_body
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json

    def get_response(self, sol_msgs, Ckey_number):
        """Get a command response on z/OS Console.

        Parameters
        ----------
        Ckey_number
            The command response key from the Issue Command request.

        Returns
        -------
        json
            A JSON containing the response to the command
        """
        custom_args = self._create_custom_request_arguments()
        request_url = "{}/{}".format(sol_msgs, Ckey_number)
        custom_args["url"] = "{}{}".format(self.request_endpoint, request_url)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json