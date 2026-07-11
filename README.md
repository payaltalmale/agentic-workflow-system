# Agentic Workflow System

Multi-agent pipeline matching this architecture:

```
User → POST /plan → Planner Agent → Task Graph (DAG) → Human Approval Required
     → POST /execute → Workflow Orchestrator
         → [Research Agent | Tool Router | Memory Agent] (parallel)
         → Writer Agent → Draft Document → Human Final Approval
     → POST /generate → Reflection Agent → Self Evaluation Agent
         → Quality Score > 90? → No → Rewrite Agent → (retry loop)
                              → Yes → DOCX Generator
     → SQLite Memory + Chroma Semantic Memory (persisted throughout)
     → Audit Logging (every step)
```

## Project Structure

```
agentic-workflow/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                        # FastAPI app entrypoint
├── config.py                      # Settings (env vars, thresholds, model names)
├── models/
│   └── schemas.py                 # Pydantic request/response + TaskGraph models
├── agents/
│   ├── base.py                    # BaseAgent (shared LLM call + logging)
│   ├── planner_agent.py           # Builds the Task Graph (DAG)
│   ├── research_agent.py          # Gathers info for a task node
│   ├── memory_agent.py            # Reads/writes long-term memory
│   ├── writer_agent.py            # Produces the draft document
│   ├── reflection_agent.py        # Critiques the draft
│   ├── self_eval_agent.py         # Scores quality 0-100
│   └── rewrite_agent.py           # Rewrites based on critique
├── orchestrator/
│   ├── task_graph.py              # DAG data structure + topological execution order
│   ├── tool_router.py             # Routes tool calls to the right handler
│   └── workflow_orchestrator.py   # Runs Research/Tools/Memory, then Writer
├── memory/
│   ├── sqlite_memory.py           # Structured state: runs, tasks, approvals, scores
│             
├── generators/
│   └── docx_generator.py          # Final .docx export
├── api/
│   └── routes.py                  # /plan, /execute, /generate endpoints
├── utils/
│   ├── llm_client.py              # Thin wrapper around the Anthropic API
│   └── logger.py                  # Structured audit logger → SQLite + file
└── data/                          # runtime: memory.db,  audit.log
```

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then paste your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

## Flow in practice

1. `POST /plan` — give it a goal string. Planner Agent returns a Task Graph (DAG) and the run is marked `pending_approval`. Nothing executes yet.
2. You (human) call `POST /approve/{run_id}` once you're happy with the plan.
3. `POST /execute/{run_id}` — orchestrator runs Research Agent, Tool Router, and Memory Agent per task node (respecting DAG dependencies), then the Writer Agent turns all that into a draft. Run moves to `pending_final_approval`.
4. You call `POST /approve-final/{run_id}`.
5. `POST /generate/{run_id}` — Reflection Agent critiques the draft, Self-Eval Agent scores it 0-100. If score ≤ 90, Rewrite Agent revises and it loops back through reflection (capped retries). Once score > 90, the DOCX Generator writes the final file.

Every step — plan created, approvals, each agent call, each retry, final doc — is written to the audit log (`data/audit.log` and the `audit_log` SQLite table).

## Next steps I'd suggest building in this order
1. Get `/plan` working end-to-end first (Planner Agent + Task Graph + SQLite persistence).
2. Then `/execute` (orchestrator + the 3 parallel agents + Writer).
3. Then `/generate` (reflection loop + docx).
