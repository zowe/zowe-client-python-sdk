z/OS Files Package
==================

Contains APIs to interact with files and data sets on z/OS (using z/OSMF files REST endpoints).

Examples
------------

<strong>Create a dataset</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_files_for_zowe_sdk import Files

profile = ProfileManager().load(profile_name="zosmf")
files_info = Files(profile)

print(files_info.create_data_set("DATASETNAME", options={
    "primary": 10,
    "secondary": 1,
    "alcunit": "TRK",
    "lrecl": 80
}))
```

<strong>Delete a dataset member</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zos_files_for_zowe_sdk import Files

profile = ProfileManager().load(profile_name="zosmf")

with Files(profile) as files_info:
    print(files_info.delete_data_set(dataset_name="ZOWEUSER.PUBLIC.MY.DATASET.JCL", member_name="MEMBER"))
```
