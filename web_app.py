"""
AI Operations Assistant
Version 2.1 - Data-Connected Flask Dashboard

PURPOSE
-------
Provide a browser-based dashboard for the AI Operations Assistant.

Version 2.1 connects the Flask presentation layer to the application's
persistent workflow storage.

DATA FLOW
---------
workflows.json
      ↓
storage.py
      ↓
web_app.py
      ↓
Jinja template
      ↓
Browser

The dashboard can now display real workflow information instead of
hard-coded placeholder values.
"""

from flask import Flask, render_template

from app import calculate_progress
from storage import load_workflows


# ===========================================================================
# APPLICATION CONFIGURATION
# ===========================================================================

app = Flask(__name__)


# ===========================================================================
# DASHBOARD DATA
# ===========================================================================


def build_dashboard_data():
    """
    Build the data required by the dashboard.

    Returns
    -------
    dict
        Dashboard information including:
        - total workflow count
        - active workflow count
        - completed workflow count
        - workflow summaries

    DESIGN DECISION
    ---------------
    Dashboard calculations are performed in Python rather than HTML.

    The template's responsibility is presentation.

    Python's responsibility is application logic.
    """

    workflows = load_workflows()

    total_workflows = len(workflows)

    active_workflows = sum(
        1 for workflow in workflows if workflow["status"] == "Active"
    )

    completed_workflows = sum(
        1 for workflow in workflows if workflow["status"] == "Completed"
    )

    # Add progress information to each workflow summary.
    #
    # We create new dictionaries rather than modifying the stored workflow
    # objects directly. This keeps dashboard presentation data separate
    # from persisted application data.

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

    # Show newest workflows first.
    workflow_summaries.reverse()

    return {
        "total": total_workflows,
        "active": active_workflows,
        "completed": completed_workflows,
        "workflows": workflow_summaries,
    }


# ===========================================================================
# HOME ROUTE
# ===========================================================================


@app.route("/")
def home():
    """
    Render the dashboard using real application data.

    Flask passes the dashboard dictionary into Jinja.

    The template can access values such as:

        dashboard.total
        dashboard.active
        dashboard.workflows
    """

    dashboard = build_dashboard_data()

    return render_template(
        "index.html",
        dashboard=dashboard,
    )


# ===========================================================================
# APPLICATION START
# ===========================================================================


if __name__ == "__main__":
    app.run(debug=True)