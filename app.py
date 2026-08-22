"""
AI Operations Assistant
Version 1.0 - Rule-Based Workflow Generator

Purpose:
    This application demonstrates how an unstructured operational request
    can be converted into a structured workflow.

Current Architecture:
    User Request
        ↓
    Text Normalization
        ↓
    Rule-Based Task Detection
        ↓
    Structured Workflow Dictionary
        ↓
    Terminal Output

Why start with rules instead of AI?
    Before introducing an LLM or external API, this version establishes
    the application's core workflow logic. This makes the system easier
    to understand, test, and improve.

Future versions will replace or supplement the rule-based analysis with
AI-powered request interpretation.
"""

from datetime import date


# ---------------------------------------------------------------------------
# WORKFLOW ANALYSIS
# ---------------------------------------------------------------------------

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

    Process
    -------
    1. Normalize the user's text.
    2. Search for operational keywords.
    3. Match those keywords to predefined actions.
    4. Store the resulting tasks in a list.
    5. Package everything into a structured dictionary.

    Example
    -------
    Input:
        "Schedule candidate interviews and track confirmations."

    Generated tasks:
        - Create interview schedule
        - Track candidate status
        - Send and track confirmations
    """

    # Convert the request to lowercase.
    #
    # This allows keyword matching to work regardless of capitalization.
    # For example, "Interview", "INTERVIEW", and "interview" will all match.
    request_lower = request.lower()

    # This list will hold each task detected from the user's request.
    tasks = []

    # -----------------------------------------------------------------------
    # RULE-BASED TASK DETECTION
    # -----------------------------------------------------------------------
    #
    # Version 1 uses simple keyword rules.
    #
    # These rules establish the basic relationship:
    #
    #     user language → operational meaning → structured task
    #
    # Later versions can use an LLM to understand context instead of relying
    # exclusively on exact keywords.

    if "interview" in request_lower:
        tasks.append("Create interview schedule")

    if "candidate" in request_lower:
        tasks.append("Track candidate status")

    if "confirmation" in request_lower or "confirm" in request_lower:
        tasks.append("Send and track confirmations")

    if "committee" in request_lower:
        tasks.append("Prepare committee update")

    # Every operational workflow should end with some form of review.
    #
    # Including a default review task also ensures that the workflow is never
    # completely empty when the program does not recognize any keywords.
    tasks.append("Review workflow and determine next action")

    # -----------------------------------------------------------------------
    # STRUCTURED WORKFLOW
    # -----------------------------------------------------------------------
    #
    # Instead of returning only a list of tasks, we organize the information
    # into a Python dictionary.
    #
    # This is important because future versions can easily add fields such as:
    #
    # - priority
    # - owner
    # - due date
    # - task ID
    # - completion status
    #
    # The dictionary could also later be converted to JSON and stored in a
    # database or sent through an API.

    workflow = {
        "request": request,
        "created": str(date.today()),
        "status": "Active",
        "tasks": tasks,
    }

    return workflow


# ---------------------------------------------------------------------------
# WORKFLOW DISPLAY
# ---------------------------------------------------------------------------

def display_workflow(workflow):
    """
    Display a structured workflow in a readable terminal format.

    Keeping display logic separate from workflow analysis is intentional.

    The analyze_request() function determines WHAT the workflow contains.

    The display_workflow() function determines HOW that workflow is shown.

    This separation will make it easier to replace the terminal interface
    with a web application later without rebuilding the workflow engine.
    """

    print("\nAI OPERATIONS ASSISTANT")
    print("=" * 40)

    # Display workflow metadata.
    print(f"\nRequest: {workflow['request']}")
    print(f"Created: {workflow['created']}")
    print(f"Status: {workflow['status']}")

    print("\nTasks")
    print("-" * 40)

    # enumerate() gives each task a number while looping through the list.
    #
    # start=1 makes the numbering user-friendly:
    #
    # 1. First task
    # 2. Second task
    #
    # instead of Python's normal zero-based numbering.

    for number, task in enumerate(workflow["tasks"], start=1):
        print(f"{number}. {task}")

    # For Version 1, the first generated task becomes the recommended
    # next action.
    #
    # Future versions will calculate the next action using priority,
    # deadlines, dependencies, and workflow status.

    print("\nNext Action")
    print("-" * 40)
    print(workflow["tasks"][0])


# ---------------------------------------------------------------------------
# APPLICATION ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    """
    Run the command-line version of the AI Operations Assistant.

    Application flow:

        1. Ask the user for an operational request.
        2. Send the request to the workflow analyzer.
        3. Receive structured workflow data.
        4. Display the generated workflow.
    """

    print("AI Operations Assistant")
    print("Turn an operational request into an organized workflow.\n")

    # input() pauses the program and waits for the user to enter a request.
    request = input(
        "Describe the work that needs to be completed:\n> "
    )

    # Convert the user's request into structured workflow data.
    workflow = analyze_request(request)

    # Present the resulting workflow to the user.
    display_workflow(workflow)


# ---------------------------------------------------------------------------
# PROGRAM START
# ---------------------------------------------------------------------------
#
# Python files can either:
#
# 1. Be executed directly.
# 2. Be imported into another Python program.
#
# This condition ensures main() runs only when this file is executed directly.
#
# That's useful later because we'll be able to import analyze_request()
# into a web application or test file without automatically starting the
# command-line interface.

if __name__ == "__main__":
    main()
