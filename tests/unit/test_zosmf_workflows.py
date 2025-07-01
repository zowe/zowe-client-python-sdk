"""Unit tests for the Zowe Python SDK z/OSMF Workflows package."""

import unittest
from unittest import mock

from zowe.zosmf_workflows_for_zowe_sdk import Workflows
from zowe.zosmf_workflows_for_zowe_sdk.response import (
    CreateWorkflowResponse,
    GetArchivedWorkflowPropertiesResponse,
    GetWorkflowDefinitionResponse,
    GetWorkflowPropertiesResponse,
    ListArchivedWorkflowsResponse,
    ListWorkflowsResponse,
)


class TestWorkflowsClass(unittest.TestCase):
    """Workflows class unit tests."""

    def setUp(self):
        """Setup fixtures for Workflows class."""
        self.connection_dict = {
            "host": "mock-url.com",
            "user": "Username",
            "password": "Password",
            "port": 443,
            "rejectUnauthorized": True,
        }

    @mock.patch("requests.Session.send")
    def test_create_workflow_success(self, mock_send_request):
        """Create a workflow should succeed when all the necessary parameters are specified"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 201
        mock_response.json.return_value = {}
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        result = workflows.create_workflow(
          workflow_name="Test workflow",
          workflow_definition_file="/some/valid/path/workflow.xml",
          system="MYSYS",
          owner="TEST",
          variable_input_file="/some/valid/path/workflow_input",
          workflow_archive_safid="TEST"
        )

        self.assertIsInstance(result, CreateWorkflowResponse)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_workflow_properties(self, mock_send_request):
        """Get workflow properties should return the workflow properies"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "steps": None, "variables": None
        }

        is_url_correct = False
        def check_correct_query(self, **other_args):
            nonlocal is_url_correct
            is_url_correct = not "steps" in self.url and not "variables" in self.url
            return mock_response
        mock_send_request.side_effect = check_correct_query

        workflows = Workflows(self.connection_dict)
        result = workflows.get_workflow_properties("test")
        self.assertIsInstance(result, GetWorkflowPropertiesResponse)
        self.assertEqual(result.steps, None)
        self.assertEqual(result.variables, None)
        mock_send_request.assert_called_once()
        self.assertEqual(is_url_correct, True)

    @mock.patch("requests.Session.send")
    def test_list_workflows(self, mock_send_request):
        """List workflows by the specified parameters should work"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {"workflows": [{}]}
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        result = workflows.list_workflows()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], ListWorkflowsResponse)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_start_workflow(self, mock_send_request):
        """Start a workflow should return a correct response code"""
        mock_response = mock.Mock()
        mock_response.status_code = 202
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        workflows.start_workflow("some_workflow_key")

        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_cancel_workflow(self, mock_send_request):
        """Cancel a workflow should return a workflow name"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200

        workflow_name = "test"
        def cancel_workflow_response(self, **other_args):
            mock_response.json.return_value = {"workflowName": workflow_name}
            return mock_response
        mock_send_request.side_effect = cancel_workflow_response

        workflows = Workflows(self.connection_dict)
        result = workflows.cancel_workflow("some_workflow_key")

        self.assertEqual(result, workflow_name)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_delete_workflow(self, mock_send_request):
        """Delete a workflow should return a correct response code"""
        mock_response = mock.Mock()
        mock_response.status_code = 204
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        workflows.delete_workflow("some_workflow_key")

        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_workflow_definition_with_steps(self, mock_send_request):
        """Get workflow definition should return the workflow definition with steps"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "steps": [{}], "variables": None
        }

        is_url_correct = False
        def check_correct_query(self, **other_args):
            nonlocal is_url_correct
            is_url_correct = "steps" in self.url and not "variables" in self.url
            return mock_response
        mock_send_request.side_effect = check_correct_query

        workflows = Workflows(self.connection_dict)
        result = workflows.get_workflow_definition("/test/workflow/path.xml", return_steps_data=True)
        self.assertIsInstance(result, GetWorkflowDefinitionResponse)
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.variables, None)
        mock_send_request.assert_called_once()
        self.assertEqual(is_url_correct, True)

    @mock.patch("requests.Session.send")
    def test_archive_workflow_success(self, mock_send_request):
        """Archive a workflow should succeed when all the necessary parameters are specified"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 201
        mock_response.json.return_value = {}

        workflow_key = "test_workflow_key"
        def archive_workflow_response(self, **other_args):
            mock_response.json.return_value = {"workflowKey": workflow_key}
            return mock_response
        mock_send_request.side_effect = archive_workflow_response

        workflows = Workflows(self.connection_dict)
        result = workflows.archive_workflow(workflow_key)

        self.assertEqual(result, workflow_key)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_list_archived_workflows(self, mock_send_request):
        """List archived workflows by the specified parameters should work"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {"archivedWorkflows": [{}, {}]}
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        result = workflows.list_archived_workflows()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ListArchivedWorkflowsResponse)
        self.assertIsInstance(result[1], ListArchivedWorkflowsResponse)
        mock_send_request.assert_called_once()

    @mock.patch("requests.Session.send")
    def test_get_archived_workflow_properties_with_variables(self, mock_send_request):
        """Get workflow archived properties should return the archived workflow properties with variables"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "steps": None, "variables": [{}, {}]
        }

        is_url_correct = False
        def check_correct_query(self, **other_args):
            nonlocal is_url_correct
            is_url_correct = not "steps" in self.url and "variables" in self.url
            return mock_response
        mock_send_request.side_effect = check_correct_query

        workflows = Workflows(self.connection_dict)
        result = workflows.get_archived_workflow_properties("test_workflow_key", return_variables_data=True)
        self.assertIsInstance(result, GetArchivedWorkflowPropertiesResponse)
        self.assertEqual(result.steps, None)
        self.assertEqual(len(result.variables), 2)
        mock_send_request.assert_called_once()
        self.assertEqual(is_url_correct, True)

    @mock.patch("requests.Session.send")
    def test_get_archived_workflow_properties_with_steps_and_variables(self, mock_send_request):
        """Get workflow archived properties should return the archived workflow properties with steps and variables"""
        mock_response = mock.Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "steps": [{}, {}], "variables": [{}]
        }

        is_url_correct = False
        def check_correct_query(self, **other_args):
            nonlocal is_url_correct
            is_url_correct = "steps%2Cvariables" in self.url
            return mock_response
        mock_send_request.side_effect = check_correct_query

        workflows = Workflows(self.connection_dict)
        result = workflows.get_archived_workflow_properties(
            "test_workflow_key", return_steps_data=True, return_variables_data=True
        )
        self.assertIsInstance(result, GetArchivedWorkflowPropertiesResponse)
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(len(result.variables), 1)
        mock_send_request.assert_called_once()
        self.assertEqual(is_url_correct, True)

    @mock.patch("requests.Session.send")
    def test_delete_archived_workflow(self, mock_send_request):
        """Delete an archived workflow should return a correct response code"""
        mock_response = mock.Mock()
        mock_response.status_code = 204
        mock_send_request.return_value = mock_response

        workflows = Workflows(self.connection_dict)
        workflows.delete_archived_workflow("some_workflow_key")

        mock_send_request.assert_called_once()
