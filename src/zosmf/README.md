z/OS Management Facility Package
================================

Contains APIs to interact with the z/OS Management Facility (using z/OSMF REST endpoints).

API Examples
------------

<strong>A Zosmf class method for returning a JSON response with the z/OSMF Info REST API data.</strong>  

```
    def get_info(self):
        """Return a JSON response from the GET request to z/OSMF info endpoint.

        Returns
        -------
        json
            A JSON containing the z/OSMF Info REST API data
        """
        
        response_json = self.request_handler.perform_request(
            "GET", self.request_arguments
        )
        return response_json
```
