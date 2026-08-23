"""
AI Operations Assistant
Automated Test Suite

PURPOSE
-------
This file tests the core workflow logic in app.py.

Automated testing helps verify that changes to the application do not
accidentally break existing functionality.

TEST COVERAGE
-------------
The tests verify:

1. Task creation
2. Keyword-based workflow generation
3. Priority-based next-action selection
4. Completed-task handling
5. Workflow progress calculations

WHY TESTING MATTERS
-------------------
As the application grows, manually checking every feature becomes
inefficient and unreliable.

Automated tests allow us to make changes with greater confidence.
"""

import unittest

from app import (
    analyze_request,
    calculate_progress,
    create_task,
    determine_next_action,
)


# ===========================================================================
# TASK CREATION TESTS
# ===========================================================================

class TestTaskCreation(unittest.TestCase):
    """Test the standardized task data model."""

    def test_create_task(self):
        """Verify that create_task() returns the expected structure."""

        task = create_task(
            1,
            "Create interview schedule",
            "Scheduling",
            "High",
        )

        self.assertEqual(task["id"], 1)
        self.assertEqual(task["task"], "Create interview schedule")
        self.assertEqual(task["category"], "Scheduling")
        self.assertEqual(task["priority"], "High")
        self.assertEqual(task["owner"], "Unassigned")
        self.assertEqual(task["status"], "Not Started")


# ===========================================================================
# REQUEST ANALYSIS TESTS
# ===========================================================================

class TestRequestAnalysis(unittest.TestCase):
    """Test conversion of user requests into operational tasks."""

    def test_interview_request_generates_scheduling_task(self):
        """
        An interview request should generate an interview scheduling task.
        """

        workflow = analyze_request(
            "Coordinate interviews with several candidates."
        )

        task_names = [
            task["task"]
            for task in workflow["tasks"]
        ]

        self.assertIn(
            "Create interview schedule",
            task_names,
        )

    def test_candidate_request_generates_tracking_task(self):
        """
        Candidate-related requests should generate candidate tracking.
        """

        workflow = analyze_request(
            "Track candidate progress."
        )

        task_names = [
            task["task"]
            for task in workflow["tasks"]
        ]

        self.assertIn(
            "Track candidate status",
            task_names,
        )

    def test_confirmation_request_generates_communication_task(self):
        """
        Confirmation requests should generate confirmation tracking.
        """

        workflow = analyze_request(
            "Confirm the interview schedule."
        )

        task_names = [
            task["task"]
            for task in workflow["tasks"]
        ]

        self.assertIn(
            "Send and track confirmations",
            task_names,
        )

    def test_unknown_engine_raises_error(self):
        """Unsupported workflow engines should raise a clear error."""

        with self.assertRaises(ValueError):
            analyze_request(
                "Create a workflow.",
                engine="unknown",
            )

# ===========================================================================
# PRIORITY TESTS
# ===========================================================================

class TestPriorityLogic(unittest.TestCase):
    """Test selection of the next recommended operational action."""

    def test_high_priority_task_selected_first(self):
        """
        High-priority tasks should be recommended before lower priorities.
        """

        workflow = {
            "tasks": [
                create_task(
                    1,
                    "Prepare report",
                    "Reporting",
                    "Medium",
                ),
                create_task(
                    2,
                    "Send confirmation",
                    "Communication",
                    "High",
                ),
                create_task(
                    3,
                    "Review workflow",
                    "Workflow Management",
                    "Low",
                ),
            ]
        }

        next_task = determine_next_action(workflow)

        self.assertEqual(
            next_task["task"],
            "Send confirmation",
        )

    def test_completed_task_is_not_recommended(self):
        """
        Completed tasks should be excluded from next-action selection.
        """

        completed_task = create_task(
            1,
            "Send confirmation",
            "Communication",
            "High",
        )

        completed_task["status"] = "Completed"

        workflow = {
            "tasks": [
                completed_task,
                create_task(
                    2,
                    "Prepare report",
                    "Reporting",
                    "Medium",
                ),
            ]
        }

        next_task = determine_next_action(workflow)

        self.assertEqual(
            next_task["task"],
            "Prepare report",
        )


