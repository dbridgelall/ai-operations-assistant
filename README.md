# AI Operations Assistant

A Python and Flask application that transforms natural-language operational requests into structured, prioritized, and trackable workflows, with local AI inference and automated request logging through n8n and Google Sheets.

AI Operations Assistant combines traditional application development, AI-assisted workflow generation, task management, and business process automation.

Users can generate workflows using either a deterministic Rules Engine or a locally hosted Qwen AI model, manage tasks through a Flask dashboard, and automatically record new operational requests through an n8n integration.

The application demonstrates how AI and automation can support internal operations without requiring paid cloud AI APIs.

## Overview

Operational requests often begin as unstructured instructions: coordinate onboarding, schedule interviews, prepare communications, track candidates, or organize administrative work.

AI Operations Assistant converts these requests into actionable workflows containing:

- Individual tasks and categories
- High, Medium, and Low priorities
- Task ownership and assignment
- Task lifecycle management
- Workflow completion progress
- Recommended next actions
- Persistent workflow storage

The application also integrates with n8n to automate request classification and logging in Google Sheets.

### Core Capabilities

| Capability | Description |
|---|---|
| Natural-language workflow generation | Converts operational requests into actionable tasks |
| Dual workflow engines | Supports deterministic rules and local AI inference |
| Task prioritization | Assigns High, Medium, and Low priorities |
| Task ownership | Allows users to assign and update task owners |
| Task lifecycle management | Tracks tasks through Incomplete, In Progress, and Completed states |
| Workflow progress | Automatically calculates completion progress |
| Recommended next actions | Identifies the next task to prioritize |
| Persistent storage | Saves workflows and task updates using JSON |
| n8n automation | Processes new workflow requests through an HTTP webhook |
| Google Sheets integration | Automatically records request information and priority classifications |

## Application Preview

### Workflow Dashboard

![AI Operations Assistant Dashboard](docs/images/dashboard.png)

The Flask dashboard provides workflow creation, engine selection, workflow metrics, progress tracking, and access to saved workflows.

### AI-Generated Workflow

![AI-generated workflow](docs/images/ai-workflow.png)

The Local AI engine converts operational requests into structured tasks with categories, relative priorities, and trackable statuses.

Users can manage task ownership, update task statuses, and monitor workflow completion through the web interface.

## Workflow Engines

The application supports two approaches to workflow generation.

### Rules Engine

The deterministic Rules Engine analyzes keywords in an operational request and generates predefined tasks.

This provides predictable workflow generation without requiring an AI model.

The Rules Engine is useful when consistent, repeatable workflow structures are preferred.

### Local AI Engine

The Local AI engine sends an operational request to **Qwen3 1.7B running locally through Ollama**.

The model interprets the request and decomposes it into 2–6 actionable tasks, assigning each a category and relative priority.

Python then validates the model output and converts it into the application's standardized task structure.

Because inference runs locally, workflow requests do not require a paid cloud AI API.

### Separation of Responsibilities

The AI model is responsible for interpreting and decomposing operational requests.

Python remains responsible for:

- Validating generated output
- Creating task and workflow identifiers
- Managing task ownership
- Managing task statuses
- Calculating workflow progress
- Managing application state
- Persisting workflow data

This separation allows the application to use AI for interpretation without giving the model direct control over application state.

## Key Features

### Workflow Generation

- Natural-language operational request input
- Dual workflow engines: Rules and Local AI
- Local Qwen integration through Ollama
- Structured AI output validation
- High, Medium, and Low task prioritization
- Automatic task and workflow creation

### Task Management

- Assign and update task owners
- Track tasks through Incomplete, In Progress, and Completed states
- Reopen completed tasks
- Return tasks to Incomplete when necessary
- Automatically calculate workflow completion progress
- Identify recommended next actions
- Persist task updates across application sessions

### Application Reliability

- Graceful handling of unavailable AI models
- Validation of malformed AI responses
- Controlled handling of invalid task counts
- Persistent JSON workflow storage
- Automated unit and Flask application testing

### Workflow Automation

- Flask-to-n8n integration using HTTP POST requests
- Webhook-triggered automation
- Conditional routing based on request priority
- Automated urgent and standard message generation
- Google Sheets request logging
- Separate application and automation responsibilities

## Example Workflow

**Input:**

> Coordinate onboarding for three new employees, request system access, schedule orientation, and notify their managers.

**Example Local AI output:**

