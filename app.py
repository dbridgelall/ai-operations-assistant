"""
AI Operations Assistant
Version 1.1 - Rule-Based Workflow Generator

PURPOSE
-------
This application demonstrates how an unstructured operational request
can be converted into a structured workflow.

CURRENT ARCHITECTURE
--------------------
User Request
    ↓
Text Normalization
    ↓
Rule-Based Task Detection
    ↓
Structured Workflow Dictionary
    ↓
Terminal Output

WHY START WITH RULES INSTEAD OF AI?
-----------------------------------
Before introducing an LLM or external API, this version establishes
the application's core workflow logic.

This makes the application easier to:
- Understand
- Test
- Debug
- Expand

Future versions can supplement or replace these rules with
AI-powered natural-language interpretation.
"""

from datetime import date


# ===========================================================================
# WORKFLOW ANALYSIS
# ===========================================================================

def analyze_request(request):
    """
    Analyze a plain-English operational request and generate a workflow.

    Parameters
    ----------
    request : str
        The operational request entered by the user.

    Returns
    -------
    dict
        A structured workflow containing:
        - original request
        - creation date
        - workflow status
        - generated tasks

    Example
    -------
    Input:
        "Schedule candidate interviews and track confirmations."

    Generated tasks:
        1. Create interview schedule
        2. Track candidate status
        3. Send and track confirmations
        4. Review workflow and determine next action
    """

    # -----------------------------------------------------------------------
    # STEP 1: NORMALIZE USER INPUT
    # -----------------------------------------------------------------------
    #
    # Converting the request to lowercase makes keyword detection
    # case-insensitive.
    #
    # For example:
    # "Interview", "INTERVIEW", and "interview"
    # will all be interpreted the same way.

    request_lower = request.lower()

    # This list will contain the operational tasks detected by the engine.
    tasks = []

    # -----------------------------------------------------------------------
    # STEP 2: RULE-BASED TASK DETECTION
    # -----------------------------------------------------------------------
    #
    # Version 1 uses simple keyword matching.
    #
    # The basic relationship is:
    #
    # USER LANGUAGE
    #       ↓
    # KEYWORD DETECTION
    #       ↓
    # OPERATIONAL TASK
    #
    # Example:
    #
    # "We need to interview candidates."
    #
    #           ↓ detects "interview"
    #
    # "Create interview schedule"
    #
    # Future versions will use AI to understand context instead of
    # relying exclusively on predefined keywords.

    if "interview" in request_lower:
        tasks.append("Create interview schedule")

    if "candidate" in request_lower:
        tasks.append("Track candidate status")

    if "confirmation" in request_lower or "confirm" in request_lower:
        tasks.append("Send and track confirmations")

    if "committee" in request_lower:
        tasks.append("Prepare committee update")

    if "schedule" in request_lower:
        tasks.append("Review scheduling requirements")

    if "email" in request_lower:
        tasks.append("Prepare required email communication")

    if "report" in request_lower:
        tasks.append("Prepare operational report")

    if "document" in request_lower:
        tasks.append("Prepare or review documentation")

    # -----------------------------------------------------------------------
    # STEP 3: DEFAULT REVIEW TASK
    # -----------------------------------------------------------------------
    #
    # Every workflow ends with a review step.
    #
    # This also ensures the workflow contains at least one task even when
    # the rule engine does not recognize any keywords.

    tasks.append("Review workflow and determine next action")

    # -----------------------------------------------------------------------
    # STEP 4: BUILD STRUCTURED WORKFLOW DATA
    # -----------------------------------------------------------------------
    #
    # Instead of returning only a list of tasks, the application stores
    # workflow information inside a Python dictionary.
    #
    # Current structure:
    #
    # workflow
    # ├── request
    # ├── created
    # ├── status
    # └── tasks
    #
    # This structure makes future expansion easier.
    #
    # Future versions can add:
    #
    # - workflow ID
    # - priority
    # - task owner
    # - due date
    # - task status
    # - dependencies
    # - completion percentage
    #
    # The dictionary can also later be converted into JSON for APIs,
    # databases, or web applications.

    workflow = {
        "request": request,
        "created": str(date.today()),
        "status": "Active",
        "tasks": tasks,
    }

    return workflow


