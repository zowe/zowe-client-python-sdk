z/OS Management Facility Package
================================

Contains APIs to interact with the z/OS Management Facility (using z/OSMF REST endpoints).

Examples
------------

<strong>Check z/OSMF status</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zosmf_for_zowe_sdk import Zosmf

profile = ProfileManager().load(profile_type="zosmf")
zosmf_info = Zosmf(profile)

print(zosmf_info.get_info())

```