| Task | Category | Priority | Status |
|---|---|---|---|
| Coordinate onboarding for three new employees | Onboarding | High | Incomplete |
| Request system access for the three employees | System Access | Medium | Incomplete |
| Schedule orientation for the three employees | Orientation | Medium | Incomplete |
| Notify managers about onboarding activities | Communication | Low | Incomplete |

The generated tasks can then be assigned, started, completed, reopened, and tracked through the Flask interface.

Workflow progress updates as tasks are completed.

## n8n Workflow Automation

AI Operations Assistant integrates with n8n to demonstrate how a Python application can initiate automated business processes.

When a user creates a workflow through the Flask application, the application sends an HTTP POST request to an n8n webhook.

The automation extracts the request details, evaluates the priority, prepares an appropriate message, and records the request in Google Sheets.

### Automation Architecture

```text
              Flask Application
                     |
                     v
              HTTP POST Request
                     |
                     v
                n8n Webhook
                     |
                     v
             Extract Request Data
                     |
                     v
              Evaluate Priority
                     |
          +----------+----------+
          |                     |
          v                     v
    High Priority          Other Priority
          |                     |
          v                     v
    Prepare Urgent        Prepare Standard
       Message                Message
          |                     |
          +----------+----------+
                     |
                     v
             Google Sheets Log
```

### Request Processing

The Flask application sends request information to n8n.

Example payload:

```json
{
  "request": "Coordinate employee onboarding",
  "department": "Operations",
  "priority": "High"
}
```

n8n evaluates the priority and routes the request through the appropriate branch.

High-priority requests generate an urgent message:

```text
URGENT REQUEST: Coordinate employee onboarding
```

Other requests generate a standard message:

```text
STANDARD REQUEST: Coordinate employee onboarding
```

Both branches record their results in Google Sheets.

### Google Sheets Request Log

The automation records the following information:

| Field | Description |
|---|---|
| request_id | n8n execution identifier |
| timestamp | Request processing timestamp |
| request | Original operational request |
| department | Department associated with the request |
| priority | Request priority |
| notification_type | URGENT or STANDARD |
| message | Generated request message |

This creates a centralized record of incoming operational requests.

**Note:** Urgent and standard messages are currently generated and logged. Email and messaging-platform notifications are potential future integrations.

### Exported n8n Workflow

The automation configuration is included in this repository:

[View Operations Request Automation](automation/operations-request-workflow.json)

The exported workflow is sanitized for public sharing.

To reproduce the automation, import the JSON file into n8n and configure your own Google Sheets credentials and destination spreadsheet.

## Application Architecture

```text
                       User
                        |
              +---------+---------+
              |                   |
              v                   v
          CLI App             Flask Web App
          app.py               web_app.py
              |                   |
              +---------+---------+
                        |
                        v
                workflow_engine.py
                        |
              +---------+---------+
              |                   |
              v                   v
         Rules Engine         Local AI
                                  |
                                  v
                            Ollama / Qwen

              Generated Workflow
                        |
                        v
                    storage.py
                        |
                        v
                 JSON Persistence


                 Flask Web App
                        |
                        v
                  automation.py
                        |
                        v
                   HTTP POST
                        |
                        v
                   n8n Webhook
                        |
                        v
                Priority Evaluation
                        |
                        v
                  Google Sheets
```

The application separates workflow interpretation, task management, persistence, web presentation, and external automation.

The shared workflow engine allows both the CLI and Flask application to use the same core workflow logic.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13 | Core application development |
| Flask 3.1 | Web application and routing |
| Ollama Python Client | Local AI model communication |
| Qwen3 1.7B | Natural-language workflow generation |
| HTML / CSS | Web interface |
| Jinja | Dynamic HTML templates |
| JSON | Workflow persistence and data exchange |
| n8n | Workflow automation and conditional routing |
| HTTP / Webhooks | Flask-to-n8n communication |
| Google Sheets | Automated operational request logging |
| Docker | Local n8n environment |
| unittest | Automated application testing |
| Git / GitHub | Version control and project documentation |

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dbridgelall/ai-operations-assistant.git
cd ai-operations-assistant
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

The project currently uses:

```text
Flask==3.1.3
ollama==0.6.2
```

## Local AI Setup

The Rules Engine works without Ollama.

To use the Local AI engine, install Ollama and download the Qwen model.

After installing Ollama:

```bash
ollama pull qwen3:1.7b
```

Verify that the model is available:

```bash
ollama list
```

The application communicates with the locally running model through the Ollama Python client.

Local AI generation may take longer on systems running the model entirely on CPU.

