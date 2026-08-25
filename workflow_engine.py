"""
AI Operations Assistant
Workflow Engine

Shared business logic for generating, validating, prioritizing,
and managing operational workflows.

Both the command-line interface and Flask web application use
this module.
"""

# Imports

import json
from datetime import date

import ollama

from storage import load_workflows

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

def get_task(workflow, task_id):
    """
    Return a task from a workflow by its ID.

    Returns None when no matching task exists.
    """

    for task in workflow["tasks"]:
        if task["id"] == task_id:
            return task

    return None


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