# ===========================================================================
# WORKFLOW DISPLAY
# ===========================================================================

def display_workflow(workflow):
    """
    Display workflow information in a readable terminal format.

    DESIGN DECISION
    ---------------
    Workflow analysis and workflow presentation are deliberately
    separated.

    analyze_request()
        Determines WHAT the workflow contains.

    display_workflow()
        Determines HOW the workflow is presented.

    This separation will allow a future web interface to use the same
    workflow engine without rewriting the underlying analysis logic.
    """

    print("\nAI OPERATIONS ASSISTANT")
    print("=" * 50)

    # -----------------------------------------------------------------------
    # WORKFLOW METADATA
    # -----------------------------------------------------------------------

    print(f"\nRequest: {workflow['request']}")
    print(f"Created: {workflow['created']}")
    print(f"Status: {workflow['status']}")

    # -----------------------------------------------------------------------
    # GENERATED TASKS
    # -----------------------------------------------------------------------

    print("\nGenerated Tasks")
    print("-" * 50)

    # enumerate() provides both:
    #
    # - the task itself
    # - a sequential task number
    #
    # start=1 creates user-friendly numbering beginning at 1 rather than 0.

    for number, task in enumerate(workflow["tasks"], start=1):
        print(f"{number}. {task}")

    # -----------------------------------------------------------------------
    # NEXT ACTION
    # -----------------------------------------------------------------------
    #
    # Version 1 considers the first generated task the next action.
    #
    # Later versions can determine this using:
    #
    # - priority
    # - deadlines
    # - dependencies
    # - workflow status
    # - AI recommendations

    print("\nNext Action")
    print("-" * 50)

    print(workflow["tasks"][0])

    print("\n" + "=" * 50)


# ===========================================================================
# APPLICATION ENTRY POINT
# ===========================================================================

def main():
    """
    Run the command-line version of the AI Operations Assistant.

    APPLICATION FLOW
    ----------------

    1. Start application
            ↓
    2. Request operational work description
            ↓
    3. Analyze request
            ↓
    4. Generate structured workflow
            ↓
    5. Display workflow

    ENVIRONMENT HANDLING
    --------------------
    A normal terminal supports Python's input() function.

    Some browser-based or cloud execution environments do not.

    If interactive input is unavailable, the application automatically
    switches to demonstration mode instead of crashing.
    """

    print("AI Operations Assistant")
    print("-" * 50)
    print("Turn an operational request into an organized workflow.\n")

    try:

        # -------------------------------------------------------------------
        # INTERACTIVE MODE
        # -------------------------------------------------------------------
        #
        # input() pauses execution and waits for the user to enter an
        # operational request.

        request = input(
            "Describe the work that needs to be completed:\n> "
        )

        # strip() removes whitespace from the beginning and end.
        #
        # If nothing meaningful was entered, we treat the request as empty.

        if not request.strip():
            raise ValueError("No operational request was entered.")

    except (OSError, EOFError, ValueError):

        # -------------------------------------------------------------------
        # DEMONSTRATION MODE
        # -------------------------------------------------------------------
        #
        # Some execution environments cannot provide interactive keyboard
        # input.
        #
        # Instead of terminating the application, we provide a realistic
        # example request so the workflow engine can still be demonstrated.

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
        print()

    # -----------------------------------------------------------------------
    # PROCESS REQUEST
    # -----------------------------------------------------------------------

    workflow = analyze_request(request)

    # -----------------------------------------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------------------------------------

    display_workflow(workflow)


# ===========================================================================
# PROGRAM START
# ===========================================================================
#
# Python files can either:
#
# 1. Be executed directly.
# 2. Be imported into another Python program.
#
# __name__ contains information about how Python loaded this file.
#
# When this file is executed directly:
#
#     __name__ == "__main__"
#
# Therefore the following condition starts the application only when
# app.py itself is executed.
#
# This becomes important later because another file will be able to:
#
#     from app import analyze_request
#
# without automatically launching the command-line program.


if __name__ == "__main__":
    main()
