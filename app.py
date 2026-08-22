"""
AI Operations Assistant
Version 1.2 - Structured Task Management

PURPOSE
-------
Transform plain-English operational requests into structured workflows.

Version 1.2 introduces a TASK DATA MODEL.

Previously, tasks were stored as simple strings:

    "Create interview schedule"

Tasks are now structured dictionaries:

    {
        "id": 1,
        "task": "Create interview schedule",
        "category": "Scheduling",
        "priority": "High",
        "owner": "Unassigned",
        "status": "Not Started"
    }

WHY THIS MATTERS
----------------
Structured data allows future versions of the application to:

- Sort tasks by priority
- Assign task owners
- Track completion
- Calculate workflow progress
- Export workflows
- Store workflows in JSON or databases
- Display workflows in a web dashboard
- Allow AI to modify workflow attributes
"""

from datetime import date
from storage import save_workflow, count_workflows

# ===========================================================================
# TASK CREATION
# ===========================================================================


def create_task(task_id, name, category, priority="Medium"):
    """
    Create a standardized task object.

    Parameters
    ----------
    task_id : int
        Unique number identifying the task.

    name : str
        Human-readable description of the work.

    category : str
        Operational category associated with the task.

    priority : str
        Importance level. Defaults to "Medium".

    Returns
    -------
    dict
        Structured task data.

    DESIGN DECISION
    ---------------
    Task creation is handled by one function so every task follows
    the same data structure.

    Later, additional fields such as due dates and dependencies can
    be added here without rewriting every workflow rule.
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
# WORKFLOW ANALYSIS
# ===========================================================================


def analyze_request(request):
    """
    Convert an operational request into structured workflow data.

    PROCESS
    -------
    1. Normalize user input.
    2. Detect operational concepts.
    3. Generate structured tasks.
    4. Assign task IDs.
    5. Package tasks inside a workflow object.

    NOTE
    ----
    Version 1.2 still uses rule-based keyword detection.

    Future AI integration will improve interpretation of requests that
    use different wording but describe the same operational concept.
    """

    request_lower = request.lower()

    tasks = []

    # task_id increases every time a task is created.
    #
    # This provides each task with a unique identifier inside the workflow.

    task_id = 1

    # -----------------------------------------------------------------------
    # SCHEDULING / INTERVIEWS
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
    # GENERAL EMAIL REQUESTS
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
    # DEFAULT REVIEW TASK
    # -----------------------------------------------------------------------
    #
    # Every workflow receives a final review step.
    #
    # This provides a logical closing action and ensures the workflow
    # is never empty.

    tasks.append(
        create_task(
            task_id,
            "Review workflow and determine next action",
            "Workflow Management",
            "Low",
        )
    )

    # -----------------------------------------------------------------------
    # WORKFLOW OBJECT
    # -----------------------------------------------------------------------

    workflow = {
        "request": request,
        "created": str(date.today()),
        "status": "Active",
        "tasks": tasks,
    }

    return workflow


# ===========================================================================
# WORKFLOW METRICS
# ===========================================================================


def calculate_progress(workflow):
    """
    Calculate workflow completion percentage.

    A task is considered complete when:

        status == "Completed"

    Formula:

        completed tasks / total tasks * 100

    Example
    -------
    2 completed tasks out of 5:

        2 / 5 * 100 = 40%

    This functionality becomes useful when workflows are later displayed
    inside dashboards.
    """

    total_tasks = len(workflow["tasks"])

    if total_tasks == 0:
        return 0

    completed_tasks = sum(
        1 for task in workflow["tasks"] if task["status"] == "Completed"
    )

    return round((completed_tasks / total_tasks) * 100)


# ===========================================================================
# NEXT ACTION LOGIC
# ===========================================================================


def determine_next_action(workflow):
    """
    Determine the next recommended task.

    Version 1.2 uses priority as the primary decision rule.

    Priority ranking:

        High   = 1
        Medium = 2
        Low    = 3

    Future versions can consider:
    - deadlines
    - dependencies
    - assigned owners
    - workload
    - AI recommendations
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

    # min() selects the task with the smallest priority ranking.
    #
    # Because High = 1, high-priority work is selected first.
    #
    # task["id"] acts as a secondary sorting value so earlier tasks win
    # when multiple tasks have the same priority.

    return min(
        incomplete_tasks,
        key=lambda task: (
            priority_rank.get(task["priority"], 99),
            task["id"],
        ),
    )


# ===========================================================================
# WORKFLOW DISPLAY
# ===========================================================================


def display_workflow(workflow):
    """
    Display workflow information and structured tasks.

    Presentation remains separate from workflow analysis.

    This separation will allow the command-line interface to eventually
    be replaced by a web interface while keeping the workflow engine.
    """

    print("\nAI OPERATIONS ASSISTANT")
    print("=" * 60)

    print(f"\nRequest: {workflow['request']}")
    print(f"Created: {workflow['created']}")
    print(f"Status: {workflow['status']}")

    progress = calculate_progress(workflow)

    print(f"Progress: {progress}%")

    print("\nTASKS")
    print("=" * 60)

    for task in workflow["tasks"]:

        print(f"\nTASK {task['id']:03}")

        print(task["task"])

        print(f"Category: {task['category']}")
        print(f"Priority: {task['priority']}")
        print(f"Owner: {task['owner']}")
        print(f"Status: {task['status']}")

        print("-" * 60)

    # -----------------------------------------------------------------------
    # NEXT RECOMMENDED ACTION
    # -----------------------------------------------------------------------

    next_task = determine_next_action(workflow)

    print("\nNEXT RECOMMENDED ACTION")
    print("=" * 60)

    if next_task:

        print(f"TASK {next_task['id']:03} - " f"{next_task['task']}")

        print(f"Priority: {next_task['priority']}")

    else:

        print("All tasks completed.")

    print("\n" + "=" * 60)


# ===========================================================================
# APPLICATION ENTRY POINT
# ===========================================================================


def main():
    """
    Run the command-line application.

    If interactive input is unavailable, the program automatically
    switches to demonstration mode.
    """

    print("AI Operations Assistant")
    print("-" * 60)

    print("Transform operational requests into structured workflows.\n")

    try:
        request = input("Describe the work that needs to be completed:\n> ")

        if not request.strip():
            raise ValueError("No request entered.")

    except (OSError, EOFError, ValueError):
        print(
            "\nInteractive input is unavailable."
            "\nRunning demonstration workflow instead.\n"
        )

        request = (
            "Coordinate interviews with five candidates, "
            "track confirmations, and prepare an update "
            "for the hiring committee."
        )

        print("Demo Request:")
        print(request)

    # Generate the structured workflow.
    workflow = analyze_request(request)

    # Display the workflow before saving it.
    display_workflow(workflow)

    # Persist the workflow so it remains available after the
    # application closes.
    save_workflow(workflow)

    print("\nWorkflow saved successfully.")
    print(f"Total saved workflows: {count_workflows()}")


# ===========================================================================
# PROGRAM START
# ===========================================================================

if __name__ == "__main__":
    main()

