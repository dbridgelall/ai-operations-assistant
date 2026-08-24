import unittest
from unittest.mock import patch

from web_app import app


class TestWebApp(unittest.TestCase):
    """Test the Flask web interface."""

    def setUp(self):
        """Create a Flask test client before each test."""

        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("web_app.update_workflow")
    @patch("web_app.get_workflow")
    def test_start_task(self, mock_get_workflow, mock_update_workflow):
        """Starting a task should change its status to In Progress."""

        workflow = {
            "id": "WF-001",
            "request": "Test workflow",
            "created": "2026-08-22",
            "status": "Active",
            "tasks": [
                {
                    "id": 1,
                    "task": "Test task",
                    "category": "Testing",
                    "priority": "Medium",
                    "owner": "Unassigned",
                    "status": "Not Started",
                }
            ],
        }

        mock_get_workflow.return_value = workflow

        response = self.client.post("/workflows/WF-001/tasks/1/start")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            workflow["tasks"][0]["status"],
            "In Progress",
        )

        self.assertEqual(
            workflow["status"],
            "Active",
        )

        mock_update_workflow.assert_called_once_with(workflow)

    @patch("web_app.update_workflow")
    @patch("web_app.get_workflow")
    def test_complete_task(self, mock_get_workflow, mock_update_workflow):
        """Completing the final task should complete the workflow."""

        workflow = {
            "id": "WF-001",
            "request": "Test workflow",
            "created": "2026-08-22",
            "status": "Active",
            "tasks": [
                {
                    "id": 1,
                    "task": "Test task",
                    "category": "Testing",
                    "priority": "Medium",
                    "owner": "Unassigned",
                    "status": "In Progress",
                }
            ],
        }

        mock_get_workflow.return_value = workflow

        response = self.client.post("/workflows/WF-001/tasks/1/complete")

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            workflow["tasks"][0]["status"],
            "Completed",
        )

        self.assertEqual(
            workflow["status"],
            "Completed",
        )

        mock_update_workflow.assert_called_once_with(workflow)

    @patch("web_app.save_workflow")
    @patch("web_app.analyze_request")
    def test_create_workflow_uses_selected_ai_engine(
        self,
        mock_analyze_request,
        mock_save_workflow,
    ):
        """Creating a workflow should pass the selected engine to the analyzer."""

        mock_analyze_request.return_value = {
            "id": "WF-001",
            "request": "Test AI workflow",
            "created": "2026-08-24",
            "status": "Active",
            "tasks": [],
        }

        response = self.client.post(
            "/workflows",
            data={
                "request": "Test AI workflow",
                "engine": "ai",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        mock_analyze_request.assert_called_once_with(
            "Test AI workflow",
            engine="ai",
        )

        mock_save_workflow.assert_called_once()
        
    @patch("web_app.save_workflow")
    @patch("web_app.analyze_request")
    def test_ai_failure_shows_friendly_error(
        self,
        mock_analyze_request,
        mock_save_workflow,
    ):
        """AI failures should return a friendly message without saving."""

        from app import AIWorkflowError

        mock_analyze_request.side_effect = AIWorkflowError(
            "Local AI failed."
        )

        response = self.client.post(
            "/workflows",
            data={
                "request": "Create an onboarding workflow.",
                "engine": "ai",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            b"Workflow generation failed",
            response.data,
        )

        self.assertIn(
            b"Local AI could not generate this workflow",
            response.data,
        )

        mock_save_workflow.assert_not_called()

if __name__ == "__main__":
    unittest.main()
