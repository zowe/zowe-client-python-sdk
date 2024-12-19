First steps
============

After you install the package in your project, integrate the SDK in your script:

1. Import the class for the required sub-package in order to call the individual SDK method and run plug-in commands. 

    For example, the `Console` class must be imported for z/OS Console commands to be issued. 

2. Create a dictionary to add connection information to communicate with the plug-in:

    .. code-block:: python

        from zowe.zos_console_for_zowe_sdk import Console
        profile = {
            "host": "<host address>",
            "port": 443, # Include the port if different from the default (443)
            "user": "<user>",
            "password": "<password>",
            # "rejectUnauthorized": True, # Set to False to disable SSL verification
            # "basePath": "", # Define base path if using Zowe API ML (e.g. "/ibmzosmf/api/v1" for z/OSMF)
            # "protocol": "https", # Include the protocol if different from the default (https)
        }

        my_console = Console(profile)    

    Alternatively you can use an existing Zowe CLI profile instead:

    .. code-block:: python

            from zowe.zos_console_for_zowe_sdk import Console
            from zowe.core_for_zowe_sdk import ProfileManager

            # Load the profile using ProfileManager
            profile = ProfileManager().load(profile_name="<profile name>")

            my_console = Console(profile)
