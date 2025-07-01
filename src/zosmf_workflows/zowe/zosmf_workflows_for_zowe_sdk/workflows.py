"""Zowe Client Python SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.

Contributors:
    Zowe Community
    Uladzislau Kalesnikau
"""

from typing import Any, Literal, Optional

from zowe.core_for_zowe_sdk import SdkApi

from .response import (
    CreateWorkflowResponse,
    GetArchivedWorkflowPropertiesResponse,
    GetWorkflowDefinitionResponse,
    GetWorkflowPropertiesResponse,
    ListArchivedWorkflowsResponse,
    ListWorkflowsResponse,
)


class Workflows(SdkApi):
    """
    Representation of the base z/OSMF Workflows API.
    
    See more at https://www.ibm.com/docs/en/zos/3.1.0?topic=services-zosmf-workflow.

    Parameters
    ----------
    connection: dict[str, Any]
        The connection object
    version: str
        The supported version of z/OSMF Workflows (1.0 is the only version available for now)
    """
    
    def __init__(self, connection: dict[str, Any], version: str = "1.0"):
        super().__init__(connection, "/zosmf/workflow/rest/{}".format(version))

    def _step_variables_body(
        self, return_steps_data: bool, return_variables_data: bool
    ) -> dict[str, Any]:
        """
        Form steps-variables request body.

        If `return_steps_data` is true, "steps" body parameter is added.
        If `return_variables_data` is true, "variables" body parameter is added.
        If both parameters are true, "steps,variables" body parameter is added.
        Otherwise it returns an empty dictionary
        """
        params = {}
        if return_steps_data:
            params["returnData"] = "steps"
            if return_variables_data:
                params["returnData"] += ",variables"
        elif return_variables_data:
            params["returnData"] = "variables"
        return params

    def create_workflow(
        self,
        workflow_name: str,
        workflow_definition_file: str,
        system: str,
        owner: str,
        workflow_definition_file_system: Optional[str] = None,
        variable_input_file: Optional[str] = None,
        variables: Optional[list[dict]] = None,
        resolve_global_conflict_by_using: Literal['global', 'input'] = "global",
        workflow_archive_safid: Optional[str] = None,
        comments: Optional[str] = None,
        assign_to_owner: bool = True,
        access_type: Literal['Public', 'Restricted', 'Private'] = "Public",
        account_info: Optional[str] = None,
        job_statement: Optional[str] = None,
        delete_completed_jobs: bool = False,
        jobs_output_directory: Optional[str] = None,
        auto_delete_on_completion: bool = False,
        target_systemuid: Optional[str] = None,
        target_systempwd: Optional[str] = None
    ) -> CreateWorkflowResponse:
        """
        You can use this operation to create a z/OSMF workflow on a z/OS system.

        See https://www.ibm.com/docs/en/zos/3.1.0?topic=services-create-workflow for more information.
        Detailed request body parameters description:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-create-workflow#POSTMethodCreateAWorkflow__WorkflowRequestContent__title__1

        Parameters
        ----------
        workflow_name: str
            Descriptive name for the workflow (up to 100 characters).
        workflow_definition_file: str
            Location of the workflow definition file.
        system: str
            Nickname of the system on which the workflow is to be created.
        owner: str
            User ID of the workflow owner.
        workflow_definition_file_system: Optional[str]
            Nickname of the system on which the specified workflow definition file and any related files reside.
        variable_input_file: Optional[str]
            Specifies an optional properties file that you can use to pre-specify values for one or more
            of the variables that are defined in the workflow definition file.
        variables: Optional[list[dict]]
            A list of one or more variables for this workflow. Empty list by default.
        resolve_global_conflict_by_using: Literal['global', 'input']
            **Optional** When input variables are provided, this property specifies which type of the variable is used.
            "global" by default.
        workflow_archive_safid: Optional[str]
            Indicates who can access the archived workflow, which is archived from the current workflow
            to a user specified directory. The default value is the current user ID of the workflow owner.
        comments: Optional[str]
            Specifies any information that you want to associate with the creation of this workflow 
            (up to 500 characters).
        assign_to_owner: bool
            **Optional** Indicates whether the workflow steps are assigned to the workflow owner when
            the workflow is created. The default is "true".
        access_type: Literal['Public', 'Restricted', 'Private']
            **Optional** Specifies the access type for the workflow. If you omit this property,
            the workflow is "public", by default.
        account_info: Optional[str]
            For a workflow that submits a job, this property specifies the account information 
            to use in the JCL JOB statement.
        job_statement: Optional[str]
            For a workflow that submits a job, this property specifies the JOB statement JCL
            that is used in the job.
        delete_completed_jobs: bool
            **Optional** For a workflow that submits a job, this property specifies whether the job is deleted from
            the JES spool after it completes successfully. If you omit this property, the completed job is retained
            on the JES spool.
        jobs_output_directory: Optional[str]
            For a workflow that submits a job, this property specifies the name of a UNIX directory
            that is to be used for automatically saving job spool files from the workflow. If you omit this property,
            the job spool files are not saved.
        auto_delete_on_completion: bool
            **Optional** Indicates whether the workflow is automatically deleted from the local system when all
            of its steps are marked complete or skipped. If you omit this property, the workflow instance is retained.
        target_systemuid: Optional[str]
            The user ID to be used for remote system basic authentication.
        target_systempwd: Optional[str]
            The password to be used for remote system basic authentication.

        Returns
        -------
        CreateWorkflowResponse
            A CreateWorkflowResponse object containing the result created workflow information
        """
        body = {
            "workflowName": workflow_name,
            "workflowDefinitionFile": workflow_definition_file,
            "workflowDefinitionFileSystem": workflow_definition_file_system,
            "variableInputFile": variable_input_file,
            "variables": variables,
            "resolveGlobalConflictByUsing": resolve_global_conflict_by_using,
            "system": system,
            "owner": owner,
            "workflowArchiveSAFID": workflow_archive_safid,
            "comments": comments,
            "assignToOwner": assign_to_owner,
            "accessType": access_type,
            "accountInfo": account_info,
            "jobStatement": job_statement,
            "deleteCompletedJobs": delete_completed_jobs,
            "jobsOutputDirectory": jobs_output_directory,
            "autoDeleteOnCompletion": auto_delete_on_completion,
            "targetSystemuid": target_systemuid,
            "targetSystempwd": target_systempwd
        }

        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}".format(self._request_endpoint, "workflows")
        custom_args["url"] = request_url

        custom_args["json"] = { k: v for k, v in body.items() if v not in [None, ""] }

        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        return CreateWorkflowResponse(response_json)

    def get_workflow_properties(
        self,
        workflow_key: str,
        return_steps_data: bool = False,
        return_variables_data: bool = False
    ) -> GetWorkflowPropertiesResponse:
        """
        You can use this operation to retrieve the properties of a z/OSMF workflow.

        See https://www.ibm.com/docs/en/zos/3.1.0?topic=services-get-properties-workflow for more information.
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-get-properties-workflow#GETMethodRetrieveInformationAboutWF__QueryParameterReturnData__title__1

        Parameters
        ----------
        workflow_key: str
            Identifies the workflow to be queried.
        return_steps_data: bool
            **Optional** Response will contain an array of **WorkflowStepResponse** objects if True.
        return_variables_data: bool
            **Optional** Response will contain an array of **WorkflowVariableResponse** objects if True.

        Returns
        -------
        GetWorkflowPropertiesResponse
            A GetWorkflowPropertiesResponse object containing the workflow properties
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}".format(self._request_endpoint, "workflows", self._encode_uri_component(workflow_key))
        custom_args["url"] = request_url

        params = self._step_variables_body(return_steps_data, return_variables_data)
        custom_args["params"] = params

        response_json = self.request_handler.perform_request("GET", custom_args)
        return GetWorkflowPropertiesResponse(response_json)

    def list_workflows(
        self,
        workflow_name: Optional[str] = None,
        category: Optional[Literal['general', 'configuration']] = None,
        system: Optional[str] = None,
        status_name: Optional[Literal['in-progress', 'complete', 'automation-in-progress', 'canceled']] = None,
        owner: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> list[ListWorkflowsResponse]:
        """
        You can use this operation to list the z/OSMF workflows for a system or sysplex.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-list-workflows-system-sysplex
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-list-workflows-system-sysplex#GETMethodListWorkflows__QueryParametersFilters__title__1

        Parameters
        ----------
        workflow_name: Optional[str]
            Workflow name. You can specify a regular expression here to match desired workflow names.
        category: Optional[Literal['general', 'configuration']]
            Category of the workflow, which is either general or configuration.
        system: Optional[str]
            Nickname of the system on which the workflow is to be performed.
        status_name: Optional[Literal['in-progress', 'complete', 'automation-in-progress', 'canceled']]
            Workflow status.
        owner: Optional[str]
            Workflow owner (a valid z/OS user ID).
        vendor: Optional[str]
            Name of the vendor that provided the workflow definition file.

        Returns
        -------
        list[ListWorkflowsResponse]
            A ListWorkflowsResponse array of objects containing the workflows short information
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}".format(self._request_endpoint, "workflows")
        custom_args["url"] = request_url

        params = {
            "workflowName": workflow_name,
            "category": category,
            "statusName": status_name,
            "system": system,
            "owner": owner,
            "vendor": vendor,
        }
        custom_args["params"] = params

        response_json = self.request_handler.perform_request("GET", custom_args)
        return list(
            map(lambda workflow_raw: ListWorkflowsResponse(workflow_raw), response_json["workflows"])
        )

    def start_workflow(
        self,
        workflow_key: str,
        resolve_conflict_by_using: Literal['outputFileValue', 'existingValue', 'leaveConflict']="outputFileValue",
        step_name: Optional[str] = None,
        perform_subsequent: bool = True,
        notification_url: Optional[str] = None,
        target_systemuid: Optional[str] = None,
        target_systempwd: Optional[str] = None
    ):
        """
        You can use this operation to start a z/OSMF workflow on a z/OS system.

        The workflow to be started must contain at least one automated step.
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-start-workflow
        Detailed request body parameters description:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-start-workflow#PUTMethodStartAWorkflow__WorkflowRequestContent__title__1

        Parameters
        ----------
        workflow_key: str
            Identifies the workflow to be started.
        resolve_conflict_by_using: Literal['outputFileValue', 'existingValue', 'leaveConflict']
            **Optional** Indicates how variable conflicts, if any, are to be handled when the Workflows task reads 
            in the output file from a step that runs a REXX exec or UNIX shell script.
        step_name: Optional[str]
            The name of the step at which automation is to begin.
        perform_subsequent: bool
            **Optional** If the workflow contains any subsequent automated steps, this property indicates whether 
            z/OSMF is to perform the steps.
        notification_url: Optional[str]
            A notification URL (up to 2000 characters).
        target_systemuid: Optional[str]
            The user ID to be used for remote system basic authentication.
        target_systempwd: Optional[str]
            The password to be used for remote system basic authentication.
        """
        body = {
            "resolveConflictByUsing": resolve_conflict_by_using,
            "stepName": step_name,
            "performSubsequent": perform_subsequent,
            "notificationUrl": notification_url,
            "targetSystemuid": target_systemuid,
            "targetSystempwd": target_systempwd
        }

        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}/operations/start".format(
            self._request_endpoint, 
            "workflows", 
            self._encode_uri_component(workflow_key)
        )
        custom_args["url"] = request_url

        custom_args["json"] = { k: v for k, v in body.items() if v not in [None, ""] }

        self.request_handler.perform_request("PUT", custom_args, expected_code=[202])

    def cancel_workflow(self, workflow_key: str) -> str: 
        """
        You can use this operation to cancel a z/OSMF workflow on a z/OS system.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-cancel-workflow

        Parameters
        ----------
        workflow_key: str
            Identifies the workflow to be canceled.

        Returns
        -------
        workflowName: str
            The new name of the canceled workflow on successful cancellation.
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}/operations/cancel".format(
            self._request_endpoint, 
            "workflows", 
            self._encode_uri_component(workflow_key)
        )
        custom_args["url"] = request_url

        response_json = self.request_handler.perform_request("PUT", custom_args)
        return response_json["workflowName"]
    
    def delete_workflow(self, workflow_key: str):
        """
        You can use this operation to remove a z/OSMF workflow from a z/OS system.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-delete-workflow

        Parameters
        ----------
        workflow_key: str
            Identifies the workflow to be deleted.
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}".format(self._request_endpoint, "workflows", self._encode_uri_component(workflow_key))
        custom_args["url"] = request_url

        self.request_handler.perform_request("DELETE", custom_args, expected_code=[204])

    def get_workflow_definition(
        self,
        definition_file_path: str,
        workflow_definition_file_system: Optional[str] = None,
        return_steps_data: bool = False,
        return_variables_data: bool = False
    ) -> GetWorkflowDefinitionResponse:
        """
        You can use this operation to retrieve the contents of a z/OSMF workflow definition from a z/OS system.
        
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-retrieve-workflow-definition
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-retrieve-workflow-definition#GETMethodRetrieveWorkflowDefinition__QueryParameters__title__1

        Parameters
        ----------
        definition_file_path: str
            Specifies the location of the workflow definition file, which is either a UNIX path name 
            (including the file name) or a fully qualified z/OS data set name.
        workflow_definition_file_system: Optional[str]
            Nickname of the system on which the specified workflow definition file and 
            any related files reside.
        return_steps_data: bool
            **Optional** Response will contain an array of **WorkflowDefinitionStepResponse** objects if True.
        return_variables_data: bool
            **Optional** Response will contain an array of **WorkflowDefinitionVariableResponse** objects if True.

        Returns
        -------
        GetWorkflowDefinitionResponse
            A GetWorkflowDefinitionResponse object containing the workflow definition file information
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}".format(self._request_endpoint, "workflowDefinition")
        custom_args["url"] = request_url

        params = {
            "definitionFilePath": definition_file_path,
            "workflowDefinitionFileSystem": workflow_definition_file_system,
        } | self._step_variables_body(return_steps_data, return_variables_data)
        custom_args["params"] = params

        response_json = self.request_handler.perform_request("GET", custom_args)
        return GetWorkflowDefinitionResponse(response_json)

    def archive_workflow(self, workflow_key: str) -> str:
        """
        You can use this operation to archive a z/OSMF workflow instance on a z/OS system.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-archive-workflow-instance
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-retrieve-workflow-definition#GETMethodRetrieveWorkflowDefinition__QueryParameters__title__1

        Parameters
        ----------
        workflow_key: str
            Identifies the workflow to be archived.

        Returns
        -------
        workflowKey: str
            The archived workflow key.
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}/operations/archive".format(
            self._request_endpoint, 
            "workflows", 
            self._encode_uri_component(workflow_key)
        )
        custom_args["url"] = request_url

        response_json = self.request_handler.perform_request("POST", custom_args, expected_code=[201])
        return response_json["workflowKey"]

    def list_archived_workflows(
        self, 
        order_by: Optional[Literal['desc', 'asc']] = None,
        view: Optional[Literal['user', 'domain']] = None
    ) -> list[ListArchivedWorkflowsResponse]:
        """
        You can use this operation to list the archived z/OSMF workflows for a system or sysplex.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-list-archived-workflows-system
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-list-archived-workflows-system#GETMethodListArchivedWorkflows__QueryParametersFilters__title__1
        
        Parameters
        ----------
        order_by: Optional[Literal['desc', 'asc']]
            To sort the returned instances by time.
        view: Optional[Literal['user', 'domain']]
            To select the list instances by view.

        Returns
        -------
        list[ListArchivedWorkflowsResponse]
            An array of ListArchivedWorkflowsResponse objects containing archived workflows information
        """
        custom_args = self._create_custom_request_arguments()

        params = {
            "orderBy": order_by,
            "view": view,
        }
        custom_args["params"] = params

        request_url = "{}/{}".format(self._request_endpoint, "archivedworkflows")
        custom_args["url"] = request_url

        response_json = self.request_handler.perform_request("GET", custom_args)
        return list(
            map(lambda workflow_raw: ListArchivedWorkflowsResponse(workflow_raw), response_json["archivedWorkflows"])
        )

    def get_archived_workflow_properties(
        self,
        workflow_key: str,
        return_steps_data: bool = False,
        return_variables_data: bool = False,
    ) -> GetArchivedWorkflowPropertiesResponse:
        """
        You can use this operation to retrieve the properties of an archived z/OSMF workflow.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-get-properties-archived-workflow
        Query parameters definition:
        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-get-properties-archived-workflow#GETMethodRetrieveInformationArchived__QueryParameterReturnData__title__1
        
        Parameters
        ----------
        workflow_key: str
            Identifies the archived workflow to be queried.
        return_steps_data: bool
            **Optional** Response will contain an array of **ArchivedWorkflowStepResponse** objects if True.
        return_variables_data: bool
            **Optional** Response will contain an array of **ArchivedWorkflowVariableResponse** objects if True.

        Returns
        -------
        GetArchivedWorkflowPropertiesResponse
            A GetArchivedWorkflowPropertiesResponse object the containing archived workflow properties
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}".format(self._request_endpoint, "archivedworkflows", self._encode_uri_component(workflow_key))
        custom_args["url"] = request_url

        params = self._step_variables_body(return_steps_data, return_variables_data)
        custom_args["params"] = params

        response_json = self.request_handler.perform_request("GET", custom_args)
        return GetArchivedWorkflowPropertiesResponse(response_json)

    def delete_archived_workflow(self, workflow_key: str):
        """
        You can use this operation to remove an archived z/OSMF workflow from a z/OS system.

        https://www.ibm.com/docs/en/zos/3.1.0?topic=services-delete-archived-workflow
        
        Parameters
        ----------
        workflow_key: str
            Identifies the archived workflow to be deleted.
        """
        custom_args = self._create_custom_request_arguments()

        request_url = "{}/{}/{}".format(self._request_endpoint, "archivedworkflows", self._encode_uri_component(workflow_key))
        custom_args["url"] = request_url

        self.request_handler.perform_request("DELETE", custom_args, expected_code=[204])
