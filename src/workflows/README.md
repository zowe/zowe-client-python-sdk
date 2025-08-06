z/OSMF Workflows Package
================================

Contains APIs to interact with the z/OSMF Workflows functionality (using z/OSMF REST endpoints).

Examples
------------

<strong>Create a z/OSMF workflow and get it's properties</strong>  

```
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.workflows_for_zowe_sdk import Workflows

profile = ProfileManager().load(profile_type="zosmf")
workflows = Workflows(profile)

created_workflow = workflows.create_workflow(
  workflow_name="Installation Workflow",
  workflow_definition_file="/some/valid/path",
  system="MYSYS",
  owner="ZOSMFAD",
  variable_input_file="/some/valid/path",
  workflow_archive_safid="ZOSMFAD"
)
created_workflow_properties = workflows.get_workflow_properties(created_workflow.workflowKey, True, True)
```
