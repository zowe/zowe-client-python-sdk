z/OSMF Workflows Package
================================

Contains APIs to interact with the z/OSMF Workflows functionality (using z/OSMF REST endpoints).

Examples
------------

<strong>Create a z/OSMF workflow and get it's properties</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.zosmf_for_zowe_sdk import Zosmf

profile = ProfileManager().load(profile_type="zosmf")
zosmf_workflows = Workflows(profile)

created_workflow = zosmf_workflows.create_workflow(
  workflow_name="Installation Workflow",
  workflow_definition_file="/some/valid/path",
  system="MYSYS",
  owner="ZOSMFAD",
  variable_input_file="/some/valid/path",
  workflow_archive_safid="ZOSMFAD"
)
created_workflow_properties = zosmf_workflows.get_workflow_properties(created_workflow.workflowKey, True, True)
```
