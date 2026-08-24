"""
AI Operations Assistant
Version 2.2 - Web Workflow Creation

PURPOSE
-------
Provide a browser-based interface for creating and reviewing
operational workflows.

Version 2.2 connects the dashboard form to the existing Python
workflow engine.

DATA FLOW
---------
User enters operational request
            ↓
HTML form sends POST request
            ↓
Flask receives request
            ↓
analyze_request()
            ↓
Structured workflow generated
            ↓
save_workflow()
            ↓
JSON persistence
            ↓
Browser redirected to dashboard
"""

from flask import Flask, redirect, render_template, request, url_for

from app import analyze_request, calculate_progress
from storage import (
    get_workflow,
    load_workflows,
    save_workflow,
    update_workflow,
)


# ===========================================================================
# APPLICATION CONFIGURATION
# ===========================================================================

app = Flask(__name__)


# ===========================================================================
# DASHBOARD DATA
# ===========================================================================


def build_dashboard_data():
    """
    Build dashboard metrics and workflow summaries.

    Presentation-specific data is calculated here rather than inside
    the HTML template.

    This keeps business logic in Python and presentation logic in HTML.
    """

    workflows = load_workflows()

    total_workflows = len(workflows)

    active_workflows = sum(
        1 for workflow in workflows if workflow["status"] == "Active"
    )

    completed_workflows = sum(
        1 for workflow in workflows if workflow["status"] == "Completed"
    )

    workflow_summaries = []

    for workflow in workflows:
        summary = {
            "id": workflow["id"],
            "request": workflow["request"],
            "created": workflow["created"],
            "status": workflow["status"],
            "progress": calculate_progress(workflow),
            "task_count": len(workflow["tasks"]),
        }

        workflow_summaries.append(summary)

    # Newest workflows appear first.
    workflow_summaries.reverse()

    return {
        "total": total_workflows,
        "active": active_workflows,
        "completed": completed_workflows,
        "workflows": workflow_summaries,
    }


# ===========================================================================
# DASHBOARD ROUTE
# ===========================================================================


@app.route("/")
def home():
    """
    Display the workflow dashboard.
    """

    dashboard = build_dashboard_data()

    return render_template(
        "index.html",
        dashboard=dashboard,
    )


# ===========================================================================
# CREATE WORKFLOW ROUTE
# ===========================================================================


@app.route("/workflows", methods=["POST"])
def create_workflow():
    """
    Create a workflow from a browser form submission.

    HTTP POST
    ---------
    POST is used when the browser sends data that changes application
    state.

    In this case, submitting the form creates and stores a new workflow.

    PROCESS
    -------
    1. Read the request field from the HTML form.
    2. Remove unnecessary surrounding whitespace.
    3. Reject empty submissions.
    4. Send valid text through the existing workflow engine.
    5. Save the generated workflow.
    6. Redirect the browser back to the dashboard.

    WHY REDIRECT?
    -------------
    Redirecting after a successful POST implements the common
    Post/Redirect/Get pattern.

    This prevents a browser refresh from accidentally submitting the
    same workflow twice.
    """
    operational_request = request.form.get(
        "request",
        "",
    ).strip()

    engine = request.form.get(
        "engine",
        "rules",
    ).strip()

    # Empty submissions do not create workflows.
    if not operational_request:
        return redirect(url_for("home"))

    # Reuse the workflow engine originally built for the CLI.
    workflow = analyze_request(
    operational_request,
    engine=engine,
)
    # Persist the generated workflow.
    save_workflow(workflow)

    # Return the user to the updated dashboard.
    return redirect(url_for("home"))

# ===========================================================================
# WORKFLOW DETAILS ROUTE
# ===========================================================================


@app.route("/workflows/<workflow_id>")
def workflow_details(workflow_id):
    """
    Display the complete details of one workflow.

    DYNAMIC ROUTES
    --------------
    The <workflow_id> portion of the URL is dynamic.

    For example:

        /workflows/WF-001
        /workflows/WF-002

    Flask extracts the workflow ID from the URL and passes it into
    this function.

    The storage layer then retrieves the matching workflow.
    """

    workflow = get_workflow(workflow_id.upper())

    if workflow is None:
        return "Workflow not found.", 404

    progress = calculate_progress(workflow)

    return render_template(
        "workflow.html",
        workflow=workflow,
        progress=progress,
    )
# ===========================================================================
# START TASK ROUTE
# ===========================================================================

@app.route(
    "/workflows/<workflow_id>/tasks/<int:task_id>/start",
    methods=["POST"],
)
def start_task(workflow_id, task_id):
    """
    Mark one workflow task as in progress.
    """

    workflow = get_workflow(workflow_id.upper())

    if workflow is None:
        return "Workflow not found.", 404

    selected_task = None

    for task in workflow["tasks"]:
        if task["id"] == task_id:
            selected_task = task
            break

    if selected_task is None:
        return "Task not found.", 404

    selected_task["status"] = "In Progress"
    workflow["status"] = "Active"

    update_workflow(workflow)

    return redirect(
        url_for(
            "workflow_details",
            workflow_id=workflow["id"],
        )
    )

# ===========================================================================
# COMPLETE TASK ROUTE
# ===========================================================================


@app.route(
    "/workflows/<workflow_id>/tasks/<int:task_id>/complete",
    methods=["POST"],
)
def complete_task(workflow_id, task_id):
    """
    Mark one workflow task as completed.
    """

    workflow = get_workflow(workflow_id.upper())

    if workflow is None:
        return "Workflow not found.", 404

    selected_task = None

    for task in workflow["tasks"]:
        if task["id"] == task_id:
            selected_task = task
            break

    if selected_task is None:
        return "Task not found.", 404

    selected_task["status"] = "Completed"

    if all(
        task["status"] == "Completed"
        for task in workflow["tasks"]
    ):
        workflow["status"] = "Completed"
    else:
        workflow["status"] = "Active"

    update_workflow(workflow)

    return redirect(
        url_for(
            "workflow_details",
            workflow_id=workflow["id"],
        )
    )

# ===========================================================================
# APPLICATION START
# ===========================================================================


if __name__ == "__main__":
    app.run(debug=True)