# ===========================================================================
# PROGRESS TESTS
# ===========================================================================

class TestProgressCalculation(unittest.TestCase):
    """Test workflow completion calculations."""

    def test_zero_percent_progress(self):
        """A new workflow should begin at 0% completion."""

        workflow = {
            "tasks": [
                create_task(
                    1,
                    "Task One",
                    "Testing",
                ),
                create_task(
                    2,
                    "Task Two",
                    "Testing",
                ),
            ]
        }

        self.assertEqual(
            calculate_progress(workflow),
            0,
        )

    def test_fifty_percent_progress(self):
        """One completed task out of two should equal 50%."""

        task_one = create_task(
            1,
            "Task One",
            "Testing",
        )

        task_two = create_task(
            2,
            "Task Two",
            "Testing",
        )

        task_one["status"] = "Completed"

        workflow = {
            "tasks": [
                task_one,
                task_two,
            ]
        }

        self.assertEqual(
            calculate_progress(workflow),
            50,
        )

    def test_full_completion(self):
        """All completed tasks should produce 100% progress."""

        task_one = create_task(
            1,
            "Task One",
            "Testing",
        )

        task_two = create_task(
            2,
            "Task Two",
            "Testing",
        )

        task_one["status"] = "Completed"
        task_two["status"] = "Completed"

        workflow = {
            "tasks": [
                task_one,
                task_two,
            ]
        }

        self.assertEqual(
            calculate_progress(workflow),
            100,
        )


# ===========================================================================
# TEST RUNNER
# ===========================================================================
# ===========================================================================
# WORKFLOW STATUS AND EDGE-CASE TESTS
# ===========================================================================


class TestWorkflowBehavior(unittest.TestCase):
    """
    Test workflow behavior beyond basic task generation.

    These tests verify that the workflow engine behaves correctly as
    tasks move through their lifecycle.
    """

    def test_completed_high_priority_task_is_skipped(self):
        """
        The recommendation engine should ignore completed work even when
        that work has a higher priority than remaining tasks.
        """

        high_priority_task = create_task(
            1,
            "Urgent communication",
            "Communication",
            "High",
        )

        medium_priority_task = create_task(
            2,
            "Prepare report",
            "Reporting",
            "Medium",
        )

        high_priority_task["status"] = "Completed"

        workflow = {
            "tasks": [
                high_priority_task,
                medium_priority_task,
            ]
        }

        next_task = determine_next_action(workflow)

        self.assertEqual(
            next_task["task"],
            "Prepare report",
        )

    def test_all_completed_tasks_return_no_next_action(self):
        """
        When every task is complete, no next action should be returned.
        """

        task_one = create_task(
            1,
            "Task One",
            "Testing",
            "High",
        )

        task_two = create_task(
            2,
            "Task Two",
            "Testing",
            "Medium",
        )

        task_one["status"] = "Completed"
        task_two["status"] = "Completed"

        workflow = {
            "tasks": [
                task_one,
                task_two,
            ]
        }

        self.assertIsNone(
            determine_next_action(workflow)
        )

    def test_unknown_request_still_generates_review_task(self):
        """
        Requests containing no recognized keywords should still produce
        the default workflow review task.
        """

        workflow = analyze_request(
            "Organize the miscellaneous items."
        )

        self.assertEqual(
            len(workflow["tasks"]),
            1,
        )

        self.assertEqual(
            workflow["tasks"][0]["task"],
            "Review workflow and determine next action",
        )

    def test_task_ids_are_sequential(self):
        """
        Generated tasks should receive sequential IDs beginning with 1.
        """

        workflow = analyze_request(
            "Interview candidates, confirm schedules, "
            "email the committee, and prepare a report."
        )

        task_ids = [
            task["id"]
            for task in workflow["tasks"]
        ]

        expected_ids = list(
            range(1, len(task_ids) + 1)
        )

        self.assertEqual(
            task_ids,
            expected_ids,
        )
        
if __name__ == "__main__":
    unittest.main()