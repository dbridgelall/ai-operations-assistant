"""
AI Operations Assistant
Core Workflow Engine

PURPOSE
-------
Transform plain-English operational requests into structured,
prioritized, and trackable workflows.

WORKFLOW ENGINES
----------------
Rules Engine
    Uses deterministic keyword-based rules to generate predictable
    operational tasks.

Local AI Engine
    Uses Qwen through Ollama to interpret operational requests and
    generate structured tasks locally.

ARCHITECTURE
------------
User Request
    |
    v
Workflow Engine
    |
    +-- Rules Engine
    |
    +-- Local AI (Ollama / Qwen)
    |
    v
Validated Task Data
    |
    v
Workflow Management
    |
    v
JSON Persistence
"""

import json
import ollama

from storage import (
    count_workflows,
    get_workflow,
    load_workflows,
    save_workflow,
    update_workflow,
)

from workflow_engine import (
    AIWorkflowError,
    analyze_request,
    calculate_progress,
    create_task,
    determine_next_action,
    get_task,
)

# ===========================================================================
# DISPLAY WORKFLOW DETAILS
# ===========================================================================


def display_workflow(workflow):
    """
    Display complete information for one workflow.
    """

    print("\n" + "=" * 65)
    print("WORKFLOW DETAILS")
    print("=" * 65)

    print(f"Workflow ID: {workflow['id']}")
    print(f"Created: {workflow['created']}")
    print(f"Status: {workflow['status']}")
    print(f"Progress: {calculate_progress(workflow)}%")

    print(f"\nRequest:\n{workflow['request']}")

    print("\nTASKS")
    print("-" * 65)

    for task in workflow["tasks"]:
        print(f"\nTASK {task['id']:03}")
        print(task["task"])
        print(f"Category: {task['category']}")
        print(f"Priority: {task['priority']}")
        print(f"Owner: {task['owner']}")
        print(f"Status: {task['status']}")

    next_task = determine_next_action(workflow)

    print("\n" + "-" * 65)
    print("NEXT RECOMMENDED ACTION")

    if next_task:
        print(
            f"TASK {next_task['id']:03} - "
            f"{next_task['task']} [{next_task['priority']}]"
        )
    else:
        print("All tasks completed.")

    print("=" * 65)


# ===========================================================================
# CREATE WORKFLOW
# ===========================================================================


def create_new_workflow():
    """
    Collect an operational request and create a persistent workflow.
    """

    print("\nCREATE NEW WORKFLOW")
    print("-" * 65)

    request = input(
        "Describe the operational work that needs to be completed:\n> "
    ).strip()

    if not request:
        print("\nA workflow cannot be created from an empty request.")
        return

    workflow = analyze_request(request)

    save_workflow(workflow)

    print(f"\nWorkflow {workflow['id']} created successfully.")

    display_workflow(workflow)


# ===========================================================================
# LIST WORKFLOWS
# ===========================================================================


def list_saved_workflows():
    """
    Display a compact summary of all saved workflows.
    """

    workflows = load_workflows()

    print("\nSAVED WORKFLOWS")
    print("=" * 65)

    if not workflows:
        print("No workflows have been saved.")
        return

    for workflow in workflows:
        progress = calculate_progress(workflow)

        request_preview = workflow["request"]

        if len(request_preview) > 45:
            request_preview = request_preview[:42] + "..."

        print(
            f"{workflow['id']} | "
            f"{workflow['status']:<9} | "
            f"{progress:>3}% | "
            f"{request_preview}"
        )

    print("-" * 65)
    print(f"Total workflows: {count_workflows()}")


# ===========================================================================
# WORKFLOW SELECTION
# ===========================================================================


def request_workflow_id():
    """
    Ask the user for a workflow ID and normalize its format.

    Entering either:

        1

    or:

        WF-001

    resolves to:

        WF-001
    """

    workflow_id = input(
        "\nEnter workflow ID (example: WF-001): "
    ).strip().upper()

    if workflow_id.isdigit():
        workflow_id = f"WF-{int(workflow_id):03}"

    return workflow_id


# ===========================================================================
# VIEW ONE WORKFLOW
# ===========================================================================


def view_workflow_details():
    """
    Retrieve and display a selected workflow.
    """

    workflow_id = request_workflow_id()

    workflow = get_workflow(workflow_id)

    if workflow is None:
        print(f"\nWorkflow {workflow_id} was not found.")
        return

    display_workflow(workflow)


# ===========================================================================
# UPDATE TASK STATUS
# ===========================================================================


def update_task_status():
    """
    Update the status of a task inside a saved workflow.

    Valid statuses:
        1. Not Started
        2. In Progress
        3. Completed
    """

    workflow_id = request_workflow_id()

    workflow = get_workflow(workflow_id)

    if workflow is None:
        print(f"\nWorkflow {workflow_id} was not found.")
        return

    display_workflow(workflow)

    try:
        task_id = int(input("\nEnter the task number to update: "))

    except ValueError:
        print("\nTask number must be numeric.")
        return

    selected_task = get_task(workflow, task_id)

    if selected_task is None:
        print(f"\nTask {task_id} was not found.")
        return

    print("\nSELECT NEW STATUS")
    print("1. Incomplete")
    print("2. In Progress")
    print("3. Completed")

    status_choice = input("\nSelection: ").strip()

    statuses = {
        "1": "Incomplete",
        "2": "In Progress",
        "3": "Completed",
    }

    new_status = statuses.get(status_choice)

    if new_status is None:
        print("\nInvalid status selection.")
        return

    selected_task["status"] = new_status

    # Automatically close the workflow once every task is complete.
    if all(task["status"] == "Completed" for task in workflow["tasks"]):
        workflow["status"] = "Completed"
    else:
        workflow["status"] = "Active"

    update_workflow(workflow)

    print(
        f"\nTASK {selected_task['id']:03} updated to "
        f"'{selected_task['status']}'."
    )

    print(f"Workflow progress: {calculate_progress(workflow)}%")


# ===========================================================================
# MAIN MENU
# ===========================================================================


def display_menu():
    """
    Display the application's primary navigation menu.
    """

    print("\n" + "=" * 65)
    print("AI OPERATIONS ASSISTANT")
    print("=" * 65)

    print("1. Create New Workflow")
    print("2. View Saved Workflows")
    print("3. View Workflow Details")
    print("4. Update Task Status")
    print("5. Exit")

    print("-" * 65)


# ===========================================================================
# APPLICATION
# ===========================================================================


def main():
    """
    Run the interactive workflow manager.

    The menu remains active until the user explicitly chooses Exit.
    """

    while True:
        display_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            create_new_workflow()

        elif choice == "2":
            list_saved_workflows()

        elif choice == "3":
            view_workflow_details()

        elif choice == "4":
            update_task_status()

        elif choice == "5":
            print("\nAI Operations Assistant closed.")
            break

        else:
            print("\nInvalid selection. Choose an option from 1 through 5.")


# ===========================================================================
# PROGRAM START
# ===========================================================================


if __name__ == "__main__":
    main()
