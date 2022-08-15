z/OS TSO Package
=================

Contains APIs to interact with TSO on z/OS (using z/OSMF TSO REST endpoints).

API Examples
------------

<strong>A Tso class method for starting a TSO session.</strong>  

```
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
```

<strong>A Tso class method for pinging an existing TSO session.</strong>  

```
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
```

<strong>A Tso class method for sending a command to an existing TSO session.</strong>  

```
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
        custom_args["url"] = "{}/{}".format(self.request_endpoint, str(session_key))
        custom_args["json"] = {"TSO RESPONSE":{"VERSION":"0100","DATA":str(message)}}
        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json["tsoData"]
```

<strong>A Tso class method for stopping an existing TSO session.</strong>   

```
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
        custom_args["url"] = "{}/{}".format(self.request_endpoint, session_key)
        response_json = self.request_handler.perform_request("DELETE", custom_args)
        message_id_list = self.parse_message_ids(response_json)
        return (
            "Session ended"
            if self.session_not_found not in message_id_list
            else "Session already ended"
        )
```
