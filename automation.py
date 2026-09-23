import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "http://127.0.0.1:5678/webhook/operations-request",
)

logger = logging.getLogger(__name__)


def get_workflow_priority(workflow):
    """
    Determine the overall priority of a generated workflow.

    If any task is High priority, the workflow is High.
    Otherwise, if any task is Medium, the workflow is Medium.
    Otherwise, the workflow is Low.
    """

    priorities = [
        task["priority"]
        for task in workflow["tasks"]
    ]

    if "High" in priorities:
        return "High"

    if "Medium" in priorities:
        return "Medium"

    return "Low"


def send_workflow_to_n8n(workflow):
    """
    Send a generated workflow to the local n8n webhook.

    Returns True if n8n accepts the request.
    Returns False if n8n is unavailable.
    """

    payload = {
        "request": workflow["request"],
        "department": "Operations",
        "priority": get_workflow_priority(workflow),
    }

    data = json.dumps(payload).encode("utf-8")

    http_request = Request(
        N8N_WEBHOOK_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(http_request, timeout=5) as response:
            return 200 <= response.status < 300

    except (HTTPError, URLError, TimeoutError, OSError) as error:
        logger.warning(
            "Could not send workflow to n8n: %s",
            error,
        )
        return False