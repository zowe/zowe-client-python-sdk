z/OS Files Package
==================

Contains APIs to interact with files and data sets on z/OS (using z/OSMF files REST endpoints).

API Examples
------------

<strong>A Files class method for creating a dataset.</strong>  

```
    def create_data_set(self, dataset_name, options = {}):    
        """Create a sequential or partitioned dataset.
        
        Parameters
        ----------
            dataset_name
        Returns
        -------
        json
        """
    
        for opt in ("volser", "unit", "dsorg", "alcunit", 
            "primary", "secondary", "dirblk", "avgblk", "recfm", 
            "blksize", "lrecl", "storclass", "mgntclass", "dataclass", 
            "dsntype", "like"):
    
            if opt == "dsorg":
                if options.get(opt) is not None and options[opt] not in ("PO", "PS"):
                    raise KeyError
    
            if opt == "alcunit":
                if options.get(opt) is None:
                    options[opt] = "TRK"
                else:
                    if options[opt] not in ("CYL", "TRK"):
                        raise KeyError
    
            if opt == "primary":
                if options.get(opt) is not None:
                    if options["primary"] > 16777215:
                        raise ValueError
    
            if opt == "secondary":
                if options.get("primary") is not None:
                    if options.get(opt) is None:
                        options["secondary"] = int(options["primary"] / 10)
                    if options["secondary"] > 16777215:
                        raise ValueError
    
            if opt == "dirblk":
                if options.get(opt) is not None:
                    if options.get("dsorg") == "PS":
                        if options["dirblk"] != 0:
                            raise ValueError
                    elif options.get("dsorg") == "PO":
                        if options["dirblk"] == 0:
                            raise ValueError
    
            if opt == "recfm":
                if options.get(opt) is None:
                    options[opt] = "F"
                else:
                    if options[opt] not in ("F", "FB", "V", "VB", "U"):
                        raise KeyError
    
            if opt == "blksize":
                if options.get(opt) is None and options.get("lrecl") is not None:
                    options[opt] = options["lrecl"]
    
        custom_args = self._create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        custom_args["json"] = options
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code = [201])
        return response_json
```

<strong>A Files class method for creating a file or a directory.</strong>  

```
    def create_uss(self, file_path, type, mode = None):        
        """Add a file or directory
        
        Parameters
        ----------
        file_path of the file to add
        type = "file" or "dir"
        mode Ex:- rwxr-xr-x
        """

        data = {
            "type": type,
            "mode": mode
        }
        
        custom_args = self._create_custom_request_arguments()
        custom_args["json"] = data
        custom_args["url"] = "{}fs/{}".format(self.request_endpoint, file_path.lstrip("/"))
        response_json = self.request_handler.perform_request("POST", custom_args, expected_code = [201])
        return response_json
```

<strong>A Files class method for retrieving the list of members on a given PDS/PDSE.</strong>  

```
    def list_dsn_members(self, dataset_name, member_pattern=None,
                         member_start=None, limit=1000, attributes='member'):        
        """Retrieve the list of members on a given PDS/PDSE.
    
        Returns
        -------
        json
            A JSON with a list of members from a given PDS/PDSE
        """
        
        custom_args = self._create_custom_request_arguments()
        additional_parms = {}
        if member_start is not None:
            additional_parms['start'] = member_start
        if member_pattern is not None:
            additional_parms['pattern'] = member_pattern
        url = "{}ds/{}/member".format(self.request_endpoint, dataset_name)
        separator = '?'
        for k,v in additional_parms.items():
            url = "{}{}{}={}".format(url,separator,k,v)
            separator = '&'
        custom_args['url'] = url
        custom_args["headers"]["X-IBM-Max-Items"]  = "{}".format(limit)
        custom_args["headers"]["X-IBM-Attributes"] = attributes
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json['items']
```

<strong>A Files class method for deleting a dataset.</strong>  

```
    def delete_data_set(self, dataset_name, volume=None, member_name=None):        
        """Deletes a sequential or partitioned data.
        """
        
        custom_args = self._create_custom_request_arguments()
        if member_name is not None:
            dataset_name = f'{dataset_name}({member_name})'
        url = "{}ds/{}".format(self.request_endpoint, dataset_name)
        if volume is not None:
            url = "{}ds/-{}/{}".format(self.request_endpoint, volume, dataset_name)
        custom_args["url"] = url
        response_json = self.request_handler.perform_request(
            "DELETE", custom_args, expected_code=[200, 202, 204])
        return response_json
```
