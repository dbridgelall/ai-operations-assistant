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


if __name__ == "__main__":
    unittest.main()
