"""
AI Operations Assistant
Workflow Storage Module

PURPOSE
-------
Manage persistent workflow data stored as JSON.

This module separates data-storage responsibilities from the main
application logic.

RESPONSIBILITIES
----------------
- Initialize application storage
- Load saved workflows
- Save new workflows
- Retrieve workflows
- Update stored workflows
- Count saved workflows

Separating storage from app.py makes it easier to replace JSON storage
with a database in a future version.
"""

import json
from pathlib import Path


# ===========================================================================
# STORAGE CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
WORKFLOW_FILE = DATA_DIR / "workflows.json"


# ===========================================================================
# STORAGE INITIALIZATION
# ===========================================================================


def initialize_storage():
    """
    Create the data directory and workflow file when they do not exist.
    """

    DATA_DIR.mkdir(exist_ok=True)

    if not WORKFLOW_FILE.exists():
        with WORKFLOW_FILE.open("w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


# ===========================================================================
# LOAD WORKFLOWS
# ===========================================================================


def load_workflows():
    """
    Load all saved workflows from JSON storage.

    Returns
    -------
    list
        Saved workflow dictionaries.

    If the file contains invalid JSON, an empty list is returned rather
    than crashing the application.
    """

    initialize_storage()

    try:
        with WORKFLOW_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return []


# ===========================================================================
# WRITE WORKFLOWS
# ===========================================================================


def write_workflows(workflows):
    """
    Replace the stored workflow collection.

    This helper centralizes JSON writing so both workflow creation and
    workflow updates use the same persistence logic.
    """

    initialize_storage()

    with WORKFLOW_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            workflows,
            file,
            indent=4,
            ensure_ascii=False,
        )


# ===========================================================================
# SAVE NEW WORKFLOW
# ===========================================================================


def save_workflow(workflow):
    """
    Add one new workflow to persistent storage.
    """

    workflows = load_workflows()
    workflows.append(workflow)
    write_workflows(workflows)


# ===========================================================================
# RETRIEVE WORKFLOW
# ===========================================================================


def get_workflow(workflow_id):
    """
    Retrieve one workflow using its unique workflow ID.

    Returns None when no matching workflow exists.
    """

    workflows = load_workflows()

    for workflow in workflows:
        if workflow.get("id") == workflow_id:
            return workflow

    return None


# ===========================================================================
# UPDATE WORKFLOW
# ===========================================================================


def update_workflow(updated_workflow):
    """
    Replace an existing stored workflow with an updated version.

    Returns
    -------
    bool
        True when the workflow was found and updated.
        False when no matching workflow exists.
    """

    workflows = load_workflows()

    for index, workflow in enumerate(workflows):
        if workflow.get("id") == updated_workflow.get("id"):
            workflows[index] = updated_workflow
            write_workflows(workflows)
            return True

    return False


# ===========================================================================
# WORKFLOW COUNT
# ===========================================================================


def count_workflows():
    """Return the total number of stored workflows."""

    return len(load_workflows())