# Agentic Workflow System

An autonomous **Multi-Agent AI Workflow System** built with **FastAPI**, **Python**, **SQLite**, and a **locally hosted Llama 3.2 model using Ollama**. The system transforms a high-level user goal into a structured business proposal through intelligent planning, workflow orchestration, **Human-in-the-Loop (HITL)** approvals, quality evaluation, iterative rewriting, and Microsoft Word document generation.

---

# Architecture

```text
                              User
                                │
                                ▼
                         POST /plan
                                │
                                ▼
                         Planner Agent
                                │
                                ▼
                       Task Graph (DAG)
                                │
                                ▼
                 Human Approval Required
                                │
                                ▼
                  POST /approve/{run_id}
                                │
                                ▼
                   Workflow Orchestrator
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   Research Agent         Tool Router         Memory Agent
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                ▼
                          Writer Agent
                                │
                                ▼
                         Draft Proposal
                                │
                                ▼
                  Human Final Approval
                                │
                                ▼
             POST /approve-final/{run_id}
                                │
                                ▼
                 POST /generate/{run_id}
                                │
                                ▼
                     Reflection Agent
                                │
                                ▼
                  Self Evaluation Agent
                                │
                                ▼
                        Quality Score
                                │
                Score ≥ Quality Threshold ?
                      │                   │
                     Yes                  No
                      │                   │
                      ▼                   ▼
               DOCX Generator      Rewrite Agent
                                          │
                                          ▼
                                   Reflection Loop
                                          │
                                          └── Retry Until Threshold
                                                or Maximum Retries

            SQLite Memory + Structured Audit Logging
```

---

# Features

* Multi-Agent AI architecture
* Human-in-the-Loop (HITL) workflow
* Planner Agent for task planning
* Directed Acyclic Graph (DAG) based workflow generation
* Dependency-aware task execution
* Topological sorting for execution scheduling
* Research Agent
* Tool Router
* Memory Agent
* Writer Agent
* Reflection Agent
* Self Evaluation Agent
* Rewrite Agent
* Manual approval before workflow execution
* Manual approval before final document generation
* Automatic proposal generation
* Reflection-based quality improvement loop
* Configurable quality threshold
* SQLite-based workflow memory
* Structured audit logging
* Microsoft Word (.docx) generation
* RESTful APIs using FastAPI
* Local LLM inference using Ollama (Llama 3.2)

---

# Technology Stack

* Python
* FastAPI
* Pydantic
* SQLite
* Requests
* python-docx
* Ollama
* Llama 3.2
* Uvicorn

---

# Project Structure

```text
agentic-workflow/
│
├── agents/
│   ├── base.py
│   ├── planner_agent.py
│   ├── research_agent.py
│   ├── memory_agent.py
│   ├── writer_agent.py
│   ├── reflection_agent.py
│   ├── self_eval_agent.py
│   └── rewrite_agent.py
│
├── api/
│   └── routes.py
│
├── generators/
│   └── docx_generator.py
│
├── memory/
│   └── sqlite_memory.py
│
├── models/
│   └── schemas.py
│
├── orchestrator/
│   ├── reflection_loop.py
│   ├── task_graph.py
│   ├── tool_router.py
│   └── workflow_orchestrator.py
│
├── utils/
│   ├── llm_client.py
│   └── logger.py
│
├── data/
│   ├── memory.db
│   ├── audit.log
│   └── generated_docs/
│
├── config.py
├── main.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# Workflow

## Step 1 – Plan Generation

**Endpoint**

```http
POST /plan
```

The Planner Agent:

* Accepts the user's goal
* Generates a Task Graph (DAG)
* Stores workflow information in SQLite
* Sets the workflow status to **Pending Approval**

---

## Step 2 – Human Approval

**Endpoint**

```http
POST /approve/{run_id}
```

A human reviews the generated execution plan.

If approved:

* Workflow status changes to **Approved**
* Workflow execution is enabled

---

## Step 3 – Execute Workflow

**Endpoint**

```http
POST /execute/{run_id}
```

The Workflow Orchestrator:

* Computes execution waves using Topological Sorting
* Executes tasks according to dependencies
* Dispatches tasks to:

  * Research Agent
  * Tool Router
  * Memory Agent
* Stores intermediate outputs
* Writer Agent generates the proposal draft
* Updates the workflow status to **Pending Final Approval**

---

## Step 4 – Human Final Approval

**Endpoint**

```http
POST /approve-final/{run_id}
```

The generated proposal draft is reviewed.

If approved:

* Workflow status changes to **Final Approved**
* The quality refinement process begins

---

## Step 5 – Quality Improvement & Document Generation

**Endpoint**

```http
POST /generate/{run_id}
```

The approved draft passes through the following pipeline:

```text
Reflection Agent
        │
        ▼
Self Evaluation Agent
        │
        ▼
Quality Score
        │
        ▼
Score ≥ Threshold ?
      │
 ┌────┴─────┐
 │          │
Yes         No
 │           │
 ▼           ▼
DOCX     Rewrite Agent
Generator      │
               ▼
        Reflection Loop
```

The workflow stops when:

* The configured quality threshold is reached, or
* The maximum number of rewrite attempts is exceeded.

---

# API Endpoints

| Method | Endpoint                  | Description                                |
| ------ | ------------------------- | ------------------------------------------ |
| GET    | `/`                       | Health Check                               |
| POST   | `/plan`                   | Generate Task Graph                        |
| POST   | `/approve/{run_id}`       | Approve generated execution plan           |
| POST   | `/execute/{run_id}`       | Execute approved workflow                  |
| POST   | `/approve-final/{run_id}` | Approve generated proposal draft           |
| POST   | `/generate/{run_id}`      | Improve proposal quality and generate DOCX |

---

# Installation

## Clone Repository

```bash
git clone https://github.com/payaltalmale/agentic-workflow-system.git

cd agentic-workflow-system
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Install Ollama

Download Ollama from:

https://ollama.com/download

## Pull Llama 3.2

```bash
ollama pull llama3.2:3b
```

## Start Ollama

```bash
ollama run llama3.2:3b
```

## Start FastAPI

```bash
uvicorn main:app --reload --port 8000
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# Example Workflow

```text
User Goal
     │
     ▼
Planner Agent
     │
     ▼
Task Graph (DAG)
     │
     ▼
Human Approval
     │
     ▼
Workflow Orchestrator
     │
 ┌───┼───────────┐
 ▼   ▼           ▼
Research Tool  Memory
     │
     ▼
Writer Agent
     │
     ▼
Draft Proposal
     │
     ▼
Human Final Approval
     │
     ▼
Reflection Agent
     │
     ▼
Self Evaluation Agent
     │
     ▼
Quality Check
     │
 ┌───┴────┐
 │        │
Pass    Rewrite
 │        │
 ▼        ▼
DOCX  Reflection Loop
```

---

# Output

The application generates:

* Workflow execution history
* SQLite memory database
* Structured audit logs
* Final Microsoft Word (.docx) proposal

Example:

```text
data/
├── memory.db
├── audit.log
└── generated_docs/
    └── AI_Healthcare_Proposal_ab12cd.docx
```

---

# Future Enhancements

* Parallel task execution using `asyncio.gather()`
* External API integrations
* ChromaDB vector memory
* Multi-model LLM support
* Docker deployment
* Authentication & Authorization
* Real-time workflow monitoring dashboard

