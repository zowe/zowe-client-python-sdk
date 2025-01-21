z/OS UNIX System Services (USS) Package
=======================================

Provides APIs to interact with z/OS UNIX System Services (USS) over SSH (using z/OSMF or other SSH connections).

Examples
--------

### Issue a command in the z/OS USS environment

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_uss_for_zowe_sdk import Uss

profile = ProfileManager().load(profile_name="zosmf")

with Uss(profile) as uss:
    print(uss.execute_command(command="ls -la", cwd="/u/home"))
```