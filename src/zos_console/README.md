z/OS Console Package
====================

Contains APIs to interact with the z/OS console (using z/OSMF console REST endpoints).

Examples
------------

<strong>Submit a command to the z/OS console</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_console_for_zowe_sdk import Console

profile = ProfileManager().load(profile_name="zosmf")

with Console(profile) as console_info:
    print(console_info.issue_command(command="D IPLINFO", console="EMCS"))
```
