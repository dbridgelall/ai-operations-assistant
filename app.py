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
from datetime import date

import ollama

from storage import (
    count_workflows,
    get_workflow,
    load_workflows,
    save_workflow,
    update_workflow,
)

class AIWorkflowError(Exception):
    """Raised when the local AI engine cannot generate a valid workflow."""

    pass

# ===========================================================================
# TASK CREATION
# ===========================================================================


def create_task(task_id, name, category, priority="Medium"):
    """
    Create a standardized operational task.

    Each task contains information needed for tracking and prioritization.
    """

    return {
        "id": task_id,
        "task": name,
        "category": category,
        "priority": priority,
        "owner": "Unassigned",
        "status": "Not Started",
    }


# ===========================================================================
# WORKFLOW ID GENERATION
# ===========================================================================


def generate_workflow_id():
    """
    Generate the next sequential workflow ID.

    Example
    -------
    If three workflows exist:

        WF-001
        WF-002
        WF-003

    the next workflow becomes:

        WF-004

    NOTE
    ----
    Sequential IDs are sufficient for this local application.

    A production system would typically use database-generated IDs
    or UUIDs.
    """

    workflows = load_workflows()

    highest_number = 0

    for workflow in workflows:
        workflow_id = workflow.get("id", "")

        if workflow_id.startswith("WF-"):
            try:
                number = int(workflow_id.split("-")[1])
                highest_number = max(highest_number, number)
            except (ValueError, IndexError):
                continue

    return f"WF-{highest_number + 1:03}"


# ===========================================================================
# WORKFLOW ANALYSIS
# ===========================================================================


def analyze_request_with_rules(request):
    """
    Convert a plain-English operational request into structured tasks.

    The rules engine provides predictable workflow generation without
    requiring a local AI model.
    """

    request_lower = request.lower()

    tasks = []
    task_id = 1

    # -----------------------------------------------------------------------
    # INTERVIEW SCHEDULING
    # -----------------------------------------------------------------------

    if "interview" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Create interview schedule",
                "Scheduling",
                "High",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # CANDIDATE TRACKING
    # -----------------------------------------------------------------------

    if "candidate" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Track candidate status",
                "Recruiting Operations",
                "Medium",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # CONFIRMATIONS
    # -----------------------------------------------------------------------

    if "confirmation" in request_lower or "confirm" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Send and track confirmations",
                "Communication",
                "High",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # COMMITTEE COMMUNICATION
    # -----------------------------------------------------------------------

    if "committee" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Prepare committee update",
                "Communication",
                "Medium",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # EMAIL
    # -----------------------------------------------------------------------

    if "email" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Prepare required email communication",
                "Communication",
                "Medium",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # REPORTING
    # -----------------------------------------------------------------------

    if "report" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Prepare operational report",
                "Reporting",
                "Medium",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # DOCUMENTATION
    # -----------------------------------------------------------------------

    if "document" in request_lower:
        tasks.append(
            create_task(
                task_id,
                "Prepare or review documentation",
                "Documentation",
                "Medium",
            )
        )
        task_id += 1

    # -----------------------------------------------------------------------
    # DEFAULT WORKFLOW REVIEW
    # -----------------------------------------------------------------------

    tasks.append(
        create_task(
            task_id,
            "Review workflow and determine next action",
            "Workflow Management",
            "Low",
        )
    )

    workflow = {
        "id": generate_workflow_id(),
        "request": request,
        "created": str(date.today()),
        "status": "Active",
        "tasks": tasks,
    }

    return workflow

def analyze_request_with_ai(request):
    """
    Analyze an operational request using a locally running AI model.

    Ollama handles local model execution while Python validates and
    converts the generated task data into the application's standard
    task structure.
    """

    prompt = f"""
    You are an operations workflow assistant.

    Convert the following operational request into a concise list of
    actionable tasks.

    Operational request:
    {request}

    Return ONLY valid JSON using this exact structure:

    {{
        "tasks": [
            {{
                "task": "Task description",
                "category": "Category",
                "priority": "High"
            }}
        ]
    }}

    Requirements:
    - Generate between 2 and 6 useful tasks.
    - Tasks must be specific and actionable.
    - Valid priorities are High, Medium, or Low.

    Priority rules:
    - High: blocking, urgent, time-sensitive, or required before other tasks can proceed.
    - Medium: important work that should be completed soon but does not immediately block the workflow.
    - Low: follow-up, review, documentation, or non-urgent supporting work.
    - Prioritize tasks relative to each other.
    - Do not assign every task the same priority unless the request clearly requires it.
    - Use High priority sparingly.

    - Do not include task IDs.
    - Do not include task status.
    - Do not include task owners.
    - Do not include explanations outside the JSON.
    """

    try:
        response = ollama.chat(
            model="qwen3:1.7b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format="json",
            options={
                "temperature": 0,
            },
        )

        ai_data = json.loads(
            response["message"]["content"]
        )

        ai_tasks = ai_data["tasks"]

    except (ConnectionError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise AIWorkflowError(
            "Local AI could not generate a valid workflow."
        ) from error

    if not 2 <= len(ai_tasks) <= 6:
        raise AIWorkflowError(
    "Local AI must generate between 2 and 6 tasks."
    )
 
    tasks = []

    for task_id, ai_task in enumerate(ai_tasks, start=1):
        tasks.append(
            create_task(
                task_id,
                ai_task["task"],
                ai_task["category"],
                ai_task["priority"],
            )
        )

    workflow = {
        "id": generate_workflow_id(),
        "request": request,
        "created": str(date.today()),
        "status": "Active",
        "tasks": tasks,
    }

    return workflow

def analyze_request(request, engine="rules"):
    """
    Analyze an operational request using the selected workflow engine.

    Supported engines
    -----------------
    rules
        Deterministic keyword-based workflow generation.

    ai
        AI-powered workflow generation.
    """

    if engine == "rules":
        return analyze_request_with_rules(request)

    if engine == "ai":
        return analyze_request_with_ai(request)

    raise ValueError(
        f"Unsupported workflow engine: {engine}"
    )

# ===========================================================================
# WORKFLOW PROGRESS
# ===========================================================================


def calculate_progress(workflow):
    """
    Calculate the percentage of completed tasks.
    """

    total_tasks = len(workflow["tasks"])

    if total_tasks == 0:
        return 0

    completed_tasks = sum(
        1 for task in workflow["tasks"] if task["status"] == "Completed"
    )

    return round((completed_tasks / total_tasks) * 100)


# ===========================================================================
# NEXT ACTION
# ===========================================================================


def determine_next_action(workflow):
    """
    Select the highest-priority incomplete task.

    Ranking
    -------
    High   -> 1
    Medium -> 2
    Low    -> 3

    Task ID is used as a secondary ranking when priorities match.
    """

    priority_rank = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    incomplete_tasks = [
        task for task in workflow["tasks"] if task["status"] != "Completed"
    ]

    if not incomplete_tasks:
        return None

    return min(
        incomplete_tasks,
        key=lambda task: (
            priority_rank.get(task["priority"], 99),
            task["id"],
        ),
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

    selected_task = None

    for task in workflow["tasks"]:
        if task["id"] == task_id:
            selected_task = task
            break

    if selected_task is None:
        print(f"\nTask {task_id} was not found.")
        return

    print("\nSELECT NEW STATUS")
    print("1. Not Started")
    print("2. In Progress")
    print("3. Completed")

    status_choice = input("\nSelection: ").strip()

    statuses = {
        "1": "Not Started",
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
