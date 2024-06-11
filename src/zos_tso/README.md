z/OS TSO Package
=================

Contains APIs to interact with TSO on z/OS (using z/OSMF TSO REST endpoints).

Examples
------------

<strong>Issue the TSO command "status" to display information about jobs for your user ID</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_tso_for_zowe_sdk import Tso

profile = ProfileManager().load(profile_name="zosmf")

with Tso(profile) as tso_info:
    started_tso_session = tso_info.start_tso_session()

    issue_command = tso_info.send_tso_message(started_tso_session, message="status")
    print(issue_command)
```

<strong>Demonstrate starting, pinging, and stopping a TSO address space</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_tso_for_zowe_sdk import Tso

profile = ProfileManager().load(profile_name="zosmf")

with Tso(profile) as tso_info:
    started_tso_session = tso_info.start_tso_session()
    print(started_tso_session)

    print(tso_info.ping_tso_session(started_tso_session))

    print(tso_info.end_tso_session(started_tso_session))
```
