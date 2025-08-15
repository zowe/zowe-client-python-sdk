"""Integration tests for the Zowe Python SDK z/OSMF Workflows package."""

import json
import os
import time
import unittest

import yaml
from zowe.core_for_zowe_sdk import ProfileManager
from zowe.workflows_for_zowe_sdk import Workflows
from zowe.workflows_for_zowe_sdk.response import (
    CreateWorkflowResponse,
    GetWorkflowDefinitionResponse,
    GetWorkflowPropertiesResponse,
)
from zowe.zos_files_for_zowe_sdk import Files

FIXTURES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
FILES_FIXTURES_PATH = os.path.join(FIXTURES_PATH, "files.json")
ENV_FIXTURE_PATH = os.path.join(FIXTURES_PATH, "env.yml")
SAMPLE_WORKFLOW_FIXTURE_PATH = os.path.join(FIXTURES_PATH, "workflow.xml")
SAMPLE_WORKFLOW_INPUT_FIXTURE_PATH = os.path.join(FIXTURES_PATH, "workflow_input")


class TestZosmfWorkflowsIntegration(unittest.TestCase):
    """Workflows class integration tests."""

    created_workflow: CreateWorkflowResponse = None

    def setUp(self):
        """Setup fixtures for Zosmf class."""
        test_profile = ProfileManager(show_warnings=False).load(profile_type="zosmf")
        self.workflows = Workflows(test_profile)
        self.files = Files(test_profile)
        self.addCleanup(lambda: self.workflows.__exit__(None, None, None))
        self.addCleanup(lambda: self.files.__exit__(None, None, None))
        with open(FILES_FIXTURES_PATH, "r") as fixtures_json:
            self.files_fixtures = json.load(fixtures_json)
        with open(ENV_FIXTURE_PATH, "r") as env_yml:
            env_parsed = yaml.safe_load(env_yml)
            self.ZOS_WORKFLOWS_SYSTEM = env_parsed["ZOS_WORKFLOWS_SYSTEM"]
            self.ZOS_WORKFLOWS_OWNER = env_parsed["ZOS_WORKFLOWS_OWNER"]
            self.ZOS_WORKFLOWS_SAF_ID = env_parsed["ZOS_WORKFLOWS_SAF_ID"]
        self.test_uss_workflow = self.files_fixtures["TEST_USS_WORKFLOW"]
        self.test_uss_workflow_input = self.files_fixtures["TEST_USS_WORKFLOW_INPUT"]

    def tearDown(self):
        try:
            self.files.uss.delete(self.test_uss_workflow)
        except:
            pass
        try:
            self.files.uss.delete(self.test_uss_workflow_input)
        except:
            pass

        if self.created_workflow != None:
            try:
                self.workflows.delete_workflow(self.created_workflow.workflowKey)
            except:
                pass
            try:
                self.workflows.delete_archived_workflow(self.created_workflow.workflowKey)
            except:
                pass

    def test_get_definition_create_get_properties_list_start_cancel_delete(self):
        """Get workflow definition, create a workflow, get it's properties, list workflows by the name regex, start the workflow, cancel and delete it"""

        self.files.uss.upload(SAMPLE_WORKFLOW_FIXTURE_PATH, self.test_uss_workflow, encoding="IBM-1047")
        self.files.uss.upload(SAMPLE_WORKFLOW_INPUT_FIXTURE_PATH, self.test_uss_workflow_input, encoding="IBM-1047")

        workflow_def = self.workflows.get_workflow_definition(
            self.test_uss_workflow, return_steps_data=True, return_variables_data=True
        )

        self.assertIsInstance(workflow_def, GetWorkflowDefinitionResponse)
        self.assertEqual(workflow_def.workflowDefaultName, "Zowe Test Workflow")
        self.assertEqual(len(workflow_def.steps), 2)
        self.assertEqual(len(workflow_def.variables), 3)

        self.created_workflow = self.workflows.create_workflow(
            workflow_name="Zowe Test Workflow (Common)",
            workflow_definition_file=self.test_uss_workflow,
            system=self.ZOS_WORKFLOWS_SYSTEM,
            owner=self.ZOS_WORKFLOWS_OWNER,
            variable_input_file=self.test_uss_workflow_input,
            workflow_archive_safid=self.ZOS_WORKFLOWS_SAF_ID
        )
        self.assertIsInstance(self.created_workflow, CreateWorkflowResponse)

        workflow_props = self.workflows.get_workflow_properties(
            self.created_workflow.workflowKey, return_steps_data=True, return_variables_data=True
        )
        self.assertEqual(workflow_props.statusName, "in-progress")

        workflows_by_name = self.workflows.list_workflows(
            workflow_name="Zowe Test W.*",
        )
        self.assertEqual(len(workflows_by_name), 1)
        self.assertEqual(workflows_by_name[0].workflowKey, self.created_workflow.workflowKey)

        workflow_step_1 = next((step for step in workflow_props.steps if step.name == 'variables'), None)
        workflow_step_2 = next((step for step in workflow_props.steps if step.name == 'fake-check'), None)
        self.assertEqual(workflow_step_1.state, "Ready")
        self.assertEqual(workflow_step_2.state, "Not Ready")

        workflow_var_1 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_1'), 
            None
        )
        workflow_var_2 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_2'), 
            None
        )
        workflow_var_3 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_3'), 
            None
        )
        self.assertEqual(workflow_var_1.value, "TEST")
        self.assertEqual(workflow_var_2.value, "/tmp/test")
        self.assertEqual(workflow_var_3.value, None)

        self.workflows.start_workflow(self.created_workflow.workflowKey)

        workflow_props_after_start: GetWorkflowPropertiesResponse = None
        deadlock_check = 0
        while deadlock_check < 20:
            workflow_props_after_start = self.workflows.get_workflow_properties(
                self.created_workflow.workflowKey, return_steps_data=True
            )
            workflow_step_2_after_start = next(
                (step for step in workflow_props_after_start.steps if step.name == 'fake-check'), 
                None
            )
            if workflow_step_2_after_start.state != "Failed":
                time.sleep(1)
                deadlock_check += 1
            else:
                break

        if deadlock_check == 20:
            self.fail("Workflow start did not happen")

        self.assertNotEqual(workflow_props_after_start, None)

        workflow_step_1_after_start = next(
            (step for step in workflow_props_after_start.steps if step.name == 'variables'), 
            None
        )
        workflow_step_2_after_start = next(
            (step for step in workflow_props_after_start.steps if step.name == 'fake-check'), 
            None
        )
        self.assertEqual(workflow_step_1_after_start.state, "Complete")
        self.assertEqual(workflow_step_2_after_start.state, "Failed")

        self.workflows.cancel_workflow(self.created_workflow.workflowKey)

        workflow_props_after_cancel = self.workflows.get_workflow_properties(self.created_workflow.workflowKey)
        self.assertEqual(workflow_props_after_cancel.statusName, "canceled")

        self.workflows.delete_workflow(self.created_workflow.workflowKey)

    def test_create_archive_list_archived_get_archived_properties_delete_archived(self):
        """Create a workflow, archive it, list archived workflows by the name regex, get it's properties, and delete it"""

        self.files.uss.upload(SAMPLE_WORKFLOW_FIXTURE_PATH, self.test_uss_workflow, encoding="IBM-1047")
        self.files.uss.upload(SAMPLE_WORKFLOW_INPUT_FIXTURE_PATH, self.test_uss_workflow_input, encoding="IBM-1047")

        self.created_workflow = self.workflows.create_workflow(
            workflow_name="Zowe Test Workflow (Archived)",
            workflow_definition_file=self.test_uss_workflow,
            system=self.ZOS_WORKFLOWS_SYSTEM,
            owner=self.ZOS_WORKFLOWS_OWNER,
            variable_input_file=self.test_uss_workflow_input,
            workflow_archive_safid=self.ZOS_WORKFLOWS_SAF_ID
        )
        self.assertIsInstance(self.created_workflow, CreateWorkflowResponse)

        self.workflows.archive_workflow(self.created_workflow.workflowKey)

        workflow_props = self.workflows.get_archived_workflow_properties(
            self.created_workflow.workflowKey, return_steps_data=True, return_variables_data=True
        )
        self.assertEqual(workflow_props.statusName, "archived")

        workflow_step_1 = next((step for step in workflow_props.steps if step.name == 'variables'), None)
        workflow_step_2 = next((step for step in workflow_props.steps if step.name == 'fake-check'), None)
        self.assertEqual(workflow_step_1.state, "Ready")
        self.assertEqual(workflow_step_2.state, "Not Ready")

        workflow_var_1 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_1'), 
            None
        )
        workflow_var_2 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_2'), 
            None
        )
        workflow_var_3 = next(
            (variable for variable in workflow_props.variables if variable.name == 'ZOWE_TEST_VAR_3'), 
            None
        )
        self.assertEqual(workflow_var_1.value, "TEST")
        self.assertEqual(workflow_var_2.value, "/tmp/test")
        self.assertEqual(workflow_var_3.value, None)

        workflows_by_name = self.workflows.list_archived_workflows()
        archived_workflow = next(
            (workflow for workflow in workflows_by_name if workflow.workflowName == "Zowe Test Workflow (Archived)"), 
            None
        )
        self.assertEqual(archived_workflow.workflowKey, self.created_workflow.workflowKey)

        self.workflows.delete_archived_workflow(self.created_workflow.workflowKey)
