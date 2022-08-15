z/OS Console Package
====================

Contains APIs to interact with the z/OS console (using z/OSMF console REST endpoints).

API Examples
------------

<strong>A Console class method for issuing a command on the z/OS Console.</strong>  

```
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
        request_body = {"cmd": command}
        custom_args["json"] = request_body
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json
```
