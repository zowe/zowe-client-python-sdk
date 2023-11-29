Basic usage
============

After you install the package in your project, import the class for the required sub-package (i.e `Console` class for z/OS Console commands). 
Create a dictionary to handle communication with the plug-in:

.. code-block:: python

    from zowe.zos_console_for_zowe_sdk import Console
    profile = {
        "host": "<host address>",
        "port" : 443 , # Include the port if different from the default (443)
        "user": "<user>",
        "password": "<password>",
    }

    my_console = Console(profile)

Alternatively you can use an existing Zowe CLI profile instead:

.. code-block:: python

  from zowe.zos_console_for_zowe_sdk import Console
  from zowe.zos_core_for_zowe_sdk import ProfileManager

  # Load the profile using ProfileManager
  profile = ProfileManager().load(profile_type="<profile name>")

  my_console = Console(profile)
