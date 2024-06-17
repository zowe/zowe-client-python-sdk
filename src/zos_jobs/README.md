z/OS Jobs Package
=================

Contains APIs to interact with jobs on z/OS (using z/OSMF jobs REST endpoints).

Examples
------------

<strong>Cancel a job</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_jobs_for_zowe_sdk import Jobs

profile = ProfileManager().load(profile_name="zosmf")
jobs_info = Jobs(profile)

print(jobs_info.cancel_job("JOBNAME", "JOBID"))
```

<strong>Delete a job</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_jobs_for_zowe_sdk import Jobs

profile = ProfileManager().load(profile_name="zosmf")

with Jobs(profile) as jobs_info:
    print(jobs_info.delete_job("JOBNAME", "JOBID"))
```

<strong>Get jobs by owner</strong>   

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_jobs_for_zowe_sdk import Jobs

profile = ProfileManager().load(profile_name="zosmf")

with Jobs(profile) as jobs_info:
    job_owner = "USERNAME"
    print(jobs_info.list_jobs(job_owner))
```

<strong>Submit a job from mainframe</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_jobs_for_zowe_sdk import Jobs

profile = ProfileManager().load(profile_name="zosmf")

with Jobs(profile) as jobs_info:
    print(jobs_info.submit_from_mainframe(jcl_path="ZOWEUSER.PUBLIC.MY.DATASET.JCL(MEMBER)"))
```