## Running the Web Application

Start the Flask application:

```bash
python web_app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### Using the Application

1. Enter an operational request.
2. Select Rules Engine or Local AI — Qwen.
3. Generate the workflow.
4. Open the generated workflow.
5. Assign task owners.
6. Start, complete, or reopen tasks.
7. Track progress from the dashboard.

Workflow changes are saved locally and persist across application sessions.

## Optional n8n Automation Setup

The Flask application can be used independently of n8n.

To enable automated request logging, a running n8n instance and a configured Google Sheets connection are required.

### 1. Start n8n

Run your existing n8n Docker container:

```bash
docker start n8n
```

Alternatively, configure a new n8n instance using the official n8n documentation.

Open the n8n interface, typically available at:

```text
http://127.0.0.1:5678
```

### 2. Import the Workflow

Import:

```text
automation/operations-request-workflow.json
```

### 3. Configure Google Sheets

Create a Google Sheets document with the following column headers:

```text
request_id
timestamp
request
department
priority
notification_type
message
```

Configure the Google Sheets node to use your own credentials and spreadsheet.

### 4. Activate the Workflow

Publish or activate the workflow so its production webhook can receive requests.

The application sends requests to:

```text
http://127.0.0.1:5678/webhook/operations-request
```

This endpoint assumes n8n is running locally on its default port.

When a new workflow is created in Flask, the application sends the request to n8n for processing and logging.

Task status changes and ownership updates do not create additional request-log entries.

## Testing

Run the automated test suite:

```bash
python -m unittest discover -v
```

The test suite covers:

- Workflow generation
- Task creation and prioritization
- Workflow progress calculation
- Persistence behavior
- Flask routes
- Task status updates
- AI integration through mocking
- Malformed AI responses
- Task-count validation
- Workflow engine selection
- Graceful AI failure handling

AI calls are mocked during automated testing so the test suite does not require the local model to perform inference.

The application has also been manually tested with the n8n webhook and Google Sheets integration.

## Local AI Reliability

AI-generated data is treated as untrusted input.

The application validates model responses before creating a workflow.

Invalid JSON, malformed responses, and invalid task counts are rejected through controlled error handling.

If Local AI cannot generate a valid workflow, the web interface displays an error instead of saving a broken workflow.

The Rules Engine provides a deterministic alternative when local AI inference is not required.

## Project Structure

```text
ai-operations-assistant/
|
├── app.py
├── web_app.py
├── workflow_engine.py
├── automation.py
├── storage.py
├── requirements.txt
├── README.md
|
├── automation/
│   └── operations-request-workflow.json
|
├── templates/
│   ├── index.html
│   └── workflow.html
|
├── static/
│   └── style.css
|
├── docs/
│   └── images/
│       ├── dashboard.png
│       └── ai-workflow.png
|
├── test_app.py
└── test_web_app.py
```

Local workflow data is excluded from version control.

## Design Principles

### Separation of Concerns

The application separates workflow interpretation, business logic, storage, presentation, and external automation.

This allows individual components to evolve without requiring the entire application to be redesigned.

### Deterministic Application State

The AI model generates proposed tasks, but Python validates the results and manages workflow state.

### Local-First AI

Qwen runs locally through Ollama, avoiding the need for paid cloud AI inference.

### Reusable Workflow Logic

The CLI and Flask interface share the same workflow engine.

### Event-Driven Automation

Creating a workflow triggers an HTTP request to n8n.

Subsequent task-management actions remain within the application rather than repeatedly triggering the external request-logging automation.

### Portfolio Reproducibility

The repository includes application source code, automated tests, setup instructions, and a sanitized n8n workflow export.

## Future Enhancements

Potential future improvements include:

- Database-backed persistence
- Workflow and task editing
- Email or Slack notifications for urgent requests
- Configurable departments and workflow templates
- Additional local AI model options
- Export and reporting tools
- Asynchronous AI generation
- Expanded integration testing
- Automated task-assignment rules
- Operational analytics and reporting dashboards

## Project Status

**Core application and initial automation integration implemented.**

The project currently includes:

- Flask and CLI interfaces
- Shared Python workflow engine
- Deterministic and local AI workflow generation
- Task ownership and lifecycle management
- Workflow persistence and progress tracking
- AI response validation and error handling
- Automated application testing
- n8n webhook integration
- Priority-based request processing
- Google Sheets request logging

Current development is focused on expanding automation capabilities, improving usability, and strengthening the project's technical documentation and portfolio presentation.
